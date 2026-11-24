"""
Üniversiteye özel (q-uni-*) soruların yapısal denetimi: scripts/add_university_questions.py ile eklenir.
"""
import collections
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class TestUniversityQuestions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all = load(ROOT / "data" / "questions.json")
        cls.uni = [q for q in cls.all if q["id"].startswith("q-uni-")]
        cls.universities = {u["id"] for u in load(ROOT / "data" / "universities.json")} - {"general"}

    def test_every_university_has_four_per_level(self):
        counts = collections.Counter((q["university_id"], q["level"]) for q in self.uni)
        self.assertEqual({u for u, _ in counts}, self.universities)
        for u in self.universities:
            for lvl in LEVELS:
                self.assertEqual(counts[(u, lvl)], 4, (u, lvl))

    def test_pool_per_university_is_204(self):
        per_uni = collections.Counter(q["university_id"] for q in self.all)
        for u in self.universities:
            self.assertEqual(per_uni[u], 204, u)

    def test_each_question_is_well_formed(self):
        for q in self.uni:
            keys = [o["key"] for o in q["options"]]
            texts = [o["text"].strip().lower() for o in q["options"]]
            self.assertEqual(keys, ["A", "B", "C", "D"], q["id"])
            self.assertEqual(len(set(texts)), 4, q["id"])
            self.assertIn(q["correct_answer"], keys, q["id"])
            self.assertTrue(q["explanation_tr"], q["id"])
            self.assertNotIn("<", q["question"] + "".join(texts), q["id"])
            if q["category"] in ("Reading", "Cloze Test"):
                self.assertTrue(q.get("passage"), q["id"])

    def test_correct_option_is_not_a_length_giveaway(self):
        flagged = []
        for q in self.uni:
            lengths = sorted(((len(o["text"]), o["key"]) for o in q["options"]), reverse=True)
            (top, key), (second, _) = lengths[0], lengths[1]
            if key == q["correct_answer"] and top > 12 and top > 1.15 * second:
                flagged.append(q["id"])
        self.assertEqual(flagged, [])

    def test_answer_positions_not_predictable(self):
        dist = collections.Counter(q["correct_answer"] for q in self.uni)
        self.assertLessEqual(max(dist.values()) / len(self.uni), 0.30)

    def test_university_content_not_bundled_in_mobile_app(self):
        mobile = {q["id"] for q in load(ROOT / "mobile" / "assets" / "data" / "questions.json")}
        self.assertFalse({q["id"] for q in self.uni} & mobile)


if __name__ == "__main__":
    unittest.main()
