"""Session metadata is separate from learner files and never owns their lifetime."""
import json
import os
from pathlib import Path
import re
import time
from urllib.parse import urlencode
import uuid

from .client import atomic_json, file_lock
from .core import GymError
from .desktop import Desktop, available, dispatch, hypr


class Sessions:
    def __init__(self, client):
        self.client = client
        self.directory = client.runtime/'sessions'
        self.directory.mkdir(parents=True, exist_ok=True)

    def path(self, project):
        if not re.fullmatch(r'[A-Za-z0-9_-]+', project):
            raise GymError('Invalid project ID.')
        return self.directory/(project+'.json')

    def read(self, project):
        try:
            record = json.loads(self.path(project).read_text())
            if not isinstance(record, dict) or record.get('project') != project or not isinstance(record.get('id'),str) or not isinstance(record.get('components'),dict):
                return None
            roles = record.get('roles', ['editor','terminal','companion'])
            if not isinstance(roles,list) or any(r not in {'editor','terminal','companion','files'} for r in roles):
                return None
            for component in record['components'].values():
                if not isinstance(component,dict):return None
                if component.get('state')=='launching':
                    component.update(state='unverified',message='A previous launch was interrupted. Check existing windows before using --reopen.')
                if component.get('window') is not None and not isinstance(component['window'],dict):return None
            return record
        except (OSError, ValueError):
            return None

    def active(self):
        records = [self.read(p.stem) for p in self.directory.glob('*.json')]
        return [r for r in records if r and not r.get('endedAt')]

    def resolve(self, project=None, cwd=None):
        if project:
            self.path(project)
            return project
        cwd = Path(cwd or Path.cwd()).resolve()
        workspaces = (self.client.root/'workspaces').resolve()
        if cwd.is_relative_to(workspaces) and cwd != workspaces:
            return cwd.relative_to(workspaces).parts[0]
        records = self.active()
        if len(records) == 1:
            return records[0]['project']
        raise GymError('Choose a project with --project ID, or run this command inside its project folder.' + (' Multiple sessions are active.' if records else ' Start with omagym list.'))

    def start(self, project, *, terminal_only=False, no_editor=False, files=False, reopen=False):
        status = self.client.status(project)
        desktop = available() and not terminal_only
        folder = Path(status['folder'])
        expected = self.client.root/'workspaces'/project
        if folder != expected or folder.is_symlink() or not folder.is_dir():
            raise GymError('The project folder does not match this installation.', 409)
        with file_lock(self.path(project).with_suffix('.lock')):
            previous = self.read(project)
            record = previous if previous and not previous.get('endedAt') else {
                'id': uuid.uuid4().hex, 'project': project, 'startedAt': time.time(), 'components': {}}
            record['folder'] = str(folder)
            if not desktop:
                # Terminal use must not overwrite an active desktop session's identity.
                record.setdefault('mode', 'terminal')
                atomic_json(self.path(project), record)
                return dict(record, terminalOnly=True, warning=None if terminal_only else 'No Hyprland connection; using a terminal-only session.')
            launcher = Desktop(self.client.root, project, self.client.url+'/?'+urlencode({'mode':'session','project':project}))
            with file_lock(self.directory/'desktop-launch.lock'):
                current = hypr('activeworkspace')['name']
                if current != launcher.workspace:
                    record['previousWorkspace'] = current
                live = launcher.alive(record)
                record.update(mode='desktop', workspace=launcher.workspace)
                same_compositor = record.get('compositor') == os.environ.get('HYPRLAND_INSTANCE_SIGNATURE')
                record['compositor'] = os.environ.get('HYPRLAND_INSTANCE_SIGNATURE')
                roles = list(record.get('roles', ['editor','terminal','companion']))
                if no_editor: roles = [r for r in roles if r != 'editor']
                if files and 'files' not in roles: roles += ['files']
                record['roles'] = roles
                launcher.focus()
                # Save after each launch, so a partially successful start is resumable.
                for role in roles:
                    old = record['components'].get(role)
                    if role in live:
                        continue
                    if old and old.get('state') == 'unverified' and same_compositor and not reopen:
                        continue
                    record['components'][role] = {'state':'launching'}
                    atomic_json(self.path(project), record)
                    record['components'][role] = launcher.launch(role)
                    atomic_json(self.path(project), record)
                atomic_json(self.path(project), record)
                return record

    def end(self, project):
        with file_lock(self.path(project).with_suffix('.lock')):
            record = self.read(project)
            if not record: raise GymError('No session exists for this project.', 404)
            record['endedAt'] = time.time()
            atomic_json(self.path(project), record)
            if available() and hypr('activeworkspace')['name'] == record.get('workspace') and record.get('previousWorkspace'):
                dispatch('workspace', 'name:'+record['previousWorkspace'])
            return {'ended': True, 'project': project, 'message': 'Session ended. Your windows, files and backend remain open.'}
