"""
Adversarial Verification Suite for Milestone M1 (Questions Dataset Expansion)
Challenger 1 — Empirical Validation Harness

Authoritative specifications:
- ORIGINAL_REQUEST.md (## 2026-10-18T12:30:47Z, Requirement R1)
- PROJECT.md (Feature Inventory 1-8, Interface Contract 1)
"""

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path


def main():
    print("=" * 70)
    print("  PrepMaster M1 Questions Dataset — Adversarial Challenger Suite")
    print("=" * 70)

    project_root = Path(__file__).resolve().parent.parent
    data_path = project_root / "data" / "questions.json"
    mobile_path = project_root / "mobile" / "assets" / "data" / "questions.json"

    # --- 1. Existence and SHA-256 Byte Parity ---
    print("\n[Assertion 1] Verifying File Existence & SHA-256 Byte Parity...")
    assert data_path.exists(), f"Missing primary dataset: {data_path}"
    assert mobile_path.exists(), f"Missing mobile asset dataset: {mobile_path}"

    with open(data_path, "rb") as f:
        data_bytes = f.read()
    with open(mobile_path, "rb") as f:
        mobile_bytes = f.read()

    data_sha = hashlib.sha256(data_bytes).hexdigest()
    mobile_sha = hashlib.sha256(mobile_bytes).hexdigest()

    print(f"  data/questions.json size: {len(data_bytes)} bytes | SHA-256: {data_sha}")
    print(f"  mobile/assets/data/questions.json size: {len(mobile_bytes)} bytes | SHA-256: {mobile_sha}")

    assert data_sha == mobile_sha, (
        f"CRITICAL PARITY FAILURE: SHA-256 mismatch!\n"
        f"  data:   {data_sha}\n"
        f"  mobile: {mobile_sha}"
    )
    assert len(data_bytes) == len(mobile_bytes), "File byte sizes differ"
    print("  -> PASS: 100% SHA-256 bitwise parity confirmed.")

    # --- 2. UTF-8 & Strict JSON Parsing ---
    print("\n[Assertion 2] Verifying UTF-8 Encoding & JSON Well-Formedness...")
    try:
        data_str = data_bytes.decode("utf-8")
        assert "\ufffd" not in data_str, "Detected replacement character (\ufffd) - UTF-8 decoding issue!"
        questions = json.loads(data_str)
    except Exception as e:
        raise AssertionError(f"Strict UTF-8 / JSON parse failed: {e}")

    assert isinstance(questions, list), f"Expected JSON list, got {type(questions)}"
    total_count = len(questions)
    print(f"  Total questions loaded: {total_count}")
    assert total_count >= 195, f"Expected >= 195 questions, found {total_count}"
    print("  -> PASS: Total question count >= 195 verified.")

    # --- 3. Unique Question IDs ---
    print("\n[Assertion 3] Verifying Uniqueness and Format of Question IDs...")
    id_counts = Counter(q.get("id") for q in questions)
    duplicates = [qid for qid, count in id_counts.items() if count > 1]
    assert not duplicates, f"Found duplicate question IDs: {duplicates}"
    assert None not in id_counts, "Found question with missing ID"
    assert "" not in id_counts, "Found question with empty ID"

    id_regex = re.compile(r"^[a-zA-Z0-9_\-]+$")
    for qid in id_counts.keys():
        assert id_regex.match(qid), f"Question ID '{qid}' violates slug regex"
    print(f"  -> PASS: All {total_count} question IDs are unique and well-formatted.")

    # --- 4. University Coverage & Quotas ---
    print("\n[Assertion 4] Verifying University Distribution & 6 Target Universities...")
    uni_counts = Counter(q.get("university_id") for q in questions)
    for uni, count in sorted(uni_counts.items()):
        print(f"  University '{uni}': {count} questions")

    target_unis = ["hacettepe", "ankara", "gazi", "ege", "koc", "sabanci"]
    for uni in target_unis:
        count = uni_counts.get(uni, 0)
        assert count >= 12, f"Target university '{uni}' has {count} questions (required >= 12)"
    print(f"  -> PASS: All 6 target universities meet >= 12 questions requirement.")

    # --- 5. Schema Integrity & Pedagogical Fields ---
    print("\n[Assertion 5] Verifying Schema Integrity for Every Question...")
    valid_cefr = {"A1", "A2", "B1", "B2", "C1", "C2"}
    answer_dist = Counter()

    for i, q in enumerate(questions):
        qid = q.get("id", f"idx_{i}")
        # Required non-empty string fields
        for field in ["id", "university_id", "level", "category", "question", "correct_answer", "explanation_tr"]:
            val = q.get(field)
            assert val is not None, f"[{qid}] Missing required field '{field}'"
            assert isinstance(val, str), f"[{qid}] Field '{field}' must be a string, got {type(val)}"
            assert val.strip(), f"[{qid}] Field '{field}' is empty or whitespace"

        # CEFR level validation
        level = q["level"].upper()
        assert level in valid_cefr, f"[{qid}] Invalid CEFR level '{q['level']}'"

        # Passage check (if present)
        passage = q.get("passage")
        if passage is not None:
            assert isinstance(passage, str), f"[{qid}] Passage must be a string"
            assert passage.strip(), f"[{qid}] Passage is empty or whitespace"

        # Options check
        options = q.get("options")
        assert isinstance(options, list), f"[{qid}] Options must be a list"
        assert len(options) >= 2, f"[{qid}] Question has fewer than 2 options ({len(options)})"

        opt_keys = []
        opt_ids = []
        for opt_idx, opt in enumerate(options):
            assert isinstance(opt, dict), f"[{qid}] Option {opt_idx} is not a dictionary"
            key = opt.get("key")
            opt_id = opt.get("id")
            text = opt.get("text")
            assert key or opt_id, f"[{qid}] Option {opt_idx} has neither 'key' nor 'id'"
            primary_key = key or opt_id
            opt_keys.append(primary_key)
            if opt_id:
                opt_ids.append(opt_id)

            assert text is not None and isinstance(text, str), f"[{qid}] Option {primary_key} text is invalid"
            assert text.strip(), f"[{qid}] Option {primary_key} has empty text"

        # Option keys uniqueness within the question
        assert len(opt_keys) == len(set(opt_keys)), f"[{qid}] Duplicate option keys in question: {opt_keys}"

        # Correct answer exists in options
        correct = q["correct_answer"].strip()
        answer_dist[correct] += 1
        assert correct in opt_keys, (
            f"[{qid}] Correct answer '{correct}' not found in option keys: {opt_keys}"
        )
        if opt_ids:
            assert correct in opt_ids, (
                f"[{qid}] Correct answer '{correct}' not found in option ids: {opt_ids}"
            )

        # Turkish explanation depth check
        exp_tr = q["explanation_tr"].strip()
        assert len(exp_tr) >= 20, (
            f"[{qid}] Turkish explanation too short ({len(exp_tr)} chars): '{exp_tr}'"
        )
        # Check against trivial placeholder text using regex word boundary
        lowered_exp = exp_tr.lower()
        lowered_q = q["question"].lower()
        placeholder_patterns = [r"\btodo\b", r"\blorem\s+ipsum\b", r"\bplaceholder\b", r"\basdf\b"]
        for pat in placeholder_patterns:
            assert not re.search(pat, lowered_exp), f"[{qid}] Explanation contains placeholder '{pat}'"

        # Check question text against trivial placeholder text
        for pat in placeholder_patterns:
            assert not re.search(pat, lowered_q), f"[{qid}] Question text contains placeholder '{pat}'"

    print(f"  -> PASS: All {total_count} questions satisfy strict schema contracts.")
    print(f"  Answer distribution: {dict(answer_dist)}")

    # --- 6. Adversarial Duplicate Question Text Detection ---
    print("\n[Assertion 6] Adversarial Check for Duplicate Question Texts...")
    question_texts = [q["question"].strip().lower() for q in questions]
    q_text_counts = Counter(question_texts)
    dup_texts = [text for text, cnt in q_text_counts.items() if cnt > 1]
    # In academic tests, reading passages might have standard questions like "What is the main idea of the passage?"
    # But let's verify if there are exact duplicates that share both question text AND passage.
    passage_question_pairs = [
        (q.get("passage", "").strip().lower(), q["question"].strip().lower())
        for q in questions
    ]
    pair_counts = Counter(passage_question_pairs)
    dup_pairs = [pair for pair, cnt in pair_counts.items() if cnt > 1]
    assert not dup_pairs, f"Found identical passage-question duplicate pairs: {dup_pairs}"
    print(f"  -> PASS: No copy-paste duplicate questions found across the dataset.")

    # --- 7. Target University Specific Pedagogical Formats Check ---
    print("\n[Assertion 7] Verifying Pedagogical Category Coverage for New Universities...")
    uni_categories = {}
    for q in questions:
        u = q["university_id"]
        uni_categories.setdefault(u, set()).add(q["category"])

    expected_categories = {
        "hacettepe": {"Restatement", "Paragraph Comprehension", "Academic Structure & Reading"},
        "ankara": {"Cloze Test", "Reading Analysis", "Vocabulary in Context"},
        "gazi": {"Use of English", "Grammar & Academic Collocations"},
        "ege": {"Sentence Completion", "Contextual Inference", "Paragraph Flow"},
        "koc": {"Advanced Academic Reading", "Critical Analysis", "High-Level Restatement"},
        "sabanci": {"Search Reading", "Synthesizing Text", "Academic Vocabulary"},
    }

    for uni, expected_cats in expected_categories.items():
        actual_cats = uni_categories.get(uni, set())
        print(f"  {uni} categories: {actual_cats}")
        # Allow partial word matching or exact match
        for exp in expected_cats:
            matched = any(exp.lower() in act.lower() or act.lower() in exp.lower() for act in actual_cats)
            assert matched, f"University '{uni}' missing expected pedagogical category '{exp}'. Found: {actual_cats}"
    print("  -> PASS: Pedagogical categories align with R1 requirements.")

    # --- 8. Check Passages & Question Substantiveness ---
    print("\n[Assertion 8] Verifying Reading Passages & Question Substantiveness...")
    for q in questions:
        qid = q.get("id")
        passage = q.get("passage")
        q_text = q.get("question", "").strip()

        if passage is not None:
            assert isinstance(passage, str), f"[{qid}] Passage must be a string"
            assert len(passage.strip()) >= 50, (
                f"[{qid}] Passage too short ({len(passage.strip())} chars)"
            )
        else:
            # Standalone sentence/cloze question must have substantive prompt
            assert len(q_text) >= 20, (
                f"[{qid}] Question without passage is too brief ({len(q_text)} chars): '{q_text}'"
            )

    # Verify dedicated reading categories in target universities have passages
    must_have_passage_categories = {
        "hacettepe": ["Paragraph Comprehension"],
        "ankara": ["Reading Analysis"],
        "ege": ["Contextual Inference", "Paragraph Flow"],
        "koc": ["Advanced Academic Reading"],
        "sabanci": ["Search Reading", "Synthesizing Text"],
    }
    for q in questions:
        u = q.get("university_id")
        cat = q.get("category")
        if u in must_have_passage_categories and cat in must_have_passage_categories[u]:
            assert q.get("passage") and len(q["passage"].strip()) >= 50, (
                f"[{q.get('id')}] Category '{cat}' in '{u}' expected substantive passage."
            )
    print("  -> PASS: All reading passages and standalone questions are substantive.")

    print("\n" + "=" * 70)
    print("  ALL ADVERSARIAL ASSERTIONS PASSED WITH ZERO DEFECTS!")
    print("=" * 70)


if __name__ == "__main__":
    main()
