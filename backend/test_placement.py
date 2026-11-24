"""
Seviye tespit sınavı uç noktası: /api/placement/questions
Girişsiz çalışır, her kurdan 4 özgün (q-orj) ve okuma parçası gerektirmeyen soru döner.
"""
import os
import sys
import tempfile
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("PREPMASTER_DB_PATH", os.path.join(tempfile.mkdtemp(), "placement_test.db"))

from fastapi.testclient import TestClient  # noqa: E402

from backend.app import app  # noqa: E402

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]


class TestPlacementEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_returns_four_general_questions_per_level_without_login(self):
        res = self.client.get("/api/placement/questions")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["levels"], LEVELS)
        self.assertEqual(data["per_level"], 4)
        self.assertEqual(data["pass_mark"], 3)
        for lvl in LEVELS:
            qs = data["questions"][lvl]
            self.assertEqual(len(qs), 4, lvl)
            self.assertEqual(len({q["id"] for q in qs}), 4, lvl)
            for q in qs:
                self.assertTrue(q["id"].startswith("q-orj-"), q["id"])
                self.assertEqual(q["level"], lvl)
                self.assertEqual(q["university_id"], "general")
                self.assertFalse(q.get("passage"), q["id"])
                self.assertIn(q["correct_answer"], [o["key"] for o in q["options"]])

    def test_questions_are_randomised_between_calls(self):
        seen = set()
        for _ in range(5):
            data = self.client.get("/api/placement/questions").json()
            seen.add(tuple(q["id"] for q in data["questions"]["B1"]))
        self.assertGreater(len(seen), 1)


if __name__ == "__main__":
    unittest.main()
