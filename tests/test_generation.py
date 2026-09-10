"""Offline checks for the designer's validation and publish transaction."""
import copy
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from gym.core import Gym, GymError, MAX_FILE
from gym.generation import Generator, safe_path, validate

PRIVATE = 'PRIVATE_REFERENCE_MARKER_7d33'
CHECKS = ['TestHappy', 'TestEmpty', 'TestInvalid', 'TestBoundary']


def candidate():
    return {
        'title': 'Weekend journal', 'summary': 'Summarize local journal entries.',
        'level': 'Weekend', 'skills': ['maps', 'validation'],
        'requirements': ['Expose Analyze(text string) int.', 'Empty input returns zero.',
                         'Count every nonblank entry.'],
        'docs': [{'title': 'Strings', 'url': 'https://pkg.go.dev/strings'}],
        'entry': 'main.go', 'testFiles': ['go.mod', 'challenge_test.go'], 'checks': CHECKS[:],
        'files': [
            {'path': 'go.mod', 'content': 'module gym.local/generated\n\ngo 1.23.0\n'},
            {'path': 'main.go', 'content': 'package journal\nfunc Analyze(s string) int { return 0 }\n'},
            {'path': 'challenge_test.go', 'content': 'package journal\n// protected suite\n'},
        ],
        'referenceFiles': [{'path': 'main.go', 'content': 'package journal\n// '+PRIVATE+'\n'}],
    }


def result(passed, observed=True):
    return {'passed': passed, 'checksObserved': observed,
            'tests': [{'name': n, 'action': 'pass' if passed else 'fail'} for n in CHECKS],
            'output': 'validation output', 'runner': 'go', 'elapsed': 0.01}


class ValidationTests(unittest.TestCase):
    def reject(self, data):
        with self.assertRaises(GymError):
            validate(data, 'go', 'custom-test')

    def test_valid_candidate_keeps_reference_separate_and_rebuilds_brief(self):
        data = candidate()
        data['files'].append({'path': 'README.md', 'content': 'untrusted alternate brief'})
        meta, files, reference = validate(data, 'go', 'custom-test')
        self.assertEqual(meta['runner'], 'go')
        self.assertTrue(meta['generated'])
        self.assertEqual(meta['id'], 'custom-test')
        self.assertNotIn('referenceFiles', meta)
        self.assertNotIn(PRIVATE, json.dumps(meta)+json.dumps(files))
        self.assertIn(PRIVATE, reference['main.go'])
        self.assertIn('Expose Analyze', files['README.md'])
        self.assertNotIn('untrusted alternate brief', files['README.md'])

    def test_unsafe_file_paths(self):
        for name in ['../main.go', '/tmp/main.go', 'x/../../main.go', 'a\\main.go',
                     '.env', 'src/.secret.txt', 'node_modules/x.js', 'vendor/x.go',
                     'target/x.rs', 'AGENTS.md', 'build.rs', 'vite.config.js',
                     'src/playwright.config.js', 'script.sh', '', None]:
            with self.subTest(name=name), self.assertRaises(GymError):
                safe_path(name)
        self.assertEqual(safe_path('src/components/Task List.jsx'), 'src/components/Task List.jsx')

    def test_schema_counts_types_and_duplicate_files(self):
        changes = [lambda d: d.update(extra='unexpected'),
                   lambda d: d.update(checks=CHECKS[:3]),
                   lambda d: d.update(checks=['TestSame']*4),
                   lambda d: d.update(requirements=['too short']),
                   lambda d: d.update(title=' '),
                   lambda d: d.update(skills=[1]),
                   lambda d: d['files'].append(copy.deepcopy(d['files'][0])),
                   lambda d: d['files'][0].update(content='x'*(MAX_FILE+1))]
        for change in changes:
            data = candidate(); change(data)
            with self.subTest(change=change): self.reject(data)

    def test_entry_and_required_test_files(self):
        for entry in ['missing.go', 'challenge_test.go', '../main.go']:
            data = candidate(); data['entry'] = entry
            with self.subTest(entry=entry): self.reject(data)
        data = candidate(); data['testFiles'].remove('go.mod'); self.reject(data)
        data = candidate(); data['testFiles'].append('missing_test.go'); self.reject(data)

    def test_reference_cannot_replace_protected_or_add_unknown_files(self):
        for name in ['challenge_test.go', 'go.mod', 'README.md', 'package.json', 'new.go']:
            data = candidate()
            if name not in {'new.go', 'challenge_test.go', 'go.mod'}:
                data['files'].append({'path': name, 'content': 'original'})
            data['referenceFiles'] = [{'path': name, 'content': 'replacement'}]
            with self.subTest(name=name): self.reject(data)

    def test_unlisted_test_file_cannot_be_reference_or_entry(self):
        for name in ['extra_test.go', 'nested/README.md', 'nested/AGENTS.md']:
            data = candidate(); data['files'].append({'path': name, 'content': 'protected'})
            data['referenceFiles'] = [{'path': name, 'content': 'tampered grading'}]
            with self.subTest(name=name): self.reject(data)
        data = candidate(); data['files'].append({'path': 'extra_test.go', 'content': 'test'})
        data['entry'] = 'extra_test.go'; self.reject(data)

    def test_docs_reject_lookalikes_credentials_and_non_https(self):
        for url in ['http://pkg.go.dev/strings', 'https://pkg.go.dev.evil.test/strings',
                    'https://user:password@pkg.go.dev/strings', 'javascript:alert(1)',
                    'https://example.com/docs']:
            data = candidate(); data['docs'][0]['url'] = url
            with self.subTest(url=url): self.reject(data)


class GenerationJobTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.gym = Gym(self.tmp.name)
        self.generator = Generator(self.gym)
        self.initial_count = len(self.gym.catalog)

    def wait(self, job):
        deadline = time.monotonic()+5
        while time.monotonic() < deadline:
            current = self.generator.get(job['id'])
            if current['status'] in {'complete', 'failed'}:
                # A terminal status is persisted just before the job lock is released.
                if self.gym.job_lock.acquire(blocking=False):
                    self.gym.job_lock.release()
                    return current
            time.sleep(.005)
        self.fail('mock generation did not finish')

    def fake_codex(self, args, cwd, **kwargs):
        self.assertIn('read-only', args)
        self.assertIn('features.shell_tool=false', args)
        self.assertIn('project_doc_max_bytes=0', args)
        payload = json.loads(kwargs['stdin'])
        self.assertEqual(payload['track'], 'go')
        out = Path(args[args.index('--output-last-message')+1])
        out.write_text(json.dumps(candidate()))
        return 0, ''

    def start_with(self, runner, codex=None):
        with patch('gym.generation.shutil.which', return_value='/bin/codex'), \
             patch('gym.generation.run_process', side_effect=codex or self.fake_codex), \
             patch('gym.generation.execute', side_effect=runner):
            job = self.generator.start('Build a small local journal analyzer.', 'go')
            return self.wait(job)

    def test_async_success_publishes_starter_only_and_reloads(self):
        calls = []
        def runner(meta, files, folder, runtime):
            calls.append(copy.deepcopy(files))
            return result(PRIVATE in files['main.go'])
        job = self.start_with(runner)
        self.assertEqual(job['status'], 'complete', job)
        self.assertEqual(len(calls), 2)
        self.assertIn(PRIVATE, calls[0]['main.go'])
        self.assertNotIn(PRIVATE, calls[1]['main.go'])
        project = self.gym.project(job['projectId'])
        self.assertEqual(project['validation']['checks'], 4)
        self.assertEqual(len(self.gym.catalog), self.initial_count+1)
        for folder in [self.gym.generated, self.gym.workspaces, self.gym.runtime]:
            for path in folder.rglob('*'):
                if path.is_file():
                    self.assertNotIn(PRIVATE, path.read_text(), str(path))
        self.assertFalse(list(self.gym.runtime.glob('design-*')))
        self.assertEqual(Gym(self.tmp.name).project(job['projectId'])['title'], 'Weekend journal')

    def test_bad_reference_retries_without_publishing_or_leaking_feedback(self):
        def runner(*args):
            r = result(False); r['output'] = PRIVATE
            return r
        with patch('gym.generation.run_process', side_effect=self.fake_codex) as process, \
             patch('gym.generation.shutil.which', return_value='/bin/codex'), \
             patch('gym.generation.execute', side_effect=runner):
            job = self.wait(self.generator.start('Build a small local journal analyzer.', 'go'))
        self.assertEqual(job['status'], 'failed')
        self.assertEqual(process.call_count, 3)
        self.assertNotIn(PRIVATE, json.dumps(job))
        self.assertEqual(len(self.gym.catalog), self.initial_count)
        self.assertEqual(list(self.gym.generated.iterdir()), [])
        self.assertFalse(self.gym.job_lock.locked())

    def test_passing_or_unloadable_starter_is_not_published(self):
        for starter in [result(True), result(False, observed=False)]:
            with self.subTest(starter=starter):
                def runner(meta, files, *args):
                    return result(True) if PRIVATE in files['main.go'] else starter
                job = self.start_with(runner)
                self.assertEqual(job['status'], 'failed')
                self.assertEqual(list(self.gym.generated.iterdir()), [])

    def test_failed_browser_startup_prevents_publication(self):
        data = candidate()
        data.update(entry='index.html', testFiles=['challenge.spec.js'],
                    docs=[{'title': 'HTML', 'url': 'https://developer.mozilla.org/en-US/docs/Web/HTML'}],
                    files=[{'path': 'index.html', 'content': '<h1>Starter</h1>'},
                           {'path': 'challenge.spec.js', 'content': '// protected browser tests'}],
                    referenceFiles=[{'path': 'index.html', 'content': '<h1>'+PRIVATE+'</h1>'}])
        def codex(args, cwd, **kwargs):
            Path(args[args.index('--output-last-message')+1]).write_text(json.dumps(data))
            return 0, ''
        with patch('gym.generation.shutil.which', return_value='/bin/codex'), \
             patch('gym.generation.run_process', side_effect=codex), \
             patch('gym.generation.execute', return_value=result(True)) as run, \
             patch('gym.generation.browser_ready', side_effect=GymError('page startup failed')) as smoke:
            job = self.wait(self.generator.start('Build a small local weekend planner.', 'html'))
        self.assertEqual(job['status'], 'failed')
        self.assertEqual(smoke.call_count, 3)
        self.assertEqual(run.call_count, 3)  # Only references run; broken starters never reach grading.
        self.assertEqual(list(self.gym.generated.iterdir()), [])
        self.assertEqual(len(self.gym.catalog), self.initial_count)
        self.assertFalse(list(self.gym.runtime.glob('startup-*')))

    def test_codex_failure_releases_lock(self):
        job = self.start_with(lambda *args: self.fail('runner should not start'),
                              codex=lambda *args, **kwargs: (1, 'private diagnostic'))
        self.assertEqual(job['status'], 'failed')
        self.assertNotIn('private diagnostic', job['message'])
        self.assertFalse(self.gym.job_lock.locked())

    def test_workspace_copy_failure_rolls_back_publication(self):
        def fail_workspace(source, dest, *args, **kwargs):
            Path(dest).mkdir()
            (Path(dest)/'partial.txt').write_text('partial copy')
            raise OSError('simulated disk failure')
        def runner(meta, files, *args): return result(PRIVATE in files['main.go'])
        with patch('gym.generation.shutil.copytree', side_effect=fail_workspace):
            job = self.start_with(runner)
        self.assertEqual(job['status'], 'failed')
        self.assertEqual(list(self.gym.generated.iterdir()), [])
        self.assertFalse(list(self.gym.workspaces.glob('custom-*')))
        self.assertEqual(len(Gym(self.tmp.name).catalog), self.initial_count)

    def test_workspace_rename_failure_rolls_back_published_manifest(self):
        real_rename = Path.rename
        def fail_workspace(path, dest):
            if Path(dest).parent == self.gym.workspaces:
                raise OSError('simulated rename failure')
            return real_rename(path, dest)
        def runner(meta, files, *args): return result(PRIVATE in files['main.go'])
        with patch.object(Path, 'rename', fail_workspace):
            job = self.start_with(runner)
        self.assertEqual(job['status'], 'failed')
        self.assertEqual(list(self.gym.generated.iterdir()), [])
        self.assertFalse(list(self.gym.workspaces.glob('custom-*')))
        self.assertEqual(len(self.gym.catalog), self.initial_count)

    def test_restart_marks_interrupted_jobs_failed_and_preserves_completed(self):
        for status in ['queued', 'running', 'complete']:
            (self.gym.runtime/f'generation-{status}.json').write_text(json.dumps({'id': status, 'status': status}))
        restarted = Generator(self.gym)
        self.assertEqual(restarted.get('queued')['status'], 'failed')
        self.assertEqual(restarted.get('running')['status'], 'failed')
        self.assertEqual(restarted.get('complete')['status'], 'complete')
        with self.assertRaises(GymError): restarted.get('missing')

    def test_restart_removes_private_scratch_but_preserves_runner_cache(self):
        for prefix in ['design', 'reference', 'starter', 'startup']:
            folder = self.gym.runtime/(prefix+'-abandoned'); folder.mkdir()
            (folder/'candidate.json').write_text(PRIVATE)
        cache = self.gym.runtime/'runner-cache'; cache.mkdir()
        (cache/'keep.txt').write_text('shared build cache')
        outside = Path(self.tmp.name)/'outside'; outside.mkdir()
        (outside/'keep.txt').write_text('not generation scratch')
        link = self.gym.runtime/'design-link'; link.symlink_to(outside, target_is_directory=True)
        restarted = Generator(self.gym)
        # Server startup calls this after claiming both listeners; construction alone must not clean.
        self.assertTrue((self.gym.runtime/'design-abandoned').exists())
        restarted.cleanup_interrupted()
        for prefix in ['design', 'reference', 'starter', 'startup']:
            self.assertFalse((self.gym.runtime/(prefix+'-abandoned')).exists())
        self.assertTrue(link.is_symlink())
        self.assertEqual((outside/'keep.txt').read_text(), 'not generation scratch')
        self.assertEqual((cache/'keep.txt').read_text(), 'shared build cache')

    def test_validation_and_busy_lock_do_not_dispatch_work(self):
        for prompt, track, timebox in [('short', 'go', 'weekend'), ('x'*30, 'unknown', 'weekend'), ('x'*30, 'go', '')]:
            with self.assertRaises(GymError): self.generator.start(prompt, track, timebox)
        self.gym.job_lock.acquire()
        try:
            with self.assertRaises(GymError) as err:
                self.generator.start('Build a small local journal analyzer.', 'go')
            self.assertEqual(err.exception.status, 409)
        finally:
            self.gym.job_lock.release()
        self.assertEqual(self.generator.jobs, {})


if __name__ == '__main__': unittest.main()
