"""
Kelime listesini genişletir ve kelimelerden özgün kelime soruları üretir (15.11.2026).

Kaynak: scripts/kelime_kaynak/<SEVİYE>.txt  (elle yazıldı; biçim dosyaların ilk satırında)
  kelime|tür|okunuş|Türkçe anlam|İngilizce tanım|eş anlamlılar(;)|zıt anlamlılar(; ya da -)|örnek cümle|kalıp

1) data/vocabulary.json: mevcut 600 kayda (kimlikleri ve öğrenci ilerlemesi korunur) DOKUNMADAN,
   listede olmayan yeni kelimeleri "v-<seviye>-k<NNN>" kimliğiyle ekler.
2) data/questions.json: her kelimeden en fazla üç soru ("q-kel-*", genel havuz, Vocabulary):
   - tanım -> kelime     ("Which word means: ...?")
   - cümlede boşluk      (kelimenin KENDİ örnek cümlesi; yalnızca kelime cümlede aynen geçiyorsa)
   - eş anlamlı          ("closest in meaning to ...")
   Çeldiriciler aynı seviye ve aynı türden kelimelerden seçilir; doğru cevabın eş anlamlıları,
   aynı eş anlamlıyı paylaşan kelimeler ve aynı kökten görünen kelimeler çeldirici yapılmaz.

Kullanım:  python scripts/build_vocabulary.py          (kuru çalıştırma)
           python scripts/build_vocabulary.py --write  (data/ ve mobile/assets/data/ yazar)
Tekrar çalıştırmak güvenlidir: önce eski "v-*-k*" kelimeleri ve "q-kel-*" soruları siler.
"""
import collections
import json
import random
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "scripts" / "kelime_kaynak"
LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
LETTERS = "ABCD"
NEW_VOCAB = re.compile(r"^v-(a1|a2|b1|b2|c1|c2)-k\d+$")
QPREFIX = "q-kel-"
BAD_CHARS = set("<>&|")


def parse_sources():
    entries, problems = [], []
    for level in LEVELS:
        path = SRC / f"{level}.txt"
        if not path.exists():
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) != 9:
                problems.append(f"{level}:{n} alan sayısı {len(parts)}")
                continue
            word, pos, ipa, tr, defn, syn, ant, ex, col = parts
            if any(c in BAD_CHARS for c in "".join(parts)):
                problems.append(f"{level}:{n} yasak karakter")
                continue
            if not re.search(r"(?<![A-Za-z])" + re.escape(word.lower()) + r"(?![A-Za-z])", ex.lower()):
                problems.append(f"{level}:{n} '{word}' örnek cümlede yalın hâliyle geçmiyor")
                continue
            entries.append({
                "word": word, "level": level, "part_of_speech": pos, "pronunciation": ipa,
                "meaning_tr": tr, "definition_en": defn,
                "synonyms": [s.strip() for s in syn.split(";") if s.strip() and s.strip() != "-"],
                "antonyms": [s.strip() for s in ant.split(";") if s.strip() and s.strip() != "-"],
                "example_sentence": ex, "collocation": col,
            })
    return entries, problems


def merge_vocabulary(existing, entries):
    base = [v for v in existing if not NEW_VOCAB.match(v["id"])]
    seen = {v["word"].strip().lower() for v in base}
    added, skipped = [], []
    counters = collections.Counter()
    for e in entries:
        key = e["word"].lower()
        if key in seen:
            skipped.append(e["word"])
            continue
        seen.add(key)
        counters[e["level"]] += 1
        word = e["word"][0].upper() + e["word"][1:]  # mevcut kayıtlarla aynı yazım (baş harf büyük)
        added.append({
            "id": f"v-{e['level'].lower()}-k{counters[e['level']]:03d}",
            **{**e, "word": word}, "status": "unreviewed",
        })
    return base + added, added, skipped


# ----------------------------------------------------------------------------- sorular
def _stem(w):
    w = w.lower()
    for suf in ("ation", "ition", "ment", "ness", "ity", "ing", "ous", "ive", "ful", "ize", "ise", "ed", "es", "er", "ly", "al", "e", "s", "y"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[: -len(suf)]
    return w


def _pool(vocab):
    by = collections.defaultdict(list)
    for v in vocab:
        by[(v["level"], v["part_of_speech"])].append(v)
    return by


STOP = set("""about above after again against because before being below between could doing during
every from have having into itself other others over same should some such than that their them then there
these they this those through under until very what when where which while with would your something someone
used using make makes made able often especially particular person people thing things""".split())

# Eş anlamlı ağı: aynı kelimenin tekrar kayıtlarındaki listeler birleştirilir, bağlar iki yönlüdür.
SYN = collections.defaultdict(set)
DEFWORDS = {}


def build_synonym_graph(vocab):
    SYN.clear()
    DEFWORDS.clear()
    for v in vocab:
        w = v["word"].lower()
        for s in v.get("synonyms", []):
            s = s.lower()
            SYN[w].add(s)
            SYN[s].add(w)
        words = {t for t in re.findall(r"[a-z]+", v["definition_en"].lower()) if len(t) >= 5 and t not in STOP}
        DEFWORDS[w] = DEFWORDS.get(w, set()) | words


def _near(w):
    """Kelimenin kendisi, eş anlamlıları ve eş anlamlılarının eş anlamlıları."""
    n1 = SYN.get(w, set())
    out = {w} | n1
    for x in n1:
        out |= SYN.get(x, set())
    return out


def _load_exclusions():
    """Elle gözden geçirmede 'bu cümleye o da uyar' diye işaretlenen çiftler (celdirici_haric.txt)."""
    pairs = set()
    path = SRC / "celdirici_haric.txt"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip().lower()
            if line and not line.startswith("#") and "|" in line:
                a, b = (x.strip() for x in line.split("|", 1))
                pairs.add((a, b))
                pairs.add((b, a))
    return pairs


EXCLUDED = _load_exclusions()


def _related_words(wa, wb):
    wa, wb = wa.lower(), wb.lower()
    if (wa, wb) in EXCLUDED:
        return True
    if wa == wb or _stem(wa) == _stem(wb) or wa in wb or wb in wa:
        return True
    na, nb = _near(wa), _near(wb)
    if wb in na or wa in nb or (SYN.get(wa, set()) & SYN.get(wb, set())):
        return True
    return bool(DEFWORDS.get(wa, set()) & DEFWORDS.get(wb, set()))


def _related(a, b):
    return _related_words(a["word"], b["word"])


def _distractors(target, candidates, rng, k=3, key=lambda v: v["word"]):
    pool = [c for c in candidates if not _related(target, c)]
    rng.shuffle(pool)
    out, used = [], {key(target).lower()}
    for c in pool:
        t = key(c)
        if t and t.lower() not in used:
            out.append(c)
            used.add(t.lower())
        if len(out) == k:
            break
    return out


def _options(qid, correct, others):
    texts = [correct] + others
    rng = random.Random("prepmaster-kelime-v1:" + qid)
    order = list(range(4))
    rng.shuffle(order)
    return [{"key": LETTERS[i], "text": texts[j]} for i, j in enumerate(order)], LETTERS[order.index(0)]


def _neighbour_pool(by, level, pos):
    """Aynı seviyede aday azsa komşu seviyelerden de al."""
    i = LEVELS.index(level)
    pool = list(by[(level, pos)])
    for d in (1, -1, 2, -2):
        if len(pool) >= 12:
            break
        j = i + d
        if 0 <= j < len(LEVELS):
            pool += by[(LEVELS[j], pos)]
    return pool


def lower_word(v):
    w = v["word"]
    return w if (len(w) > 1 and w[1:].isupper()) else w[0].lower() + w[1:]


def build_questions(vocab):
    # Yalnızca tekil kelimeler (aynı kelimenin tekrar kayıtlarından ilki)
    uniq, seen = [], set()
    for v in vocab:
        k = v["word"].lower()
        if k not in seen and v["part_of_speech"] in ("noun", "verb", "adjective", "adverb"):
            seen.add(k)
            uniq.append(v)
    build_synonym_graph(vocab)
    by = _pool(uniq)
    questions = []
    n = collections.Counter()

    def add(v, kind, question, correct, others, tr, en):
        n[v["level"]] += 1
        qid = f"{QPREFIX}{v['level'].lower()}-{n[v['level']]:04d}"
        opts, ans = _options(qid, correct, others)
        questions.append({"id": qid, "university_id": "general", "level": v["level"], "category": "Vocabulary",
                          "question": question, "options": opts, "correct_answer": ans,
                          "explanation_tr": tr, "explanation_en": en})

    for v in uniq:
        rng = random.Random("prepmaster-kelime-celdirici:" + v["word"].lower())
        cands = [c for c in _neighbour_pool(by, v["level"], v["part_of_speech"]) if c is not v]
        w = lower_word(v)
        tr_base = f"'{w}' ({v['part_of_speech']}) = {v['meaning_tr']}. Tanım: {v['definition_en']}"

        # 1) tanım -> kelime
        ds = _distractors(v, cands, rng)
        if len(ds) == 3:
            add(v, "def",
                f"Which word matches the definition below?\n\n'{v['definition_en']}'",
                w, [lower_word(d) for d in ds],
                f"{tr_base} Örnek: {v['example_sentence']}",
                f"'{w}' means: {v['definition_en']} Example: {v['example_sentence']}")

        # 2) cümlede boşluk (kelime cümlede yalın hâliyle geçiyorsa)
        ex = v["example_sentence"]
        pat = re.compile(r"(?<![A-Za-z])" + re.escape(v["word"].lower()) + r"(?![A-Za-z])", re.I)
        if len(pat.findall(ex)) == 1:
            ds = _distractors(v, cands, rng)
            if len(ds) == 3:
                m = pat.search(ex)
                blanked = ex[: m.start()] + "____" + ex[m.end():]
                # "a/an" artikeli cevabı ele vermesin (gerçek sınavlardaki gibi "a(n)")
                blanked = re.sub(r"\b([Aa])n? ____", lambda mm: mm.group(1) + "(n) ____", blanked)
                first = m.start() == 0
                fmt = (lambda s: s[0].upper() + s[1:]) if first else (lambda s: s)
                add(v, "gap",
                    f"Choose the word that best completes the sentence.\n\n{blanked}",
                    fmt(w), [fmt(lower_word(d)) for d in ds],
                    f"Doğru cevap '{w}': {v['meaning_tr']}. Cümle: {ex}",
                    f"'{w}' ({v['definition_en']}) fits the sentence: {ex}")

        # 3) eş anlamlı
        syn = next((s for s in v.get("synonyms", []) if " " not in s and s.lower() != w.lower()), None)
        if syn:
            others = []
            for d in _distractors(v, cands, rng, k=8):
                s = next((x for x in d.get("synonyms", []) if " " not in x), None)
                if s and not _related_words(s, w) and not _related_words(s, syn) \
                        and all(not _related_words(s, o) for o in others):
                    others.append(s)
                if len(others) == 3:
                    break
            if len(others) == 3:
                add(v, "syn",
                    f"Choose the word that is closest in meaning to '{w}'.",
                    syn, others,
                    f"'{w}' ({v['meaning_tr']}) ile '{syn}' eş anlamlıdır. Örnek: {v['example_sentence']}",
                    f"'{syn}' is a synonym of '{w}' ({v['definition_en']})")
    return questions


def main(write):
    entries, problems = parse_sources()
    vpath = ROOT / "data" / "vocabulary.json"
    qpath = ROOT / "data" / "questions.json"
    existing = json.loads(vpath.read_text(encoding="utf-8"))
    vocab, added, skipped = merge_vocabulary(existing, entries)
    uniq_words = len({v["word"].lower() for v in vocab})

    questions = json.loads(qpath.read_text(encoding="utf-8"))
    questions = [q for q in questions if not q["id"].startswith(QPREFIX)]
    gen = build_questions(vocab)
    ids = {q["id"] for q in questions}
    assert not ids & {q["id"] for q in gen}
    questions += gen

    print("Kaynak satır:", len(entries), "| sorunlu:", len(problems))
    for p in problems[:40]:
        print("  -", p)
    print("Zaten listede olduğu için atlanan:", len(skipped), skipped[:30])
    print("Eklenen kelime:", len(added), dict(collections.Counter(a["level"] for a in added)))
    print("Kelime kaydı:", len(vocab), "| farklı kelime:", uniq_words)
    print("Üretilen kelime sorusu:", len(gen), dict(sorted(collections.Counter(q["level"] for q in gen).items())))
    print("Doğru şık dağılımı:", dict(sorted(collections.Counter(q["correct_answer"] for q in gen).items())))
    print("Toplam soru:", len(questions))
    if write:
        if problems:
            print("UYARI: sorunlu satırlar atlandı")
        vpath.write_text(json.dumps(vocab, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        qpath.write_text(json.dumps(questions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for p in (vpath, qpath):
            shutil.copyfile(p, ROOT / "mobile" / "assets" / "data" / p.name)
        print("Yazıldı: data/ ve mobile/assets/data/ (vocabulary.json, questions.json)")


if __name__ == "__main__":
    main("--write" in sys.argv)
