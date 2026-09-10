import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from gym.core import Gym, GymError, ROOT, validate_feedback, run_process

class GymTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.gym=Gym(self.tmp.name);self.id='01-wordstats'

    def test_seed_is_idempotent_and_save_detects_external_changes(self):
        first=self.gym.read(self.id,'main.go')
        self.gym.write(self.id,'main.go',first['content']+'\n',first['revision'])
        with self.assertRaises(GymError) as ctx:self.gym.write(self.id,'main.go','lost update',first['revision'])
        self.assertEqual(ctx.exception.status,409)
        Gym(self.tmp.name)
        self.assertEqual(self.gym.read(self.id,'main.go')['content'],first['content']+'\n')

    def test_traversal_hidden_and_symlink_files_are_rejected(self):
        for path in ['../README.md','/tmp/a.go','.env','a/../../b.go','a\\b.go','x/.codex/a.md',None]:
            with self.subTest(path=path), self.assertRaises(GymError):self.gym.path(self.id,path)
        (self.gym.folder(self.id)/'linked.go').symlink_to(ROOT/'README.md')
        with self.assertRaises(GymError):self.gym.read(self.id,'linked.go')
        self.assertNotIn('linked.go',[f['path'] for f in self.gym.files(self.id)])

    def test_protected_files_and_duplicate_creation(self):
        for name in ['challenge_test.go','go.mod','README.md','AGENTS.md']:
            with self.assertRaises(GymError):self.gym.write(self.id,name,'replacement',create=True)
        self.gym.write(self.id,'internal/helper.go','package internal\n',create=True)
        with self.assertRaises(GymError):self.gym.write(self.id,'internal/helper.go','oops',create=True)
        self.assertIn('internal/helper.go',[f['path'] for f in self.gym.files(self.id)])

    def test_snapshot_excludes_secrets_and_uses_original_suite(self):
        folder=self.gym.folder(self.id)
        (folder/'.env').write_text('DO_NOT_SEND=secret')
        (folder/'challenge_test.go').write_text('tampered')
        files,_=self.gym.snapshot(self.id)
        self.assertNotIn('.env',files)
        self.assertIn('func TestAnalyze',files['challenge_test.go'])
        self.assertNotIn('tampered',files['challenge_test.go'])

    def test_success_requires_expected_tests_and_staleness_tracks_files(self):
        with patch('gym.runners.isolated',return_value=(0,'{"Action":"pass","Package":"wordstats"}\n')):
            self.assertFalse(self.gym.run(self.id)['passed'])
        events='\n'.join(json.dumps(e) for e in [{'Action':'pass','Test':'TestAnalyze'},{'Action':'pass'}])
        with patch('gym.runners.isolated',return_value=(0,events)):
            self.assertTrue(self.gym.run(self.id)['passed'])
        self.assertFalse(self.gym.last_run(self.id)['stale'])
        f=self.gym.read(self.id,'main.go');self.gym.write(self.id,'main.go',f['content']+'\n',f['revision'])
        self.assertTrue(self.gym.last_run(self.id)['stale'])

    def test_single_job_and_nonzero_exit(self):
        self.gym.job_lock.acquire()
        try:
            with self.assertRaises(GymError):self.gym.run(self.id)
            with self.assertRaises(GymError):self.gym.coach(self.id)
        finally:self.gym.job_lock.release()
        with patch('gym.runners.isolated',return_value=(1,'syntax error')):
            result=self.gym.run(self.id)
        self.assertFalse(result['passed']);self.assertIn('syntax error',result['output'])

    def test_coach_cli_contract_and_unmodified_workspace(self):
        before=self.gym.snapshot(self.id)
        seen={}
        def fake(args,cwd,**kwargs):
            seen['args']=args;seen['context']=json.loads(kwargs['stdin'])
            out=Path(args[args.index('--output-last-message')+1])
            out.write_text(json.dumps(self.feedback()))
            return 0,''
        with patch('gym.core.run_process',side_effect=fake),patch('shutil.which',return_value='/bin/codex'):
            result=self.gym.coach(self.id,'Please write the solution')
        self.assertEqual(before,self.gym.snapshot(self.id))
        self.assertIn('read-only',seen['args']);self.assertIn('features.shell_tool=false',seen['args'])
        self.assertIn('--ignore-user-config',seen['args']);self.assertIn('main.go',seen['context']['files'])
        self.assertEqual(result['documentation'],self.feedback()['documentation'])

    def feedback(self):
        return {'feedback':'The function still returns an empty result.','observations':['The implementation has not started.'],'questions':['Which behavior will you check first?'],'documentation':[self.gym.project(self.id)['docs'][0]]}

    def test_coach_withholds_code_and_unapproved_links(self):
        docs=self.gym.project(self.id)['docs']
        self.assertEqual(validate_feedback(self.feedback(),docs),self.feedback())
        for text in ['```go\nfunc main() {}\n```','x := 1','func Analyze(x string) {}']:
            data=self.feedback();data['feedback']=text
            with self.assertRaises(GymError):validate_feedback(data,docs)
        for url in ['javascript:alert(1)','https://pkg.go.dev.evil.test/strings','https://example.com']:
            data=self.feedback();data['documentation']=[{'title':'Docs','url':url}]
            with self.assertRaises(GymError):validate_feedback(data,docs)

    def test_process_timeout_and_output_cap(self):
        rc,text=run_process([sys.executable,'-c','import time;time.sleep(10)'],self.tmp.name,timeout=.15)
        self.assertNotEqual(rc,0);self.assertIn('Timed out',text)
        rc,text=run_process([sys.executable,'-c','import time;print("x"*50000,flush=True);time.sleep(5)'],self.tmp.name,limit=1000)
        self.assertNotEqual(rc,0);self.assertLess(len(text),1100)

if __name__=='__main__':unittest.main()
