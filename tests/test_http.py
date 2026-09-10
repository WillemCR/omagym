import json
from http.server import ThreadingHTTPServer
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from gym.core import Gym, GymError
from gym.server import Handler

class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        handler=type('TestHandler',(Handler,),{'gym':Gym(cls.tmp.name),'log_message':lambda *args:None})
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.url=f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join();cls.tmp.cleanup()
    def request(self,path,body=None,headers=None):
        req=Request(self.url+path,data=json.dumps(body).encode() if body is not None else None,headers=headers or {})
        try:r=urlopen(req,timeout=5)
        except HTTPError as e:r=e
        with r:return r.status,json.loads(r.read())
    def test_read_and_save_cycle(self):
        code,data=self.request('/api/projects');self.assertEqual(code,200);self.assertEqual(len(data['projects']),len(self.server.RequestHandlerClass.gym.catalog));self.assertEqual(sum(p['track']=='go' for p in data['projects']),20)
        code,file=self.request('/api/file?project=01-wordstats&path=main.go');self.assertEqual(code,200)
        code,saved=self.request('/api/file',{'project':'01-wordstats','path':'main.go','content':file['content']+'\n','revision':file['revision']},{'Content-Type':'application/json','X-Code-Gym':'1'})
        self.assertEqual(code,200);self.assertNotEqual(saved['revision'],file['revision'])

    def test_identity_and_selected_project_status(self):
        code,info=self.request('/api/identity')
        self.assertEqual(code,200);self.assertEqual(info['app'],'omagym');self.assertEqual(info['apiVersion'],1)
        code,status=self.request('/api/status?project=01-wordstats')
        self.assertEqual(code,200);self.assertEqual(status['project']['id'],'01-wordstats')
        self.assertIn('main.go',status['files']);self.assertIn('fingerprint',status)
        self.assertEqual(self.request('/api/status?project=missing')[0],404)
        self.assertEqual(self.request('/api/status?project=01-wordstats',headers={'Origin':'https://evil.example'})[0],403)
    def test_reject_foreign_origin_and_rebinding(self):
        for headers in [{'Host':'evil.example'},{'Origin':'https://evil.example'},{'Sec-Fetch-Site':'cross-site'}]:
            with self.subTest(headers=headers):self.assertEqual(self.request('/api/projects',headers=headers)[0],403)
    def test_reject_unmarked_mutations_and_invalid_paths(self):
        body={'project':'01-wordstats','path':'main.go','content':'bad'}
        self.assertEqual(self.request('/api/file',body,{'Content-Type':'application/json'})[0],403)
        self.assertEqual(self.request('/api/file?project=01-wordstats&path=../README.md')[0],400)
        self.assertEqual(self.request('/api/file?project=unknown&path=main.go')[0],404)
    def test_bad_body_and_types(self):
        headers={'Content-Type':'application/json','X-Code-Gym':'1'}
        self.assertEqual(self.request('/api/file',[],headers)[0],400)
        self.assertEqual(self.request('/api/file',{'project':'01-wordstats','path':None,'content':''},headers)[0],400)

    def test_generate_forwards_project_request_and_default_timebox(self):
        gym=self.server.RequestHandlerClass.gym
        generator=Mock(spec=['start','get'])
        queued={'id':'job-123','status':'queued','message':'Preparing project designer'}
        generator.start.return_value=queued
        headers={'Content-Type':'application/json','X-Code-Gym':'1'}
        prompt='Build a weekend reading-list dashboard.'
        with patch.object(gym,'generator',generator,create=True):
            code,data=self.request('/api/generate',{'prompt':prompt,'track':'react','timebox':'Two days'},headers)
            self.assertEqual((code,data),(200,queued))
            generator.start.assert_called_once_with(prompt,'react','Two days')
            generator.start.reset_mock()
            code,data=self.request('/api/generate',{'prompt':prompt,'track':'vue'},headers)
            self.assertEqual((code,data),(200,queued))
            generator.start.assert_called_once_with(prompt,'vue','A weekend')

    def test_generation_status_and_missing_job(self):
        gym=self.server.RequestHandlerClass.gym
        generator=Mock(spec=['start','get'])
        complete={'id':'job-123','status':'complete','projectId':'custom-123','title':'Weekend planner'}
        generator.get.return_value=complete
        with patch.object(gym,'generator',generator,create=True):
            code,data=self.request('/api/generation?id=job-123')
            self.assertEqual((code,data),(200,complete))
            generator.get.assert_called_once_with('job-123')
            generator.get.side_effect=GymError('Generation not found.',404)
            code,data=self.request('/api/generation?id=missing')
            self.assertEqual(code,404)
            self.assertEqual(data,{'error':'Generation not found.'})
            generator.get.assert_called_with('missing')

    def test_preview_returns_generated_path(self):
        gym=self.server.RequestHandlerClass.gym
        preview={'path':'/react-01-counter/','fingerprint':'saved-source-digest'}
        with patch.object(gym,'preview',return_value=preview) as operation:
            code,data=self.request('/api/preview',{'project':'react-01-counter'},
                                   {'Content-Type':'application/json','X-Code-Gym':'1'})
        self.assertEqual((code,data),(200,preview))
        operation.assert_called_once_with('react-01-counter')

    def test_generator_and_preview_reject_unmarked_mutations_before_dispatch(self):
        gym=self.server.RequestHandlerClass.gym
        generator=Mock(spec=['start','get'])
        with patch.object(gym,'generator',generator,create=True), patch.object(gym,'preview') as preview:
            for path,body in [('/api/generate',{'prompt':'Build a weekend reading-list dashboard.','track':'react'}),
                              ('/api/preview',{'project':'react-01-counter'})]:
                with self.subTest(path=path):
                    self.assertEqual(self.request(path,body,{'Content-Type':'application/json'})[0],403)
            generator.start.assert_not_called()
            preview.assert_not_called()

if __name__=='__main__':unittest.main()
