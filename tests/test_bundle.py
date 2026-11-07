"""Static content and application-structure regression tests for editorial v48."""
from pathlib import Path
import hashlib
import json
import re
import unittest

BASE = Path(__file__).resolve().parents[1]
HTML = BASE / 'app/src/main/assets/index.html'
EXPECTED_SHA256 = '422756a2529207d17e46a47311fcbb478e8a7dee98fc66232325a4572f0475de'

class BundlingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = HTML.read_bytes()
        cls.html = cls.raw.decode('utf-8')
        match = re.search(r'<script>window\.STUDY=(.*?);</script>', cls.html, re.S)
        assert match, 'Missing embedded book study data'
        cls.study = json.loads(match.group(1))

    def test_html_integrity(self):
        self.assertEqual(EXPECTED_SHA256, hashlib.sha256(self.raw).hexdigest())

    def test_114_chapters(self):
        chapters = self.study['sections']
        self.assertEqual(114, len(chapters))
        self.assertEqual(list(range(1, 115)), [c['number'] for c in chapters])

    def test_full_study_text(self):
        self.assertEqual('Болезнь и исцеление', self.study['title'])
        self.assertEqual(117, len(self.study['preface']))
        self.assertTrue(all(len(c['blocks']) > 0 for c in self.study['sections']))

    def test_quiz_preserved(self):
        self.assertIn('function back()', self.html)
        self.assertIn('window.STUDY', self.html)
        self.assertIn('quiz', self.html.lower())

    def test_offline_android_shell(self):
        s = (BASE / 'app/src/main/AndroidManifest.xml').read_text(encoding='utf-8')
        self.assertIn('MainActivity', s)
        self.assertNotIn('android.permission.INTERNET', s)
        k = (BASE / 'app/src/main/java/com/xalidmuslim/diseaseandcure/MainActivity.kt').read_text(encoding='utf-8')
        self.assertIn('file:///android_asset/index.html', k)

    def test_no_audio_resources(self):
        self.assertFalse((BASE / 'source-variants').exists())
        self.assertFalse((BASE / 'app/src/main/assets/audio.html').exists())
        self.assertFalse((BASE / 'app/src/main/assets/audio').exists())

if __name__ == '__main__':
    unittest.main(verbosity=2)
