# Project: PrepMaster R1-R4 Dual-Platform Expansion

## Architecture
- **Data Layer**:
  - `data/questions.json` and `mobile/assets/data/questions.json`: Synchronized English proficiency question pools across 12 universities with CEFR levels, Turkish explanations (`explanation_tr`), and academic categories.
  - `prepmaster.db`: SQLite database storing users, profiles, student verifications, OTPs, purchases, 3DS sessions, and password reset tokens.
- **Backend (Python / FastAPI)**:
  - `backend/app.py`: REST API endpoints for authentication (`/api/auth/register`, `/api/auth/login`, `/api/auth/google`, `/api/auth/forgot-password`, `/api/auth/reset-password`), membership & payments (`/api/membership/check`, `/api/membership/3d-init`, `/api/membership/unlock`), and questions (`/api/questions`, `/api/exam/mock/{uni}`).
  - `backend/database.py`: SQLite schemas and transactions with GİB E-Arşiv receipt generation (`EARSIV-2026-XXXX`).
  - `backend/security.py`: PBKDF2 password hashing, HS256 pure-Python JWT tokens, rate limiting.
- **Web Frontend**:
  - `static/index.html`: Responsive web portal with Auth modal (Google Sign-in, Register, Forgot Password) and 50 TL Paywall modal with 3D Secure SMS simulation.
  - `static/js/auth.js`: Modular auth handlers for Google OAuth and password reset.
  - `static/js/app.js`: Core exam runner, dashboard, and paywall handlers.
- **Mobile Frontend (Flutter Native)**:
  - `mobile/lib/screens/exams_screen.dart`, `dashboard_screen.dart`: Sınav başlatma butonlarına paywall denetimi (`api_service.checkUniversityAccess`).
  - `mobile/lib/screens/university_paywall_sheet.dart`: 50 TL Paywall BottomSheet with card inputs, 3D Secure SMS step, and E-Arşiv receipt display.
  - `mobile/lib/screens/student_document_scan_sheet.dart`: Student Document Scan BottomSheet with E-Devlet paste and 1-click test templates.
  - `mobile/lib/services/api_service.dart`: API client managing local token/access state and remote endpoints.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Hacettepe Question Pool | 12+ authentic academic questions (Restatement, Comprehension, Structure) with explanation_tr | M1 | ORIGINAL_REQUEST R1 |
| 2 | Ankara Question Pool | 12+ authentic academic questions (Cloze Test, Reading Analysis, Vocabulary) with explanation_tr | M1 | ORIGINAL_REQUEST R1 |
| 3 | Gazi Question Pool | 12+ authentic academic questions (Use of English, Grammar & Collocations) with explanation_tr | M1 | ORIGINAL_REQUEST R1 |
| 4 | Ege Question Pool | 12+ authentic academic questions (Sentence Completion, Inference, Flow) with explanation_tr | M1 | ORIGINAL_REQUEST R1 |
| 5 | Koç Question Pool | 12+ authentic academic questions (KUEPE Advanced Reading, Critical Analysis, Restatement) with explanation_tr | M1 | ORIGINAL_REQUEST R1 |
| 6 | Sabancı Question Pool | 12+ authentic academic questions (ELAE Search Reading, Synthesizing, Academic Vocab) with explanation_tr | M1 | ORIGINAL_REQUEST R1 |
| 7 | Dual-Platform Question Sync | Complete parity between data/questions.json and mobile/assets/data/questions.json (>= 195 questions) | M1 | ORIGINAL_REQUEST R1 |
| 8 | Dataset Integrity Assertions | mobile/test/dataset_integrity_test.dart validating count >= 195 and per-university constraints | M1 | ORIGINAL_REQUEST AC |
| 9 | 3D Secure Payment Engine | Backend /api/membership/3d-init, SMS code simulation, expiry & verification | M2 | ORIGINAL_REQUEST R2 |
| 10 | GİB E-Arşiv Fişi Generator | Generate EARSIV-2026-XXXX format receipt with full financial breakdown (50 TL, 20% VAT) | M2 | ORIGINAL_REQUEST R2 |
| 11 | Unlock Membership 3DS API | /api/membership/unlock with 3D Secure SMS verification and university unlocking | M2 | ORIGINAL_REQUEST R2 |
| 12 | Web 3D Secure Paywall Modal | Web UI card form, 6-digit SMS verification step, and E-Arşiv receipt display in static/index.html | M2 | ORIGINAL_REQUEST R2 |
| 13 | Google OAuth 2.0 Backend | /api/auth/google accepting Google token/profile and issuing JWT session token | M3 | ORIGINAL_REQUEST R3 |
| 14 | Forgot Password Backend | /api/auth/forgot-password with 60s cooldown and /api/auth/reset-password with PBKDF2 | M3 | ORIGINAL_REQUEST R3 |
| 15 | Web Auth UI Expansion | Google Sign-in button in login modal and Forgot Password flow in static/index.html & static/js/auth.js | M3 | ORIGINAL_REQUEST R3 |
| 16 | Mobile Paywall BottomSheet | Flutter 50 TL Paywall BottomSheet with card input, 3DS SMS step, and E-Arşiv receipt display | M4 | ORIGINAL_REQUEST R4 |
| 17 | Mobile Student Scan Sheet | Flutter Student Document Scan BottomSheet with 1-click test templates and E-Devlet paste | M4 | ORIGINAL_REQUEST R4 |
| 18 | Mobile Exam Access Guard | Sınav başlatma butonlarına checkUniversityAccess denetimi (exams_screen.dart, dashboard_screen.dart) | M4 | ORIGINAL_REQUEST R4 |
| 19 | Mobile API Service Parity | api_service.dart supporting 3D secure unlock, local offline access checks, document scan | M4 | ORIGINAL_REQUEST R4 |
| 20 | Dual-Platform E2E Verification | flutter analyze (0 err/0 warn), flutter test (100%), deploy_check.py (65/65), clean git commit | M5 | ORIGINAL_REQUEST AC |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Questions Dataset Expansion (R1) | Generate 72 questions (12 per uni), sync data/ and mobile/ assets to >= 195, update dataset_integrity_test.dart | None | DONE |
| M2 | 3D Secure Sanal POS & E-Arşiv (R2) | Backend 3DS init, SMS verification, EARSIV-2026-XXXX generation, /api/membership/unlock, Web Paywall UI | None | DONE |
| M3 | Google OAuth & Forgot Password (R3) | /api/auth/google, /api/auth/forgot-password, /api/auth/reset-password, Web Google Sign-In & Reset UI | None | IN_PROGRESS |
| M4 | Flutter Mobile Paywall & Scan UI (R4) | university_paywall_sheet.dart, student_document_scan_sheet.dart, exam launch paywall check, api_service.dart | M1, M2 | IN_PROGRESS |
| M5 | E2E Quality Verification & Git Commit | Run all tests (flutter analyze, flutter test, python unittests, deploy_check.py), verify git status, commit | M1, M2, M3, M4 | PLANNED |

## Interface Contracts

### 1. Questions Schema Contract (`data/questions.json` & `mobile/assets/data/questions.json`)
```json
{
  "id": "hacettepe_comp_01",
  "university_id": "hacettepe",
  "level": "B2",
  "category": "Paragraph Comprehension",
  "passage": "Academic text...",
  "question": "What is the primary conclusion of the author?",
  "options": [
    {"id": "A", "text": "First option"},
    {"id": "B", "text": "Second option"},
    {"id": "C", "text": "Third option"},
    {"id": "D", "text": "Fourth option"}
  ],
  "correct_answer": "B",
  "explanation_tr": "Detaylı Türkçe akademik çözüm ve strateji ipucu...",
  "explanation_en": "Detailed English explanation..."
}
```

### 2. 3D Secure Payment API Contract (`/api/membership/3d-init` & `/api/membership/unlock`)
1. **Initialize 3D Secure Session**:
   - `POST /api/membership/3d-init`
   - Body: `{"user_id": 1, "university_id": "koc", "card_holder": "Ahmet Yılmaz", "card_number": "5528790000000001", "expire_month": "12", "expire_year": "28", "cvv": "123", "amount_try": 50.0}`
   - Response (200):
     ```json
     {
       "status": "success",
       "session_id": "3DS-SESSION-UUID",
       "masked_phone": "+90 (532) *** ** 42",
       "sms_code_sandbox": "654321",
       "expires_in_seconds": 180,
       "amount_try": 50.0,
       "currency": "TRY"
     }
     ```
2. **Unlock University Membership with 3DS Verification**:
   - `POST /api/membership/unlock`
   - Body:
     ```json
     {
       "user_id": 1,
       "university_id": "koc",
       "card_holder": "Ahmet Yılmaz",
       "card_number": "5528790000000001",
       "session_id": "3DS-SESSION-UUID",
       "sms_code": "654321"
     }
     ```
   - Response (200):
     ```json
     {
       "status": "success",
       "message": "Ödeme onaylandı ve üniversite erişimi açıldı.",
       "university_id": "koc",
       "receipt": {
         "receipt_no": "EARSIV-2026-9284",
         "gross_amount": 50.00,
         "vat_rate": 0.20,
         "vat_amount": 8.33,
         "net_amount": 41.67,
         "currency": "TRY",
         "payment_date": "2026-10-18T12:45:00Z",
         "card_last_four": "0001"
       }
     }
     ```

### 3. Google OAuth & Forgot Password API Contract
1. **Google Sign-In**:
   - `POST /api/auth/google`
   - Body: `{"token": "google-id-token", "email": "student@gmail.com", "name": "Ahmet Yılmaz", "avatar_url": "https://..."}`
   - Response (200): `{"access_token": "JWT_TOKEN", "token_type": "bearer", "user": {"id": 1, "email": "student@gmail.com", "name": "Ahmet Yılmaz", "university_id": "general", "is_verified": false}}`
2. **Forgot Password Request**:
   - `POST /api/auth/forgot-password`
   - Body: `{"email": "student@example.com"}`
   - Response (200): `{"status": "success", "message": "Şifre sıfırlama kodu e-posta adresinize gönderildi.", "cooldown_seconds": 60, "reset_code_sandbox": "123456"}`
3. **Reset Password Confirmation**:
   - `POST /api/auth/reset-password`
   - Body: `{"email": "student@example.com", "reset_code": "123456", "new_password": "NewStrongPassword123!"}`
   - Response (200): `{"status": "success", "message": "Şifreniz başarıyla güncellendi. Yeni şifrenizle giriş yapabilirsiniz."}`

### 4. Flutter Mobile Paywall & Scan Integration Contract
- `ApiService.checkUniversityAccess(String universityId)` -> returns `Future<bool>`
- `ApiService.unlockUniversityMembership({required String universityId, String? sessionId, String? smsCode, ...})` -> returns `Future<Map<String, dynamic>>` including `receipt` with `receipt_no`.
- `ApiService.scanStudentDocument({required String documentText, String? sampleKey})` -> returns `Future<Map<String, dynamic>>` updating local profile and active university.

## Code Layout
- `data/questions.json`: Primary questions database.
- `mobile/assets/data/questions.json`: Bundled mobile questions database (must match `data/questions.json`).
- `backend/app.py`: FastAPI routes.
- `backend/database.py`: Database operations and GİB receipt generation.
- `backend/test_payment_3ds.py`: 3D Secure and E-Arşiv test suite.
- `backend/test_auth_expansion.py`: Google OAuth and Forgot Password test suite.
- `static/index.html`: Web portal UI.
- `static/js/auth.js`: Web OAuth and password reset client.
- `mobile/lib/screens/university_paywall_sheet.dart`: 50 TL Paywall BottomSheet.
- `mobile/lib/screens/student_document_scan_sheet.dart`: Student document scan BottomSheet.
- `mobile/lib/screens/exams_screen.dart`: Exam listing & paywall guard.
- `mobile/lib/screens/dashboard_screen.dart`: Dashboard exam launch & university switcher paywall guard.
- `mobile/lib/services/api_service.dart`: Mobile networking and access management.
- `mobile/test/paywall_and_document_scan_test.dart`: Mobile paywall & scan widget/unit tests.
