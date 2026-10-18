# -*- coding: utf-8 -*-
"""
Compile 60 listening tracks into data/listening.json:
Exactly 10 tracks per CEFR level (A1, A2, B1, B2, C1, C2).
"""

import json
from pathlib import Path
from scripts.expand_listening import NEW_LISTENING_TRACKS as A1_TRACKS
from scripts.generate_all_listening import MORE_TRACKS as A2_TRACKS
from scripts.data_listening_b1 import B1_TRACKS
from scripts.data_listening_b2_c1_c2 import B2_TRACKS, C1_TRACKS, C2_TRACKS

DATA_PATH = Path("data/listening.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    existing_tracks = json.load(f)

# Combine all
all_candidates = existing_tracks + A1_TRACKS + A2_TRACKS + B1_TRACKS + B2_TRACKS + C1_TRACKS + C2_TRACKS

seen_ids = set()
final_tracks = []
by_level = {"A1": [], "A2": [], "B1": [], "B2": [], "C1": [], "C2": []}

for t in all_candidates:
    t_id = t["id"]
    lvl = t.get("level", "B2")
    if t_id not in seen_ids and lvl in by_level and len(by_level[lvl]) < 10:
        seen_ids.add(t_id)
        by_level[lvl].append(t)
        final_tracks.append(t)

print("Final listening track counts by level:")
for lvl, tracks in by_level.items():
    print(f"  {lvl}: {len(tracks)}")
    assert len(tracks) >= 10, f"Level {lvl} has only {len(tracks)} tracks, expected 10!"

with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(final_tracks, f, ensure_ascii=False, indent=2)

print(f"Successfully saved {len(final_tracks)} listening tracks to {DATA_PATH}")
