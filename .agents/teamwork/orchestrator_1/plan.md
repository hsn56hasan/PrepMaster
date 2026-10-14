# PrepMaster Orchestration Plan

## Objective
Deliver 100% feature parity across Web Portal and Native Flutter Mobile app for PrepMaster, fulfilling R1, R2, R3, and R4, meeting all acceptance criteria.

## Strategy & Phasing
- **Phase 0: Architecture & Codebase Survey**
  - Dispatch 3 parallel Explorers:
    - Explorer 1: Mobile application codebase (Flutter, state management, routes, auth, theme, listening, writing, tests)
    - Explorer 2: Web portal codebase & Backend APIs (HTML/JS/Tailwind, routes, auth endpoints, essay library, dark mode, server)
    - Explorer 3: Data assets & Test infrastructure (data/listening.json, writing data/assets, mobile/test/dataset_integrity_test.dart, test suite runner, git status)
- **Phase 1: Project Scope & Interface Contracts (PROJECT.md)**
  - Synthesize survey findings into PROJECT.md.
  - Define exact data models, API interfaces, file paths, and implementation boundaries.
- **Phase 2: Milestone 1 - Academic Listening Expansion & Sync (R3)**
  - Add 4 new university tracks (Boğaziçi, ODTÜ, İTÜ, Bilkent) to data/listening.json and mobile/assets/data/listening.json.
  - Validate dataset_integrity_test.dart.
- **Phase 3: Milestone 2 - High-Scoring Essay Library & Writing Exemplars (R2)**
  - Implement Band 85+ annotated exemplars for Opinion, For & Against, Problem-Solution across Web and Mobile.
- **Phase 4: Milestone 3 - Dark Mode Theme Support (R4)**
  - Web: Tailwind dark mode classes / CSS variables with persistence.
  - Mobile: ThemeMode.dark with custom dark AppTheme palette and persistence.
- **Phase 5: Milestone 4 - User Authentication & Account Management UI (R1)**
  - Connect /api/auth/register, /api/auth/login, /api/auth/me on both Web and Mobile.
  - Web: Modal dialogs, session header state, token persistence.
  - Mobile: Login/Register screens or bottom sheets, token storage (SharedPreferences / secure storage), session restoration, university/progress sync.
- **Phase 6: Milestone 5 - Global Verification & Quality Hardening**
  - Run flutter analyze (0 errors, 0 warnings).
  - Run flutter test (100% pass).
  - Run flutter build apk --debug (exit code 0).
  - Verify clean git commit.
  - Forensic integrity audit & final report to parent.
