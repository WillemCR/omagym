#!/usr/bin/env python3
"""Install only Omagym's launcher files; never alter default apps or bindings."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gym.client import atomic_json


def exec_quote(value):
    return '"'+str(value).replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('%', '%%')+'"'


def install(prefix, uninstall=False):
    prefix = Path(prefix).expanduser().resolve()
    link = prefix/'bin/omagym'
    entry = prefix/'share/applications/org.omagym.desktop'
    receipt = prefix/'share/omagym/installation.json'
    expected = {
        'root': str(ROOT), 'symlink': str(link),
        'entry': '[Desktop Entry]\nType=Application\nVersion=1.0\nName=Omagym\nComment=Practice a language with your own tools and a feedback-only coach\n'
                 +'Exec=xdg-terminal-exec --app-id=org.omagym.picker -e '+exec_quote(ROOT/'bin/omagym')+'\n'
                 +'Icon='+str(ROOT/'public/omagym.svg')+'\nTerminal=false\nCategories=Development;\nKeywords=code;practice;gym;learn;\nStartupNotify=false\n',
    }
    old = json.loads(receipt.read_text()) if receipt.exists() else None
    if old and old.get('root') != str(ROOT):
        raise RuntimeError('An Omagym installation from another folder owns these launchers. Uninstall it first.')
    if link.is_symlink():
        if link.resolve() != ROOT/'bin/omagym': raise RuntimeError(f'Another executable owns {link}.')
    elif link.exists(): raise RuntimeError(f'An existing file owns {link}.')
    if entry.exists() and (not old or entry.read_text() != old.get('entry')):
        raise RuntimeError(f'{entry} contains changes not owned by this installer. Preserve them before retrying.')
    if uninstall:
        if not old: return 'Omagym launcher is not installed.'
        link.unlink(missing_ok=True); entry.unlink(missing_ok=True); receipt.unlink(missing_ok=True)
        return 'Omagym launcher removed. All projects, learner files, sessions and running windows are preserved.'
    for path in (link.parent, entry.parent, receipt.parent): path.mkdir(parents=True, exist_ok=True)
    if not link.is_symlink(): link.symlink_to(ROOT/'bin/omagym')
    tmp = entry.with_suffix('.desktop.tmp'); tmp.write_text(expected['entry']); tmp.replace(entry)
    atomic_json(receipt, expected)
    return f'Omagym is installed. Open Omagym from your application launcher, or run {link}.'


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prefix', type=Path, default=Path.home()/'.local')
    p.add_argument('--uninstall', action='store_true')
    args = p.parse_args()
    try: print(install(args.prefix, args.uninstall))
    except (OSError, ValueError, RuntimeError) as e: print(str(e), file=sys.stderr); sys.exit(1)
