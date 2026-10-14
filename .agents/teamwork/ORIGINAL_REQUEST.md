# Original User Request

## 2026-10-14T09:54:56Z

Requested team: Full multi-agent team for dual-platform development (Web + Native Flutter)

Complete all remaining functional and content gaps in the PrepMaster English proficiency preparation platform across both the Web Portal and Native Flutter Mobile application with 100% feature parity.

Working directory: C:\Projeler\PrepMaster
Integrity mode: development

## Requirements

### R1. User Authentication & Account Management UI (Web & Mobile)
- Connect existing backend authentication endpoints (/api/auth/register, /api/auth/login, /api/auth/me) to the user interfaces.
- Web: Implement responsive Login / Register modals and dynamic session state in the header (displaying user name, verification badge, and logout action).
- Mobile: Implement Login and Register screens/bottom sheets with persistent local token storage and automatic session restoration.

### R2. High-Scoring Essay Library & Writing Exemplars
- Expand the Writing section with an authentic library of annotated student sample essays (Band 85+ exemplars and common pitfall analyses) for Opinion, For & Against, and Problem-Solution essay types.
- Ensure exemplars are accessible both online and offline across Web and Flutter.

### R3. Academic Listening Track Expansion (4 → 8 Tracks)
- Add 4 new university-specific academic listening tracks (covering Boğaziçi, ODTÜ, İTÜ, and Bilkent) with note-taking guidelines, transcripts, and multiple-choice questions.
- Maintain dual-platform asset synchronization between data/listening.json and mobile/assets/data/listening.json.

### R4. Dark Mode (Gece Modu) Theme Support
- Implement a persistent Dark/Light theme toggle for both Web (Tailwind dark classes / CSS variables) and Flutter Mobile (ThemeMode.dark with custom dark AppTheme palette).

## Acceptance Criteria

### Authentication & Multi-User Parity
- [ ] Users can register, log in, and log out with custom credentials on both Web and Mobile.
- [ ] Logged-in user's student status, university, and progress sync seamlessly across devices.

### Content & Parity Verification
- [ ] data/listening.json contains at least 8 complete tracks and parses with 100% valid fields in mobile/test/dataset_integrity_test.dart.
- [ ] Writing library renders annotated model essays with thesis, topic sentences, and CEFR breakdown.

### Code Quality & Build Verification
- [ ] flutter analyze reports 0 errors and 0 warnings.
- [ ] flutter test passes all unit and integration tests (100%).
- [ ] flutter build apk --debug completes with exit code 0.
- [ ] All changes are cleanly committed to Git.
