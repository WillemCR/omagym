"""Quickshell module integration and fail-closed runner reporting."""
import copy
import json
import shutil
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gym import modules
from gym.core import Gym, GymError, ROOT, validate_feedback
from gym.generation import validate
from gym.runners import execute


class QuickshellTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.gym = Gym(self.root)
        self.project = self.gym.project('quickshell-01-badge')

    def test_module_is_opt_in_and_never_installs_other_toolchains(self):
        with patch.object(modules, 'check_tools') as check, patch.object(modules, 'install_ruby') as gems:
            modules.configure(self.root, ['quickshell'])
        check.assert_called_once_with(['quickshell'])
        gems.assert_not_called()
        self.assertEqual(modules.enabled(self.root), ['quickshell'])
        self.assertFalse(modules.info(self.root, 'rails')['enabled'])
        modules.configure(self.root, ['quickshell'], action='remove')
        with self.assertRaisesRegex(GymError, 'modules add quickshell'):
            self.gym.run(self.project['id'])

    def test_five_projects_have_editable_qml_protected_suites_and_official_docs(self):
        projects = [p for p in self.gym.catalog if p['track'] == 'quickshell']
        self.assertEqual(len(projects), 5)
        for p in projects:
            with self.subTest(project=p['id']):
                files, _ = self.gym.snapshot(p['id'])
                self.assertIn('Main.qml', files)
                self.assertIn('shell.qml', files)
                self.assertTrue(self.gym.editable('Main.qml', p['id']))
                self.assertFalse(self.gym.editable('challenge_test.qml', p['id']))
                (self.gym.folder(p['id'])/'challenge_test.qml').write_text('tampered')
                restored, _ = self.gym.snapshot(p['id'])
                self.assertEqual(restored['challenge_test.qml'], files['challenge_test.qml'])
                self.assertGreaterEqual(len(p['checks']), 4)
                self.assertTrue(all(d['url'].startswith(('https://quickshell.org/', 'https://doc.qt.io/')) for d in p['docs']))
        self.gym.write(self.project['id'], 'Extra.qml', 'import QtQuick\nItem {}\n', create=True)
        self.assertIn('Extra.qml', self.gym.snapshot(self.project['id'])[0])

    def test_runner_requires_every_check_success_exit_and_completion(self):
        p = dict(self.project, checks=['test_a', 'test_b'])
        event = lambda name, action: ' DEBUG qml: OMAGYM_QML_RESULT '+json.dumps(dict(name=name,action=action))+'\n'
        for output, code, accepted in [
            (event('test_a','pass')+event('test_b','pass')+'OMAGYM_QML_COMPLETE',0,True),
            (event('test_a','pass')+'OMAGYM_QML_COMPLETE',0,False),
            (event('test_a','pass')+event('test_b','fail')+'OMAGYM_QML_COMPLETE',0,False),
            (event('test_a','pass')+event('test_b','pass'),0,False),
            (event('test_a','pass')+event('test_b','pass')+'OMAGYM_QML_COMPLETE',1,False),
            ('QML syntax error',0,False),
        ]:
            with self.subTest(output=output), tempfile.TemporaryDirectory(dir=self.root) as folder:
                with patch('gym.runners.os.access', return_value=True), patch('gym.runners.isolated', return_value=(code,output)) as run:
                    result = execute(p, {'Main.qml':'import QtQuick\nItem {}'}, Path(folder), self.root)
                self.assertEqual(result['passed'],accepted)
                args, _, _, env = run.call_args.args
                self.assertEqual(args[0],'/usr/bin/quickshell')
                self.assertIn(str(ROOT/'gym/runtime/quickshell-runner.qml'),args)
                self.assertEqual(env['QT_QPA_PLATFORM'],'offscreen')
                self.assertNotIn('WAYLAND_DISPLAY',env)
                self.assertNotIn('DBUS_SESSION_BUS_ADDRESS',env)
                self.assertEqual(env['XDG_RUNTIME_DIR'], '/tmp/omagym-qml')

    def test_generated_quickshell_protects_tests_and_reference_separation(self):
        p = self.project
        files, _ = self.gym.snapshot(p['id'])
        data = {key: copy.deepcopy(p[key]) for key in ['title','summary','level','skills','requirements','docs','entry','testFiles','checks']}
        data['files'] = [dict(path=name,content=content) for name,content in files.items()]
        data['referenceFiles'] = [dict(path='Main.qml',content='import QtQuick\nItem {}')]
        meta, published, reference = validate(data,'quickshell','custom-qml')
        self.assertEqual(meta['runner'],'quickshell')
        self.assertNotEqual(published['Main.qml'],reference['Main.qml'])
        data['referenceFiles'].append(dict(path='challenge_test.qml',content='import QtQuick\nQtObject {}'))
        with self.assertRaises(GymError): validate(data,'quickshell','custom-qml')
        data['referenceFiles'].pop()
        data['files'].append(dict(path='extra_test.qml',content='import QtQuick\nQtObject {}'))
        with self.assertRaises(GymError): validate(data,'quickshell','custom-qml')

    def test_qml_solutions_are_withheld_from_coach_feedback(self):
        for code in ['Rectangle { color: "red" }', 'property int count: 4']:
            data = dict(feedback=code, observations=[], questions=[], documentation=[self.project['docs'][0]])
            with self.assertRaises(GymError): validate_feedback(data,self.project['docs'])

    @unittest.skipUnless(Path('/usr/bin/quickshell').is_file() and shutil.which('bwrap'), 'Local Quickshell/Bubblewrap integration check')
    def test_actual_runtime_handles_syntax_errors_missing_cases_and_empty_assertions(self):
        p = dict(self.project, checks=['test_fixture'])
        fixtures = [
            ('import QtQuick\nItem { broken syntax', 'import QtQuick\nQtObject {}', False),
            ('import QtQuick\nItem {}', 'import QtQuick\nQtObject {}', True),
            ('import QtQuick\nItem {}', 'import QtQuick\nQtObject { function test_fixture(s,t) {} }', True),
        ]
        for main, suite, observed in fixtures:
            with self.subTest(main=main, suite=suite), tempfile.TemporaryDirectory(dir=self.root) as folder:
                result = execute(p, {'Main.qml':main, 'challenge_test.qml':suite}, Path(folder), self.root)
                self.assertFalse(result['passed'])
                self.assertEqual(result['checksObserved'],observed)
                self.assertLess(result['elapsed'],10, result['output'])


if __name__ == '__main__': unittest.main()
