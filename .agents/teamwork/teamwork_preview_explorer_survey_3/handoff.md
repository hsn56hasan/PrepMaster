# Handoff Report: Data Assets, Dual-Platform Parity & Test Infrastructure

**Agent**: Explorer 3 (Data & QA Explorer)  
**Date**: 2026-10-14T10:05:00Z  
**Working Directory**: `C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_survey_3`  
**Target Milestone**: Survey & Discovery Phase  

---

## 1. Observation

### 1.1 Academic Listening Datasets & Parity (R3)
- **File Locations**:
  - `C:\Projeler\PrepMaster\data\listening.json` (22,128 bytes, 268 lines)
  - `C:\Projeler\PrepMaster\mobile\assets\data\listening.json` (22,128 bytes, 268 lines)
- **Parity Status**:
  - Direct binary verification via Python (`filecmp.cmp('data/listening.json', 'mobile/assets/data/listening.json')`) confirmed `True`.
  - All 6 datasets in `data/` and `mobile/assets/data/` (`listening.json`, `questions.json`, `speaking.json`, `universities.json`, `vocabulary.json`, `writing_guides.json`) are currently 100% byte-for-byte identical.
- **Existing 4 Listening Tracks Inventory**:
  1. `id`: `"lis_buept_01"` | `university_id`: `"boun"` | `level`: `"C1"` | `type`: `"note_taking"` | `title`: `"The Psychology of Cognitive Biases in Decision Making"` | `questions`: 4 questions (`lis_buept_01_q1` to `q4`).
  2. `id`: `"lis_itu_01"` | `university_id`: `"itu"` | `level`: `"B2"` | `type`: `"while_listening"` | `title`: `"Smart Electrical Grids and Renewable Energy Integration"` | `questions`: 4 questions (`lis_itu_01_q1` to `q4`).
  3. `id`: `"lis_odtu_01"` | `university_id`: `"metu"` | `level`: `"C1"` | `type`: `"note_taking"` | `title`: `"Bioclimatic Urban Architecture and Heat Island Mitigation"` | `questions`: 4 questions (`lis_odtu_01_q1` to `q4`).
  4. `id`: `"lis_bilkent_01"` | `university_id`: `"bilkent"` | `level`: `"B2"` | `type`: `"while_listening"` | `title`: `"The Ethical Implications of Autonomous Medical AI"` | `questions`: 3 questions (`lis_bilkent_01_q1` to `q3`).
- **Data Model Contract (`mobile/lib/models/listening_track.dart`)**:
  - Required fields per track:
    - `id`: String
    - `university_id`: String (`"boun"`, `"itu"`, `"metu"`, `"bilkent"`)
    - `level`: String (`"B2"`, `"C1"`)
    - `type`: String (`"note_taking"` or `"while_listening"`)
    - `title`: String
    - `subtitle`: String
    - `target_university`: String
    - `duration_minutes`: int
    - `lecture_duration_seconds`: int
    - `instructions_tr`: String
    - `audio_script`: String (full transcript for Web Speech API / TTS / reading)
    - `suggested_notes_tr`: List<String> (ideal note-taking guidelines)
    - `questions`: List of objects:
      - `id`: String
      - `question`: String
      - `options`: List of `{"key": "A"|"B"|"C"|"D", "text": "..."}`
      - `correct_answer`: String (`"A"|"B"|"C"|"D"`)
      - `explanation_tr`: String (Turkish rationale)
- **Web Listening Implementation (`static/js/listening.js`)**:
  - Dynamically fetches `/api/listening` from FastAPI backend (`backend/app.py` lines 245-260).
  - Uses `t.type` to toggle between note-taking mode (hiding questions until lecture completes) and while-listening mode.
  - Generates speech synthesis directly from `audio_script` with speed controls and digital notepad.
- **Mobile Listening Implementation (`mobile/lib/screens/listening_screen.dart`, `mobile/lib/services/api_service.dart`)**:
  - `ApiService().getListeningTracks()` tries `$baseUrl/api/listening` (timeout 3s) and falls back seamlessly to `rootBundle.loadString('assets/data/listening.json')`.
- **Test Infrastructure Risk in `mobile/test/dataset_integrity_test.dart`**:
  - Line 9: `group('Dataset Integrity Tests for 105 Questions, 110 Vocab, 4 Listening', ...)`
  - Line 49: `test('Listening JSON loads and parses all 4 tracks with questions', () {`
  - Line 56: `expect(jsonList.length, 4);`
  - When expanding from 4 to 8 tracks, line 56 will directly fail the test suite unless updated to `expect(jsonList.length, 8);` or `expect(jsonList.length, greaterThanOrEqualTo(8));`.

---

### 1.2 Essay & Writing Datasets & Exemplar Library (R2)
- **Current State of `data/writing_guides.json`**:
  - Contains only 2 guides:
    1. `"opinion-essay"`: Opinion Essay (Fikir Belirtme Kompozisyonu)
    2. `"cause-effect-essay"`: Cause & Effect Essay (Neden - Sonuç Kompozisyonu)
  - Missing types explicitly required by R2:
    - `"for-against-essay"`: For & Against / Discussion Essay
    - `"problem-solution-essay"`: Problem - Solution Essay
  - Missing content: No actual model essays, no Band 85+ student exemplars, no annotated thesis statements, no annotated topic sentences, no CEFR rubric breakdown, and no common pitfall analyses.
- **Consumption in Web (`static/js/app.js` lines 290-340)**:
  - Fetches `/api/writing-guides` and renders structure elements, transitions, and sample topics.
  - `static/js/writing_ai.js` provides AI essay evaluation against criteria (`Task Achievement`, `Coherence & Cohesion`, `Lexical Resource`, `Grammatical Range`).
- **Consumption in Mobile (`mobile/lib/screens/writing_screen.dart`)**:
  - Has 2 tabs:
    - Tab 1: AI Essay Puanlama (`_buildAIEvaluatorTab`)
    - Tab 2: Rehber & Şablonlar (`_buildGuidesTab` using `mobile/lib/models/writing_guide.dart`)
  - No exemplar display or pitfall comparison UI currently exists in either tab.
- **Offline Availability Architecture**:
  - `mobile/pubspec.yaml` lines 62-63 defines:
    ```yaml
    assets:
      - assets/data/
    ```
    Any file placed in `mobile/assets/data/` is automatically bundled into the APK assets.
  - In `mobile/lib/services/api_service.dart`, `getWritingGuides()` already falls back to `rootBundle.loadString('assets/data/writing_guides.json')`.
  - For Web, files are served statically or via FastAPI `/api/writing-guides` (and/or `/api/writing-exemplars`).

---

### 1.3 Git Status, Repository Hygiene & Build Infrastructure
- **Git Status**:
  - Branch: `master`
  - Working tree: Clean (`nothing added to commit but untracked files present`)
  - Untracked files: Only `.agents/` (agent metadata)
- **Recent Git Log**:
  - `7ac43d4` feat: expand question pool to 105 questions and vocabulary to 110 cards across all CEFR levels
  - `933db21` feat: complete multi-user DB, student verification, cloud sync, mock exam mode, and printable PDF report
  - `ec2af49` feat: complete deficiency 2 - add Speaking & Interview Simulator on Web and Native Mobile
  - `e56a231` fix(web): resolve syntax error in app.js, export window functions, and add cache busting
  - `f2a8558` chore: update Wi-Fi local network IP to 10.247.49.48 in run.bat and api_service
- **Verification Commands & Tooling Results**:
  1. `flutter --version`: Flutter 3.47.6 (channel stable), Dart 3.13.5
  2. `flutter doctor`: All checkmarks passed ([√] Flutter, [√] Windows, [√] Android toolchain SDK 36.0.0, [√] Chrome, [√] Visual Studio 2026, [√] 3 Connected devices). No issues found.
  3. `flutter analyze`: `No issues found! (ran in 37.1s)` — 0 errors, 0 warnings.
  4. `flutter test`: `All tests passed!` — 8/8 tests passed in 4s.
  5. `flutter build apk --debug`: `√ Built build\app\outputs\flutter-apk\app-debug.apk` in 13.2s with exit code 0.
  6. Backend Python check: `python -c "import backend.app; print('Backend imports cleanly')"` returned exit code 0.

---

## 2. Logic Chain

1. **Academic Listening Track Expansion (4 → 8 Tracks)**:
   - *Observation 1.1*: The current listening dataset has 4 tracks covering `boun` (`lis_buept_01`), `itu` (`lis_itu_01`), `metu` (`lis_odtu_01`), and `bilkent` (`lis_bilkent_01`).
   - *Observation 1.1*: The R3 requirement demands 4 new university-specific tracks (covering Boğaziçi, ODTÜ, İTÜ, Bilkent) with note-taking guidelines, transcripts, and multiple-choice questions.
   - *Deduction*: The new tracks must be structured as:
     - `lis_buept_02` (`boun`): C1 Note-Taking (e.g., *Epigenetics and Environmental Gene Regulation* or *Linguistic Relativity & Cognitive Framing*), 4 MCQs, note guidelines, audio script.
     - `lis_itu_02` (`itu`): B2/C1 While-Listening (e.g., *Autonomous Electric Transportation & Urban Micro-Grids* or *Quantum Computing in Cryptography*), 4 MCQs, note guidelines, audio script.
     - `lis_odtu_02` (`metu`): C1 Note-Taking (e.g., *Circular Economy in Industrial Ecology & Waste valorization*), 4 MCQs, note guidelines, audio script.
     - `lis_bilkent_02` (`bilkent`): B2/C1 While-Listening (e.g., *Behavioral Economics: Nudge Theory and Public Policy*), 4 MCQs, note guidelines, audio script.
   - *Observation 1.1*: `mobile/test/dataset_integrity_test.dart` line 56 tests `expect(jsonList.length, 4);`.
   - *Deduction*: When adding the 4 tracks, modifying `data/listening.json` without copying to `mobile/assets/data/listening.json` breaks dual-platform parity. Modifying both without updating `dataset_integrity_test.dart` breaks the test suite. Therefore, track additions must synchronize both JSON files and update the test assertion to 8 tracks.

2. **Writing Exemplar Library Schema & Dual-Platform Architecture**:
   - *Observation 1.2*: `data/writing_guides.json` only contains basic structure templates for `opinion-essay` and `cause-effect-essay`.
   - *Observation 1.2*: R2 explicitly requires Opinion, For & Against, and Problem-Solution essay types with Band 85+ exemplars, annotated thesis, topic sentences, CEFR breakdown, and common pitfall analyses.
   - *Deduction*: The data structure can either extend `writing_guides.json` or introduce `writing_exemplars.json` (synchronized across `data/` and `mobile/assets/data/`). Extending `writing_guides.json` with an `exemplar` or `exemplars` property and adding the 2 missing guides (`for-against-essay` and `problem-solution-essay`) is backwards-compatible with existing models (`mobile/lib/models/writing_guide.dart`) and Web/Mobile fetch endpoints (`/api/writing-guides`). Alternatively, adding a dedicated `data/writing_exemplars.json` with its own model gives maximum modularity and rich UI presentation. The cleanest approach is:
     1. Add the missing essay guides (`for-against-essay`, `problem-solution-essay`) to `writing_guides.json`.
     2. Create `data/writing_exemplars.json` (and sync to `mobile/assets/data/writing_exemplars.json`) containing complete Band 85+ exemplars with full text, paragraph-by-paragraph annotations (thesis, topic sentences), CEFR 4-criteria rubric breakdown, and common pitfall analyses.
     3. Expose `/api/writing-exemplars` in `backend/app.py`.
     4. Render an interactive "Band 85+ Model Essay Library" tab/card in both Flutter (`mobile/lib/screens/writing_screen.dart`) and Web (`static/index.html` + `static/js/app.js`).

3. **Repository Health & Build Reproducibility**:
   - *Observation 1.3*: `flutter analyze`, `flutter test`, and `flutter build apk --debug` all execute cleanly with exit code 0.
   - *Deduction*: The repository is in an exemplary state. No broken dependencies or regression blockers exist. All subsequent edits by implementers must adhere strictly to these green baselines.

---

## 3. Caveats

- **No Caveats** regarding tool accessibility: `flutter`, `dart`, `python`, `git`, and Android SDK 36.0.0 are all functioning on the host.
- **Audio Assets**: The listening engine utilizes the Web Speech API and Flutter speech synthesis dynamically based on the text `audio_script` field. There are no static `.mp3` files in the repository; audio is generated in real-time. The new tracks must therefore provide rich, phonetically clean, natural-sounding academic English text in `audio_script`.
- **Test Integrity Scope**: `mobile/test/dataset_integrity_test.dart` specifically validates questions count (105), vocabulary count (110), and listening tracks count (4). It currently does not validate `writing_guides.json`. Adding a test for writing guides/exemplars in `dataset_integrity_test.dart` or `listening_writing_test.dart` is recommended.

---

## 4. Conclusion

1. **Parity Assessment**: Current datasets in `data/` and `mobile/assets/data/` are 100% in parity. The project has established a strong standard of identical copies between Web data root and Mobile asset bundle.
2. **Academic Listening Expansion (R3)**:
   - 4 new tracks (`lis_buept_02`, `lis_itu_02`, `lis_odtu_02`, `lis_bilkent_02`) must be added to both `data/listening.json` and `mobile/assets/data/listening.json`.
   - `mobile/test/dataset_integrity_test.dart` line 56 must be changed from `expect(jsonList.length, 4);` to `expect(jsonList.length, 8);`.
   - Each track must adhere to the 13 required fields in `ListeningTrack.fromJson`.
3. **Writing Exemplar Library (R2)**:
   - Complete guides for `for-against-essay` and `problem-solution-essay` must be added to `writing_guides.json`.
   - A dedicated or embedded dataset for Band 85+ exemplars must be established with explicit fields:
     - `essay_type` (`"opinion"`, `"for_against"`, `"problem_solution"`)
     - `target_university` (`"Boğaziçi"`, `"İTÜ"`, `"ODTÜ"`, `"Bilkent"`)
     - `band_score` (e.g. 88, 92, 90)
     - `annotated_sections`: Paragraphs with highlighted `thesis_statement` and `topic_sentences`
     - `cefr_rubric`: Task Achievement, Coherence & Cohesion, Lexical Resource, Grammatical Range
     - `common_pitfalls`: Comparison between typical Band 60 mistakes vs Band 85+ execution
   - Offline availability is guaranteed by placing the dataset in `mobile/assets/data/` (already registered in `pubspec.yaml`).
4. **Build & Quality Gates**:
   - Flutter and Android SDK are in 100% working order. All test runs and APK builds succeed cleanly.

---

## 5. Verification Method

To independently verify all findings in this report, execute the following commands in order:

```powershell
# 1. Verify Dataset Parity across all 6 data files (must all return True)
python -c "import os, filecmp; [print(f, filecmp.cmp('data/'+f, 'mobile/assets/data/'+f)) for f in os.listdir('data')]"

# 2. Inspect hardcoded track count in dataset integrity test
Select-String -Path "mobile\test\dataset_integrity_test.dart" -Pattern "jsonList.length"

# 3. Run Flutter test suite (should report 8/8 passed)
cd mobile
flutter test

# 4. Run Flutter analyzer (should report No issues found)
flutter analyze

# 5. Build Debug APK (should build app-debug.apk with exit code 0)
flutter build apk --debug
cd ..

# 6. Verify Python backend imports cleanly
python -c "import backend.app; print('Backend imports cleanly')"

# 7. Check Git status (should show clean master branch, only .agents untracked)
git status
```

### Invalidation Conditions:
- If `mobile/assets/data/listening.json` differs in hash or byte count from `data/listening.json`.
- If `flutter test` fails on `expect(jsonList.length, 4)` after expanding to 8 tracks without updating the test.
- If writing exemplars are added to Web but not included in `mobile/assets/data/` (breaking Flutter offline mode).
