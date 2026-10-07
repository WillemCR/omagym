"""Static consistency of the shipped catalog: metadata, briefs, starters and canonical tests agree."""
import json
from pathlib import Path
import unittest
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT/'curriculum'


def catalog():
    for manifest in sorted(CURRICULUM.glob('*.json')):
        for project in json.loads(manifest.read_text()):
            yield manifest.name, project


class CurriculumTest(unittest.TestCase):
    def test_ids_are_unique_and_match_folders(self):
        ids = [p['id'] for _, p in catalog()]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(sorted(ids), sorted(d.name for d in CURRICULUM.iterdir() if d.is_dir()))

    def test_entry_and_test_files_exist_and_entry_is_editable(self):
        for manifest, p in catalog():
            with self.subTest(p['id']):
                folder = CURRICULUM/p['id']
                entry = p.get('entry', 'main.go')
                tests = p.get('testFiles', ['challenge_test.go', 'go.mod'])
                self.assertTrue((folder/entry).is_file(), entry)
                self.assertNotIn(entry, tests)
                for name in tests:
                    self.assertTrue((folder/name).is_file(), name)

    def test_brief_states_every_requirement(self):
        for manifest, p in catalog():
            with self.subTest(p['id']):
                brief = (CURRICULUM/p['id']/'README.md').read_text().replace('`', '')
                self.assertGreaterEqual(len(p['requirements']), 2)
                for requirement in p['requirements']:
                    self.assertIn(requirement, brief)

    def test_every_declared_check_exists_in_the_canonical_tests(self):
        for manifest, p in catalog():
            if 'checks' not in p:
                continue
            with self.subTest(p['id']):
                folder = CURRICULUM/p['id']
                source = '\n'.join((folder/name).read_text() for name in p['testFiles'])
                self.assertEqual(len(p['checks']), len(set(p['checks'])))
                for check in p['checks']:
                    self.assertIn(check, source)

    def test_docs_are_https_links(self):
        for manifest, p in catalog():
            with self.subTest(p['id']):
                self.assertTrue(p['docs'])
                for doc in p['docs']:
                    url = urlparse(doc['url'])
                    self.assertEqual(url.scheme, 'https', doc['url'])
                    self.assertTrue(url.netloc and doc['title'].strip())


if __name__ == '__main__':
    unittest.main()
