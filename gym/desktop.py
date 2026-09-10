"""Launch the user's own applications; never adopt an unrelated desktop window."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from .core import GymError


def command(argv, *, timeout=5):
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise GymError(f'Could not run {argv[0]}: {e}', 503) from e
    if result.returncode:
        raise GymError(f'{argv[0]}: {result.stderr.strip() or result.stdout.strip()}', 503)
    return result.stdout.strip()


def hypr(query):
    return json.loads(command(['hyprctl', '-j', query]))


def dispatch(action, target):
    # Omarchy Quattro uses the Lua dispatcher; argv keeps this out of a shell.
    quote = lambda s: json.dumps(s, ensure_ascii=False)
    if action == 'workspace':
        lua = 'hl.dsp.focus({ workspace = '+quote(target)+' })'
    elif action == 'closewindow':
        lua = 'hl.dsp.window.close({ window = '+quote(target)+' })'
    elif action == 'movetoworkspacesilent':
        workspace, window = target.split(',', 1)
        lua = 'hl.dsp.window.move({ workspace = '+quote(workspace)+', window = '+quote(window)+', follow = false })'
    else:
        raise GymError('Unsupported desktop action.')
    try:
        result = command(['hyprctl', 'dispatch', lua])
    except GymError:
        result = command(['hyprctl', 'dispatch', action, target])
    if result != 'ok':
        raise GymError(f'Desktop could not {action}: {result}', 503)


def available():
    if not os.environ.get('HYPRLAND_INSTANCE_SIGNATURE') or not shutil.which('hyprctl'):
        return False
    try:
        hypr('activeworkspace')
        return True
    except (GymError, ValueError):
        return False


def identity(client):
    return {k: client.get(k) for k in ('address', 'pid', 'initialClass', 'stableId')}


def matching(record, client):
    return all(record.get(k) == client.get(k) for k in ('address', 'pid', 'initialClass', 'stableId'))


def defaults():
    editor_file = Path.home()/'.local/state/omarchy/defaults/editor'
    editor = editor_file.read_text().strip() if editor_file.exists() else 'nvim'
    if not shutil.which(editor):
        editor = 'nvim'
    return editor


class Desktop:
    def __init__(self, root, project_id, url):
        if not re.fullmatch(r'[a-zA-Z0-9_-]+', project_id):
            raise GymError('Invalid desktop project ID.')
        self.root = Path(root)
        self.project_id = project_id
        self.workspace = f'omagym-{project_id}'
        self.folder = self.root/'workspaces'/project_id
        self.url = url

    def focus(self):
        dispatch('workspace', 'name:'+self.workspace)

    def launch(self, role, *, timeout=12):
        marker = f'org.omagym.{role}.{self.project_id}'
        if role == 'terminal':
            argv = ['xdg-terminal-exec', '--app-id='+marker, '--dir='+str(self.folder),
                    '-e', str(self.root/'bin/omagym'), '_shell', self.project_id]
            match = lambda c: c.get('class') == marker or c.get('initialClass') == marker
        elif role == 'editor':
            editor = defaults()
            if Path(editor).name in {'nvim', 'vim', 'nano', 'micro', 'hx', 'helix', 'fresh'}:
                argv = ['xdg-terminal-exec', '--app-id='+marker, '--dir='+str(self.folder), '-e',
                        'omarchy', 'launch', 'editor', '--inline', str(self.folder)]
                match = lambda c: c.get('class') == marker or c.get('initialClass') == marker
            else:
                args = ['--new-window'] if Path(editor).name in {'code', 'code-insiders', 'cursor', 'zed'} else []
                argv = ['omarchy', 'launch', 'editor', *args, str(self.folder)]
                editor_classes = {'code': {'code', 'Code'}, 'code-insiders': {'code-insiders'},
                                  'cursor': {'cursor', 'Cursor'}, 'zed': {'dev.zed.Zed', 'dev.zed.Zed-Preview'}}
                match = lambda c: c.get('class') in editor_classes.get(Path(editor).name, set()) and self.project_id in c.get('title', '')
        elif role == 'companion':
            argv = ['omarchy', 'launch', 'webapp', self.url, '--class='+marker]
            # Chromium's existing process ignores --class for app windows. The
            # page title includes the project ID; require it AND a new app window.
            match = lambda c: (c.get('class') == marker or c.get('initialClass') == marker or
                               (c.get('class', '').startswith('chrome-127.0.0.1') and
                                f'[{self.project_id}]' in c.get('title', '')))
        elif role == 'files':
            argv = ['xdg-open', str(self.folder)]
            handler = command(['xdg-mime', 'query', 'default', 'inode/directory'])
            known = {'org.gnome.Nautilus.desktop': 'org.gnome.Nautilus',
                     'org.kde.dolphin.desktop': 'org.kde.dolphin', 'thunar.desktop': 'thunar'}
            match = lambda c: c.get('class', '').lower() == known.get(handler, '\0').lower() and self.project_id in c.get('title', '')
        else:
            raise GymError('Unknown session component.')
        before = {c['address'] for c in hypr('clients')}
        self.focus()
        log_path = self.root/'.runtime'/'desktop.log'
        with log_path.open('ab') as log:
            proc = subprocess.Popen(argv, cwd=self.folder, stdin=subprocess.DEVNULL,
                                    stdout=log, stderr=log, start_new_session=True)
        deadline = time.monotonic()+timeout
        while time.monotonic() < deadline:
            candidates = [c for c in hypr('clients') if c['address'] not in before and
                          (match(c) or c.get('pid') == proc.pid)]
            if len(candidates) == 1:
                client = candidates[0]
                if client['workspace']['name'] != self.workspace:
                    dispatch('movetoworkspacesilent', f'name:{self.workspace},address:{client["address"]}')
                return {'state': 'open', 'window': identity(client)}
            if proc.poll() not in (None, 0):
                return {'state': 'failed', 'message': f'{role.title()} could not open. See {log_path}.'}
            time.sleep(.15)
        return {'state': 'unverified', 'message': f'{role.title()} was requested, but no unique new window could be identified. Check your existing windows; Omagym left them in place.'}

    def alive(self, record):
        if record.get('compositor') != os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
            return {}
        clients = hypr('clients')
        return {role: data for role, data in record.get('components', {}).items()
                if data.get('window') and any(matching(data['window'], c) for c in clients)}
