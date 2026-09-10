import json
import io
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gym import modules
from gym.core import Gym, GymError
from gym.generation import Generator
from gym.client import Client
from gym.cli import main


class ModuleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_go_only_never_installs_or_checks_ruby(self):
        with patch.object(modules, 'check_tools') as check, patch.object(modules, 'install_ruby') as install:
            selected = modules.configure(self.root, ['go'])
        self.assertEqual(selected, ['go'])
        check.assert_called_once_with(['go'])
        install.assert_not_called()
        self.assertFalse(modules.info(self.root, 'ruby')['enabled'])
        self.assertTrue(modules.info(self.root, 'go')['enabled'])

    def test_ruby_does_not_install_rails_and_can_be_added_later(self):
        with patch.object(modules, 'check_tools'), patch.object(modules, 'install_ruby') as install:
            modules.configure(self.root, ['go'])
            self.assertEqual(modules.configure(self.root, ['ruby'], action='add'), ['go', 'ruby'])
        install.assert_called_once_with(self.root, False, None)
        self.assertFalse(modules.info(self.root, 'rails')['enabled'])

    def test_rails_includes_ruby_without_installing_two_bundles(self):
        with patch.object(modules, 'check_tools'), patch.object(modules, 'install_ruby') as install:
            self.assertEqual(modules.configure(self.root, ['rails']), ['ruby', 'rails'])
        install.assert_called_once_with(self.root, True, None)
        with patch.object(modules, 'check_tools') as check, patch.object(modules, 'install_ruby') as install:
            self.assertEqual(modules.configure(self.root, ['rails'], action='remove'), ['ruby'])
        check.assert_not_called(); install.assert_not_called()

    def test_removal_preserves_all_files_and_disables_dependent_rails(self):
        with patch.object(modules, 'check_tools'), patch.object(modules, 'install_ruby'):
            modules.configure(self.root, ['rails'])
        for name in ['workspaces/ruby-01/main.rb', 'generated/custom/exercise.json', '.runtime/gems/keep']:
            path = self.root/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text('keep')
        self.assertEqual(modules.configure(self.root, ['ruby'], action='remove'), [])
        self.assertEqual((self.root/'workspaces/ruby-01/main.rb').read_text(), 'keep')
        self.assertEqual((self.root/'.runtime/gems/keep').read_text(), 'keep')
        self.assertTrue((self.root/'generated/custom/exercise.json').exists())

    def test_failed_setup_preserves_previous_selection(self):
        with patch.object(modules, 'check_tools'):
            modules.configure(self.root, ['javascript'])
        with patch.object(modules, 'check_tools', side_effect=RuntimeError('Ruby is missing')):
            with self.assertRaisesRegex(RuntimeError, 'Ruby is missing'):
                modules.configure(self.root, ['ruby'], action='add')
        self.assertEqual(modules.enabled(self.root), ['javascript'])

    def test_missing_tools_cannot_invoke_package_manager(self):
        with patch.object(modules.os, 'access', return_value=False), patch.object(modules, 'command') as command:
            with self.assertRaisesRegex(RuntimeError, 'has not changed your system'):
                modules.check_tools(['go'])
        command.assert_not_called()

    def test_unconfigured_manual_checkout_retains_access_but_first_add_is_explicit(self):
        self.assertEqual(modules.enabled(self.root), list(modules.MODULES))
        with patch.object(modules, 'check_tools'):
            self.assertEqual(modules.configure(self.root, ['javascript'], action='add'), ['javascript'])

    def test_web_module_enables_five_tracks(self):
        with patch.object(modules, 'check_tools'):
            modules.configure(self.root, ['web'])
        for track in ['react', 'vue', 'html', 'html-css', 'tailwind']:
            self.assertTrue(modules.info(self.root, track)['enabled'])
        self.assertFalse(modules.info(self.root, 'javascript')['enabled'])

    def test_disabled_module_blocks_runner_and_generator_before_agent_or_compiler(self):
        gym = Gym(self.root)
        modules.configure(self.root, [], action='set')
        with patch('gym.runners.execute') as execute:
            with self.assertRaisesRegex(GymError, 'omagym modules add go'):
                gym.run('01-wordstats')
        execute.assert_not_called()
        generator = Generator(gym)
        with self.assertRaisesRegex(GymError, 'module is not enabled'):
            generator.start('Build a useful testable project', 'go')
        self.assertFalse(gym.job_lock.locked())
        self.assertFalse(gym.status('01-wordstats')['project']['module']['enabled'])
        self.assertEqual(len(gym.projects()), 52)

    def test_checklist_preserves_selection_and_expands_rails(self):
        from subprocess import CompletedProcess
        with patch.object(modules.sys.stdin, 'isatty', return_value=True), patch.object(modules.shutil, 'which', return_value='/usr/bin/gum'), patch.object(modules.subprocess, 'run', return_value=CompletedProcess([], 0, 'Go\nRuby on Rails · includes Ruby\n')) as run:
            self.assertEqual(modules.choose(['go', 'web']), ['go', 'ruby', 'rails'])
        args = run.call_args.args[0]
        self.assertIn('--no-limit', args)
        initial = args[args.index('--selected')+1].split(',')
        self.assertEqual(initial, ['Go', 'Web (HTML / CSS / React / Vue / Tailwind)'])
        self.assertIn('[x] ', args)

    def test_checklist_can_confirm_no_modules_and_preserves_empty_default(self):
        from subprocess import CompletedProcess
        with patch.object(modules.sys.stdin, 'isatty', return_value=True), patch.object(modules.shutil, 'which', return_value='/usr/bin/gum'), patch.object(modules.subprocess, 'run', return_value=CompletedProcess([], 0, '\n')) as run:
            self.assertEqual(modules.choose([]), [])
            args = run.call_args.args[0]
            self.assertEqual(args[args.index('--selected')+1], '')
            modules.choose()
            args = run.call_args.args[0]
            self.assertEqual(args[args.index('--selected')+1], 'Go')

    def test_cancelled_checklist_cannot_stop_backend_or_change_modules(self):
        from subprocess import CompletedProcess
        modules.configure(self.root, ['javascript'])
        with patch('gym.cli.ROOT', self.root), patch('gym.cli.Client') as client, patch.object(modules.sys.stdin, 'isatty', return_value=True), patch.object(modules.shutil, 'which', return_value='/usr/bin/gum'), patch.object(modules.subprocess, 'run', return_value=CompletedProcess([], 130, '')):
            self.assertEqual(main(['modules', 'choose']), 130)
        client.return_value.identity.assert_not_called()
        client.return_value.stop.assert_not_called()
        self.assertEqual(modules.enabled(self.root), ['javascript'])

    def test_ruby_runner_prefers_small_bundle_and_rails_keeps_full_bundle(self):
        (self.root/'.runtime/gems-ruby').mkdir(parents=True)
        (self.root/'.runtime/gems-ruby/omagym-ready').write_text('verified')
        ruby_gems, ruby_gemfile = modules.ruby_bundle(self.root, 'ruby')
        rails_gems, rails_gemfile = modules.ruby_bundle(self.root, 'rails')
        self.assertEqual(ruby_gems.name, 'gems-ruby')
        self.assertEqual(ruby_gemfile, self.root/'modules/ruby/Gemfile')
        self.assertEqual(rails_gems.name, 'gems')
        self.assertEqual(rails_gemfile, self.root/'Gemfile')

    def test_module_command_restarts_owned_backend_and_reports_selection(self):
        with patch('gym.cli.ROOT', self.root), patch('gym.cli.Client') as client, redirect_stdout(io.StringIO()) as output:
            result = main(['modules', 'add', 'javascript', '--json'])
        self.assertEqual(result, 0)
        client.return_value.stop.assert_called_once()
        client.return_value.ensure.assert_called_once()
        self.assertEqual(modules.enabled(self.root), ['javascript'])
        self.assertTrue(next(m for m in json.loads(output.getvalue())['modules'] if m['id']=='javascript')['enabled'])

    def test_busy_backend_blocks_module_change(self):
        with patch('gym.cli.ROOT', self.root), patch('gym.cli.Client') as client, redirect_stdout(io.StringIO()):
            client.return_value.stop.side_effect = GymError('An exercise is busy', 409)
            self.assertEqual(main(['modules', 'add', 'javascript', '--json']), 3)
        self.assertFalse(modules.config_path(self.root).exists())

    def test_backend_restart_keeps_verified_node_ahead_of_manager_shims(self):
        binary = self.root/'node/bin/node'; binary.parent.mkdir(parents=True); binary.touch(); binary.chmod(0o755)
        runtime = self.root/'.runtime'; runtime.mkdir()
        (runtime/'plugin-ready.json').write_text(json.dumps({'nodeExecutable': str(binary)}))
        with patch.dict(modules.os.environ, {'PATH': '/manager/shims:/usr/bin'}):
            env = Client(self.root).environment()
        self.assertEqual(env['PATH'].split(':')[:2], [str(binary.parent), '/usr/bin'])


if __name__ == '__main__':
    unittest.main()
