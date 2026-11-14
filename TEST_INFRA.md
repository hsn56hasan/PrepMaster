# PrepMaster Dual-Platform Test Infrastructure & Quality Assurance (TEST_INFRA)

## 1. Test Philosophy & Engineering Principles

### 1.1 Progressive Testability & Opaque-Box Validation
All test suites in PrepMaster are authored according to strict opaque-box validation principles:
- **Specification-Driven**: Expected outputs are derived strictly from authoritative specifications (`PROJECT.md` and `ORIGINAL_REQUEST.md`), statutory fiscal standards (Gelir İdaresi Başkanlığı E-Arşiv regulations), and cryptographic standards (RFC 2898 PBKDF2, RFC 7519 JSON Web Token), never by reverse-engineering transient implementation details.
- **Genuine Assertions (No Facades)**: Tests exercise real business logic, state machines, and persistence boundaries. Dummy facade tests that trivially return `true` without executing logic are strictly prohibited.
- **Progressive Testability**: Tests are isolated per subsystem and milestone, allowing independent execution during early development phases while progressively gating end-to-end milestone integrations.
- **Independence & Isolation**: Each test case sets up its own isolated database state (via temporary SQLite databases configured through `PREPMASTER_DB_PATH`) and cleans up after completion. Tests never depend on execution order or shared mutable side-effects.

### 1.2 Mathematical & Statutory Derivation of Expected Values
- **GİB E-Arşiv Fişi Financial Breakdown**:
  - Statutory Gross Amount: `50.00 TL`
  - Statutory VAT Rate: `20%` (`0.20`)
  - Statutory Net Amount: $\text{Net} = \frac{\text{Gross}}{1 + \text{VAT Rate}} = \frac{50.00}{1.20} = 41.6666... \approx 41.67\text{ TL}$
  - Statutory VAT Amount: $\text{VAT} = \text{Gross} - \text{Net} = 50.00 - 41.67 = 8.33\text{ TL}$
  - Balance Equation Check: $\text{Net} + \text{VAT} = 41.67 + 8.33 = 50.00\text{ TL}$ (Exact zero-remainder parity).
  - Receipt Reference Regex: `^EARSIV-2026-[A-Z0-9]{4,}$` (GİB E-Arşiv 2026 financial serial identifier).
- **Cryptographic Bounds**:
  - PBKDF2 Password Hashing: 100,000 iterations, HMAC-SHA256, 16-byte cryptographically secure random salt (`pbkdf2:sha256:100000$<salt>$<hash>`).
  - SMS & Reset OTP: Exactly 6 numeric digits (`^\d{6}$`), uniform distribution in $[100000, 999999]$.
  - Cooldowns: Exactly 60 seconds minimum window before consecutive OTP requests.

---

## 2. Feature Inventory (Features 1–20)

| # | Feature Name | Target Scope & Files | Authoritative Spec Source | Primary Test Suite |
|---|--------------|----------------------|---------------------------|--------------------|
| 1 | Hacettepe Question Pool | 12+ academic questions with `explanation_tr` | ORIGINAL_REQUEST R1 | `mobile/test/dataset_integrity_test.dart` |
| 2 | Ankara Question Pool | 12+ academic questions with `explanation_tr` | ORIGINAL_REQUEST R1 | `mobile/test/dataset_integrity_test.dart` |
| 3 | Gazi Question Pool | 12+ academic questions with `explanation_tr` | ORIGINAL_REQUEST R1 | `mobile/test/dataset_integrity_test.dart` |
| 4 | Ege Question Pool | 12+ academic questions with `explanation_tr` | ORIGINAL_REQUEST R1 | `mobile/test/dataset_integrity_test.dart` |
| 5 | Koç Question Pool | 12+ academic questions with `explanation_tr` | ORIGINAL_REQUEST R1 | `mobile/test/dataset_integrity_test.dart` |
| 6 | Sabancı Question Pool | 12+ academic questions with `explanation_tr` | ORIGINAL_REQUEST R1 | `mobile/test/dataset_integrity_test.dart` |
| 7 | Dual-Platform Question Sync | Parity between `data/` and `mobile/assets/data/` (>= 195) | ORIGINAL_REQUEST R1 | `mobile/test/dataset_integrity_test.dart` |
| 8 | Dataset Integrity Assertions | Count, field completeness, CEFR validation | ORIGINAL_REQUEST AC | `mobile/test/dataset_integrity_test.dart` |
| 9 | 3D Secure Payment Engine | `/api/membership/3d-init`, session generation, 6-digit SMS | ORIGINAL_REQUEST R2 | `backend/test_payment_3ds.py` |
| 10 | GİB E-Arşiv Fişi Generator | `EARSIV-2026-XXXX`, 50 TL, 20% VAT, net 41.67 TL | ORIGINAL_REQUEST R2 | `backend/test_payment_3ds.py` |
| 11 | Unlock Membership 3DS API | `/api/membership/unlock` with SMS verification & DB entitlement | ORIGINAL_REQUEST R2 | `backend/test_payment_3ds.py` |
| 12 | Web 3D Secure Paywall Modal | Card form, SMS modal, E-Arşiv receipt display | ORIGINAL_REQUEST R2 | `backend/test_payment_3ds.py` |
| 13 | Google OAuth 2.0 Backend | `/api/auth/google`, user ingestion, JWT issuance | ORIGINAL_REQUEST R3 | `backend/test_auth_expansion.py` |
| 14 | Forgot Password Backend | `/api/auth/forgot-password` (60s cooldown), `/reset-password` | ORIGINAL_REQUEST R3 | `backend/test_auth_expansion.py` |
| 15 | Web Auth UI Expansion | Google Sign-in button, Forgot Password wizard | ORIGINAL_REQUEST R3 | `backend/test_auth_expansion.py` |
| 16 | Mobile Paywall BottomSheet | Flutter card form, 3DS SMS step, E-Arşiv receipt display | ORIGINAL_REQUEST R4 | `mobile/test/paywall_and_document_scan_test.dart` |
| 17 | Mobile Student Scan Sheet | 1-click test templates, E-Devlet text paste, uni switch | ORIGINAL_REQUEST R4 | `mobile/test/paywall_and_document_scan_test.dart` |
| 18 | Mobile Exam Access Guard | `checkUniversityAccess` gate on mock & category exam launch | ORIGINAL_REQUEST R4 | `mobile/test/paywall_and_document_scan_test.dart` |
| 19 | Mobile API Service Parity | Offline-safe university access, 3DS unlock, document scan | ORIGINAL_REQUEST R4 | `mobile/test/paywall_and_document_scan_test.dart` |
| 20 | Dual-Platform E2E Verification | `deploy_check.py` (65/65), `flutter analyze` (0/0), `flutter test` (100%) | ORIGINAL_REQUEST AC | System Pre-Flight & CI Runners |

---

## 3. Four-Tier Test Coverage Architecture

### Tier 1: Feature-Level & Unit Tests
Focuses on individual endpoint contracts, schema parsers, and component behaviors in isolation:
- **Question Datasets**: Verifies that every question JSON record adheres strictly to the required schema (`id`, `university_id`, `level`, `category`, `passage`/`question`, `options`, `correct_answer`, `explanation_tr`).
- **3D Secure Session Initialization**: Verifies that `POST /api/membership/3d-init` validates input card details, creates a session with a unique UUID/prefix, returns masked phone number, 6-digit SMS code, and expires in 180 seconds.
- **Google OAuth Registration**: Verifies that `POST /api/auth/google` ingests Google user profiles, generates a unique username, stores the user in SQLite, and returns a valid HS256 JWT session token.
- **Forgot Password OTP Generation**: Verifies that `POST /api/auth/forgot-password` generates a 6-digit numeric reset code and records the expiration in `password_resets`.
- **Mobile Access Logic**: Verifies that `ApiService.checkUniversityAccess` grants free access to `general` and `all` modules, as well as the student's registered or verified university.

### Tier 2: Boundary & Security Defense Tests
Focuses on edge conditions, malformed payloads, rate limiters, and adversarial inputs:
- **SMS Code Guessing / Brute-Force Defense**: Verifies that submitting invalid SMS codes increments the attempt counter and locks out after 3 failed attempts with HTTP 400.
- **Session Expiry**: Verifies that attempting to verify an expired 3D Secure session or reset code fails immediately with HTTP 400.
- **Password Reset Cooldown**: Verifies that calling `POST /api/auth/forgot-password` twice within 60 seconds triggers a cooldown violation with HTTP 400 and remaining seconds detail.
- **Sliding-Window Rate Limiting**: Verifies that rapid bursts of requests trigger HTTP 429 (`Too Many Requests`) with `Retry-After` response headers.
- **Input Sanitization & Injection Prevention**: Verifies that XSS tags (`<script>`, `onerror=`, `javascript:`) in cardholder names or student names are sanitized, and SQL injection strings (`' OR '1'='1`) in auth identifiers are safely neutralized via parameterized queries.
- **One-Time Code Consumption**: Verifies that once a reset code or 3DS session code is used, it cannot be replayed or reused (`is_used = 1`).

### Tier 3: Cross-Feature Integration Tests
Focuses on end-to-end workflows traversing multiple modules, database states, and client services:
- **Complete 3D Secure Purchase to Exam Access Workflow**:
  1. User checks access for a target university (e.g., `hacettepe`) -> returns `has_access: false`, `requires_membership: true`.
  2. User initiates 3D Secure session via `POST /api/membership/3d-init` -> receives `session_id` and `sms_code`.
  3. User completes verification via `POST /api/membership/unlock` with `session_id` and `sms_code`.
  4. Response verifies GİB E-Arşiv format `EARSIV-2026-XXXX`, 50.00 TL gross, 8.33 TL VAT, 41.67 TL net.
  5. SQLite `users` table updates `unlocked_universities` JSON column to include `hacettepe`.
  6. Subsequent call to `POST /api/membership/check` or `ApiService.checkUniversityAccess` returns `has_access: true`.
  7. Mobile exam runner launches `ExamRunnerScreen` without triggering paywall bottom sheet.
- **Google OAuth to Profile Synchronization Workflow**:
  1. Google user signs in via `POST /api/auth/google`.
  2. Backend issues session JWT token.
  3. Subsequent call to `GET /api/auth/me` with `Authorization: Bearer <token>` authenticates user.
  4. Mobile client persists user session locally in `SharedPreferences`.
  5. Student scans E-Devlet document via `POST /api/student/scan-document`.
  6. Local profile updates `verified_university` and grants instant access.
- **Password Reset to Re-Authentication Workflow**:
  1. User requests password reset via `POST /api/auth/forgot-password`.
  2. User updates password via `POST /api/auth/reset-password` using the received OTP and new password.
  3. Old password fails authentication at `POST /api/auth/login` (HTTP 401).
  4. New password succeeds at `POST /api/auth/login` and returns new session token.

### Tier 4: Real-World Scenarios & Adversarial Verification
Focuses on resilience under unexpected network conditions, offline scenarios, and edge-case execution:
- **Mobile Offline Resilience**: Verifies that `ApiService.checkUniversityAccess` gracefully allows local offline access based on cached user entitlements in `SharedPreferences` when backend server is unreachable.
- **Direct Legacy Payment Fallback**: Verifies that direct calls to `/api/membership/unlock` (legacy mobile API without 3DS session) continue to succeed in sandbox mode, ensuring zero regressions for legacy mobile clients.
- **Document Scanner OCR Noise & Fuzzy Matching**: Verifies that student document scanning accurately extracts university names, student numbers, and barcodes even with noisy OCR text, formatting variances, and varying case sensitivity.
- **Deployment Hardening Integrity**: Verifies that all 65 pre-flight integrity checks in `deploy_check.py` remain fully satisfied, ensuring that database schema migrations, Docker isolation, and Nginx reverse proxy configurations are never compromised.

---

## 4. Test Execution Guide

### Backend Test Suites
```powershell
# Run 3D Secure payment & E-Arşiv test suite
python -m unittest backend/test_payment_3ds.py

# Run Google OAuth & Forgot Password test suite
python -m unittest backend/test_auth_expansion.py

# Run Security & Rate-Limiting test suite
python -m unittest backend/test_security.py

# Run Student OTP lifecycle test suite
python -m unittest backend/test_otp.py

# Run complete backend test suite
python -m unittest discover -s backend -p "test_*.py"

# Run production deployment & system integrity check (65/65 checks)
python deploy_check.py
```

### Mobile Flutter Test Suites
```powershell
# Run Flutter static analysis (must report 0 errors and 0 warnings)
cd C:\Projeler\PrepMaster\mobile
flutter analyze

# Run Paywall, Document Scan & Access Guard tests
flutter test test/paywall_and_document_scan_test.dart

# Run Dataset Integrity tests (Questions, Vocab, Listening parity)
flutter test test/dataset_integrity_test.dart

# Run Listening, Writing & Theme tests
flutter test test/listening_writing_test.dart

# Run full Flutter mobile test suite
flutter test
```
