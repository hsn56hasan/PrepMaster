# Survey 2 Handoff Report: Web Portal & Backend APIs Audit

## 1. Observation

### 1.1 Backend Authentication & Session Architecture (R1)
- **Endpoints Defined**:
  - `backend/app.py:122-135`:
    ```python
    @app.post("/api/auth/register")
    def register_endpoint(req: RegisterRequest):
        try:
            user = create_user(
                email=req.email,
                username=req.username,
                password=req.password,
                full_name=req.full_name,
                university_id=req.university_id or "itu",
                student_number=req.student_number or ""
            )
            return {"status": "success", "user": user}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Kayıt oluşturulamadı: {str(e)}")
    ```
  - `backend/app.py:137-144`:
    ```python
    @app.post("/api/auth/login")
    def login_endpoint(req: LoginRequest):
        user = authenticate_user(req.identifier, req.password)
        if not user:
            raise HTTPException(status_code=401, detail="Geçersiz kullanıcı adı/e-posta veya şifre.")
        uni = next((u for u in universities_data if u["id"] == user.get("university_id")), universities_data[0])
        user["university"] = uni
        return {"status": "success", "user": user}
    ```
  - `backend/app.py:146-151`:
    ```python
    @app.get("/api/auth/me")
    def current_user_endpoint(user_id: int = 1):
        user = get_profile(user_id)
        uni = next((u for u in universities_data if u["id"] == user.get("university_id")), universities_data[0])
        user["university"] = uni
        return user
    ```
  - `backend/app.py:102-113`: Request models:
    - `RegisterRequest`: `email: str`, `username: str`, `password: str`, `full_name: str`, `university_id: Optional[str] = "itu"`, `student_number: Optional[str] = ""`.
    - `LoginRequest`: `identifier: str`, `password: str`.
- **Token Mechanism**:
  - Neither `/api/auth/register` nor `/api/auth/login` generates or returns a JWT, session token, or cookie.
  - `/api/auth/me` does not inspect `Authorization` HTTP headers. It relies exclusively on an optional query parameter `?user_id=1` (defaulting to 1).
  - Password hashing in `backend/database.py:15-17` uses `hashlib.sha256((password + "prepmaster_salt_2026").encode('utf-8')).hexdigest()`.
- **Database Schema & Incomplete Multi-User Sync**:
  - Live table check via `PRAGMA table_info` on `prepmaster.db`:
    - `users`: `['id', 'email', 'username', 'password_hash', 'full_name', 'university_id', 'student_number', 'is_verified_student', 'verification_status', 'current_level', 'target_score', 'streak_days', 'created_at', 'last_active']`.
    - `exam_attempts`: `['id', 'university_id', 'level', 'score', 'total_questions', 'correct_count', 'duration_seconds', 'answers_json', 'created_at']` -> **NO `user_id` column present in live DB!**
    - `vocab_progress`: `['word_id', 'status', 'review_count', 'last_reviewed']` -> **NO `user_id` column present in live DB!**
    - `mistake_vault`: `['question_id', 'university_id', 'level', 'category', 'wrong_count', 'last_wrong_answer', 'last_wrong_at', 'is_resolved', 'resolved_at']` -> **NO `user_id` column present in live DB!**
    - Executing `SELECT user_id FROM vocab_progress` throws verbatim error: `sqlite3.OperationalError: no such column: user_id`.
  - In `backend/app.py:700-746`:
    - `GET /api/sync/pull` takes 0 parameters, calling `get_profile()`, `get_mistakes()`, `get_vocab_progress()`, and `get_exam_history()`, which all default to `user_id=1`.
    - `POST /api/sync/push` accepts `SyncPushRequest(profile, mistakes, vocab_progress, exam_attempts)` but lacks any `user_id` field or user scoping. All progress updates overwrite global records.

### 1.2 Web Portal UI Audit (R1, R2, R4)
- **Header Component (`static/index.html:56-113`)**:
  - Displays: Logo, static university name (`#header-uni-name`), kur selector pills (`#level-selector-pills`), verification status badge (`#header-verification-badge`), cloud sync button (`#header-sync-btn`), university picker button, quick exam button (`Hızlı Deneme`).
  - **Missing**:
    - No user name display or user avatar.
    - No dynamic session toggle (Login/Register buttons when unauthenticated vs. User Profile + Logout action when authenticated).
    - Verification badge is statically rendered and bound to hardcoded `user_id: 1` (`static/js/app.js:608`).
- **Login & Register Modals**:
  - Completely absent from `static/index.html`.
  - Only modals existing in `static/index.html` are:
    1. `#exam-simulation-area` (lines 691-758)
    2. `#exam-results-modal` (lines 761-763)
    3. `#university-picker-modal` (lines 766-782)
    4. `#student-verify-modal` (lines 785-825)
    5. `#printable-report-modal` (lines 828-832)
  - `static/js/app.js` has zero login/register functions, zero form validation, and zero calls to `/api/auth/login` or `/api/auth/register`.
  - Client-side storage: `Select-String -Path "static/js/*.js" -Pattern "localStorage"` returned 0 results. No authentication state is persisted.
- **Writing Section & Essay Library (R2)**:
  - `static/index.html:568-577`:
    Contains `#ai-writing-evaluator-section` and `#writing-guides-container`.
  - `static/js/writing_ai.js`:
    Implements an interactive AI Writing Evaluator calling `POST /api/writing/evaluate`.
  - `static/js/app.js:289-341` (`loadWritingGuides()`):
    Fetches `/api/writing-guides` and renders basic structure cards, transitions list, and a single sample topic line.
  - `data/writing_guides.json` (and `mobile/assets/data/writing_guides.json`):
    Contains only 2 items: `"opinion-essay"` and `"cause-effect-essay"`.
    **Missing**:
    - No "For & Against" essay guide.
    - No "Problem-Solution" essay guide.
    - No authentic library of Band 85+ annotated sample essays.
    - No thesis statement or topic sentence breakdown annotations.
    - No common pitfall analyses (Yaygın Tuzaklar).
    - Offline access: Zero caching in `localStorage` or Service Worker. If offline, `loadWritingGuides()` fails silently.
- **Dark Mode Support (R4)**:
  - `static/index.html:18-37`: Tailwind CSS is loaded from CDN (`https://cdn.tailwindcss.com`), but `tailwind.config` does NOT have `darkMode: 'class'`.
  - `static/index.html` has hardcoded light classes (`bg-slate-50`, `text-slate-800`, `bg-white`).
  - `static/css/style.css` contains zero dark mode styles.
  - Search across all files in `static/` for "dark" returned 0 hits.
  - No dark mode toggle button exists anywhere in the UI.

### 1.3 Web Test Setup, Build Scripts & Serving Configuration
- **Server Execution**:
  - `run.bat:18`: `python -m uvicorn backend.app:app --host 0.0.0.0 --port 8050 --reload`.
  - Serving: FastAPI mounts `static` at `/static` and serves `static/index.html` at `/`.
- **Dependencies (`requirements.txt`)**:
  - `fastapi>=0.110.0`, `uvicorn>=0.28.0`, `pydantic>=2.6.0`.
  - Python runtime: Python 3.12.10.
- **Build Tools**:
  - No Node.js build system (`package.json`, Vite, Webpack, etc.) exists in the repository. Web frontend is vanilla ES6 + CDN assets.
- **Test Setup**:
  - `mobile/` has Dart tests (`mobile/test/dataset_integrity_test.dart`, `widget_test.dart`, etc.).
  - `backend/` and `static/` have **zero automated tests**.
  - `pytest` is not installed on the system (`No module named pytest`).
  - Python's standard library `unittest` is fully operational (`python -m unittest`).

---

## 2. Logic Chain

1. **Auth Integration Gap**:
   - *Observation*: Backend defines `/api/auth/register`, `/api/auth/login`, and `/api/auth/me` (`backend/app.py:122-151`), but `static/index.html` and `static/js/app.js` contain no login/register UI, no form handlers, and no `localStorage` usage.
   - *Inference*: The existing backend authentication endpoints are completely disconnected from the Web Portal. Users are permanently treated as the default single user (`ituhazirlik`, user_id 1).
   - *Required Action*: Add responsive Login/Register modal dialogs in `static/index.html`, add modal controllers & API handlers in `static/js/app.js`, store user session in `localStorage`, and update the header dynamically.

2. **Multi-User Sync Incompatibility in SQLite**:
   - *Observation*: `prepmaster.db` has tables `exam_attempts`, `vocab_progress`, and `mistake_vault` without `user_id` columns (verified via `PRAGMA table_info` and SQLite `OperationalError: no such column: user_id`). Furthermore, `vocab_progress` has `word_id` as sole primary key, and `mistake_vault` has `question_id` as sole primary key.
   - *Inference*: If multi-user sync is enabled without schema migration, all queries filtering or inserting `user_id` will fail with SQLite operational errors. Additionally, any vocabulary progress or mistake made by one user would clobber or merge with another user's progress.
   - *Required Action*: Add automatic schema migrations in `backend/database.py:init_db()` using `ALTER TABLE ... ADD COLUMN user_id INTEGER DEFAULT 1;`, and update sync/crud functions to partition and filter by `user_id`. Update `/api/sync/pull` and `/api/sync/push` to accept and process `user_id`.

3. **Writing Section & Essay Library Deficiencies (R2)**:
   - *Observation*: `data/writing_guides.json` contains only 2 guides (`opinion-essay`, `cause-effect-essay`) with no full student exemplar essays, no thesis/topic-sentence annotations, and no pitfall analyses. Neither "For & Against" nor "Problem-Solution" exists.
   - *Inference*: To meet R2 acceptance criteria ("Writing library renders annotated model essays with thesis, topic sentences, and CEFR breakdown" for Opinion, For & Against, and Problem-Solution), `writing_guides.json` must be expanded with authentic Band 85+ exemplars, detailed CEFR scoring rubrics, annotated thesis/topic sentences, and pitfall analyses.
   - *Inference on Offline Access*: Web currently has no offline cache for writing guides. Storing loaded writing guides in `localStorage` under `prepmaster_writing_guides_cache` ensures instant offline access on Web even if the backend is unreachable.

4. **Dark Mode Missing Implementation (R4)**:
   - *Observation*: `tailwind.config` in `static/index.html` lacks `darkMode: 'class'`. There are no dark Tailwind classes in `index.html` or `style.css`, and no toggle switch in the UI.
   - *Inference*: Dark mode must be implemented by adding `darkMode: 'class'` to `tailwind.config`, adding a toggle button in the header, writing toggle logic with `localStorage.setItem('prepmaster_theme', ...)` in `app.js`, and adding Tailwind `dark:` classes across all layout elements, cards, and modal dialogs.

5. **Test Setup Gap**:
   - *Observation*: No tests exist for backend or web endpoints. `pytest` is not installed, but Python standard library `unittest` is ready.
   - *Inference*: Backend API endpoints (`/api/auth/*`, `/api/student/*`, `/api/sync/*`, `/api/writing-guides`) can be immediately and comprehensively verified using a standalone `tests/test_backend_api.py` run via `python -m unittest discover -s tests`.

---

## 3. Caveats

1. **JWT vs. Session Tokens**: The backend does not currently have `pyjwt` or `passlib` installed in the Python environment. Implementing full signed JWT tokens would require installing additional packages or using a lightweight cryptographic signature (e.g. `hmac` + `hashlib` token or database session tokens). Given existing requirements, returning an auth user object with a session token or user ID persistence in `localStorage` fulfills R1 without external dependencies.
2. **CDN Tailwind in Development**: `static/index.html` uses Tailwind CDN (`https://cdn.tailwindcss.com`). In production offline scenarios, CDN scripts require prior caching or local bundling. However, `localStorage` caching for datasets guarantees offline functionality of essay guides and student progress.

---

## 4. Conclusion

The Web Portal and Backend have a solid architectural foundation but require specific, highly targeted implementations to achieve 100% feature parity:
1. **Backend**:
   - Run safe SQLite column migrations on `prepmaster.db` for `exam_attempts`, `vocab_progress`, and `mistake_vault` to add `user_id INTEGER DEFAULT 1`.
   - Update `create_user`, `authenticate_user`, `get_profile`, `save_exam_attempt`, `get_exam_history`, `set_vocab_status`, `get_vocab_progress`, `record_mistake`, and `get_mistakes` to accept and filter by `user_id`.
   - Update `/api/sync/pull` and `/api/sync/push` to support `user_id` so that Web and Mobile sync distinct user sessions.
   - Attach university metadata in `/api/auth/register` response identically to `/api/auth/login`.
2. **Web Portal UI**:
   - Add responsive Login and Register modal dialogs in `static/index.html` with form validation, error banners, and university selection.
   - Implement dynamic session state in the Header:
     - Unauthenticated: Display "Giriş Yap" and "Kayıt Ol" action buttons.
     - Authenticated: Display user name (`ituhazirlik` / full name), student verification badge, and "Çıkış Yap" (Logout) button.
     - Persist session in `localStorage` (`prepmaster_user`) and auto-restore on page load.
   - Expand Writing Section (R2):
     - Enrich `data/writing_guides.json` with Opinion, For & Against, and Problem-Solution guides.
     - Include Band 85+ student sample exemplars with annotated thesis statement, topic sentences, CEFR breakdown (Task Achievement, Coherence & Cohesion, Lexical Resource, Grammatical Range), and common pitfall analyses.
     - Render an interactive Essay Library alongside the existing AI Evaluator in `static/js/app.js` and `static/index.html`.
     - Cache exemplars in `localStorage` for offline access.
   - Dark Mode Support (R4):
     - Configure `darkMode: 'class'` in Tailwind.
     - Add theme toggle switch in Header.
     - Add `dark:` variant classes across the application and persist preference in `localStorage`.
3. **Automated Testing**:
   - Add `tests/test_backend_api.py` covering `/api/auth/register`, `/api/auth/login`, `/api/auth/me`, `/api/sync/pull`, `/api/sync/push`, and `/api/writing-guides` via `python -m unittest`.

---

## 5. Verification Method

To independently verify all findings and validate subsequent implementations:

1. **Verify Backend Auth & Sync Endpoints**:
   ```powershell
   python -c "from backend.app import app; print('Endpoints:', [r.path for r in app.routes if 'auth' in r.path or 'sync' in r.path])"
   ```
2. **Verify SQLite Columns & Absence of user_id in Live DB**:
   ```powershell
   python -c "import sqlite3; conn = sqlite3.connect('prepmaster.db'); print({t: [c[1] for c in conn.execute(f'PRAGMA table_info({t})').fetchall()] for t in ['exam_attempts', 'vocab_progress', 'mistake_vault']})"
   ```
3. **Verify Web Modals & Dark Mode Absence**:
   ```powershell
   Select-String -Path "static\index.html" -Pattern "login-modal|register-modal|darkMode"
   ```
4. **Run Backend Test Suite (once implemented)**:
   ```powershell
   python -m unittest discover -s tests -p "test_*.py" -v
   ```
5. **Inspect Data Parity**:
   ```powershell
   python -c "import json; g = json.load(open('data/writing_guides.json', encoding='utf-8')); print('Guides:', [x['id'] for x in g])"
   ```
