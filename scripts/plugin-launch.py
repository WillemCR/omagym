#!/usr/bin/env python3
"""Set up an Omagym app outside the removable Omarchy plugin, then open it."""
import argparse
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

SOURCE = Path(__file__).resolve().parent.parent
REPOSITORY = 'https://github.com/WillemCR/omagym.git'
PLUGIN_ID = 'willemcr.omagym'
sys.path.insert(0, str(SOURCE))
from gym import modules as practice_modules


def run(args, *, cwd=None, env=None, capture=False):
    result = subprocess.run([str(a) for a in args], cwd=cwd, env=env,
                            text=True, stdout=subprocess.PIPE if capture else None,
                            stderr=subprocess.PIPE if capture else None)
    if result.returncode:
        detail = result.stderr.strip() if capture else 'See the command output above.'
        raise RuntimeError(f'{args[0]} failed ({result.returncode}). {detail}')
    return result.stdout.strip() if capture else ''


def data_directory():
    configured = os.environ.get('XDG_DATA_HOME', '')
    base = Path(configured) if configured and Path(configured).is_absolute() else Path.home()/'.local/share'
    return base/'omagym'


@contextmanager
def setup_lock(base):
    base.mkdir(parents=True, exist_ok=True)
    with (base/'setup.lock').open('a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError('Omagym setup is already running in another terminal.') from error
        yield


def save_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2)+'\n')
    temporary.replace(path)


def read_json(path):
    return json.loads(path.read_text()) if path.exists() else None


def node_runtime():
    launcher = shutil.which('node')
    if not launcher:
        raise RuntimeError('Node.js is not installed or is not on PATH.')
    # Runtime-manager shims depend on argv[0]. Resolving a mise "node" symlink
    # before launching it turns a Node invocation into a mise CLI invocation.
    info = json.loads(run([launcher, '-p',
                          'JSON.stringify({executable:process.execPath,version:process.versions.node})'],
                         capture=True))
    if not isinstance(info, dict) or not isinstance(info.get('executable'), str) or not isinstance(info.get('version'), str):
        raise RuntimeError('Node.js did not report a valid runtime path and version.')
    executable = Path(info['executable'])
    if not executable.is_absolute() or not executable.is_file() or not os.access(executable, os.X_OK):
        raise RuntimeError('Node.js reported an unavailable runtime executable.')
    # The actual executable, unlike the manager shim, can be mounted in the
    # exercise sandbox and supplies the matching npm through its bin directory.
    return executable.resolve(), info['version']


def prerequisites(allow_packages):
    if sys.version_info < (3, 11):
        raise RuntimeError('Python 3.11 or newer is required.')
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        raise RuntimeError('This plugin release targets x86-64 Linux/Omarchy.')
    # Core setup only needs the shared app runtime. Never invoke a system
    # package manager: its dependency resolution may upgrade existing tools.
    commands = {'git': 'git', 'node': 'nodejs', 'npm': 'npm', 'bwrap': 'bubblewrap'}
    missing = sorted({pkg for cmd, pkg in commands.items() if not shutil.which(cmd)})
    if missing:
        raise RuntimeError('Missing base requirements: '+', '.join(missing)
                           +'. Install compatible tools yourself, then retry. Omagym has not changed your system.')
    node, version = node_runtime()
    # Node 24+ supports all test-reporter options used by this release.
    if int(version.split('.')[0]) < 24:
        raise RuntimeError('Node 24+ is required for plugin setup. The tested version is in .node-version; select it with your runtime manager and retry.')
    run(['bwrap', '--unshare-all', '--ro-bind', '/', '/', '--', '/usr/bin/true'], capture=True)
    env = dict(os.environ)
    env['PATH'] = str(node.parent)+':/usr/bin:'+os.environ.get('PATH', '')
    return env, {'node': version, 'nodeExecutable': str(node), 'python': platform.python_version()}


def sync_application(source, base, before_change):
    """Import only reviewed plugin commits; keep ignored learner files on updates."""
    revision = run(['git', '-C', source, 'rev-parse', 'HEAD'], capture=True)
    if run(['git', '-C', source, 'status', '--porcelain', '--untracked-files=no'], capture=True):
        raise RuntimeError('The plugin has local source edits. Commit or preserve them before setup.')
    app = base/'app'
    receipt = base/'managed-app.json'
    owner = {'plugin': PLUGIN_ID, 'app': str(app.resolve())}
    if app.exists():
        if read_json(receipt) != owner or not (app/'.git').is_dir():
            raise RuntimeError(f'{app} is not an app owned by this plugin. Preserve it before choosing a new install location.')
        if run(['git', '-C', app, 'status', '--porcelain', '--untracked-files=no'], capture=True):
            raise RuntimeError(f'Application source has local edits in {app}; updates will not overwrite them.')
        if run(['git', '-C', app, 'rev-parse', 'HEAD'], capture=True) != revision:
            before_change(app)
            run(['git', '-C', app, 'fetch', '--quiet', str(source), revision])
            run(['git', '-C', app, 'merge', '--ff-only', revision])
    else:
        staging = Path(tempfile.mkdtemp(prefix='.app-', dir=base))
        try:
            run(['git', 'clone', '--quiet', '--no-hardlinks', '--no-checkout', '--', source, staging])
            run(['git', '-C', staging, 'checkout', '--quiet', '-B', 'installed', revision])
            run(['git', '-C', staging, 'remote', 'set-url', 'origin', REPOSITORY])
            staging.rename(app)
            save_json(receipt, owner)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
    return app, revision


def stop_owned_backend(app):
    """Ask the existing app to stop only a verified, idle backend it owns."""
    python = app/'.venv/bin/python'
    if not python.exists():
        return
    env = dict(os.environ, PYTHONPATH=str(app))
    check = subprocess.run([str(python), '-m', 'gym.cli', 'server', 'status', '--json'],
                           cwd=app, env=env, capture_output=True, text=True, timeout=10)
    if check.returncode:
        # An offline/foreign backend cannot be modified by rebuilding this app.
        # A recorded owned process needs inspection if its status cannot be read.
        if (app/'.runtime/server-process.json').exists():
            raise RuntimeError('Cannot verify the recorded backend. Run this app’s bin/omagym server status before updating.')
        return
    run([python, '-m', 'gym.cli', 'server', 'stop'], cwd=app, env=env)


def prepare(source, base, allow_packages=True, install_launcher=True, modules=None, choose_modules=False):
    env, versions = prerequisites(allow_packages)
    with setup_lock(base):
        app, revision = sync_application(source, base, stop_owned_backend)
        runtime = app/'.runtime'
        runtime.mkdir(exist_ok=True)
        ready = runtime/'plugin-ready.json'
        stamp = dict(versions, revision=revision)
        if read_json(ready) != stamp or not (app/'dist/client/index.html').exists() or not (app/'.venv/bin/python').exists():
            stop_owned_backend(app)
            print('Preparing Omagym. The first installation can take several minutes.', flush=True)
            run([sys.executable, '-m', 'venv', app/'.venv'], env=env)
            local = dict(env, SHARP_IGNORE_GLOBAL_LIBVIPS='1')
            run(['npm', 'ci', '--no-fund'], cwd=app, env=local)
            run(['npm', 'run', 'build'], cwd=app, env=local)
            save_json(ready, stamp)
        configured = practice_modules.config_path(app).exists()
        if modules is not None or choose_modules or not configured:
            selected = modules
            if selected is None:
                selected = practice_modules.choose(practice_modules.enabled(app) if configured else []) if sys.stdin.isatty() else []
            stop_owned_backend(app)
            practice_modules.configure(app, selected, env=env)
        else:
            print('Enabled modules: '+(', '.join(practice_modules.enabled(app)) or 'none')+'. Add more with: omagym modules choose', flush=True)
        # A pre-existing hand-installed copy may own these names; never replace it.
        if install_launcher:
            installed = subprocess.run([sys.executable, str(app/'scripts/install-desktop.py')], cwd=app, env=env)
            if installed.returncode:
                print('The existing launcher was preserved. This plugin can still open its own app.', flush=True)
        return app, env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--setup-only', action='store_true', help='Prepare dependencies without opening a practice session')
    parser.add_argument('--no-packages', action='store_true', help='Compatibility flag; setup never installs system packages')
    parser.add_argument('--no-launcher', action='store_true', help='Keep command/application launchers unchanged (useful for isolated setup testing)')
    parser.add_argument('--modules', help='Choose comma-separated modules: go,rust,javascript,web,ruby,rails,quickshell (or none)')
    parser.add_argument('--choose-modules', action='store_true', help='Choose which practice modules to enable')
    args = parser.parse_args()
    print('Omagym · independent community software\nNot officially supported or endorsed by DHH or Omacom.\n', flush=True)
    try:
        selected = None if args.modules is None else [] if args.modules == 'none' else practice_modules.normalize(args.modules.split(','))
        app, env = prepare(SOURCE, data_directory(), not args.no_packages, not args.no_launcher, selected, args.choose_modules)
        if args.setup_only:
            print(f'Ready. Application and learner data: {app}')
            return 0
        return subprocess.call([str(app/'bin/omagym')], cwd=app, env=env)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f'\nOmagym setup could not finish: {error}', file=sys.stderr, flush=True)
        if sys.stdin.isatty():
            input('Press Enter to close; click Omagym to retry after fixing the issue. ')
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
