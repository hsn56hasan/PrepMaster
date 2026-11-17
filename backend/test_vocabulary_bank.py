"""
Kelime bankası ve kelimelerden üretilen soruların denetimi (scripts/build_vocabulary.py).
"""
import collections
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


class TestVocabularyBank(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vocab = load("vocabulary.json")
        cls.questions = load("questions.json")
        cls.kel = [q for q in cls.questions if q["id"].startswith("q-kel-")]

    def test_minimum_sizes(self):
        self.assertGreaterEqual(len({v["word"].lower() for v in self.vocab}), 2000)
        self.assertGreaterEqual(len(self.questions), 10000)

    def test_vocab_entries_complete_and_ids_unique(self):
        ids = [v["id"] for v in self.vocab]
        self.assertEqual(len(ids), len(set(ids)))
        for v in self.vocab:
            for f in ("word", "level", "part_of_speech", "meaning_tr", "definition_en", "example_sentence"):
                self.assertTrue(v.get(f), f"{v['id']} {f}")
            self.assertIn(v["level"], {"A1", "A2", "B1", "B2", "C1", "C2"})
        # Eski 600 kayıt (öğrenci ilerlemesi bu kimliklere bağlı) yerinde
        self.assertEqual(sum(1 for v in self.vocab if not re.match(r"^v-..-k\d+$", v["id"])), 600)

    def test_generated_questions_well_formed(self):
        self.assertGreater(len(self.kel), 5000)
        for q in self.kel:
            texts = [o["text"].strip().lower() for o in q["options"]]
            self.assertEqual([o["key"] for o in q["options"]], ["A", "B", "C", "D"], q["id"])
            self.assertEqual(len(set(texts)), 4, q["id"])
            self.assertIn(q["correct_answer"], "ABCD", q["id"])
            self.assertEqual(q["university_id"], "general")
            self.assertNotRegex(q["question"], r"\b[Aa]n? ____", q["id"])  # artikel cevabı ele vermemeli
        dist = collections.Counter(q["correct_answer"] for q in self.kel)
        self.assertLessEqual(max(dist.values()) / len(self.kel), 0.30)

    def test_reviewed_ambiguous_distractors_never_appear(self):
        """Elle gözden geçirmede 'o da cümleye uyar' diye işaretlenen çiftler (celdirici_haric.txt)."""
        pairs = set()
        for line in (ROOT / "scripts" / "kelime_kaynak" / "celdirici_haric.txt").read_text(encoding="utf-8").splitlines():
            line = line.strip().lower()
            if line and not line.startswith("#") and "|" in line:
                a, b = line.split("|", 1)
                pairs |= {(a, b), (b, a)}
        self.assertGreater(len(pairs), 400)
        for q in self.kel:
            correct = next(o["text"] for o in q["options"] if o["key"] == q["correct_answer"]).lower()
            for o in q["options"]:
                self.assertNotIn((correct, o["text"].lower()), pairs, q["id"])

    def test_question_ids_unique_and_mobile_in_sync(self):
        ids = [q["id"] for q in self.questions]
        self.assertEqual(len(ids), len(set(ids)))
        mobile = ROOT / "mobile" / "assets" / "data"
        self.assertEqual((ROOT / "data" / "vocabulary.json").read_bytes(), (mobile / "vocabulary.json").read_bytes())
        # APK herkese açık bir dosyadır: ücretli (üniversiteye özel) içerik içine gömülmez
        for name in ("questions.json", "listening.json", "speaking.json"):
            shipped = json.loads((mobile / name).read_text(encoding="utf-8"))
            self.assertEqual({x.get("university_id") for x in shipped}, {"general"}, name)
            free = [x for x in load(name) if x.get("university_id") == "general"]
            self.assertEqual(shipped, free, f"{name}: python scripts/sync_mobile_assets.py çalıştırın")


if __name__ == "__main__":
    unittest.main()
