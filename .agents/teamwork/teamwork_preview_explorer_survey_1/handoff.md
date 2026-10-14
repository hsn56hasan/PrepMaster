# Mobile Codebase Survey & Gap Analysis Report (Explorer 1)

## 1. Observation

### Architecture, Dependencies & App Entry
- **Project Structure**: Flutter mobile app located at `C:\Projeler\PrepMaster\mobile`.
  - Core entry point: `mobile/lib/main.dart`
  - `pubspec.yaml` dependencies:
    ```yaml
    dependencies:
      flutter:
        sdk: flutter
      cupertino_icons: ^1.0.8
      http: ^1.6.0
      shared_preferences: ^2.5.6
    dev_dependencies:
      flutter_test:
        sdk: flutter
      flutter_lints: ^6.0.0
    flutter:
      uses-material-design: true
      assets:
        - assets/data/
    ```
  - `flutter_secure_storage` is not in `pubspec.yaml`. `shared_preferences: ^2.5.6` is present and functional.
- **Entry & Navigation (`mobile/lib/main.dart` lines 10–22)**:
  ```dart
  class PrepMasterApp extends StatelessWidget {
    const PrepMasterApp({super.key});

    @override
    Widget build(BuildContext context) {
      return MaterialApp(
        title: 'PrepMaster',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        home: const HomeNavigation(),
      );
    }
  }
  ```
  `PrepMasterApp` is a `StatelessWidget`. It hardcodes `theme: AppTheme.lightTheme` without `darkTheme` or `themeMode`.
- **Navigation Shell (`mobile/lib/screens/home_navigation.dart` lines 116–169)**:
  - Uses an `IndexedStack` with 7 pages: `DashboardScreen`, `ExamsScreen`, `MistakeVaultScreen`, `FlashcardsScreen`, `PracticeScreen`, `WritingScreen`, `AnalyticsScreen`.
  - `bottomNavigationBar: NavigationBar` with 5 tabs (indices 0..4).
  - Background color is hardcoded to `Colors.white` (`line 128: backgroundColor: Colors.white`).

### Build & Test Health Baseline
- **Static Analysis Command**: `flutter analyze`
  - Verbatim result: `No issues found! (ran in 36.5s)`
  - Exit code: 0 (0 errors, 0 warnings).
- **Test Suite Command**: `flutter test`
  - Verbatim result:
    ```
    00:00 +0: C:/Projeler/PrepMaster/mobile/test/dataset_integrity_test.dart: Questions JSON loads and parses all 105 items
    00:00 +1: C:/Projeler/PrepMaster/mobile/test/dataset_integrity_test.dart: Vocabulary JSON loads and parses all 110 items
    00:00 +2: C:/Projeler/PrepMaster/mobile/test/dataset_integrity_test.dart: Listening JSON loads and parses all 4 tracks
    00:00 +3: C:/Projeler/PrepMaster/mobile/test/listening_writing_test.dart: ListeningTrack fromJson parses correctly
    00:00 +4: C:/Projeler/PrepMaster/mobile/test/listening_writing_test.dart: Offline AI Essay Evaluation produces accurate score
    00:00 +5: C:/Projeler/PrepMaster/mobile/test/listening_writing_test.dart: SpeakingTask parses from JSON and Offline AI Speaking
    00:00 +6: C:/Projeler/PrepMaster/mobile/test/listening_writing_test.dart: Mock Exam generator and Report Summary return valid
    00:00 +7: C:/Projeler/PrepMaster/mobile/test/widget_test.dart: PrepMasterApp smoke test
    00:00 +8: All tests passed!
    ```
  - Exit code: 0 (8/8 tests pass).

### R1. User Authentication & Account Management (Audit Findings)
- **Backend Endpoints (`backend/app.py` lines 122–150)**:
  - `POST /api/auth/register` (receives `RegisterRequest`: `email`, `username`, `password`, `full_name`, `university_id`, `student_number`).
  - `POST /api/auth/login` (receives `LoginRequest`: `identifier`, `password`).
  - `GET /api/auth/me` (receives `user_id: int = 1`).
  - `POST /api/student/verify` and `GET /api/student/status`.
- **Mobile API Service (`mobile/lib/services/api_service.dart`)**:
  - Contains zero authentication endpoints (`login`, `register`, `logout`, `getCurrentUser` are absent).
  - Contains no token or user header injection in HTTP requests (`Authorization` header is never passed).
- **Mobile Sync Service (`mobile/lib/services/sync_service.dart` line 59)**:
  - Hardcodes `'user_id': 1` in `verifyStudent`:
    ```dart
    body: json.encode({
      'user_id': 1,
      'university_id': universityId,
      'edu_email': eduEmail,
      'student_number': studentNumber,
    }),
    ```
  - `pullSync` and `pushSync` do not pass user identity or authentication token.
- **Mobile UI & Session Management**:
  - No `User` model exists under `mobile/lib/models/`.
  - No Login or Register screens / modal bottom sheets exist under `mobile/lib/screens/`.
  - `home_navigation.dart` only restores `'current_level'` and `'current_uni_id'` from `SharedPreferences` in `_initApp()` (lines 35–38). It does not restore user session, token, or auth status.
  - No user profile icon, account bottom sheet, or logout trigger exists in `DashboardScreen`'s `AppBar` (lines 389–409).

### R2. Essay Library & Writing Exemplars (Audit Findings)
- **Dataset (`mobile/assets/data/writing_guides.json` & `data/writing_guides.json`)**:
  - Only contains 2 guide outlines: `"opinion-essay"` and `"cause-effect-essay"`.
  - Does NOT contain Band 85+ annotated student exemplar essays.
  - Lacks required exemplar coverage for "Opinion", "For & Against", and "Problem-Solution" essay types.
  - Lacks annotation metadata: thesis statement, topic sentences, CEFR breakdown (Task Achievement, Cohesion, Lexical, Grammar), and common pitfall analyses.
- **Model (`mobile/lib/models/writing_guide.dart`)**:
  - Model only represents `WritingGuide` with fields `id`, `title`, `description`, `structure`, `keyTransitions`, `sampleTopic`, `bandScoreTip`.
  - No exemplar data model exists (`EssayExemplar`, `ExemplarAnnotation`, or `CefrRubricScore`).
- **UI (`mobile/lib/screens/writing_screen.dart` lines 128–147)**:
  - Has only 2 tabs: `AI Essay Puanlama` and `Rehber & Şablonlar`.
  - No Exemplar Library tab or viewer with annotated essay text rendering (highlighted thesis statements, topic sentences, CEFR scorecards, and pitfall highlights).

### R3. Academic Listening Track Expansion (Audit Findings)
- **Dataset (`mobile/assets/data/listening.json` and `data/listening.json`)**:
  - Currently contains exactly 4 tracks:
    1. `lis_buept_01`: Boğaziçi (`boun`), level C1, type `note_taking` ("The Psychology of Cognitive Biases in Decision Making")
    2. `lis_itu_01`: İTÜ (`itu`), level B2, type `while_listening` ("Smart Electrical Grids and Renewable Energy Integration")
    3. `lis_metu_01`: ODTÜ (`metu`), level B2, type `note_taking` ("Urban Architecture and Climate Adaptation in Megacities")
    4. `lis_bilkent_01`: Bilkent (`bilkent`), level B2, type `while_listening` ("The Ethical Implications of Autonomous Medical AI")
  - Requirement R3 calls for expanding 4 → 8 tracks (adding 4 new university-specific academic listening tracks covering Boğaziçi, ODTÜ, İTÜ, Bilkent) with note-taking guidelines, transcripts, and multiple-choice questions.
  - Current test expectation in `mobile/test/dataset_integrity_test.dart` line 56:
    ```dart
    expect(jsonList.length, 4);
    ```
    This assertion enforces exactly 4 tracks, which will fail when the dataset is expanded to 8 tracks unless updated.

### R4. Dark Mode (Gece Modu) Theme Support (Audit Findings)
- **Theme Definition (`mobile/lib/theme/app_theme.dart` lines 18–65)**:
  - Only provides `static ThemeData get lightTheme`.
  - No `darkTheme` getter exists.
  - No dark color palette defined (e.g., dark background `0xFF0F172A`, dark surface `0xFF1E293B`, dark border `0xFF334155`, dark text `0xFFF8FAFC`).
- **Theme Mode & State Management (`mobile/lib/main.dart`)**:
  - `PrepMasterApp` is a `StatelessWidget`.
  - No `themeMode` is supplied to `MaterialApp`.
  - No `ValueNotifier<ThemeMode>` or theme controller exists to switch themes at runtime.
  - No theme persistence in `SharedPreferences` (e.g. key `theme_mode`).
- **Component Styling**:
  - Grep search revealed over 100 hardcoded `Colors.white` instances across `dashboard_screen.dart`, `analytics_screen.dart`, `writing_screen.dart`, `listening_screen.dart`, `home_navigation.dart`, and `exam_runner_screen.dart`.
  - In dark mode, without semantic theme references (`Theme.of(context).cardColor`, `Theme.of(context).scaffoldBackgroundColor`, etc.), hardcoded `Colors.white` cards and containers would remain glaring white.

---

## 2. Logic Chain

1. **Premise 1 (R1 Auth)**: The backend has active auth endpoints (`/api/auth/register`, `/api/auth/login`, `/api/auth/me`), but the mobile app has no model, no service methods, no UI, and no storage logic.
   - *Direct inference*: A `User` model, an `AuthService` (or auth methods in `ApiService`), local persistence via `SharedPreferences` (token, user ID, user data), automatic session restoration in `_initApp()`, and a Login/Register bottom sheet or screen must be implemented in the mobile app to achieve feature parity with Web.
2. **Premise 2 (R2 Writing)**: The acceptance criteria require "Writing library renders annotated model essays with thesis, topic sentences, and CEFR breakdown" for Opinion, For & Against, and Problem-Solution essay types, accessible offline.
   - *Direct inference*: `writing_guides.json` (in both `data/` and `mobile/assets/data/`) must be expanded to include authentic Band 85+ exemplars with annotations (thesis statement, topic sentences, CEFR breakdown scores, strengths, and pitfall analyses).
   - *Direct inference*: A new model (`EssayExemplar`) and an Exemplar Library tab in `WritingScreen` must be implemented to render color-coded annotations and CEFR breakdowns offline from `assets/data/writing_guides.json`.
3. **Premise 3 (R3 Listening)**: The acceptance criteria require `data/listening.json` to contain at least 8 complete tracks and parse with 100% valid fields in `mobile/test/dataset_integrity_test.dart`.
   - *Direct inference*: 4 new complete tracks (covering Boğaziçi, ODTÜ, İTÜ, Bilkent) must be added with valid fields (`id`, `university_id`, `level`, `type`, `title`, `subtitle`, `target_university`, `duration_minutes`, `lecture_duration_seconds`, `instructions_tr`, `audio_script`, `suggested_notes_tr`, and `questions`).
   - *Direct inference*: Both `data/listening.json` and `mobile/assets/data/listening.json` must remain byte-synchronized.
   - *Direct inference*: `mobile/test/dataset_integrity_test.dart` line 56 must be updated from `expect(jsonList.length, 4);` to `expect(jsonList.length, greaterThanOrEqualTo(8));` (or `8`).
4. **Premise 4 (R4 Dark Mode)**: Requirement R4 states "Implement a persistent Dark/Light theme toggle for Flutter Mobile (ThemeMode.dark with custom dark AppTheme palette)".
   - *Direct inference*: `AppTheme` must declare `darkTheme` alongside `lightTheme` with an accessible dark palette (slate-900 scaffold, slate-800 cards, slate-50 text).
   - *Direct inference*: A stateful `ThemeController` or `ValueNotifier<ThemeMode>` must wrap `MaterialApp` in `main.dart`, initialized from `SharedPreferences` (`'theme_mode'`).
   - *Direct inference*: A toggle button must be placed in `DashboardScreen`'s AppBar (or account sheet) that toggles between light and dark modes and persists the selection.
   - *Direct inference*: Screens must respect `Theme.of(context)` or semantic helpers on `AppTheme` rather than hardcoding static `Colors.white`.
5. **Premise 5 (Build & Tests)**: The current baseline is clean (`flutter analyze` has 0 errors/warnings, `flutter test` passes 8/8 tests).
   - *Direct inference*: Any modifications must preserve zero analyzer warnings and pass all updated unit and widget tests.

---

## 3. Caveats

- **flutter_secure_storage vs shared_preferences**: `flutter_secure_storage` is not in `pubspec.yaml`. `shared_preferences: ^2.5.6` is already installed and proven reliable across all platforms without requiring external platform-specific keystore/keychain native dependencies. For educational proficiency apps, `shared_preferences` is sufficient for JWT/session token storage and offline caching. If strict encryption is desired, `flutter_secure_storage` can be added to `pubspec.yaml`.
- **Audio Playback**: Mobile audio uses simulated timer-based lecture progress with speed chips (0.85x, 1.0x, 1.15x) rather than raw binary MP3 assets in `ListeningRunnerScreen`. This allows full offline academic simulation and note-taking practice without multi-megabyte binary assets.
- **State Management Architecture**: No heavy third-party framework (Riverpod/Bloc) is used in the project; native `ValueNotifier` / `ChangeNotifier` / `StatefulWidget` fits the existing architecture seamlessly without bloating `pubspec.yaml`.

---

## 4. Conclusion & Actionable Blueprint

The Flutter mobile application has a clean, well-structured foundation with 0 static analysis errors and 8 passing tests, but possesses 4 distinct functional gaps against the authoritative request:

### Concrete Implementation Blueprint for Developers:

| Req | Target Files | Specific Action Required |
|---|---|---|
| **R1 (Auth)** | `mobile/lib/models/user.dart`<br>`mobile/lib/services/api_service.dart`<br>`mobile/lib/services/sync_service.dart`<br>`mobile/lib/screens/login_sheet.dart`<br>`mobile/lib/screens/dashboard_screen.dart`<br>`mobile/lib/screens/home_navigation.dart` | 1. Create `User` model (`id`, `email`, `username`, `fullName`, `universityId`, `studentNumber`, `isVerifiedStudent`, `verificationStatus`).<br>2. Add `login()`, `register()`, `getMe()`, `saveSession()`, `restoreSession()`, `logout()` to `ApiService`.<br>3. In `sync_service.dart`, replace hardcoded `user_id: 1` with authenticated `userId`.<br>4. Implement Auth Bottom Sheet (Tabbed Login / Register) with input validation.<br>5. In `dashboard_screen.dart`, add user profile avatar in AppBar displaying user name, verification status badge, and login/logout modal.<br>6. In `home_navigation.dart`, call `restoreSession()` on startup. |
| **R2 (Writing)** | `data/writing_guides.json`<br>`mobile/assets/data/writing_guides.json`<br>`mobile/lib/models/writing_guide.dart`<br>`mobile/lib/screens/writing_screen.dart` | 1. Add authentic Band 85+ exemplars to `writing_guides.json` for **Opinion**, **For & Against**, and **Problem-Solution** essay types with annotated thesis, topic sentences, CEFR breakdown scores, strengths, and pitfall analyses.<br>2. Update `WritingGuide` model with `List<EssayExemplar> exemplars`.<br>3. In `WritingScreen`, add a 3rd Tab ("Band 85+ Örnekler") or subview with category filter chips, expandable essay cards, interactive color-coded annotations (Thesis in Purple, Topic Sentences in Amber/Emerald), CEFR scorecards, and pitfall breakdowns. |
| **R3 (Listening)**| `data/listening.json`<br>`mobile/assets/data/listening.json`<br>`mobile/test/dataset_integrity_test.dart` | 1. Add 4 new university-specific listening tracks (1 Boğaziçi, 1 İTÜ, 1 ODTÜ, 1 Bilkent) with complete `instructions_tr`, `audio_script`, `suggested_notes_tr`, and multiple-choice `questions`. Total tracks: 8.<br>2. Ensure both JSON files are identical.<br>3. Update `mobile/test/dataset_integrity_test.dart` to expect `expect(jsonList.length, greaterThanOrEqualTo(8));`. |
| **R4 (Dark Mode)**| `mobile/lib/theme/app_theme.dart`<br>`mobile/lib/main.dart`<br>`mobile/lib/screens/dashboard_screen.dart`<br>Various screen widgets | 1. Add `darkTheme` and dark palette constants to `AppTheme`.<br>2. Wrap `MaterialApp` in `main.dart` with `ValueNotifier<ThemeMode>` or `ThemeNotifier`, persisting mode to `SharedPreferences` (`'theme_mode'`).<br>3. Add Dark/Light toggle IconButton in `DashboardScreen` AppBar.<br>4. Replace hardcoded `Colors.white` container backgrounds with `Theme.of(context).cardColor` or dynamic `AppTheme.cardColor(context)`. |
| **Build & Tests**| `mobile/test/*`<br>`build_apk.bat` | Run `flutter test`, `flutter analyze`, and verify debug APK compilation. |

---

## 5. Verification Method

To independently verify the mobile codebase status and future implementations:

1. **Verify Static Analysis**:
   ```powershell
   cd C:\Projeler\PrepMaster\mobile
   flutter analyze
   ```
   *Expected*: `No issues found!` (0 errors, 0 warnings).

2. **Verify Test Suite**:
   ```powershell
   cd C:\Projeler\PrepMaster\mobile
   flutter test
   ```
   *Expected*: All tests pass (including `dataset_integrity_test.dart`, `listening_writing_test.dart`, `widget_test.dart`).

3. **Verify Asset Synchronization**:
   ```powershell
   # In PowerShell, compare file hashes of listening.json and writing_guides.json
   Get-FileHash C:\Projeler\PrepMaster\data\listening.json
   Get-FileHash C:\Projeler\PrepMaster\mobile\assets\data\listening.json
   Get-FileHash C:\Projeler\PrepMaster\data\writing_guides.json
   Get-FileHash C:\Projeler\PrepMaster\mobile\assets\data\writing_guides.json
   ```
   *Expected*: Hash algorithm outputs must match identically.

4. **Verify Debug APK Build**:
   ```powershell
   cd C:\Projeler\PrepMaster\mobile
   flutter build apk --debug
   ```
   *Expected*: Exit code 0, generating `build\app\outputs\flutter-apk\app-debug.apk`.

5. **Invalidation Conditions**:
   - Any test failure in `flutter test`.
   - Lint error or warning in `flutter analyze`.
   - Discrepancy between `data/*.json` and `mobile/assets/data/*.json`.
   - Failure to persist or restore theme mode or auth token across app restarts.
