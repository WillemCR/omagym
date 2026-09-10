"""Canonical runner selection and isolated execution, independent of exercise prose."""
import json
import os
from pathlib import Path
import re
import shutil
import time
from .core import ROOT, GymError, run_process

TRACKS = {
 'ruby': ('Ruby','ruby','main.rb','https://www.ruby-lang.org/en/documentation/'),
 'rails': ('Ruby on Rails','rails','app/models/model.rb','https://guides.rubyonrails.org/'),
 'go': ('Go','go','main.go','https://go.dev/doc/'),
 'rust': ('Rust','rust','src/lib.rs','https://doc.rust-lang.org/book/'),
 'javascript': ('Modern JavaScript','javascript','main.js','https://developer.mozilla.org/en-US/docs/Web/JavaScript'),
 'react': ('React','browser','src/App.jsx','https://react.dev/learn'),
 'vue': ('Vue','browser','src/App.vue','https://vuejs.org/guide/introduction.html'),
 'html': ('HTML','browser','index.html','https://developer.mozilla.org/en-US/docs/Web/HTML'),
 'html-css': ('HTML + CSS','browser','styles.css','https://developer.mozilla.org/en-US/docs/Web/CSS'),
 'tailwind': ('Tailwind','browser','index.html','https://tailwindcss.com/docs/styling-with-utility-classes'),
}

def isolated(args, folder, runtime, env, timeout=120):
    bwrap=shutil.which('bwrap')
    if not bwrap:
        raise GymError('Bubblewrap is required to run exercise code in isolation.',503)
    folder=Path(folder).resolve();runtime=Path(runtime).resolve()
    # No host home, credentials or network. Only the exercise and disposable caches are writable.
    cmd=[bwrap,'--unshare-all','--die-with-parent','--new-session',
         '--ro-bind','/usr','/usr','--ro-bind','/etc','/etc',
         '--symlink','usr/bin','/bin','--symlink','usr/lib','/lib','--symlink','usr/lib','/lib64',
         '--proc','/proc','--dev','/dev','--tmpfs','/tmp','--dir','/home/learner',
         '--bind',str(folder),str(folder),
         '--ro-bind',str(ROOT/'node_modules'),str(ROOT/'node_modules'),
         '--ro-bind',str(ROOT/'gym/runtime'),str(ROOT/'gym/runtime')]
    gems=ROOT/'.runtime/gems'
    if gems.exists():cmd += ['--ro-bind',str(gems),str(gems),'--ro-bind',str(ROOT/'Gemfile'),str(ROOT/'Gemfile'),'--ro-bind',str(ROOT/'Gemfile.lock'),str(ROOT/'Gemfile.lock')]
    node=Path(shutil.which('node') or '/usr/bin/node').resolve()
    if not node.is_relative_to('/usr'):
        cmd += ['--ro-bind',str(node.parent),str(node.parent)]
    cache=runtime/'runner-cache';cache.mkdir(parents=True,exist_ok=True)
    cmd += ['--bind',str(cache),str(cache),'--chdir',str(folder),'--'] + [str(a) for a in args]
    clean={'PATH':str(node.parent)+':/usr/bin','HOME':'/home/learner','LANG':'C.UTF-8',
           'TMPDIR':'/tmp','NO_COLOR':'1', **env}
    return run_process(cmd, folder, env=clean, timeout=timeout, limit=250_000)

def execute(project, files, folder, runtime):
    folder=Path(folder);runtime=Path(runtime)
    for name,content in files.items():
        target=folder/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(content)
    cache=runtime/'runner-cache';cache.mkdir(parents=True,exist_ok=True)
    runner=project['runner'];expected=project.get('checks',[])
    start=time.monotonic();tests={};lines=[]
    if runner=='go':
        go=shutil.which('go')
        if not go:raise GymError('Go is not installed.',503)
        env=dict(GOCACHE=str(cache/'go'),GOMODCACHE=str(cache/'gomod'),GOTOOLCHAIN='local',GOWORK='off',GOENV='off',GOPROXY='off',GOSUMDB='off')
        rc,output=isolated([go,'test','-json','-count=1','-race','-timeout=15s','./...'],folder,runtime,env)
        for line in output.splitlines():
            try:e=json.loads(line)
            except ValueError:lines.append(line);continue
            if e.get('Output'):lines.append(e['Output'].rstrip())
            if e.get('Test') and e.get('Action') in ('pass','fail','skip'):tests[e['Test']]=e['Action']
        if not expected:
            expected=re.findall(r'^func (Test\w+)\(', '\n'.join(v for n,v in files.items() if n.endswith('_test.go')),re.M)
    elif runner=='rust':
        cargo=shutil.which('cargo')
        if not cargo:raise GymError('Rust and Cargo are not installed.',503)
        rc,output=isolated([cargo,'test','--offline','--color','never','--','--test-threads=1'],folder,runtime,
                          {'CARGO_HOME':str(cache/'cargo-home'),'CARGO_TARGET_DIR':str(cache/'rust'/project['id'])})
        lines=output.splitlines()
        for name,status in re.findall(r'^test (.+?) \.\.\. (ok|FAILED|ignored)',output,re.M):tests[name]={'ok':'pass','FAILED':'fail','ignored':'skip'}[status]
    elif runner=='javascript':
        node=shutil.which('node')
        if not node:raise GymError('Node.js is not installed.',503)
        test_files=[str(folder/n) for n in project['testFiles'] if n.endswith('.test.js')]
        rc,output=isolated([node,'--test','--test-reporter',str(ROOT/'gym/runtime/node-reporter.mjs'),*test_files],folder,runtime,{})
        for line in output.splitlines():
            try:e=json.loads(line)
            except ValueError:lines.append(line);continue
            if e.get('name'):tests[e['name']]=e['action'];lines.append(f"{e['action'].upper()} {e['name']} {e.get('detail','')}")
            if e.get('output'):lines.append(e['output'])
    elif runner in ('ruby','rails'):
        ruby=shutil.which('ruby')
        if not ruby:raise GymError('Ruby is not installed.',503)
        gems=ROOT/'.runtime/gems'
        env={'GEM_HOME':str(gems),'GEM_PATH':str(gems),'BUNDLE_GEMFILE':str(ROOT/'Gemfile'),'BUNDLE_FROZEN':'true'}
        rc,output=isolated([ruby,'-rbundler/setup','-r'+str(ROOT/'gym/runtime/ruby-reporter.rb'),'challenge_test.rb','--verbose'],folder,runtime,env)
        lines=output.splitlines()
        for line in re.findall(r'OMAGYM_RESULT (\{[^\n]+\})',output):
            try:
                result=json.loads(line);tests[result['name']]=result['action']
            except (ValueError,KeyError):pass
    elif runner=='browser':
        node=shutil.which('node')
        if not node or not shutil.which('chromium'):raise GymError('Node.js and Chromium are required for browser exercises.',503)
        # ESM test imports resolve against the root's installed, locked dependencies.
        (folder/'node_modules').symlink_to(ROOT/'node_modules',target_is_directory=True)
        (folder/'package.json').write_text('{"type":"module"}\n')
        env={'OMAGYM_PROJECT':str(folder),'OMAGYM_TRACK':project['track']}
        rc,output=isolated([node,str(ROOT/'node_modules/@playwright/test/cli.js'),'test','--config',str(ROOT/'gym/runtime/playwright.config.mjs')],folder,runtime,env,timeout=180)
        lines=output.splitlines()
        report=folder/'.test-report.json'
        if report.exists():
            try:data=json.loads(report.read_text())
            except ValueError:data={}
            def walk(suites):
                for suite in suites:
                    for spec in suite.get('specs',[]):
                        result=spec.get('tests',[{}])[0].get('results',[{}])[-1]
                        status=result.get('status')
                        tests[spec['title']]='pass' if status=='passed' else 'skip' if status=='skipped' else 'fail'
                        lines.append(f"{tests[spec['title']].upper()} {spec['title']}")
                        for error in result.get('errors',[]):lines.append(error.get('message','Browser assertion failed'))
                    walk(suite.get('suites',[]))
            walk(data.get('suites',[]))
            for error in data.get('errors',[]):lines.append(error.get('message','Browser test error'))
    else:raise GymError('Unsupported test runner.')
    passed=rc==0 and bool(expected) and all(tests.get(n)=='pass' for n in expected)
    leaf=[dict(name=n,action=a) for n,a in tests.items() if not any(other.startswith(n+'/') for other in tests)]
    return dict(passed=passed,output='\n'.join(lines),tests=leaf,elapsed=round(time.monotonic()-start,2),
                checksObserved=all(n in tests for n in expected),runner=runner)

def browser_ready(project, files, folder, runtime):
    folder=Path(folder)
    for name,content in files.items():
        target=folder/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(content)
    (folder/'node_modules').symlink_to(ROOT/'node_modules',target_is_directory=True)
    (folder/'package.json').write_text('{"type":"module"}\n')
    rc,output=isolated([shutil.which('node'),str(ROOT/'gym/runtime/browser-smoke.mjs')],folder,runtime,{'OMAGYM_PROJECT':str(folder),'OMAGYM_TRACK':project['track']},timeout=60)
    if rc or 'OMAGYM_BROWSER_READY' not in output:
        raise GymError('Browser starter must compile and render without page errors:\n'+output[-12000:],502)
