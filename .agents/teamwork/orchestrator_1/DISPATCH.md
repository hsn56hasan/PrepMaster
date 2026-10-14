## 2026-10-14T09:55:52Z
Sender: 4b17ee20-fdfd-4572-90c2-8cf3b95d3d6a
Priority: MESSAGE_PRIORITY_HIGH

You are the Project Orchestrator for PrepMaster.
Your working directory is: C:\Projeler\PrepMaster\.agents\teamwork\orchestrator_1
The authoritative user request is recorded in: C:\Projeler\PrepMaster\.agents\teamwork\ORIGINAL_REQUEST.md
Project root is: C:\Projeler\PrepMaster

Your mission:
Complete all remaining functional and content gaps in the PrepMaster English proficiency preparation platform across both the Web Portal and Native Flutter Mobile application with 100% feature parity.
Integrity mode: development.

Key Requirements:
R1. User Authentication & Account Management UI (Web & Mobile)
- Connect existing backend authentication endpoints (/api/auth/register, /api/auth/login, /api/auth/me) to the user interfaces.
- Web: Implement responsive Login / Register modals and dynamic session state in the header (displaying user name, verification badge, and logout action).
- Mobile: Implement Login and Register screens/bottom sheets with persistent local token storage and automatic session restoration.

R2. High-Scoring Essay Library & Writing Exemplars
- Expand the Writing section with an authentic library of annotated student sample essays (Band 85+ exemplars and common pitfall analyses) for Opinion, For & Against, and Problem-Solution essay types.
- Ensure exemplars are accessible both online and offline across Web and Flutter.

R3. Academic Listening Track Expansion (4 -> 8 Tracks)
- Add 4 new university-specific academic listening tracks (covering Boğaziçi, ODTÜ, İTÜ, and Bilkent) with note-taking guidelines, transcripts, and multiple-choice questions.
- Maintain dual-platform asset synchronization between data/listening.json and mobile/assets/data/listening.json.

R4. Dark Mode (Gece Modu) Theme Support
- Implement a persistent Dark/Light theme toggle for both Web (Tailwind dark classes / CSS variables) and Flutter Mobile (ThemeMode.dark with custom dark AppTheme palette).

Acceptance Criteria:
- Authentication & Multi-User Parity:
  * Users can register, log in, and log out with custom credentials on both Web and Mobile.
  * Logged-in user's student status, university, and progress sync seamlessly across devices.
- Content & Parity Verification:
  * data/listening.json contains at least 8 complete tracks and parses with 100% valid fields in mobile/test/dataset_integrity_test.dart.
  * Writing library renders annotated model essays with thesis, topic sentences, and CEFR breakdown.
- Code Quality & Build Verification:
  * flutter analyze reports 0 errors and 0 warnings.
  * flutter test passes all unit and integration tests (100%).
  * flutter build apk --debug completes with exit code 0.
  * All changes are cleanly committed to Git.

Maintain your plan.md, progress.md, and BRIEFING.md in your working directory C:\Projeler\PrepMaster\.agents\teamwork\orchestrator_1.
When finished and all acceptance criteria are met, report completion back to me.
