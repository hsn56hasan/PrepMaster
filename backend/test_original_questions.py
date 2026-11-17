"""
Özgün (q-orj-*) soruların yapısal denetimi: scripts/add_original_questions.py ile eklenir.
"""
import collections
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class TestOriginalQuestions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all = load(ROOT / "data" / "questions.json")
        cls.orj = [q for q in cls.all if q["id"].startswith("q-orj-")]

    def test_count_and_spread(self):
        self.assertEqual(len(self.orj), 120)
        self.assertEqual(set(collections.Counter(q["level"] for q in self.orj).values()), {20})
        self.assertTrue(all(q["university_id"] == "general" for q in self.orj))

    def test_each_question_is_well_formed(self):
        for q in self.orj:
            keys = [o["key"] for o in q["options"]]
            texts = [o["text"].strip().lower() for o in q["options"]]
            self.assertEqual(keys, ["A", "B", "C", "D"], q["id"])
            self.assertEqual(len(set(texts)), 4, q["id"])
            self.assertIn(q["correct_answer"], keys, q["id"])
            self.assertTrue(q["explanation_tr"] and q["explanation_en"], q["id"])
            if q["category"] in ("Reading", "Cloze Test"):
                self.assertTrue(q.get("passage"), q["id"])

    def test_answer_positions_not_predictable(self):
        dist = collections.Counter(q["correct_answer"] for q in self.orj)
        self.assertLessEqual(max(dist.values()) / len(self.orj), 0.35)

    def test_ids_unique_and_not_treated_as_templates(self):
        ids = [q["id"] for q in self.all]
        self.assertEqual(len(ids), len(set(ids)))
        template = re.compile(r"^q_[a-z_]+_(a1|a2|b1|b2|c1|c2)_\d+$|^q_general_prac_")
        self.assertFalse(any(template.search(q["id"]) for q in self.orj))

    def test_original_questions_ship_in_mobile_app(self):
        mobile = {q["id"] for q in load(ROOT / "mobile" / "assets" / "data" / "questions.json")}
        self.assertTrue({q["id"] for q in self.orj} <= mobile)


if __name__ == "__main__":
    unittest.main()
