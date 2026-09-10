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


def prerequisites(allow_packages):
    if sys.version_info < (3, 11):
        raise RuntimeError('Python 3.11 or newer is required.')
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        raise RuntimeError('This plugin release targets x86-64 Linux/Omarchy.')
    # Compilers/Ruby are system tools so they remain available inside Bubblewrap.
    system = {'/usr/bin/go': 'go', '/usr/bin/cargo': 'rust', '/usr/bin/rustc': 'rust',
              '/usr/bin/ruby': 'ruby', '/usr/bin/gem': 'ruby', '/usr/bin/chromium': 'chromium',
              '/usr/bin/cc': 'base-devel', '/usr/bin/make': 'base-devel'}
    commands = {'git': 'git', 'node': 'nodejs', 'npm': 'npm', 'bwrap': 'bubblewrap'}
    missing = sorted({pkg for path, pkg in system.items() if not Path(path).is_file()}
                     | {pkg for cmd, pkg in commands.items() if not shutil.which(cmd)})
    if missing:
        print('Required system packages: '+', '.join(missing), flush=True)
        if not allow_packages or not shutil.which('omarchy') or not sys.stdin.isatty():
            raise RuntimeError('Install with: omarchy pkg add '+' '.join(missing))
        if input('Install these missing packages with Omarchy? [y/N] ').strip().lower() not in ('y', 'yes'):
            raise RuntimeError('Setup cancelled; system packages were not installed.')
        run(['omarchy', 'pkg', 'add', *missing])
    node = Path(shutil.which('node') or '').resolve()
    version = run([node, '-p', 'process.versions.node'], capture=True)
    # Node 24+ supports all test-reporter options used by this release.
    if int(version.split('.')[0]) < 24:
        raise RuntimeError('Node 24+ is required for plugin setup. The tested version is in .node-version; select it with your runtime manager and retry.')
    ruby = run(['/usr/bin/ruby', '-e', 'print RUBY_VERSION'], capture=True)
    if tuple(map(int, ruby.split('.')[:2])) < (3, 4):
        raise RuntimeError('System Ruby 3.4+ is required for the locked Rails bundle.')
    run(['bwrap', '--unshare-all', '--ro-bind', '/', '/', '--', '/usr/bin/true'], capture=True)
    env = dict(os.environ)
    env['PATH'] = str(node.parent)+':/usr/bin:'+os.environ.get('PATH', '')
    return env, {'node': version, 'ruby': ruby, 'python': platform.python_version()}


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


def prepare(source, base, allow_packages=True, install_launcher=True):
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
            local = dict(env, SHARP_IGNORE_GLOBAL_LIBVIPS='1',
                         GEM_HOME=str(runtime/'gems'), GEM_PATH=str(runtime/'gems'),
                         BUNDLE_GEMFILE=str(app/'Gemfile'), BUNDLE_FROZEN='true')
            run(['npm', 'ci', '--no-fund'], cwd=app, env=local)
            run(['/usr/bin/gem', 'install', 'bundler', '-v', '4.0.20', '--no-document', '--no-user-install',
                 '--install-dir', runtime/'gems', '--bindir', runtime/'gems/bin'], cwd=app, env=local)
            run([runtime/'gems/bin/bundle', 'install'], cwd=app, env=local)
            run(['npm', 'run', 'build'], cwd=app, env=local)
            save_json(ready, stamp)
        # A pre-existing hand-installed copy may own these names; never replace it.
        if install_launcher:
            installed = subprocess.run([sys.executable, str(app/'scripts/install-desktop.py')], cwd=app, env=env)
            if installed.returncode:
                print('The existing launcher was preserved. This plugin can still open its own app.', flush=True)
        return app, env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--setup-only', action='store_true', help='Prepare dependencies without opening a practice session')
    parser.add_argument('--no-packages', action='store_true', help='Report missing system packages instead of offering to install them')
    parser.add_argument('--no-launcher', action='store_true', help='Keep command/application launchers unchanged (useful for isolated setup testing)')
    args = parser.parse_args()
    print('Omagym · independent community software\nNot officially supported or endorsed by DHH or Omacom.\n', flush=True)
    try:
        app, env = prepare(SOURCE, data_directory(), not args.no_packages, not args.no_launcher)
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
