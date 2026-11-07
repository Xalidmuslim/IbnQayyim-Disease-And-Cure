"""Regression tests for reminder and search highlighting (v49)."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_FILE = ROOT / "app/src/main/assets/index.html"
BOOK_SHA256 = "14697ec798708c1c7fb6e66f3817297bde12f60a56c789735cb41992eaaf0704"

class JumpHighlightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML_FILE.read_text(encoding="utf-8")
        m = re.search(r"<script>window\.STUDY=(.*?);</script>", cls.html, re.S)
        if not m:
            raise RuntimeError("Book data missing")
        cls.book_raw = m.group(1)
        cls.data = json.loads(cls.book_raw)
        cls.sections = [{"blocks":cls.data["preface"]}, *cls.data["sections"],
                        {"blocks":cls.data["appendixRendered"]}]
        q = re.search(r"const HOME_QUOTES=(\[.*?\]);", cls.html, re.S)
        if not q:
            raise RuntimeError("Reminder data missing")
        cls.quotes = json.loads(q.group(1))

    def test_original_book_content_unchanged(self):
        self.assertEqual(BOOK_SHA256, hashlib.sha256(self.book_raw.encode("utf-8")).hexdigest())
        self.assertEqual(114, len(self.data["sections"]))
        self.assertEqual(502, sum(len(s["questions"]) for s in self.data["sections"]))

    def test_84_reminders_have_exact_targets(self):
        self.assertEqual(84,len(self.quotes))
        for i,quote in enumerate(self.quotes,1):
            with self.subTest(reminder=i):
                self.assertTrue(0<=quote["section"]<len(self.sections))
                blocks=self.sections[quote["section"]]["blocks"]
                self.assertTrue(0<=quote["block"]<len(blocks))
                txt=blocks[quote["block"]]["text"]
                self.assertEqual(quote["text"],txt[quote["start"]:quote["start"]+len(quote["text"])])

    def test_search_passes_exact_match_position(self):
        for token in ("data-find-block=", "data-find-start=", "data-find-length=",
                      "const bi=s.blocks.findIndex", "if(d.findBlock!==undefined)",
                      "quoteJump=typeof t==='string'"):
            self.assertIn(token,self.html)

    def test_chapter_title_matches_are_highlighted(self):
        for token in ("data-find-title-start=", "if(d.findTitleStart!==undefined)",
                      "quoteJump&&quoteJump.title&&quoteJump.section===current"):
            self.assertIn(token,self.html)

    def test_highlight_temporarily_visible_then_fades(self):
        for token in ('node.scrollIntoView(', 'quoteJump=null},4500);',
                      'quote-highlight-exit', 'quote-highlight-gone',
                      'id="quote-highlight"'):
            self.assertIn(token,self.html)

if __name__ == "__main__":
    unittest.main()
