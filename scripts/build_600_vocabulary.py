# -*- coding: utf-8 -*-
"""
Build 600 items for vocabulary.json: exactly 100 items per CEFR level (A1, A2, B1, B2, C1, C2).
"""

import json
from pathlib import Path
from scripts.data_a1_a2 import A1_DATA, A2_DATA
from scripts.data_b1_b2 import B1_DATA, B2_DATA
from scripts.data_c1_c2 import C1_DATA, C2_DATA

OUTPUT_PATH = Path("data/vocabulary.json")

def format_item(level, index, tuple_item):
    word, pos, pron, meaning_tr, def_en, syns, ants, ex, colloc = tuple_item
    item_id = f"v-{level.lower()}-{index}"
    return {
        "id": item_id,
        "word": word,
        "level": level,
        "part_of_speech": pos,
        "pronunciation": pron,
        "meaning_tr": meaning_tr,
        "definition_en": def_en,
        "synonyms": syns,
        "antonyms": ants,
        "example_sentence": ex,
        "collocation": colloc,
        "status": "unreviewed"
    }

final_vocab = []

level_datasets = [
    ("A1", A1_DATA),
    ("A2", A2_DATA),
    ("B1", B1_DATA),
    ("B2", B2_DATA),
    ("C1", C1_DATA),
    ("C2", C2_DATA)
]

for level, dataset in level_datasets:
    # Ensure exactly 100 items
    assert len(dataset) == 100, f"Dataset for {level} has {len(dataset)} items, expected 100!"
    for i, item in enumerate(dataset, 1):
        formatted = format_item(level, i, item)
        final_vocab.append(formatted)

print(f"Total vocabulary items compiled: {len(final_vocab)}")

# Verify counts per level
from collections import Counter
counts = Counter(item["level"] for item in final_vocab)
print("Counts by level:", dict(counts))

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(final_vocab, f, ensure_ascii=False, indent=2)

print(f"Successfully saved to {OUTPUT_PATH}")
