"""Source-grounded regression tests for all v48 study exercises."""
from pathlib import Path
import json, re, unittest

P = Path(__file__).resolve().parents[1] / "app/src/main/assets/index.html"
class QuizContentAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        html = P.read_text(encoding="utf-8")
        m = re.search(r"<script>window\.STUDY=(.*?);</script>", html, re.S)
        if not m:
            raise RuntimeError("STUDY data missing")
        cls.book=json.loads(m.group(1))
        cls.chapters=cls.book["sections"]
        cls.questions=[(c,q) for c in cls.chapters for q in c["questions"]]

    def test_all_730_study_assignments_exist(self):
        self.assertEqual(114,len(self.chapters))
        self.assertEqual(502,len(self.questions))
        self.assertEqual(228,sum(len(c["reflection"]) for c in self.chapters))

    def test_502_question_options_and_answers(self):
        for num,(section,q) in enumerate(self.questions,1):
            with self.subTest(question=num):
                self.assertEqual("multiple_choice",q["type"])
                self.assertEqual(4,len(q["options"]))
                self.assertEqual(4,len(set(o.strip().casefold() for o in q["options"])))
                self.assertIn(q["correct"],range(4))
                self.assertTrue(q["text"].strip())
                self.assertTrue(q["options"][q["correct"]].strip())

    def test_502_evidence_fragments_and_source_pages(self):
        for num,(section,q) in enumerate(self.questions,1):
            with self.subTest(question=num):
                evidence=q["evidence"]
                self.assertTrue(evidence)
                self.assertTrue(any(evidence in b["text"] for b in section["blocks"]))
                pages={b["page"] for b in section["blocks"]}
                self.assertTrue(q["sourcePage"] in pages or q["sourcePage"]==section["page"])

    def test_confirmed_ambiguities_closed(self):
        def q(n):return self.questions[n-1][1]
        # Previously two almost identical correct answers.
        self.assertIn("врагами людей",q(177)["options"][0])
        self.assertNotIn("Зачем же вы берете", " ".join(q(177)["options"]))
        self.assertNotIn("не касались, и удерживал", " ".join(q(357)["options"]))
        # Wrongly sequenced passage in chapter 23.
        self.assertIn("слепца",q(80)["options"][q(80)["correct"]])
        # Source Quran translation, not outdated versions.
        for n in (43,84,85,86,124,317,338):
            sec,qx=self.questions[n-1]
            self.assertTrue(qx["options"][qx["correct"]].rstrip(" .!;") in " ".join(b["text"] for b in sec["blocks"]))
        # Numeric answers fit the question.
        for n in (385,478,493):
            self.assertRegex(q(n)["options"][q(n)["correct"]],r"(Два|Три)")

    def test_book_note_and_block_counts(self):
        self.assertEqual(2301,sum(len(c["blocks"]) for c in self.chapters))
        self.assertEqual(117,len(self.book["preface"]))
        self.assertGreaterEqual(len(self.book["appendix"]),213)

if __name__=="__main__":unittest.main()
