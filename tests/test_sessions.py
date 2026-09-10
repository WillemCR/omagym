import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

from gym.client import Client, atomic_json
from gym.core import Gym, GymError
from gym.cli import main, plain
from gym.desktop import Desktop, matching
from gym.sessions import Sessions


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='omagym test space ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.gym = Gym(self.root)
        self.client = Client(self.root)
        self.client.status = self.gym.status
        self.sessions = Sessions(self.client)
        self.id = '01-wordstats'

    def test_terminal_session_preserves_files_and_infers_project(self):
        before = self.gym.snapshot(self.id)
        record = self.sessions.start(self.id, terminal_only=True)
        self.assertTrue(record['terminalOnly'])
        self.assertEqual(self.sessions.resolve(cwd=self.root), self.id)
        self.assertEqual(self.sessions.resolve(cwd=self.root/'workspaces'/self.id/'subfolder'), self.id)
        with patch('gym.sessions.available', return_value=False): self.sessions.end(self.id)
        self.assertEqual(before, self.gym.snapshot(self.id))
        with self.assertRaises(GymError): self.sessions.resolve(cwd=self.root)

    def test_ambiguous_sessions_and_invalid_ids(self):
        self.sessions.start(self.id, terminal_only=True)
        self.sessions.start('02-tasklist', terminal_only=True) if any(p['id']=='02-tasklist' for p in self.gym.catalog) else self.sessions.start(self.gym.catalog[1]['id'], terminal_only=True)
        with self.assertRaises(GymError): self.sessions.resolve(cwd=self.root)
        with self.assertRaises(GymError): self.sessions.read('../outside')

    def test_status_external_create_delete_and_feedback_staleness(self):
        initial = self.gym.status(self.id)
        atomic_json(self.gym.runtime/(self.id+'-feedback.json'), {'fingerprint':initial['fingerprint'],'feedback':'review'})
        self.assertFalse(self.gym.status(self.id)['feedback']['stale'])
        extra = self.gym.folder(self.id)/'extra.go'; extra.write_text('package main\n')
        changed = self.gym.status(self.id)
        self.assertIn('extra.go', changed['files']); self.assertTrue(changed['feedback']['stale'])
        extra.unlink()
        self.assertEqual(initial['fingerprint'], self.gym.status(self.id)['fingerprint'])

    def test_external_save_during_snapshot_retries_instead_of_mixing(self):
        read = self.gym.read
        changed = False
        def editing(id, name):
            nonlocal changed
            result = read(id, name)
            if name == 'main.go' and not changed:
                changed = True
                (self.gym.folder(id)/name).write_text(result['content']+'\n// external save\n')
            return result
        with patch.object(self.gym, 'read', side_effect=editing): files, _ = self.gym.snapshot(self.id)
        self.assertIn('external save', files['main.go'])

    def test_continuously_changing_files_have_clear_error(self):
        read = self.gym.read
        def editing(id, name):
            result = read(id, name)
            if name == 'main.go': (self.gym.folder(id)/name).write_text(result['content']+'\n')
            return result
        with patch.object(self.gym, 'read', side_effect=editing), self.assertRaisesRegex(GymError, 'changed while reading'):
            self.gym.snapshot(self.id)

    def test_desktop_resume_avoids_duplicate_windows(self):
        launched = []
        window = {'address':'0x1','pid':10,'initialClass':'test','stableId':'1'}
        with patch('gym.sessions.available',return_value=True), patch('gym.sessions.hypr',return_value={'name':'1'}), patch('gym.sessions.Desktop') as klass:
            launcher = klass.return_value; launcher.workspace='omagym-'+self.id
            launcher.alive.side_effect = [{}, {r: {'window':window} for r in ('editor','terminal','companion')}]
            launcher.launch.side_effect = lambda role: launched.append(role) or {'state':'open','window':window}
            first = self.sessions.start(self.id); second = self.sessions.start(self.id)
        self.assertEqual(first['id'], second['id'])
        self.assertEqual(launched, ['editor','terminal','companion'])

    def test_simultaneous_starts_share_one_session(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            records = list(pool.map(lambda _: self.sessions.start(self.id,terminal_only=True), range(2)))
        self.assertEqual(records[0]['id'], records[1]['id'])
        self.assertEqual(len(self.sessions.active()),1)

    def test_terminal_only_resume_keeps_no_editor_choice(self):
        with patch('gym.sessions.available',return_value=True), patch('gym.sessions.hypr',return_value={'name':'1'}), patch('gym.sessions.Desktop') as klass:
            launcher=klass.return_value;launcher.workspace='omagym-'+self.id;launcher.alive.return_value={}
            launcher.launch.return_value={'state':'failed'}
            self.sessions.start(self.id,no_editor=True)
            record=self.sessions.start(self.id)
        self.assertEqual(record['roles'],['terminal','companion'])

    def test_missing_compositor_falls_back_without_spawning(self):
        with patch('gym.sessions.available',return_value=False),patch('gym.sessions.Desktop') as desktop:
            record=self.sessions.start(self.id)
        self.assertTrue(record['terminalOnly']);desktop.assert_not_called()

    def test_stale_compositor_cannot_adopt_old_windows(self):
        d=Desktop(self.root,self.id,'http://127.0.0.1:4310/')
        with patch.dict('os.environ',{'HYPRLAND_INSTANCE_SIGNATURE':'new'}),patch('gym.desktop.hypr') as query:
            self.assertEqual(d.alive({'compositor':'old','components':{}}),{})
        query.assert_not_called()

    def test_corrupt_and_interrupted_records_do_not_cause_duplicate_launches(self):
        atomic_json(self.sessions.path(self.id),{'project':self.id,'id':'test','components':[]})
        self.assertIsNone(self.sessions.read(self.id))
        atomic_json(self.sessions.path(self.id),{'project':self.id,'id':'test','components':{'terminal':{'state':'launching'}}})
        self.assertEqual(self.sessions.read(self.id)['components']['terminal']['state'],'unverified')

    def test_window_identity_does_not_match_recycled_pid(self):
        record={'address':'0x1','pid':2,'initialClass':'foot','stableId':'old'}
        self.assertFalse(matching(record,dict(record,stableId='new')))

    def test_desktop_arguments_preserve_spaces_without_shell(self):
        d = Desktop(self.root, self.id, 'http://127.0.0.1:4310/')
        marker=f'org.omagym.terminal.{self.id}'
        client={'address':'0xabc','pid':123,'initialClass':marker,'class':marker,'stableId':'1','workspace':{'name':d.workspace}}
        with patch('gym.desktop.hypr',side_effect=[[],[client]]),patch.object(d,'focus'),patch('gym.desktop.subprocess.Popen') as popen:
            d.launch('terminal')
        argv=popen.call_args.args[0]
        self.assertIn('--dir='+str(self.root/'workspaces'/self.id),argv)
        self.assertNotIn('shell',popen.call_args.kwargs)

    def test_cli_removes_terminal_escape_sequences(self):
        self.assertEqual(plain('hello\x1b]52;c;clipboard\x07\x1b[31m world\x1b[0m\x00\x9b'), 'hello world')

    def test_cli_failure_exit_codes(self):
        with patch('gym.cli.Client') as klass:
            klass.return_value.ensure.side_effect=GymError('busy',409)
            self.assertEqual(main(['test','--project',self.id,'--json']),3)
            klass.return_value.ensure.side_effect=GymError('offline',503)
            self.assertEqual(main(['test','--project',self.id,'--json']),2)


class InstallerTests(unittest.TestCase):
    def test_install_uninstall_ownership_and_repeatability(self):
        spec=importlib.util.spec_from_file_location('installer',Path(__file__).resolve().parents[1]/'scripts/install-desktop.py')
        installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
        with tempfile.TemporaryDirectory() as directory:
            prefix=Path(directory)
            installer.install(prefix);installer.install(prefix)
            link=prefix/'bin/omagym'; self.assertTrue(link.is_symlink())
            entry=prefix/'share/applications/org.omagym.desktop'
            original=entry.read_text();entry.write_text(original+'# user change\n')
            with self.assertRaises(RuntimeError):installer.install(prefix,True)
            self.assertTrue(link.is_symlink())
            entry.write_text(original);installer.install(prefix,True);installer.install(prefix,True)
            self.assertFalse(link.exists());self.assertFalse(entry.exists())


if __name__=='__main__': unittest.main()
