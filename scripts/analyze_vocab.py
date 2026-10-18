# -*- coding: utf-8 -*-
"""
Generate exactly 100 CEFR words for each level (A1, A2, B1, B2, C1, C2).
Total: 600 rich, fully-populated vocabulary items with IPA, definition, Turkish translation,
synonyms, antonyms, example sentences, and collocations.
"""

import json
from pathlib import Path

# Load existing words
with open("data/vocabulary.json", "r", encoding="utf-8") as f:
    existing_vocab = json.load(f)

# Group existing by level
by_level = {"A1": [], "A2": [], "B1": [], "B2": [], "C1": [], "C2": []}
existing_words = set()

for item in existing_vocab:
    lvl = item.get("level", "B2")
    w = item.get("word", "").strip().lower()
    if lvl in by_level and w and w not in existing_words:
        # Standardize item structure
        standardized = {
            "id": item.get("id"),
            "word": item.get("word").strip(),
            "level": lvl,
            "part_of_speech": item.get("part_of_speech", "noun"),
            "pronunciation": item.get("pronunciation", "/.../"),
            "meaning_tr": item.get("meaning_tr", ""),
            "definition_en": item.get("definition_en", ""),
            "synonyms": item.get("synonyms", []),
            "antonyms": item.get("antonyms", []),
            "example_sentence": item.get("example_sentence", ""),
            "collocation": item.get("collocation") or (item.get("collocations")[0] if item.get("collocations") else ""),
            "status": "unreviewed"
        }
        by_level[lvl].append(standardized)
        existing_words.add(w)

print("Existing counts per level:", {k: len(v) for k, v in by_level.items()})
