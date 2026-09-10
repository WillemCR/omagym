"""Exercise plugin installation ownership and updates using real temporary Git repos."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

SPEC = importlib.util.spec_from_file_location('plugin_launch', Path(__file__).resolve().parents[1]/'scripts/plugin-launch.py')
plugin = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plugin)


class PluginTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='omagym plugin ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root/'plugin'; self.source.mkdir()
        self.base = self.root/'data'; self.base.mkdir()
        self.git(self.source, 'init', '-q', '-b', 'main')
        (self.source/'.gitignore').write_text('workspaces/\n.runtime/\ngenerated/\n')
        (self.source/'app.txt').write_text('version one')
        self.commit('First version')

    def git(self, folder, *args):
        return subprocess.check_output(['git', '-C', str(folder), *args], text=True, stderr=subprocess.PIPE).strip()

    def commit(self, message):
        self.git(self.source, 'add', '.')
        self.git(self.source, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', message)

    def test_clone_is_independent_and_updates_preserve_learner_data(self):
        stop = Mock()
        app, old = plugin.sync_application(self.source, self.base, stop)
        self.assertNotEqual(app, self.source)
        self.assertEqual(self.git(app, 'remote', 'get-url', 'origin'), plugin.REPOSITORY)
        stop.assert_not_called()
        learner = app/'workspaces/mine/main.go'; learner.parent.mkdir(parents=True); learner.write_text('my work')
        custom = app/'generated/mine/exercise.json'; custom.parent.mkdir(parents=True); custom.write_text('{}')
        (self.source/'app.txt').write_text('version two'); self.commit('Update app')
        _, current = plugin.sync_application(self.source, self.base, stop)
        self.assertNotEqual(current, old)
        stop.assert_called_once_with(app)
        self.assertEqual((app/'app.txt').read_text(), 'version two')
        self.assertEqual(learner.read_text(), 'my work')
        self.assertEqual(custom.read_text(), '{}')
        plugin.sync_application(self.source, self.base, stop)
        stop.assert_called_once()

    def test_refuses_existing_unowned_app(self):
        app = self.base/'app'; app.mkdir(); (app/'keep.txt').write_text('valuable')
        with self.assertRaisesRegex(RuntimeError, 'not an app owned'):
            plugin.sync_application(self.source, self.base, Mock())
        self.assertEqual((app/'keep.txt').read_text(), 'valuable')

    def test_refuses_local_source_edits_without_stopping_backend(self):
        stop = Mock()
        app, _ = plugin.sync_application(self.source, self.base, stop)
        (app/'app.txt').write_text('local customization')
        (self.source/'app.txt').write_text('upstream change'); self.commit('Update')
        with self.assertRaisesRegex(RuntimeError, 'local edits'):
            plugin.sync_application(self.source, self.base, stop)
        stop.assert_not_called()
        self.assertEqual((app/'app.txt').read_text(), 'local customization')

    def test_busy_backend_prevents_source_update(self):
        app, old = plugin.sync_application(self.source, self.base, Mock())
        (self.source/'app.txt').write_text('upstream change'); self.commit('Update')
        stop = Mock(side_effect=RuntimeError('Backend is busy'))
        with self.assertRaisesRegex(RuntimeError, 'busy'):
            plugin.sync_application(self.source, self.base, stop)
        self.assertEqual(self.git(app, 'rev-parse', 'HEAD'), old)

    def test_dirty_plugin_is_not_silently_ignored(self):
        (self.source/'app.txt').write_text('uncommitted')
        with self.assertRaisesRegex(RuntimeError, 'plugin has local source edits'):
            plugin.sync_application(self.source, self.base, Mock())
        self.assertFalse((self.base/'app').exists())

    def test_setup_lock_refuses_concurrent_setup(self):
        with plugin.setup_lock(self.base):
            with self.assertRaisesRegex(RuntimeError, 'already running'):
                with plugin.setup_lock(self.base):
                    self.fail('Second installer acquired the lock')

    def test_uses_absolute_xdg_data_directory_only(self):
        with patch.dict(os.environ, {'XDG_DATA_HOME': str(self.base)}):
            self.assertEqual(plugin.data_directory(), self.base/'omagym')
        with patch.dict(os.environ, {'XDG_DATA_HOME': 'relative'}):
            self.assertEqual(plugin.data_directory(), Path.home()/'.local/share/omagym')

    def test_node_symlink_shim_keeps_its_dispatch_name_and_reports_real_runtime(self):
        manager = self.root/'runtime-manager'
        binary = self.root/'installed/bin/node'; binary.parent.mkdir(parents=True)
        binary.write_text('#!/bin/sh\nexit 0\n'); binary.chmod(0o755)
        info = json.dumps({'executable': str(binary), 'version': '25.2.1'})
        manager.write_text('#!/usr/bin/env python3\nimport sys\nfrom pathlib import Path\n'
                           'if Path(sys.argv[0]).name != "node":\n'
                           '    sys.exit("error: unexpected argument -p found")\n'
                           f'print({info!r})\n')
        manager.chmod(0o755)
        shim = self.root/'shims/node'; shim.parent.mkdir(); shim.symlink_to(manager)
        with patch.object(plugin.shutil, 'which', return_value=str(shim)):
            node, version = plugin.node_runtime()
        self.assertEqual(node, binary)
        self.assertEqual(version, '25.2.1')
        self.assertNotEqual(node.parent, shim.parent)

    def test_node_runtime_rejects_unavailable_reported_executable(self):
        with patch.object(plugin.shutil, 'which', return_value='/usr/bin/node'), \
             patch.object(plugin, 'run', return_value=json.dumps({'executable': 'relative/node', 'version': '25.2.1'})):
            with self.assertRaisesRegex(RuntimeError, 'unavailable runtime'):
                plugin.node_runtime()

    def test_core_prerequisites_never_probe_ruby_or_install_system_packages(self):
        def which(name):
            self.assertIn(name, ['git', 'node', 'npm', 'bwrap'])
            return '/usr/bin/'+name
        with patch.object(plugin.shutil, 'which', side_effect=which), \
             patch.object(plugin, 'node_runtime', return_value=(Path('/usr/bin/node'), '25.2.1')), \
             patch.object(plugin, 'run', return_value='') as run:
            _, versions = plugin.prerequisites(True)
        self.assertNotIn('ruby', versions)
        self.assertEqual([call.args[0][0] for call in run.call_args_list], ['bwrap'])

    def test_missing_base_tools_are_reported_without_package_manager(self):
        with patch.object(plugin.shutil, 'which', return_value=None), patch.object(plugin, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'has not changed your system'):
                plugin.prerequisites(True)
        run.assert_not_called()

    def test_ready_install_skips_build_and_preserves_other_launcher(self):
        app, revision = plugin.sync_application(self.source, self.base, Mock())
        for name in ['dist/client/index.html', '.venv/bin/python']:
            path = app/name; path.parent.mkdir(parents=True, exist_ok=True); path.touch()
        runtime = app/'.runtime'; runtime.mkdir()
        versions = {'node': '25.2.1', 'ruby': '3.4.10', 'python': '3.14.7'}
        (runtime/'plugin-ready.json').write_text(json.dumps(dict(versions, revision=revision)))
        (runtime/'modules.json').write_text(json.dumps({'schemaVersion': 1, 'enabled': []}))
        # Test fixtures emulate dependencies without making tracked source edits.
        original = subprocess.run
        with patch.object(plugin, 'prerequisites', return_value=({}, versions)), \
             patch.object(plugin.subprocess, 'run', wraps=subprocess.run) as process:
            # Mock only the desktop installer; real Git calls still enforce ownership.
            def dispatch(args, **kwargs):
                if any(str(a).endswith('install-desktop.py') for a in args):
                    return subprocess.CompletedProcess(args, 1)
                return original(args, **kwargs)
            process.side_effect = dispatch
            result, _ = plugin.prepare(self.source, self.base, False)
        self.assertEqual(result, app)
        self.assertFalse(any(str(call.args[0][0]) in ('npm', '/usr/bin/gem') for call in process.call_args_list))


if __name__ == '__main__':
    unittest.main()
