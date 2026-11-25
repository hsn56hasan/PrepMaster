"""Konu Yolu: seviyeye göre ilerleyen, alıştırmalı gündelik hayat dersleri.

Yapı (data/lessons.json): seviye -> ünite (5 konu) -> konu (ders).
Kurallar:
- Bir seviye, öğrencinin başlangıç seviyesine (seviye tespiti, yoksa profil kuru) kadar açıktır;
  üstündeki seviye, bir önceki seviyenin konularının %80'i tamamlanınca açılır.
- Seviye içinde konular sırayla açılır: bir konu, bir önceki konu geçilince (en az 1 yıldız) açılır.
- Ünite tekrarı, ünitenin bütün konuları geçilince açılır; ilerlemeyi engellemez, ek XP verir.
- Karışık tekrar, geçilen konulardan en zayıf/en eski olanları karıştırır.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
LEVEL_UNLOCK_RATIO = 0.8
XP_LESSON = 10
XP_PERFECT_BONUS = 5
XP_UNIT_REVIEW = 20
XP_MIXED_REVIEW = 10
REVIEW_TOPIC_COUNT = 4


class LessonPath:
    def __init__(self, data: Dict[str, Any]):
        self.data = data or {"levels": []}
        self.levels: Dict[str, Dict[str, Any]] = {}
        self.topics: Dict[str, Dict[str, Any]] = {}
        self.units: Dict[str, Dict[str, Any]] = {}
        self.topic_order: Dict[str, List[str]] = {}
        for lv in self.data.get("levels", []):
            code = lv["level"]
            self.levels[code] = lv
            order: List[str] = []
            for ui, unit in enumerate(lv.get("units", [])):
                unit["_level"] = code
                unit["_index"] = ui
                self.units[unit["id"]] = unit
                for t in unit.get("topics", []):
                    t["_level"] = code
                    t["_unit"] = unit["id"]
                    self.topics[t["id"]] = t
                    order.append(t["id"])
            self.topic_order[code] = order

    @classmethod
    def load(cls, path: Path) -> "LessonPath":
        if not path.exists():
            return cls({"levels": []})
        with open(path, "r", encoding="utf-8") as f:
            return cls(json.load(f))

    # ---------- kilit kuralları ----------
    @staticmethod
    def _passed(progress: Dict[str, Dict[str, Any]], node_id: str) -> bool:
        return (progress.get(node_id) or {}).get("stars", 0) >= 1

    def level_done_count(self, progress, level: str) -> int:
        return sum(1 for tid in self.topic_order.get(level, []) if self._passed(progress, tid))

    def level_unlocked(self, progress, start_level: str, level: str) -> bool:
        if level not in LEVELS:
            return False
        start = LEVELS.index(start_level) if start_level in LEVELS else 0
        idx = LEVELS.index(level)
        if idx <= start:
            return True
        prev = LEVELS[idx - 1]
        total = len(self.topic_order.get(prev, []))
        return total > 0 and self.level_done_count(progress, prev) >= total * LEVEL_UNLOCK_RATIO \
            and self.level_unlocked(progress, start_level, prev)

    def topic_unlocked(self, progress, start_level: str, topic_id: str) -> bool:
        t = self.topics.get(topic_id)
        if not t:
            return False
        level = t["_level"]
        if not self.level_unlocked(progress, start_level, level):
            return False
        order = self.topic_order[level]
        i = order.index(topic_id)
        return i == 0 or self._passed(progress, order[i - 1]) or self._passed(progress, topic_id)

    def unit_unlocked(self, progress, start_level: str, unit_id: str) -> bool:
        u = self.units.get(unit_id)
        if not u or not self.level_unlocked(progress, start_level, u["_level"]):
            return False
        return all(self._passed(progress, t["id"]) for t in u.get("topics", []))

    # ---------- çıktı ----------
    @staticmethod
    def public_topic(t: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in t.items() if not k.startswith("_")}

    def overview(self, progress, start_level: str, selected: Optional[str] = None) -> Dict[str, Any]:
        levels_out = []
        current_topic = None
        for code in LEVELS:
            if code not in self.levels:
                continue
            unlocked = self.level_unlocked(progress, start_level, code)
            levels_out.append({
                "level": code,
                "title": self.levels[code].get("title", code),
                "unlocked": unlocked,
                "done": self.level_done_count(progress, code),
                "total": len(self.topic_order[code]),
            })
        if selected not in self.levels:
            # Varsayılan: açık seviyelerden yarım kalan ilki, yoksa açık olan en yüksek seviye
            open_lv = [l for l in levels_out if l["unlocked"]]
            start = start_level if start_level in self.levels else (open_lv[0]["level"] if open_lv else "A1")
            pending = [l for l in open_lv if l["done"] < l["total"] and LEVELS.index(l["level"]) >= LEVELS.index(start)]
            selected = pending[0]["level"] if pending else (open_lv[-1]["level"] if open_lv else start)

        units_out = []
        lv = self.levels.get(selected, {"units": []})
        for unit in lv.get("units", []):
            nodes = []
            for t in unit.get("topics", []):
                p = progress.get(t["id"]) or {}
                is_open = self.topic_unlocked(progress, start_level, t["id"])
                passed = self._passed(progress, t["id"])
                status = "done" if passed else ("current" if is_open else "locked")
                if status == "current" and current_topic is None:
                    current_topic = t["id"]
                nodes.append({
                    "id": t["id"], "title_tr": t["title_tr"], "title_en": t["title_en"],
                    "icon": t.get("icon", "book-open"), "status": status,
                    "stars": p.get("stars", 0), "best_pct": p.get("best_pct", 0),
                })
            up = progress.get(unit["id"]) or {}
            units_out.append({
                "id": unit["id"], "index": unit["_index"] + 1, "title_tr": unit["title_tr"],
                "done": sum(1 for n in nodes if n["status"] == "done"), "total": len(nodes),
                "review_unlocked": self.unit_unlocked(progress, start_level, unit["id"]),
                "review_stars": up.get("stars", 0),
                "topics": nodes,
            })

        completed = sum(1 for tid in self.topics if self._passed(progress, tid))
        reviewable = [tid for tid in self.topics if self._passed(progress, tid)]
        return {
            "start_level": start_level,
            "selected_level": selected,
            "levels": levels_out,
            "units": units_out,
            "current_topic": current_topic,
            "stats": {
                "xp_total": sum(int(p.get("xp_total") or 0) for p in progress.values()),
                "completed": completed,
                "total": len(self.topics),
                "perfect": sum(1 for tid in self.topics if (progress.get(tid) or {}).get("stars", 0) >= 3),
                "review_available": len(reviewable) > 0,
            },
        }

    def unit_bundle(self, unit_id: str) -> Dict[str, Any]:
        u = self.units[unit_id]
        return {
            "kind": "unit", "id": unit_id, "level": u["_level"],
            "title_tr": f"Ünite {u['_index'] + 1} tekrarı · {u['title_tr']}",
            "topics": [self.public_topic(t) for t in u.get("topics", [])],
        }

    def review_bundle(self, progress, level: Optional[str] = None) -> Dict[str, Any]:
        """Geçilen konulardan en az yıldızlı ve en uzun süredir dokunulmayanları seçer."""
        cands = [tid for tid in self.topics if self._passed(progress, tid)
                 and (not level or self.topics[tid]["_level"] == level)]
        cands.sort(key=lambda tid: (progress[tid].get("stars", 0), progress[tid].get("last_at") or ""))
        chosen = cands[:REVIEW_TOPIC_COUNT]
        lvl = level or (self.topics[chosen[0]]["_level"] if chosen else None)
        return {
            "kind": "review", "id": f"review-{(lvl or 'all').lower()}", "level": lvl,
            "title_tr": "Karışık tekrar",
            "topics": [self.public_topic(self.topics[t]) for t in chosen],
        }

    def node_kind(self, node_id: str) -> Optional[str]:
        if node_id in self.topics:
            return "topic"
        if node_id in self.units:
            return "unit"
        if node_id.startswith("review-") and node_id[7:].upper() in LEVELS + ["ALL"]:
            return "review"
        return None

    def xp_for(self, kind: str, pct: int) -> int:
        if kind == "topic":
            return XP_LESSON + (XP_PERFECT_BONUS if pct >= 100 else 0)
        if kind == "unit":
            return XP_UNIT_REVIEW
        return XP_MIXED_REVIEW
