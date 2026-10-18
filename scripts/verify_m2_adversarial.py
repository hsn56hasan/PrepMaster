"""
Adversarial Verification Suite for Milestone M2 (3D Secure Sanal POS & GİB E-Arşiv Fişi)
Reviewer / Adversarial Critic Harness

Authoritative specifications:
- ORIGINAL_REQUEST.md (## 2026-10-18T12:30:47Z, Requirement R2)
- PROJECT.md (Feature Inventory 9-12, Interface Contract 2)
"""

import os
import sys
import re
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Setup environment
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

os.environ["SECRET_KEY"] = "super_secret_adversarial_m2_test_key_2026"

from fastapi.testclient import TestClient
from backend.app import app
from backend.database import get_db, init_db, generate_gib_receipt
import backend.security as sec


def main():
    print("=" * 75)
    print("  PrepMaster M2 3D Secure POS & GİB E-Arşiv — Adversarial Critic Suite")
    print("=" * 75)

    client = TestClient(app)
    sec.rate_limiter.reset()

    # --- 1. GİB Financial & Mathematical Invariants ---
    print("\n[Assertion 1] GİB E-Arşiv Receipt Format & Statutory Tax Invariants...")
    receipt_numbers = set()
    for _ in range(50):
        rc = generate_gib_receipt(card_last_four="9876", card_holder="Mustafa Kemal", university_id="koc")
        r_no = rc["receipt_no"]
        assert re.match(r"^EARSIV-2026-[A-F0-9]{4,}$", r_no), f"Receipt number format mismatch: {r_no}"
        receipt_numbers.add(r_no)

        gross = rc["gross_amount"]
        vat_rate = rc["vat_rate"]
        vat = rc["vat_amount"]
        net = rc["net_amount"]

        assert gross == 50.00, f"Gross must be 50.00, got {gross}"
        assert vat_rate == 0.20, f"VAT rate must be 0.20, got {vat_rate}"
        assert vat == 8.33, f"VAT amount must be 8.33, got {vat}"
        assert net == 41.67, f"Net amount must be 41.67, got {net}"
        assert round(net + vat, 2) == 50.00, f"Net + VAT must equal Gross 50.00 exactly: {net} + {vat} != {gross}"
        assert rc["currency"] == "TRY"
        assert rc["card_last_four"] == "9876"
        assert rc["card_holder"] == "Mustafa Kemal"
        assert rc["tax_office"] == "Mecidiyeköy Vergi Dairesi"
        assert rc["tax_number"] == "8930491823"
        assert rc["gib_status"] == "GİB E-Arşiv Fatura Sistemi Onaylı"

    assert len(receipt_numbers) > 40, f"Receipt sequence entropy too low: {len(receipt_numbers)} unique out of 50"
    print(f"  -> PASS: 50 receipts generated. Strict mathematical equality net(41.67) + vat(8.33) == gross(50.00) verified.")

    # --- 2. 3D Secure Session Initialization & Bounds Checking ---
    print("\n[Assertion 2] 3D Secure Session Creation & Adversarial Input Bounds...")
    # 2.1 Valid Session Creation
    init_res = client.post("/api/membership/3d-init", json={
        "user_id": 1,
        "university_id": "hacettepe",
        "card_holder": "Ahmet Yılmaz",
        "card_number": "5528 7900 0000 0001",
        "expire_month": "12",
        "expire_year": "28",
        "cvv": "123",
        "amount_try": 50.0
    })
    assert init_res.status_code == 200, f"Init failed: {init_res.text}"
    init_data = init_res.json()

    assert init_data["status"] == "success"
    assert init_data["session_id"].startswith("3DS-")
    assert len(init_data["session_id"]) >= 16
    assert re.match(r"^\d{6}$", init_data["sms_code_sandbox"])
    assert "*" in init_data["masked_phone"]
    assert init_data["expires_in_seconds"] == 180
    assert init_data["amount_try"] == 50.0

    # 2.2 Malformed Card Number (Alphabetic)
    res_alpha = client.post("/api/membership/3d-init", json={
        "university_id": "hacettepe",
        "card_number": "abcdefghijklmnop",
        "cvv": "123"
    })
    assert res_alpha.status_code in (400, 422), f"Expected 400/422 for alphabetic card, got: {res_alpha.status_code}"

    # 2.3 Malformed Card Number (<12 digits)
    res_short = client.post("/api/membership/3d-init", json={
        "university_id": "hacettepe",
        "card_number": "12345678",
        "cvv": "123"
    })
    assert res_short.status_code in (400, 422), f"Expected 400/422 for short card, got: {res_short.status_code}"

    # 2.4 Malformed CVV (1 digit)
    res_bad_cvv = client.post("/api/membership/3d-init", json={
        "university_id": "hacettepe",
        "card_number": "5528790000000001",
        "cvv": "9"
    })
    assert res_bad_cvv.status_code in (400, 422), f"Expected 400/422 for invalid CVV, got: {res_bad_cvv.status_code}"

    # 2.5 Malformed Amount (Negative or zero)
    res_neg_amt = client.post("/api/membership/3d-init", json={
        "university_id": "hacettepe",
        "card_number": "5528790000000001",
        "cvv": "123",
        "amount_try": -10.0
    })
    assert res_neg_amt.status_code in (400, 422), f"Expected 400/422 for negative amount, got: {res_neg_amt.status_code}"
    print("  -> PASS: Session creation and input boundary constraints validated.")

    # --- 3. 3-Attempt Lockout Defense ---
    print("\n[Assertion 3] 3-Attempt Lockout & Permanent Session Locking...")
    lock_init = client.post("/api/membership/3d-init", json={
        "user_id": 1,
        "university_id": "ankara",
        "card_holder": "Adversarial Lockout",
        "card_number": "5528790000000001",
        "cvv": "123"
    })
    assert lock_init.status_code == 200
    lock_sess = lock_init.json()["session_id"]
    correct_sms = lock_init.json()["sms_code_sandbox"]

    # Wrong code 1
    r1 = client.post("/api/membership/unlock", json={"user_id": 1, "university_id": "ankara", "session_id": lock_sess, "sms_code": "000001"})
    assert r1.status_code == 400
    assert "Kalan hak: 2" in r1.json()["detail"]

    # Wrong code 2
    r2 = client.post("/api/membership/unlock", json={"user_id": 1, "university_id": "ankara", "session_id": lock_sess, "sms_code": "000002"})
    assert r2.status_code == 400
    assert "Kalan hak: 1" in r2.json()["detail"]

    # Wrong code 3 -> Triggers lockout
    r3 = client.post("/api/membership/unlock", json={"user_id": 1, "university_id": "ankara", "session_id": lock_sess, "sms_code": "000003"})
    assert r3.status_code == 400
    assert "kilitlendi" in r3.json()["detail"].lower()

    # Attempt 4 with the REAL correct SMS code -> MUST STILL BE BLOCKED
    r4 = client.post("/api/membership/unlock", json={"user_id": 1, "university_id": "ankara", "session_id": lock_sess, "sms_code": correct_sms})
    assert r4.status_code == 400, f"Lockout bypassed! Expected 400, got: {r4.status_code}"
    assert "kilitlendi" in r4.json()["detail"].lower()

    # Verify SQLite status is 'locked'
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT status, attempts FROM payment_3ds_sessions WHERE session_id = ?", (lock_sess,))
    row = c.fetchone()
    assert row["status"] == "locked", f"Expected db status 'locked', got: {row['status']}"
    assert row["attempts"] == 3, f"Expected 3 attempts, got: {row['attempts']}"
    conn.close()
    print("  -> PASS: 3-attempt lockout strictly enforced. Locked session cannot be salvaged even with correct SMS code.")

    # --- 4. 180s Session Expiry Defense ---
    print("\n[Assertion 4] 180s Session Expiry Enforcement...")
    exp_init = client.post("/api/membership/3d-init", json={
        "user_id": 1,
        "university_id": "gazi",
        "card_holder": "Expiry Tester",
        "card_number": "5528790000000001",
        "cvv": "123"
    })
    assert exp_init.status_code == 200
    exp_sess = exp_init.json()["session_id"]
    exp_code = exp_init.json()["sms_code_sandbox"]

    # Rewind expires_at in DB
    past_ts = (datetime.now(timezone.utc) - timedelta(seconds=60)).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    conn.execute("UPDATE payment_3ds_sessions SET expires_at = ? WHERE session_id = ?", (past_ts, exp_sess))
    conn.commit()
    conn.close()

    # Attempt unlock with valid code -> MUST FAIL (400)
    exp_res = client.post("/api/membership/unlock", json={
        "user_id": 1,
        "university_id": "gazi",
        "session_id": exp_sess,
        "sms_code": exp_code
    })
    assert exp_res.status_code == 400, f"Expired session allowed! Status: {exp_res.status_code}"
    assert "süresi dolmuştur" in exp_res.json()["detail"].lower()

    # Check status transitioned to expired
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT status FROM payment_3ds_sessions WHERE session_id = ?", (exp_sess,))
    row = c.fetchone()
    assert row["status"] == "expired", f"Expected db status 'expired', got: {row['status']}"
    conn.close()
    print("  -> PASS: Expired 3DS session rejected and transitioned to 'expired' status.")

    # --- 5. Anti-Replay Defense ---
    print("\n[Assertion 5] Anti-Replay Defense (One-Time Session Consumption)...")
    rep_init = client.post("/api/membership/3d-init", json={
        "user_id": 1,
        "university_id": "ege",
        "card_holder": "Replay Defense",
        "card_number": "5528790000000001",
        "cvv": "123"
    })
    assert rep_init.status_code == 200
    rep_sess = rep_init.json()["session_id"]
    rep_code = rep_init.json()["sms_code_sandbox"]

    # First consumption -> 200 OK
    rep1 = client.post("/api/membership/unlock", json={
        "user_id": 1,
        "university_id": "ege",
        "session_id": rep_sess,
        "sms_code": rep_code
    })
    assert rep1.status_code == 200, f"First unlock failed: {rep1.text}"
    receipt = rep1.json()["receipt"]
    assert receipt["receipt_no"].startswith("EARSIV-2026-")

    # Second consumption attempt -> MUST FAIL (400)
    rep2 = client.post("/api/membership/unlock", json={
        "user_id": 1,
        "university_id": "ege",
        "session_id": rep_sess,
        "sms_code": rep_code
    })
    assert rep2.status_code == 400, f"Replay vulnerability detected! Got: {rep2.status_code}"
    assert "tekrar kullanılamaz" in rep2.json()["detail"].lower()
    print("  -> PASS: Consumed session cannot be reused. Anti-replay defense verified.")

    # --- 6. SQL Injection & Missing Parameter Sanitization ---
    print("\n[Assertion 6] SQL Injection & Parameter Tampering Hardening...")
    sqli_sessions = [
        "' OR '1'='1",
        "3DS-123' UNION SELECT * FROM users --",
        "non-existent-session-id-9999",
        "<script>alert(1)</script>"
    ]
    for s in sqli_sessions:
        r = client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "koc",
            "session_id": s,
            "sms_code": "123456"
        })
        assert r.status_code == 400, f"Expected 400 for bad session_id '{s}', got {r.status_code}"
        assert "detail" in r.json()

    # Missing session_id with sms_code
    r_no_sess = client.post("/api/membership/unlock", json={
        "user_id": 1,
        "university_id": "koc",
        "sms_code": "123456"
    })
    assert r_no_sess.status_code == 400
    assert "session_id" in r_no_sess.json()["detail"]

    # Missing sms_code with session_id
    r_no_code = client.post("/api/membership/unlock", json={
        "user_id": 1,
        "university_id": "koc",
        "session_id": "3DS-SOME-VALID-ID"
    })
    assert r_no_code.status_code == 400
    assert "sms" in r_no_code.json()["detail"].lower()
    print("  -> PASS: Parameterized SQLite queries safe against injection and malformed parameters.")

    # --- 7. Full SQLite Persistence & Audit Trail ---
    print("\n[Assertion 7] Complete SQLite Audit Trail & Financial Record Verification...")
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, gib_receipt_no, tax_amount, net_amount, currency, receipt_json FROM university_purchases WHERE user_id = 1 AND university_id = 'ege' ORDER BY id DESC LIMIT 1")
    purch = c.fetchone()
    print(f"  Latest purchase row for ege: id={purch['id']}, gib_receipt_no={purch['gib_receipt_no']}")
    assert purch is not None, "Missing purchase record in university_purchases"
    assert purch["gib_receipt_no"] is not None and purch["gib_receipt_no"].startswith("EARSIV-2026-")
    assert purch["tax_amount"] == 8.33
    assert purch["net_amount"] == 41.67
    assert purch["currency"] == "TRY"
    parsed_json = json.loads(purch["receipt_json"])
    assert parsed_json["receipt_no"] == purch["gib_receipt_no"]
    assert parsed_json["tax_office"] == "Mecidiyeköy Vergi Dairesi"
    conn.close()
    print("  -> PASS: Database records contain full financial audit trail and GİB metadata.")

    # --- 8. Backward Compatibility: Mobile Direct Unlock ---
    print("\n[Assertion 8] Backward Compatibility: Legacy Direct Unlock Fallback...")
    leg_res = client.post("/api/membership/unlock", json={
        "user_id": 1,
        "university_id": "sabanci",
        "card_holder": "Direct Mobile User",
        "card_number": "4242 4242 4242 4242"
    })
    assert leg_res.status_code == 200
    leg_data = leg_res.json()
    assert leg_data["status"] == "success"
    assert leg_data["university_id"] == "sabanci"
    assert "receipt" in leg_data
    assert leg_data["receipt"]["receipt_no"].startswith("EARSIV-2026-")
    print("  -> PASS: Legacy mobile direct unlock fallback seamlessly supported.")

    print("\n" + "=" * 75)
    print("  ALL M2 ADVERSARIAL ASSERTIONS PASSED WITH ZERO DEFECTS (8/8)!")
    print("=" * 75)


if __name__ == "__main__":
    main()
