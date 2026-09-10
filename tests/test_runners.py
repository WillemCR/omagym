"""Runner contracts tested without executing learner or generated code."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from gym.core import GymError, ROOT
from gym.runners import execute, isolated, browser_ready


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.folder = self.root/'exercise'; self.folder.mkdir()
        self.runtime = self.root/'runtime'; self.runtime.mkdir()

    def run_output(self, runner, output, expected=None, rc=0):
        project = {'id': 'fixture', 'track': runner, 'runner': runner,
                   'checks': expected if expected is not None else ['required'],
                   'testFiles': ['challenge.test.js']}
        files = {'main.txt': 'learner data'}
        with patch('gym.runners.shutil.which', return_value='/usr/bin/tool'), \
             patch('gym.runners.isolated', return_value=(rc, output)) as process:
            result = execute(project, files, self.folder, self.runtime)
        self.assertEqual((self.folder/'main.txt').read_text(), 'learner data')
        return result, process.call_args

    def test_go_requires_actual_expected_checks_and_zero_exit(self):
        for output, rc, passed, observed in [
            ('{"Action":"pass","Package":"challenge"}', 0, False, False),
            ('{"Action":"skip","Test":"required"}', 0, False, True),
            ('{"Action":"pass","Test":"required"}', 1, False, True),
            ('{"Action":"pass","Test":"required"}', 0, True, True),
        ]:
            with self.subTest(output=output, rc=rc):
                result, call = self.run_output('go', output, rc=rc)
                self.assertEqual(result['passed'], passed)
                self.assertEqual(result['checksObserved'], observed)
                self.assertIn('-race', call.args[0])
                self.assertEqual(call.args[3]['GOPROXY'], 'off')

    def test_go_discovers_original_suite_and_reports_leaf_subtests(self):
        project = {'id': 'old-go', 'track': 'go', 'runner': 'go', 'testFiles': ['challenge_test.go']}
        files = {'challenge_test.go': 'func TestLegacy(t *testing.T) {}\n'}
        output = '\n'.join(json.dumps(e) for e in [
            {'Action': 'pass', 'Test': 'TestLegacy/case'},
            {'Action': 'pass', 'Test': 'TestLegacy'},
            {'Output': 'ok package\n'},
        ])
        with patch('gym.runners.shutil.which', return_value='/usr/bin/go'), \
             patch('gym.runners.isolated', return_value=(0, output)):
            result = execute(project, files, self.folder, self.runtime)
        self.assertTrue(result['passed'])
        self.assertEqual(result['tests'], [{'name': 'TestLegacy/case', 'action': 'pass'}])
        self.assertIn('ok package', result['output'])

    def test_rust_ignored_and_failed_cases_cannot_pass(self):
        for status, passed in [('ok', True), ('ignored', False), ('FAILED', False)]:
            result, call = self.run_output('rust', f'test required ... {status}\n')
            self.assertEqual(result['passed'], passed)
            self.assertIn('--offline', call.args[0])

    def test_javascript_reporter_events_and_skips(self):
        for action, passed in [('pass', True), ('fail', False), ('skip', False)]:
            result, call = self.run_output('javascript', json.dumps({'name': 'required', 'action': action}))
            self.assertEqual(result['passed'], passed)
            self.assertIn('--test-reporter', call.args[0])
        result, _ = self.run_output('javascript', '{malformed\n'+json.dumps({'output': 'diagnostic'}))
        self.assertFalse(result['passed']); self.assertIn('diagnostic', result['output'])

    def test_ruby_and_rails_parse_minitest_status(self):
        for runner in ['ruby', 'rails']:
            for status, passed in [('.', True), ('F', False), ('E', False), ('S', False)]:
                with self.subTest(runner=runner, status=status):
                    result, _ = self.run_output(runner, 'warning: noisy Ruby output\nOMAGYM_RESULT '+json.dumps({'name': 'test_required', 'action': 'pass' if status=='.' else 'skip' if status=='S' else 'fail'})+'\n', ['test_required'])
                    self.assertEqual(result['passed'], passed)

    def test_browser_uses_owned_config_and_requires_each_named_result(self):
        project = {'id': 'web', 'track': 'react', 'runner': 'browser', 'checks': ['visible', 'interactive'], 'testFiles': ['challenge.spec.js']}
        def fake(args, folder, runtime, env, **kwargs):
            self.assertIn(str(ROOT/'gym/runtime/playwright.config.mjs'), args)
            self.assertEqual(env['OMAGYM_TRACK'], 'react')
            report = {'suites': [{'specs': [{'title': 'visible', 'tests': [{'results': [{'status': 'passed'}]}]}],
                                  'suites': [{'specs': [{'title': 'interactive', 'tests': [{'results': [{'status': 'skipped'}]}]}]}]}]}
            (folder/'.test-report.json').write_text(json.dumps(report))
            return 0, ''
        with patch('gym.runners.shutil.which', return_value='/usr/bin/tool'), patch('gym.runners.isolated', side_effect=fake):
            result = execute(project, {'index.html': '<h1>Starter</h1>', 'package.json': '{"scripts":{"unsafe":"ignored"}}'}, self.folder, self.runtime)
        self.assertFalse(result['passed']); self.assertTrue(result['checksObserved'])
        self.assertEqual(json.loads((self.folder/'package.json').read_text()), {'type': 'module'})
        self.assertEqual((self.folder/'node_modules').resolve(), (ROOT/'node_modules').resolve())

    def test_browser_startup_requires_success_and_ready_marker(self):
        for rc, output, accepted in [(0, 'OMAGYM_BROWSER_READY', True),
                                      (1, 'OMAGYM_BROWSER_READY', False),
                                      (0, 'vite started but page crashed', False)]:
            with self.subTest(rc=rc, output=output), tempfile.TemporaryDirectory(dir=self.root) as folder:
                with patch('gym.runners.shutil.which', return_value='/usr/bin/node'), \
                     patch('gym.runners.isolated', return_value=(rc, output)) as run:
                    args = ({'track': 'react'}, {'index.html': '<h1>Starter</h1>'}, Path(folder), self.runtime)
                    if accepted:
                        browser_ready(*args)
                    else:
                        with self.assertRaises(GymError): browser_ready(*args)
                self.assertIn(str(ROOT/'gym/runtime/browser-smoke.mjs'), run.call_args.args[0])
                self.assertEqual(run.call_args.kwargs['timeout'], 60)

    def test_isolation_uses_clean_env_private_network_and_readonly_dependencies(self):
        def which(name): return '/usr/bin/'+name
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'never-forward', 'SSH_AUTH_SOCK': '/secret/agent'}), \
             patch('gym.runners.shutil.which', side_effect=which), \
             patch('gym.runners.run_process', return_value=(0, 'ok')) as process:
            self.assertEqual(isolated(['/usr/bin/go', 'test'], self.folder, self.runtime, {'GOPROXY': 'off'}), (0, 'ok'))
        args, cwd = process.call_args.args
        env = process.call_args.kwargs['env']
        self.assertIn('--unshare-all', args)
        self.assertIn('--die-with-parent', args)
        self.assertNotIn('OPENAI_API_KEY', env); self.assertNotIn('SSH_AUTH_SOCK', env)
        self.assertEqual(env['HOME'], '/home/learner')
        self.assertEqual(env['GOPROXY'], 'off')
        i = args.index(str(ROOT/'node_modules'))
        self.assertEqual(args[i-1], '--ro-bind')
        self.assertIn(str(self.runtime/'runner-cache'), args)
        self.assertEqual(cwd, self.folder)

    def test_missing_isolator_fails_closed(self):
        with patch('gym.runners.shutil.which', return_value=None), patch('gym.runners.run_process') as process:
            with self.assertRaises(GymError) as err:
                isolated(['/usr/bin/go'], self.folder, self.runtime, {})
        self.assertEqual(err.exception.status, 503); process.assert_not_called()

    def test_actual_node_reporter_marks_skip_and_todo_as_incomplete(self):
        node = shutil.which('node')
        if not node: self.skipTest('Node.js is unavailable')
        fixture = self.folder/'reporter.test.mjs'
        fixture.write_text("import test from 'node:test';\ntest('skipped',{skip:true},()=>{});\ntest('todo',{todo:true},()=>{});\ntest('real',()=>{});\n")
        run = subprocess.run([node, '--test', '--test-isolation=none', '--test-reporter', str(ROOT/'gym/runtime/node-reporter.mjs'), str(fixture)],
                             capture_output=True, text=True, timeout=15)
        self.assertEqual(run.returncode, 0, run.stderr)
        events = {e['name']: e['action'] for line in run.stdout.splitlines() if (e := json.loads(line)).get('name')}
        self.assertEqual(events, {'skipped': 'skip', 'todo': 'skip', 'real': 'pass'})

    def test_actual_ruby_reporter_handles_pass_fail_skip_and_noisy_output(self):
        ruby = shutil.which('ruby')
        if not ruby: self.skipTest('Ruby is unavailable')
        fixture = self.folder/'reporter_test.rb'
        fixture.write_text("require 'minitest/autorun'\nclass ReporterFixture < Minitest::Test\n  def test_pass; warn 'a diagnostic'; assert true; end\n  def test_fail; assert_equal 1, 2; end\n  def test_skip; skip 'not ready'; end\nend\n")
        env = dict(os.environ, GEM_HOME=str(ROOT/'.runtime/gems'), GEM_PATH=str(ROOT/'.runtime/gems'),
                   BUNDLE_GEMFILE=str(ROOT/'Gemfile'), BUNDLE_FROZEN='true')
        run = subprocess.run([ruby, '-rbundler/setup', '-r'+str(ROOT/'gym/runtime/ruby-reporter.rb'), str(fixture)],
                             env=env, capture_output=True, text=True, timeout=15)
        self.assertNotEqual(run.returncode, 0)
        events = {}
        for line in run.stdout.splitlines():
            if 'OMAGYM_RESULT ' in line:
                event = json.loads(line.split('OMAGYM_RESULT ', 1)[1])
                events[event['name']] = event['action']
        self.assertEqual(events, {'test_pass': 'pass', 'test_fail': 'fail', 'test_skip': 'skip'}, run.stdout+run.stderr)



if __name__ == '__main__': unittest.main()
