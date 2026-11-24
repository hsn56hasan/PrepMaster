"""
Üniversiteye özel ÖZGÜN sorular (24.11.2026).

Kaynak: scripts/universite_sorulari/<üniversite>.py — elle yazıldı, gerçek sınavlardan KOPYA DEĞİL;
her üniversitenin sınav bölümlerine (data/universities.json "sections") göre soru tipi seçildi.
Her üniversite için 24 soru, her seviyeden 4:
  A1, A2, B2, C2 -> ITEMS (dil bilgisi, kelime, restatement, cümle/paragraf tamamlama, diyalog)
  B1             -> CLOZE  (4 boşluklu metin)
  C1             -> READING (üniversite bağlamlı okuma parçası, 4 soru)

Kullanım:  python scripts/add_university_questions.py          (kuru çalıştırma, denetler)
           python scripts/add_university_questions.py --write  (data/ yazar, mobil kopyayı günceller)
Tekrar çalıştırmak güvenlidir: önce eski "q-uni-*" kayıtları silinir.
"""
import collections
import importlib.util
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "scripts" / "universite_sorulari"
PREFIX = "q-uni-"
LETTERS = "ABCD"
CATS = {"Grammar", "Vocabulary", "Restatement", "Sentence Completion", "Dialogue",
        "Paragraph Completion", "Cloze Test", "Reading"}
STEM = {
    "Grammar": "Choose the option that best completes the sentence.",
    "Vocabulary": "Choose the word or phrase that best completes the sentence.",
    "Sentence Completion": "Choose the option that best completes the sentence.",
    "Restatement": "Choose the sentence that is closest in meaning to the given sentence.",
    "Dialogue": "Choose the option that best completes the dialogue.",
    "Paragraph Completion": "Choose the sentence that best fills the gap in the paragraph.",
}


def load_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def options(qid, correct, distractors):
    texts = [correct] + list(distractors)
    assert len(texts) == 4, qid
    assert len({t.strip().lower() for t in texts}) == 4, f"{qid}: tekrar eden şık"
    rng = random.Random("prepkampus-uni-v1:" + qid)
    order = list(range(4))
    rng.shuffle(order)
    return [{"key": LETTERS[i], "text": texts[j]} for i, j in enumerate(order)], LETTERS[order.index(0)]


def check_text(qid, *parts):
    for s in parts:
        assert not any(c in (s or "") for c in "<>&"), f"{qid}: HTML karakteri"


def build_university(mod, uni_ids):
    uni = mod.UNI
    assert uni in uni_ids, f"bilinmeyen üniversite: {uni}"
    out, n = [], collections.Counter()

    def add(level, cat, question, correct, distractors, tr, passage=None):
        assert cat in CATS, (uni, cat)
        n[level] += 1
        qid = f"{PREFIX}{uni}-{level.lower()}-{n[level]:02d}"
        check_text(qid, question, correct, *distractors, tr, passage)
        opts, ans = options(qid, correct, distractors)
        item = {"id": qid, "university_id": uni, "level": level, "category": cat,
                "question": question, "options": opts, "correct_answer": ans, "explanation_tr": tr}
        if passage:
            item["passage"] = passage
        out.append(item)

    for level, cat, stem, correct, distractors, tr in mod.ITEMS:
        add(level, cat, f"{STEM[cat]}\n\n{stem}", correct, distractors, tr)
    cloze_text, cloze_items = mod.CLOZE
    assert len(cloze_items) == 4, (uni, "cloze")
    for i, (correct, distractors, tr) in enumerate(cloze_items, 1):
        assert f"({i})" in cloze_text, (uni, f"cloze ({i}) yok")
        add("B1", "Cloze Test", f"Choose the option that best fills blank ({i}) in the text.", correct, distractors, tr, cloze_text)
    reading_text, reading_items = mod.READING
    assert len(reading_items) == 4, (uni, "reading")
    for q, correct, distractors, tr in reading_items:
        add("C1", "Reading", q, correct, distractors, tr, reading_text)

    counts = collections.Counter(q["level"] for q in out)
    assert all(counts[l] == 4 for l in ("A1", "A2", "B1", "B2", "C1", "C2")), (uni, dict(counts))
    return out


def main(write):
    uni_ids = {u["id"] for u in json.loads((ROOT / "data" / "universities.json").read_text(encoding="utf-8"))}
    files = sorted(p for p in SRC.glob("*.py") if not p.name.startswith("_"))
    new = []
    for f in files:
        new += build_university(load_module(f), uni_ids)

    qpath = ROOT / "data" / "questions.json"
    data = [q for q in json.loads(qpath.read_text(encoding="utf-8")) if not q["id"].startswith(PREFIX)]
    assert not {q["id"] for q in data} & {q["id"] for q in new}
    data += new

    covered = sorted({q["university_id"] for q in new})
    missing = sorted(uni_ids - set(covered) - {"general"})
    print(f"Eklenen üniversite sorusu: {len(new)} ({len(covered)} üniversite)")
    if missing:
        print("Henüz yazılmayan:", ", ".join(missing))
    print("Doğru şık dağılımı:", dict(sorted(collections.Counter(q["correct_answer"] for q in new).items())))
    longest = [q["id"] for q in new
               if (lambda L: L[0][1] == q["correct_answer"] and L[0][0] > 1.15 * L[1][0] and L[0][0] > 12)(
                   sorted(((len(o["text"]), o["key"]) for o in q["options"]), reverse=True))]
    print(f"Doğru şık belirgin en uzun olan: {len(longest)}", longest)
    per_uni = collections.Counter(q["university_id"] for q in data)
    print("Üniversite başına toplam soru (örnek):", {k: per_uni[k] for k in covered[:5]})
    print("Toplam soru:", len(data))
    if write:
        qpath.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        sys.path.insert(0, str(ROOT / "scripts"))
        import sync_mobile_assets
        sync_mobile_assets.sync()  # APK'ya yalnız ücretsiz genel içerik (üniversite soruları sunucudan)
        print("Yazıldı: data/questions.json")


if __name__ == "__main__":
    main("--write" in sys.argv)
