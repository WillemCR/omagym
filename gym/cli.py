"""Omagym's terminal interface. All grading and coaching stays in the server."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys

from .client import Client, file_lock
from .core import GymError, ROOT
from .desktop import Desktop, available, command
from .sessions import Sessions


def plain(value):
    # Drop OSC (including clipboard sequences), CSI, and remaining controls.
    text = str(value)
    text = re.sub(r'\x1b\][^\x07\x1b]*(?:\x07|\x1b\\|$)', '', text)
    text = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', text)
    return ''.join(c for c in text if c in '\n\t' or (ord(c) >= 32 and not 127 <= ord(c) <= 159))


def show(value):
    print(plain(value))


def brief(project):
    show(f"\nOMAGYM / {project['track'].upper()}\n{project['title']}\n{project['level']}\n\n{project['summary']}\n")
    for i, requirement in enumerate(project['requirements'], 1): show(f'{i}. {requirement}')
    show('\nDocumentation')
    for doc in project['docs']: show(f"  {doc['title']}\n  {doc['url']}")


def render_run(run):
    show(('PASS' if run['passed'] else 'KEEP GOING') + (' · saved files have changed since this run' if run.get('stale') else ''))
    for test in run['tests']:
        show(f"  {test['action'].upper():5} {test['name']}")
    show(f"\n{run['elapsed']:.1f}s · snapshot {run['fingerprint'][:12]}\n")
    show(run.get('output', ''))


def render_feedback(feedback):
    if feedback.get('stale'): show('Saved files have changed since this review.\n')
    show(feedback['feedback'])
    for heading, key in [('Observations', 'observations'), ('Think about', 'questions')]:
        if feedback[key]:
            show('\n'+heading)
            for item in feedback[key]: show('  • '+item)
    show('\nDocumentation')
    for doc in feedback['documentation']: show(f"  {doc['title']}\n  {doc['url']}")


def parser():
    p = argparse.ArgumentParser(prog='omagym', description='A guided development session, using your own tools.')
    p.add_argument('--json', action='store_true', help='Machine-readable output')
    p.add_argument('--project', help='Explicit project ID (otherwise inferred from your folder/session)')
    sub = p.add_subparsers(dest='action')
    for name, help_text in [
        ('list', 'Browse available projects'), ('start', 'Start a project session'),
        ('resume', 'Resume a session and reopen missing windows'), ('status', 'Show saved-file and session status'),
        ('brief', 'Read the challenge and documentation'), ('test', 'Run tests against saved files'),
        ('coach', 'Request feedback without solutions'), ('preview', 'Build a web exercise preview'),
        ('files', 'Open your default file manager'), ('end', 'End session tracking, keeping your work')]:
        s = sub.add_parser(name, help=help_text)
        s.add_argument('--json', action='store_true', default=argparse.SUPPRESS)
        s.add_argument('--project', default=argparse.SUPPRESS)
        if name in {'start', 'resume'}:
            s.add_argument('id', nargs='?')
        if name in {'start', 'resume'}:
            s.add_argument('--terminal-only', action='store_true', help='Use the current terminal; launch no windows')
            s.add_argument('--no-editor', action='store_true', help='Open a terminal and companion without an editor')
            s.add_argument('--files', action='store_true', help='Also open the default file manager')
            s.add_argument('--shell', action='store_true', help='Enter a project subshell (implies --terminal-only)')
            s.add_argument('--reopen', action='store_true', help='Retry components whose windows could not be verified')
        if name == 'list': s.add_argument('--track', help='Filter by language or framework ID')
        if name == 'coach': s.add_argument('question', nargs='*')
        if name == 'preview': s.add_argument('--open', action='store_true', help='Open the preview in your default browser')
    server = sub.add_parser('server', help='Manage the local backend')
    server.add_argument('operation', choices=['start', 'status', 'stop'])
    server.add_argument('--json', action='store_true', default=argparse.SUPPRESS)
    return p


def pick(client):
    if not sys.stdin.isatty(): raise GymError('Choose a project with omagym start ID. Use omagym list to see IDs.')
    projects = client.request('/projects')['projects']
    show('\n  OMAGYM\n  Pick your next workout.\n')
    tracks = list(dict.fromkeys(p['track'] for p in projects))
    labels = {'go':'Go','rust':'Rust','javascript':'Modern JavaScript','react':'React','vue':'Vue',
              'html':'HTML','html-css':'HTML + CSS','tailwind':'Tailwind','ruby':'Ruby','rails':'Ruby on Rails'}
    for i, track in enumerate(tracks, 1):
        show(f' {i:2}. {labels.get(track, track)} · {sum(p["track"]==track for p in projects)} projects')
    try: answer = input('\nLanguage number (Enter to cancel): ').strip()
    except EOFError: return None
    if not answer: return None
    if not answer.isdecimal() or not 1 <= int(answer) <= len(tracks): raise GymError('Choose a number from the list.')
    track = tracks[int(answer)-1]
    projects = [p for p in projects if p['track']==track]
    show('\n'+labels.get(track,track)+' projects\n')
    for i, project in enumerate(projects, 1):
        complete = project.get('run') or {}
        mark = '✓' if complete.get('passed') and not complete.get('stale') else ' '
        show(f" {i:2}. {mark} {project['track']:12} {project['title']}")
    try:
        answer = input('\nProject number (Enter to cancel): ').strip()
    except EOFError: return None
    if not answer: return None
    if not answer.isdecimal() or not 1 <= int(answer) <= len(projects): raise GymError('Choose a number from the list.')
    return projects[int(answer)-1]['id']


def shell(folder, project):
    os.chdir(folder)
    os.environ['PATH'] = str(ROOT/'bin')+os.pathsep+os.environ.get('PATH', '')
    os.environ['OMAGYM_PROJECT'] = project
    show('\nOMAGYM · Your practice terminal\n\n  omagym brief      Read the challenge\n  omagym test       Check saved files\n  omagym coach      Get feedback\n  omagym status     See your progress\n\nSave in your editor before tests or feedback. Type exit to leave this terminal.\n')
    executable = os.environ.get('SHELL', '/bin/bash')
    if not Path(executable).is_file(): executable = '/bin/bash'
    os.execv(executable, [executable])


def main(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments[:1] == ['_shell'] and len(arguments) == 2:
        args = argparse.Namespace(action='_shell',project=arguments[1],json=False)
    else:
        args = parser().parse_args(arguments)
    client = Client()
    output = None
    code = 0
    try:
        if args.action == 'server':
            output = client.ensure() if args.operation == 'start' else client.stop() if args.operation == 'stop' else client.identity()
            if not args.json: show('Backend stopped.' if args.operation == 'stop' else f'Omagym is ready at {client.url}')
        else:
            client.ensure()
            sessions = Sessions(client)
            if args.action == 'list':
                projects = client.request('/projects')['projects']
                if args.track: projects = [p for p in projects if p['track'] == args.track]
                output = {'projects': projects}
                if not args.json:
                    for p in projects: show(f"{p['id']:28} {p['track']:12} {p['title']}")
                    show('\nStart: omagym start <project-id>\nTerminal only: omagym start <project-id> --terminal-only')
            else:
                explicit = getattr(args, 'id', None) or args.project
                if args.action in (None, 'start') and not explicit:
                    explicit = pick(client)
                    if explicit is None: return 0
                project = sessions.resolve(explicit)
                action = args.action or 'start'
                if action in {'start', 'resume'}:
                    only = getattr(args, 'terminal_only', False) or getattr(args, 'shell', False)
                    output = sessions.start(project, terminal_only=only,
                                            no_editor=getattr(args,'no_editor',False), files=getattr(args,'files',False),
                                            reopen=getattr(args,'reopen',False))
                    status = client.status(project)
                    if not args.json:
                        if output.get('warning'): show(output['warning'])
                        show(f"\n{status['project']['title']}\n{output['folder']}")
                        if output.get('terminalOnly'): brief(status['project'])
                        else:
                            show('Workspace: '+output['workspace'])
                            for role, component in output['components'].items():
                                show(f"  {role}: {component['state']}")
                                if component.get('message'): show('  '+component['message'])
                            if any(c['state']!='open' for c in output['components'].values()):
                                show('Retry unverified windows explicitly: omagym resume '+project+' --reopen')
                        show('\nNext: save your work, then run omagym test.')
                    if not output.get('terminalOnly') and any(output['components'].get(role,{}).get('state')!='open' for role in output.get('roles',[]) if role!='files'):
                        code = 2
                    if getattr(args,'shell',False): shell(output['folder'], project)
                elif action == '_shell': shell(client.status(project)['folder'], project)
                elif action == 'end':
                    output = sessions.end(project)
                    if not args.json: show(output['message'])
                elif action == 'status':
                    output = client.status(project)
                    output['session'] = sessions.read(project)
                    if not args.json:
                        show(f"{output['project']['title']}\n{output['folder']}\n{len(output['files'])} files · snapshot {output['fingerprint'][:12]}")
                        show('An operation is running.' if output['busy'] else 'Ready for your next run.')
                        if output['run']: show('Last test: '+('passed' if output['run']['passed'] else 'incomplete')+(' · outdated' if output['run']['stale'] else ' · current'))
                        else: show('No tests run yet.')
                elif action == 'brief':
                    output = client.status(project)['project']
                    if not args.json: brief(output)
                elif action == 'test':
                    if not args.json: print('Checking saved files…', file=sys.stderr)
                    output = client.request('/run', {'project':project})
                    if not args.json: render_run(output)
                    code = 0 if output['passed'] else 1
                elif action == 'coach':
                    if not args.json: print('Your coach is reading the saved project…', file=sys.stderr)
                    output = client.request('/coach', {'project':project,'question':' '.join(args.question)})
                    if not args.json: render_feedback(output)
                elif action == 'preview':
                    if not args.json: print('Building saved source…', file=sys.stderr)
                    output = client.request('/preview', {'project':project})
                    output['url'] = 'http://127.0.0.1:4312'+output['path']
                    if args.open: command(['xdg-open', output['url']])
                    if not args.json: show(output['url'])
                elif action == 'files':
                    status = client.status(project)
                    if available():
                        with file_lock(sessions.directory/'desktop-launch.lock'):
                            output = Desktop(client.root, project, client.url).launch('files')
                    else:
                        command(['xdg-open',status['folder']]); output={'state':'requested'}
                    if not args.json: show(output.get('message', 'Opened your default file manager.'))
        if args.json: print(json.dumps(output, ensure_ascii=True))
        return code
    except (GymError, OSError) as e:
        code = 3 if getattr(e, 'status', None) == 409 else 2
        if args.json: print(json.dumps({'error':str(e),'code':code}))
        else: print('Omagym: '+plain(e), file=sys.stderr)
        return code
    except KeyboardInterrupt:
        print('\nCancelled. Running backend operations may continue.', file=sys.stderr)
        return 130


if __name__ == '__main__':
    sys.exit(main())
