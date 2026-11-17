"""
Şablon içerikteki mekanik hataları düzeltir (15.11.2026 içerik denetimi).

1. Açıklamalara sızmış Çince "随机" ifadesi ("klinik çalışma随机 (rastgele) seçimi")
2. 25 numaralı şablonun yanlış cevabı: cümle zıtlık bildiriyor ("ciddi kısıtlarla karşılaştı;
   ____, ekip verim artışı sağladı") -> doğru bağlaç "nevertheless"; anahtar "conversely" idi
   ve doğru seçenek şıklarda hiç yoktu.
3. Dinleme metinlerinde "Proficiency proficiency" tekrarı
4. Şablon sorularda doğru şıkkın yeri soru numarasına göre sabit bir örüntü izliyordu
   (#1->B, #2->C, ...). Şıklar soru kimliğinden türeyen tohumla kalıcı karıştırılır.
   Şablon açıklamalarında harf atfı yoktur (kontrol edilir).

Kullanım:  python scripts/fix_template_content.py          (kuru çalıştırma)
           python scripts/fix_template_content.py --write  (data/ ve mobile/assets/data/ yazar)
15.11.2026'da BİR KEZ --write ile çalıştırıldı. 1-3 idempotenttir; 4 ise mevcut sırayı yeniden karıştırır
(cevaplar yine doğru kalır ama sıra değişir), bu yüzden --write ile tekrar çalıştırmaya gerek yoktur.
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
TEMPLATE_ID = re.compile(r"^q_[a-z_]+_(a1|a2|b1|b2|c1|c2)_\d+$|^q_general_prac_")
LETTER_REF = re.compile(r"(?<![A-Za-zÇĞİÖŞÜçğıöşü0-9'’°-])([A-E])(?![A-Za-zÇĞİÖŞÜçğıöşü0-9-])")

S25_EXPL = ("Cümlenin ilk yarısı olumsuz bir durumu (ciddi termal kısıtlar), ikinci yarısı buna rağmen "
            "elde edilen olumlu sonucu (verim artışı) anlatır. Bu zıtlığı 'nevertheless' (yine de / buna rağmen) "
            "kurar. 'accordingly', 'hence' ve 'thus' sonuç bildirir; 'conversely' ise iki farklı grubu karşılaştırır.")


def fix_strings(obj, stats):
    if isinstance(obj, dict):
        return {k: fix_strings(v, stats) for k, v in obj.items()}
    if isinstance(obj, list):
        return [fix_strings(v, stats) for v in obj]
    if isinstance(obj, str):
        s = obj
        if "随机" in s:
            s = s.replace("klinik çalışma随机 (rastgele) seçimi", "klinik çalışmalarda rastgele seçim")
            s = s.replace("随机 (rastgele)", "rastgele").replace("随机", "")
            stats["cince"] += 1
        new = re.sub(r"\b([Pp]roficiency) proficiency\b", r"\1", s)
        if new != s:
            stats["proficiency"] += 1
            s = new
        return s
    return obj


def fix_slot25(q, stats):
    correct = next(o for o in q["options"] if o["key"] == q["correct_answer"])
    if (correct["text"].strip().lower() == "conversely" and "encountered severe" in q["question"]
            and not any(o["text"].strip().lower() == "nevertheless" for o in q["options"])):
        correct["text"] = "nevertheless"
        q["explanation_tr"] = S25_EXPL
        stats["slot25"] += 1


def shuffle_template(q):
    if not TEMPLATE_ID.search(q["id"]):
        return False
    for f in ("explanation_tr", "explanation_en"):
        assert not LETTER_REF.search(q.get(f) or ""), f"{q['id']} açıklaması harfe atıf yapıyor"
    opts = q["options"]
    rng = random.Random("prepmaster-sablon-v2:" + q["id"])
    order = list(range(len(opts)))
    rng.shuffle(order)
    mapping = {}
    new_opts = []
    for new_pos, old_pos in enumerate(order):
        mapping[opts[old_pos]["key"]] = LETTERS[new_pos]
        new_opts.append({**opts[old_pos], "key": LETTERS[new_pos]})
    q["correct_answer"] = mapping[q["correct_answer"]]
    q["options"] = new_opts
    return True


def main(write):
    stats = collections.Counter()
    paths = {n: ROOT / "data" / f"{n}.json" for n in ("questions", "listening", "speaking")}
    data = {n: json.loads(p.read_text(encoding="utf-8")) for n, p in paths.items()}
    original_q = {q["id"]: q for q in json.loads(paths["questions"].read_text(encoding="utf-8"))}

    for n in data:
        data[n] = fix_strings(data[n], stats)

    for q in data["questions"]:
        fix_slot25(q, stats)
        if shuffle_template(q):
            stats["karistirilan"] += 1

    # Doğrulama: doğru şıkkın METNİ değişmedi (slot 25 hariç), şık kümesi aynı
    for q in data["questions"]:
        o = original_q[q["id"]]
        new_text = next(x["text"] for x in q["options"] if x["key"] == q["correct_answer"])
        old_text = next(x["text"] for x in o["options"] if x["key"] == o["correct_answer"])
        if old_text.strip().lower() == "conversely" and new_text == "nevertheless":
            continue
        assert old_text == new_text, q["id"]

    tmpl = [q for q in data["questions"] if TEMPLATE_ID.search(q["id"])]
    by_slot = collections.defaultdict(collections.Counter)
    for q in tmpl:
        by_slot[q["id"].rsplit("_", 1)[-1]][q["correct_answer"]] += 1
    worst = max(max(c.values()) / sum(c.values()) for c in by_slot.values())
    print(dict(stats))
    print("Şablon doğru şık dağılımı:", dict(sorted(collections.Counter(q["correct_answer"] for q in tmpl).items())))
    print(f"Aynı soru numarasında en baskın harfin payı: %{worst*100:.0f} (eskiden %100)")

    if write:
        for n, p in paths.items():
            p.write_text(json.dumps(data[n], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            shutil.copyfile(p, ROOT / "mobile" / "assets" / "data" / p.name)
        print("Yazıldı: data/ ve mobile/assets/data/")


if __name__ == "__main__":
    main("--write" in sys.argv)
