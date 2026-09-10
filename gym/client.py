"""One local backend, shared by the browser and all command-line sessions."""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, build_opener, ProxyHandler

from .core import ROOT, GymError


@contextmanager
def file_lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield


def atomic_json(path, data):
    tmp = path.with_name(path.name+f'.{os.getpid()}.tmp')
    try:
        tmp.write_text(json.dumps(data, indent=2)+'\n')
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


def process_stamp(pid):
    try:
        stat = Path(f'/proc/{int(pid)}/stat').read_text().rsplit(')', 1)[1].split()
        if stat[0] == 'Z':
            return None
        return {'start': stat[19], 'command': Path(f'/proc/{int(pid)}/cmdline').read_bytes().decode().split('\0')[:-1]}
    except (OSError, ValueError, TypeError):
        return None


class Client:
    def __init__(self, root=ROOT, port=4310):
        self.root = Path(root).resolve()
        self.runtime = self.root/'.runtime'
        self.port = port
        self.url = f'http://127.0.0.1:{port}'
        self.opener = build_opener(ProxyHandler({}))

    def request(self, path, body=None, *, timeout=240):
        req = Request(self.url+'/api'+path,
                      data=json.dumps(body).encode() if body is not None else None,
                      headers={'Content-Type': 'application/json', 'X-Code-Gym': '1'})
        try:
            with self.opener.open(req, timeout=timeout) as response:
                return json.loads(response.read())
        except HTTPError as e:
            try:
                message = json.loads(e.read()).get('error', str(e))
            except (ValueError, AttributeError):
                message = str(e)
            finally:
                e.close()
            raise GymError(message, e.code) from e
        except (URLError, TimeoutError, ConnectionError, OSError) as e:
            raise GymError('The local backend could not be reached. If an operation was running, its outcome is unknown; check status before retrying.', 503) from e
        except (ValueError, AttributeError) as e:
            raise GymError('The local service returned an invalid response.', 502) from e

    def identity(self):
        value = self.request('/identity', timeout=2)
        if not isinstance(value, dict) or value.get('app') != 'omagym' or value.get('apiVersion') != 1 or value.get('root') != str(self.root):
            raise GymError('This port belongs to another service or an incompatible Omagym. Stop the old Omagym manually if upgrading.', 409)
        return value

    def ensure(self):
        self.runtime.mkdir(exist_ok=True)
        with file_lock(self.runtime/'server.lock'):
            try:
                return self.identity()
            except GymError as error:
                # A listening port is never ours to replace, even if health fails.
                for port in (self.port, 4312):
                    with socket.socket() as probe:
                        # Match HTTPServer's reuse policy: recently closed HTTP
                        # connections must not look like a foreign listener.
                        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        try:
                            probe.bind(('127.0.0.1', port))
                        except OSError:
                            raise GymError(f'Port {port} is already in use. {error}', 409) from error
            python = self.root/'.venv/bin/python'
            if not python.is_file() or not (self.root/'dist/client/index.html').is_file():
                raise GymError('Omagym needs its local environment and dashboard build. Follow the project README setup.', 503)
            with (self.runtime/'server.log').open('ab') as log:
                proc = subprocess.Popen([str(python), '-u', '-m', 'gym.server', '--port', str(self.port)],
                                        cwd=self.root, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                        start_new_session=True)
            stamp = process_stamp(proc.pid)
            for _ in range(80):
                if proc.poll() is not None:
                    raise GymError(f'Backend startup failed. See {self.runtime / "server.log"}.', 503)
                try:
                    info = self.identity()
                    if info['pid'] != proc.pid:
                        raise GymError('Another process claimed the port during startup.', 409)
                    atomic_json(self.runtime/'server-process.json', dict(info, process=stamp))
                    (self.runtime/'server.pid').write_text(str(proc.pid)+'\n')
                    return info
                except GymError:
                    time.sleep(.1)
            # Terminate only the still-live child of this specific startup attempt.
            if proc.poll() is None:
                proc.terminate()
                try: proc.wait(timeout=5)
                except subprocess.TimeoutExpired: proc.kill(); proc.wait()
            raise GymError('Backend startup timed out. See .runtime/server.log.', 503)

    def stop(self):
        with file_lock(self.runtime/'server.lock'):
            try:
                record = json.loads((self.runtime/'server-process.json').read_text())
            except (OSError, ValueError):
                raise GymError('This backend was not started by the Omagym launcher; use its documented stop command.', 409)
            if not isinstance(record,dict):
                raise GymError('The backend ownership record is invalid. No process was stopped.',409)
            if process_stamp(record.get('pid')) != record.get('process') or not record.get('process'):
                raise GymError('The recorded backend is no longer running. No process was stopped.', 409)
            info = self.identity()
            if any(info.get(k) != record.get(k) for k in ('pid', 'instance', 'root')):
                raise GymError('Backend identity changed. No process was stopped.', 409)
            if self.request('/busy', timeout=2)['busy']:
                raise GymError('An exercise operation is running. Wait for it before stopping the server.', 409)
            os.kill(record['pid'], signal.SIGTERM)
            for _ in range(50):
                if process_stamp(record['pid']) != record['process']:
                    (self.runtime/'server-process.json').unlink(missing_ok=True)
                    (self.runtime/'server.pid').unlink(missing_ok=True)
                    return {'stopped': True}
                time.sleep(.1)
            raise GymError('The backend is still running or finishing an operation. Check server status before retrying.', 503)

    def status(self, project):
        return self.request('/status?'+urlencode({'project': project}))
