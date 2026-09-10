"""Loopback-only HTTP server for a trusted personal coding workspace."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import mimetypes
import threading
import os
import uuid
import signal
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from .core import Gym, GymError, ROOT

class Handler(BaseHTTPRequestHandler):
    gym: Gym
    instance = uuid.uuid4().hex
    def reply(self,status,data):
        payload=json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(payload)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers();self.wfile.write(payload)

    def guarded(self):
        # Reject DNS rebinding and cross-site calls. No wildcard CORS.
        host=self.headers.get('Host','')
        allowed={f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}','127.0.0.1:4310','localhost:4310'}
        if host not in allowed: raise GymError('Unrecognized host.',403)
        origin=self.headers.get('Origin')
        if origin and origin not in {f'http://{h}' for h in allowed}:
            raise GymError('Cross-origin requests are not allowed.',403)
        if self.headers.get('Sec-Fetch-Site')=='cross-site':
            raise GymError('Cross-site requests are not allowed.',403)

    def do_GET(self):
        try:
            self.guarded()
            url=urlsplit(self.path);q=parse_qs(url.query)
            if url.path=='/api/generation':return self.reply(200,self.gym.generator.get(q.get('id',[''])[0]))
            if url.path=='/api/projects':return self.reply(200,{'projects':self.gym.projects()})
            if url.path=='/api/files':return self.reply(200,{'files':self.gym.files(q.get('project',[''])[0])})
            if url.path=='/api/file':return self.reply(200,self.gym.read(q.get('project',[''])[0],q.get('path',[''])[0]))
            if url.path=='/api/health':return self.reply(200,{'ok':True})
            if url.path=='/api/identity':return self.reply(200,{'app':'omagym','apiVersion':1,'instance':self.instance,'pid':os.getpid(),'root':str(self.gym.root.resolve())})
            if url.path=='/api/busy':return self.reply(200,{'busy':self.gym.job_lock.locked()})
            if url.path=='/api/status':return self.reply(200,self.gym.status(q.get('project',[''])[0]))
            if url.path.startswith('/api/'):raise GymError('Unknown endpoint.',404)
            static=ROOT/'dist/client';name=url.path.lstrip('/') or 'index.html'
            path=(static/name).resolve()
            if not path.is_relative_to(static.resolve()) or not path.is_file():raise GymError('Page not found. Build the dashboard with npm run build.',404)
            payload=path.read_bytes();self.send_response(200)
            self.send_header('Content-Type',mimetypes.guess_type(path)[0] or 'application/octet-stream')
            self.send_header('Content-Length',str(len(payload)))
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Cache-Control','no-cache')
            self.end_headers();self.wfile.write(payload)
        except GymError as e:self.reply(e.status,{'error':str(e)})
        except (OSError,ValueError):self.reply(500,{'error':'Could not read the workspace. Check local file permissions.'})

    def do_POST(self):
        try:
            self.guarded()
            if self.headers.get('X-Code-Gym')!='1' or self.headers.get_content_type()!='application/json':
                raise GymError('JSON requests from the gym are required.',403)
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<1_000_000:raise GymError('Request size is invalid.',413)
            body=json.loads(self.rfile.read(length))
            if not isinstance(body,dict):raise GymError('Expected a JSON object.')
            id=body.get('project','')
            if self.path=='/api/file':data=self.gym.write(id,body.get('path',''),body.get('content'),body.get('revision'),body.get('create',False))
            elif self.path=='/api/run':data=self.gym.run(id)
            elif self.path=='/api/preview':data=self.gym.preview(id)
            elif self.path=='/api/generate':data=self.gym.generator.start(body.get('prompt'),body.get('track'),body.get('timebox','A weekend'))
            elif self.path=='/api/coach':data=self.gym.coach(id,body.get('question',''))
            else:raise GymError('Unknown endpoint.',404)
            self.reply(200,data)
        except GymError as e:self.reply(e.status,{'error':str(e)})
        except (ValueError,TypeError):self.reply(400,{'error':'Invalid request.'})
        except OSError:self.reply(500,{'error':'Could not complete the local operation. Check file permissions and installed tools.'})

    def log_message(self,format,*args):
        # Requests contain no source or review text in their log entries.
        super().log_message(format,*args)

class PreviewHandler(BaseHTTPRequestHandler):
    root: Path
    def do_GET(self):
        name=urlsplit(self.path).path.lstrip('/')
        if name.endswith('/'):name+='index.html'
        path=(self.root/name).resolve()
        if not path.is_relative_to(self.root.resolve()) or not path.is_file():
            self.send_error(404);return
        content=path.read_bytes();self.send_response(200)
        self.send_header('Content-Type',mimetypes.guess_type(path)[0] or 'application/octet-stream')
        self.send_header('Content-Length',str(len(content)))
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Security-Policy',"default-src 'self' data: blob:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors http://127.0.0.1:4310 http://localhost:4310")
        self.end_headers();self.wfile.write(content)
    def log_message(self,*args):pass

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=4311);args=parser.parse_args()
    Handler.gym=Gym()
    from .generation import Generator
    PreviewHandler.root=Handler.gym.runtime/'previews'
    preview=ThreadingHTTPServer(('127.0.0.1',4312),PreviewHandler)
    try:server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    except Exception:
        preview.server_close();raise
    Handler.gym.generator=Generator(Handler.gym)
    Handler.gym.generator.cleanup_interrupted()
    threading.Thread(target=preview.serve_forever,daemon=True).start()
    def stop_when_idle(signum, frame):
        # Close the check/stop race: once acquired, no new operation can start.
        if Handler.gym.job_lock.acquire(blocking=False):
            threading.Thread(target=server.shutdown, daemon=True).start()
        else:
            print('Omagym is busy; finish the current operation before stopping.', flush=True)
    signal.signal(signal.SIGTERM, stop_when_idle)
    print(f'Omagym: http://127.0.0.1:{args.port}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close();preview.shutdown();preview.server_close()

if __name__=='__main__':main()
