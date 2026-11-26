"""
Soru bankası kategorileri: rakip/sınav karşılaştırmasıyla eklenen yeni kategoriler (2026-11)
her seviyede yeterli, biçimi doğru sorularla genel havuzda yer almalı; mobil kopya da aynı soruları içermeli.
"""
import json
import re
import unittest
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
QUESTIONS = json.loads((BASE_DIR / "data" / "questions.json").read_text(encoding="utf-8"))
MOBILE = json.loads((BASE_DIR / "mobile" / "assets" / "data" / "questions.json").read_text(encoding="utf-8"))
LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
NEW_CATEGORIES = ["Irrelevant Sentence", "Sentence Insertion", "Error Identification", "Word Formation", "Translation"]
GROWN_CATEGORIES = {"Paragraph Completion": 99, "Dialogue": 89}


class TestQuestionCategories(unittest.TestCase):
    def test_new_categories_cover_every_level(self):
        for cat in NEW_CATEGORIES:
            per_level = Counter(q["level"] for q in QUESTIONS if q["category"] == cat and q["university_id"] == "general")
            for lvl in LEVELS:
                self.assertGreaterEqual(per_level[lvl], 8, f"{cat} {lvl}")

    def test_thin_categories_were_expanded(self):
        counts = Counter(q["category"] for q in QUESTIONS)
        for cat, minimum in GROWN_CATEGORIES.items():
            self.assertGreaterEqual(counts[cat], minimum, cat)

    def test_new_questions_are_well_formed(self):
        new = [q for q in QUESTIONS if re.match(r"q-gen-(irr|ins|err|wf|tr|dlg|pc)-", q["id"])]
        self.assertGreaterEqual(len(new), 336)
        ids = [q["id"] for q in QUESTIONS]
        self.assertEqual(len(ids), len(set(ids)))
        for q in new:
            self.assertEqual([o["key"] for o in q["options"]], ["A", "B", "C", "D"], q["id"])
            self.assertIn(q["correct_answer"], "ABCD", q["id"])
            self.assertTrue(q["explanation_tr"].strip(), q["id"])
            self.assertNotRegex(json.dumps(q, ensure_ascii=False), "[âîû]", q["id"])

    def test_mobile_copy_has_all_general_questions(self):
        mobile_ids = {q["id"] for q in MOBILE}
        missing = [q["id"] for q in QUESTIONS if re.match(r"q-gen-(irr|ins|err|wf|tr|dlg|pc)-", q["id"]) and q["id"] not in mobile_ids]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
