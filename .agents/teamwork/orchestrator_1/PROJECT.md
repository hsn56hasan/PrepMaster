# Project: PrepMaster Full Parity & Content Expansion

## Architecture
- **Dual-Platform Preparation Platform**:
  - **Web Portal**: Vanilla ES6 + Tailwind CSS (served via FastAPI at port 8050)
  - **Native Mobile**: Flutter 3.47+ / Dart 3.13+ (Android, Windows, Web targets)
  - **Backend API**: FastAPI (Python 3.12) with SQLite (`prepmaster.db`)
  - **Asset Datasets**: Synchronized JSON assets in `data/` and `mobile/assets/data/`
- **Data Flow & Cross-Platform Contracts**:
  - Web fetches endpoints from `/api/*` or loads cached data from `localStorage`.
  - Flutter calls `ApiService` which targets the FastAPI backend with immediate offline fallback to bundled `assets/data/*.json`.
  - Authentication state persists via `localStorage` on Web and `SharedPreferences` on Mobile.
  - Theme preference persists via `localStorage` on Web (`prepmaster_theme`) and `SharedPreferences` on Mobile (`theme_mode`).

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1 | Listening Dataset Expansion | Add 4 new university academic listening tracks (Boğaziçi, ODTÜ, İTÜ, Bilkent) with note-taking guidelines, transcripts, 4 MCQs each | M1 | R3, Survey 3 |
| F2 | Listening Test & Asset Sync | Synchronize data/listening.json and mobile/assets/data/listening.json; update dataset_integrity_test.dart | M1 | R3, Survey 1 & 3 |
| F3 | Essay Exemplars Dataset | Band 85+ model essays for Opinion, For & Against, Problem-Solution with thesis, topic sentences, CEFR breakdown, pitfall analyses | M2 | R2, Survey 3 |
| F4 | Web Writing Exemplars UI | Exemplar Library view in static/index.html and app.js with category filtering, annotation rendering, and localStorage offline cache | M2 | R2, Survey 2 |
| F5 | Flutter Writing Exemplars UI | EssayExemplar model, Exemplar Library tab in WritingScreen with color-coded annotations, CEFR scorecards, and offline loading | M2 | R2, Survey 1 |
| F6 | Web Dark Mode Support | Tailwind darkMode: 'class', dark palette classes across all elements, header toggle button, localStorage persistence | M3 | R4, Survey 2 |
| F7 | Flutter Dark Mode Support | AppTheme.darkTheme, ValueNotifier<ThemeMode>, AppBar toggle, semantic card/surface styling, SharedPreferences persistence | M3 | R4, Survey 1 |
| F8 | Backend Auth & DB Migration | SQLite column migrations adding user_id to exam_attempts, vocab_progress, mistake_vault; update /api/auth/* and /api/sync/* | M4 | R1, Survey 2 |
| F9 | Web Auth & Session Header | Responsive Login/Register modals, form validation, dynamic session state in header, localStorage persistence | M4 | R1, Survey 2 |
| F10 | Flutter Auth & Session UI | User model, ApiService auth methods, Login/Register bottom sheet, SharedPreferences token storage, session auto-restore, progress sync | M4 | R1, Survey 1 |
| F11 | E2E QA, Build & Git Commit | flutter analyze (0 issues), flutter test (100% pass), flutter build apk --debug (exit code 0), clean Git commit | M5 | Acceptance Criteria |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Listening Expansion & Sync | F1, F2 (data/listening.json, mobile/assets/data/listening.json, dataset_integrity_test.dart) | none | IN_PROGRESS |
| 2 | High-Scoring Essay Library | F3, F4, F5 (writing_guides.json, static/index.html, static/js/app.js, writing_screen.dart) | M1 | PLANNED |
| 3 | Dark Mode (Gece Modu) | F6, F7 (static/index.html, static/css/style.css, static/js/app.js, app_theme.dart, main.dart, dashboard_screen.dart) | none | PLANNED |
| 4 | Authentication & Multi-User Parity | F8, F9, F10 (database.py, app.py, static/index.html, static/js/app.js, api_service.dart, user.dart, login_sheet.dart, dashboard_screen.dart, home_navigation.dart) | M1, M2, M3 | PLANNED |
| 5 | Global Verification & Git Commit | F11 (tests/test_backend_api.py, flutter analyze, flutter test, flutter build apk, git status & commit) | M1, M2, M3, M4 | PLANNED |

## Interface Contracts

### 1. Academic Listening Contract (`data/listening.json` & `mobile/assets/data/listening.json`)
```json
{
  "id": "lis_buept_02",
  "university_id": "boun",
  "level": "C1",
  "type": "note_taking",
  "title": "String",
  "subtitle": "String",
  "target_university": "Boğaziçi BUEPT / BUEPT-PBT",
  "duration_minutes": 15,
  "lecture_duration_seconds": 180,
  "instructions_tr": "String",
  "audio_script": "String (natural academic spoken English transcript)",
  "suggested_notes_tr": ["Note bullet 1", "Note bullet 2"],
  "questions": [
    {
      "id": "lis_buept_02_q1",
      "question": "String",
      "options": [
        {"key": "A", "text": "Option A"},
        {"key": "B", "text": "Option B"},
        {"key": "C", "text": "Option C"},
        {"key": "D", "text": "Option D"}
      ],
      "correct_answer": "B",
      "explanation_tr": "Rationale in Turkish"
    }
  ]
}
```

### 2. Writing Exemplars Contract (`data/writing_guides.json` & `mobile/assets/data/writing_guides.json`)
```json
{
  "id": "opinion-essay",
  "title": "Opinion Essay",
  "category": "opinion",
  "exemplars": [
    {
      "id": "ex_opinion_01",
      "title": "Should University Education Be Fully Subsidized by the State?",
      "target_university": "Boğaziçi / ODTÜ",
      "band_score": 92,
      "prompt": "...",
      "thesis_statement": "...",
      "topic_sentences": [
        "First and foremost, universal higher education dismantles socioeconomic stratification...",
        "Furthermore, a highly educated populace yields substantial macroeconomic dividends..."
      ],
      "cefr_rubric": {
        "task_achievement": {"score": 24, "max": 25, "feedback": "..."},
        "coherence_cohesion": {"score": 23, "max": 25, "feedback": "..."},
        "lexical_resource": {"score": 23, "max": 25, "feedback": "..."},
        "grammatical_range": {"score": 22, "max": 25, "feedback": "..."}
      },
      "paragraphs": [
        {"type": "introduction", "text": "..."},
        {"type": "body_1", "text": "..."},
        {"type": "body_2", "text": "..."},
        {"type": "conclusion", "text": "..."}
      ],
      "pitfalls_analysis": [
        {
          "common_pitfall": "Vague thesis lacking clear stance or roadmap",
          "band_60_mistake": "In this essay I will discuss both sides of university education.",
          "band_85_remedy": "This essay argues that state-funded university tuition is indispensable for societal mobility and long-term economic resilience."
        }
      ]
    }
  ]
}
```

### 3. Backend Auth Contract (`/api/auth/*`)
- `POST /api/auth/register` -> Request: `{email, username, password, full_name, university_id, student_number}` -> Response: `{status: "success", user: {...}, token: "pm_token_..."}`
- `POST /api/auth/login` -> Request: `{identifier, password}` -> Response: `{status: "success", user: {...}, token: "pm_token_..."}`
- `GET /api/auth/me` -> Header: `Authorization: Bearer <token>` or Query: `?user_id=1` -> Response: User profile with university metadata.

## Code Layout
- Backend:
  - `backend/app.py`: FastAPI routes, auth endpoints, sync endpoints
  - `backend/database.py`: SQLite connection, table schemas, column migration, queries
  - `data/listening.json`: Canonical listening dataset
  - `data/writing_guides.json`: Canonical writing guides & exemplars dataset
  - `tests/test_backend_api.py`: Automated Python tests
- Web Frontend:
  - `static/index.html`: Web layout, Header, Auth modals, Exemplar viewer, Dark mode classes
  - `static/js/app.js`: Web client logic, auth state, writing exemplar viewer, dark mode toggle
  - `static/css/style.css`: Custom utility and dark mode styling
- Mobile App:
  - `mobile/lib/main.dart`: App entrypoint, ThemeMode state
  - `mobile/lib/theme/app_theme.dart`: Light and Dark themes, palettes
  - `mobile/lib/models/user.dart`: User data model
  - `mobile/lib/models/writing_guide.dart`: WritingGuide & EssayExemplar models
  - `mobile/lib/models/listening_track.dart`: ListeningTrack model
  - `mobile/lib/services/api_service.dart`: HTTP calls, auth endpoints, session management
  - `mobile/lib/services/sync_service.dart`: User-scoped sync
  - `mobile/lib/screens/login_sheet.dart`: Login & Register bottom sheet
  - `mobile/lib/screens/dashboard_screen.dart`: Header, User profile avatar, Theme toggle button
  - `mobile/lib/screens/writing_screen.dart`: Exemplar Library tab with annotations & CEFR scorecards
  - `mobile/lib/screens/home_navigation.dart`: Session restoration, tab routing
  - `mobile/assets/data/listening.json`: Bundled mobile listening dataset
  - `mobile/assets/data/writing_guides.json`: Bundled mobile writing guides & exemplars
  - `mobile/test/dataset_integrity_test.dart`: Integrity test suite for datasets
