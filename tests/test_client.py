from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch

from gym.client import Client, atomic_json, process_stamp
from gym.core import GymError, ROOT


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/'.runtime').mkdir()

    def test_identity_rejects_foreign_service_and_does_not_spawn(self):
        class Foreign(BaseHTTPRequestHandler):
            def do_GET(self):
                payload=b'{"app":"someone-else"}'
                self.send_response(200);self.end_headers();self.wfile.write(payload)
            def log_message(self,*args):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Foreign)
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        try:
            client=Client(self.root,server.server_port)
            with patch('gym.client.subprocess.Popen') as spawn,self.assertRaisesRegex(GymError,'already in use'):
                client.ensure()
            spawn.assert_not_called()
        finally:server.shutdown();server.server_close();worker.join()

    def test_exited_backend_record_is_cleared_without_signalling(self):
        client=Client(self.root)
        atomic_json(client.runtime/'server-process.json',{'pid':123,'process':{'start':'old'}})
        (client.runtime/'server.pid').write_text('123\n')
        for stamp in ({'start':'new'}, None):
            with patch('gym.client.process_stamp',return_value=stamp),patch('gym.client.os.kill') as kill:
                if (client.runtime/'server-process.json').exists():
                    self.assertEqual(client.stop(),{'stopped':False,'stale':True})
            kill.assert_not_called()
        self.assertFalse((client.runtime/'server-process.json').exists())
        self.assertFalse((client.runtime/'server.pid').exists())

    def test_launcher_ignores_gym_packages_in_the_working_directory(self):
        decoy=self.root/'gym';decoy.mkdir()
        (decoy/'__init__.py').write_text('raise SystemExit("decoy imported")\n')
        run=subprocess.run([str(ROOT/'bin/omagym'),'--help'],cwd=self.root,capture_output=True,text=True,timeout=30)
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertIn('usage: omagym',run.stdout)

    def test_invalid_record_means_no_stop(self):
        client=Client(self.root)
        atomic_json(client.runtime/'server-process.json',{'pid':123})
        with patch('gym.client.os.kill') as kill:
            with self.assertRaisesRegex(GymError,'No process was stopped'):client.stop()
        kill.assert_not_called()

    def test_busy_server_cannot_be_stopped(self):
        client=Client(self.root)
        record={'pid':123,'process':{'start':'same'},'instance':'same','root':str(self.root)}
        atomic_json(client.runtime/'server-process.json',record)
        with patch('gym.client.process_stamp',return_value=record['process']),patch.object(client,'identity',return_value=record),patch.object(client,'request',return_value={'busy':True}),patch('gym.client.os.kill') as kill:
            with self.assertRaisesRegex(GymError,'operation is running'):client.stop()
        kill.assert_not_called()

    def test_http_mutation_uses_required_headers_and_preserves_arguments(self):
        seen={}
        class Backend(BaseHTTPRequestHandler):
            def do_POST(self):
                seen['headers']=self.headers;seen['body']=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                self.send_response(409);self.end_headers();self.wfile.write(b'{"error":"Busy"}')
            def log_message(self,*args):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Backend)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with self.assertRaises(GymError) as error:
                Client(self.root,server.server_port).request('/coach',{'question':'$(do not execute) `anything`'})
            self.assertEqual(error.exception.status,409)
            self.assertEqual(seen['headers']['X-Code-Gym'],'1')
            self.assertEqual(seen['body']['question'],'$(do not execute) `anything`')
        finally:server.shutdown();server.server_close();thread.join()

    def test_invalid_process_stamp_is_unavailable(self):
        self.assertIsNone(process_stamp(None))


if __name__=='__main__':unittest.main()
