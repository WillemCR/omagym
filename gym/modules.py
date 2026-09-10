"""Optional practice modules. Never install or upgrade host system packages."""
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

MODULES = {
    'go': {'name': 'Go', 'tracks': ['go'], 'tools': ['go', 'cc'], 'packages': ['go', 'base-devel']},
    'rust': {'name': 'Rust', 'tracks': ['rust'], 'tools': ['cargo', 'rustc', 'cc'], 'packages': ['rust', 'base-devel']},
    'javascript': {'name': 'JavaScript', 'tracks': ['javascript'], 'tools': [], 'packages': []},
    'web': {'name': 'Web (HTML, CSS, React, Vue, Tailwind)', 'tracks': ['html', 'html-css', 'react', 'vue', 'tailwind'], 'tools': ['chromium'], 'packages': ['chromium']},
    'ruby': {'name': 'Ruby', 'tracks': ['ruby'], 'tools': ['ruby', 'gem', 'cc', 'make'], 'packages': ['ruby', 'base-devel']},
    'rails': {'name': 'Ruby on Rails', 'tracks': ['rails'], 'tools': ['ruby', 'gem', 'cc', 'make'], 'packages': ['ruby', 'base-devel']},
}


def normalize(names, dependencies=True):
    names = set(names)
    unknown = names - MODULES.keys()
    if unknown:
        raise ValueError('Unknown modules: '+', '.join(sorted(unknown)))
    if dependencies and 'rails' in names:
        names.add('ruby')
    return [name for name in MODULES if name in names]


def config_path(root):
    return Path(root)/'.runtime/modules.json'


def enabled(root):
    path = config_path(root)
    if not path.exists():
        # Existing manual checkouts retain their behavior until explicitly configured.
        return list(MODULES)
    value = json.loads(path.read_text())
    if not isinstance(value, dict) or value.get('schemaVersion') != 1 or not isinstance(value.get('enabled'), list):
        raise ValueError('Invalid module configuration. Restore .runtime/modules.json from your backup.')
    return normalize(value['enabled'])


def for_track(track):
    return next(name for name, module in MODULES.items() if track in module['tracks'])


def info(root, track):
    name = for_track(track)
    return {'id': name, 'name': MODULES[name]['name'], 'enabled': name in enabled(root),
            'command': 'omagym modules add '+name}


def choose(current=()):
    names = list(MODULES)
    print('\nChoose the languages you want to practice. Other toolchains are optional.\n')
    for i, name in enumerate(names, 1):
        print(f"  {i}. {MODULES[name]['name']}"+(' [enabled]' if name in current else ''))
    default = ','.join(current) if current else 'go'
    answer = input(f'\nNames or numbers, separated by commas [{default}], or none: ').strip()
    answer = answer or default
    if answer.lower() == 'none':
        return []
    values = [part.strip().lower() for part in answer.replace(' ', ',').split(',') if part.strip()]
    try:
        values = [names[int(v)-1] if v.isdecimal() and 1 <= int(v) <= len(names) else v for v in values]
        return normalize(values)
    except (ValueError, TypeError) as error:
        raise ValueError('Choose module names or numbers from the list.') from error


def command(args, *, cwd=None, env=None, capture=False):
    result = subprocess.run([str(arg) for arg in args], cwd=cwd, env=env, text=True,
                            stdout=subprocess.PIPE if capture else sys.stderr,
                            stderr=subprocess.PIPE if capture else None)
    if result.returncode:
        raise RuntimeError(f'{args[0]} failed ({result.returncode}). '+(result.stderr.strip() if capture else 'See output above.'))
    return result.stdout.strip() if capture else ''


def check_tools(names):
    missing = sorted({tool for name in names for tool in MODULES[name]['tools']
                      if not os.access('/usr/bin/'+tool, os.X_OK)})
    if missing:
        packages = sorted({pkg for name in names if any(tool in missing for tool in MODULES[name]['tools'])
                           for pkg in MODULES[name]['packages']})
        raise RuntimeError('Missing tools for the selected modules: '+', '.join(missing)
                           +'. Omagym has not changed your system. Install compatible system tools yourself '
                           +'(Omarchy package names: '+', '.join(packages)+'), then retry.')
    if set(names) & {'ruby', 'rails'}:
        ruby = command(['/usr/bin/ruby', '-e', 'print RUBY_VERSION'], capture=True)
        if tuple(map(int, ruby.split('.')[:2])) < (3, 4):
            raise RuntimeError('Ruby modules need system Ruby 3.4+. Your Ruby version was left unchanged.')


def ruby_bundle(root, runner):
    root = Path(root)
    if runner == 'ruby' and (root/'.runtime/gems-ruby/omagym-ready').is_file():
        return root/'.runtime/gems-ruby', root/'modules/ruby/Gemfile'
    return root/'.runtime/gems', root/'Gemfile'


def install_ruby(root, rails, env=None):
    root = Path(root)
    gemfile = root/'Gemfile' if rails else root/'modules/ruby/Gemfile'
    gems = root/'.runtime'/('gems' if rails else 'gems-ruby')
    ruby = command(['/usr/bin/ruby', '-e', 'print RUBY_VERSION'], capture=True)
    signature = hashlib.sha256(gemfile.read_bytes()+gemfile.with_name('Gemfile.lock').read_bytes()+ruby.encode()).hexdigest()
    ready = gems/'omagym-ready'
    if ready.exists() and ready.read_text() == signature:
        return
    gems.mkdir(parents=True, exist_ok=True)
    local = dict(os.environ if env is None else env, GEM_HOME=str(gems), GEM_PATH=str(gems),
                 BUNDLE_GEMFILE=str(gemfile), BUNDLE_FROZEN='true')
    local['PATH'] = '/usr/bin'+os.pathsep+local.get('PATH', '')
    print('Installing local '+('Rails' if rails else 'Ruby')+' gems; system Ruby is unchanged.', file=sys.stderr, flush=True)
    command(['/usr/bin/gem', 'install', 'bundler', '-v', '4.0.20', '--no-document', '--no-user-install',
             '--install-dir', gems, '--bindir', gems/'bin'], cwd=root, env=local)
    command([gems/'bin/bundle', 'install'], cwd=root, env=local)
    ready.write_text(signature)


@contextmanager
def lock(root):
    runtime = Path(root)/'.runtime'; runtime.mkdir(exist_ok=True)
    with (runtime/'modules.lock').open('a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError('Another module setup is already running.') from error
        yield


def configure(root, names, action='set', env=None):
    names = normalize(names, dependencies=action != 'remove')
    with lock(root):
        current = enabled(root) if config_path(root).exists() or action == 'remove' else []
        if action == 'remove':
            removing = set(names)
            if 'ruby' in removing:
                removing.add('rails')
            selected = [name for name in current if name not in removing]
        else:
            selected = normalize(current+names) if action == 'add' else names
            check_tools(names)
            if 'rails' in names:
                install_ruby(root, True, env)
            elif 'ruby' in names:
                install_ruby(root, False, env)
        path = config_path(root); temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps({'schemaVersion': 1, 'enabled': selected}, indent=2)+'\n')
        temporary.replace(path)
    return selected
