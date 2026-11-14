"""
Cevap anahtarını dengeler (14.11.2026).

Sorun: 197 sorunun %70'inde doğru şık "A", dinleme sorularının %70'inde "B" idi;
şıklar hiçbir istemcide karıştırılmıyordu. Okumadan hep aynı harfi işaretleyen
yüksek puan alıyordu.

Çözüm: her sorunun şıkları, soru kimliğinden türeyen sabit bir tohumla KALICI
olarak karıştırılır (tüm istemciler ve çevrimdışı mobil aynı veriyi görür,
puanlama değişmez). Açıklamalardaki "B şıkkı", "Option C", "(A)" gibi harf
atıfları yeni harflere çevrilir.

Harf sayılmayan durumlar: "Metin A", "Text B", "Hall A", "60°C" ve
explanation_en'in başındaki İngilizce "A" artikeli.

Kullanım:  python scripts/shuffle_answer_keys.py          (kuru çalıştırma)
           python scripts/shuffle_answer_keys.py --write  (data/ ve mobile/assets/data/ yazar)
Bir kez çalıştırın: her çalıştırma şıkları yeniden karıştırır.
"""
import collections
import json
import random
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LETTERS = "ABCDE"

TOKEN = re.compile(r"(?<![A-Za-zÇĞİÖŞÜçğıöşü0-9'’°-])([A-E])(?![A-Za-zÇĞİÖŞÜçğıöşü0-9-])")
NOT_OPTION_BEFORE = re.compile(r"(Text|Metin|Hall)\s$")


def remap_text(text: str, mapping: dict, field: str) -> str:
    def repl(m):
        start = m.start()
        if NOT_OPTION_BEFORE.search(text[max(0, start - 6):start]):
            return m.group(0)
        # İngilizce açıklamanın başındaki artikel: "A continuous ...", "A 'syllabus' ..."
        if field == "explanation_en" and start == 0 and m.group(1) == "A" and re.match(r"\s+[a-z']", text[1:]):
            return m.group(0)
        return mapping.get(m.group(1), m.group(1))
    return TOKEN.sub(repl, text)


def shuffle_item(item: dict, text_fields) -> None:
    opts = item["options"]
    old_keys = [o["key"] for o in opts]
    rng = random.Random("prepmaster-v1:" + item["id"])
    order = list(range(len(opts)))
    rng.shuffle(order)
    new_opts = []
    mapping = {}
    for new_pos, old_pos in enumerate(order):
        new_key = LETTERS[new_pos]
        mapping[old_keys[old_pos]] = new_key
        new_opts.append({**opts[old_pos], "key": new_key})
    item["options"] = new_opts
    item["correct_answer"] = mapping[item["correct_answer"]]
    for f in text_fields:
        if isinstance(item.get(f), str):
            item[f] = remap_text(item[f], mapping, f)


def main(write: bool):
    qpath = ROOT / "data" / "questions.json"
    lpath = ROOT / "data" / "listening.json"
    questions = json.loads(qpath.read_text(encoding="utf-8"))
    listening = json.loads(lpath.read_text(encoding="utf-8"))

    before_q = collections.Counter(q["correct_answer"] for q in questions)
    before_l = collections.Counter(q["correct_answer"] for t in listening for q in t["questions"])

    for q in questions:
        shuffle_item(q, ("explanation_tr", "explanation_en"))
    for track in listening:
        for q in track["questions"]:
            shuffle_item(q, ("explanation_tr", "explanation_en"))

    # Doğrulama: doğru şıkkın METNİ değişmemeli
    orig_q = {q["id"]: q for q in json.loads(qpath.read_text(encoding="utf-8"))}
    for q in questions:
        o = orig_q[q["id"]]
        old_text = next(x["text"] for x in o["options"] if x["key"] == o["correct_answer"])
        new_text = next(x["text"] for x in q["options"] if x["key"] == q["correct_answer"])
        assert old_text == new_text, q["id"]
        assert sorted(x["text"] for x in o["options"]) == sorted(x["text"] for x in q["options"]), q["id"]

    print("Sorular   önce:", dict(sorted(before_q.items())), " sonra:",
          dict(sorted(collections.Counter(q["correct_answer"] for q in questions).items())))
    print("Dinleme   önce:", dict(sorted(before_l.items())), " sonra:",
          dict(sorted(collections.Counter(q["correct_answer"] for t in listening for q in t["questions"]).items())))

    if write:
        qpath.write_text(json.dumps(questions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        lpath.write_text(json.dumps(listening, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for name in ("questions.json", "listening.json"):
            shutil.copyfile(ROOT / "data" / name, ROOT / "mobile" / "assets" / "data" / name)
        print("Yazıldı: data/ ve mobile/assets/data/")


if __name__ == "__main__":
    main("--write" in sys.argv)
