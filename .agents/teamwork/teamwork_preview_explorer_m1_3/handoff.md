# Handoff Report: Milestone 1 - Explorer 3 (Listening Test & Parity Strategy)

**Author**: Explorer 3 (`teamwork_preview_explorer_m1_3`)  
**Parent / Orchestrator**: `d4d0cbdf-16eb-4100-bcd6-7f1e5ca40628`  
**Date**: 2026-10-14  
**Type**: Hard Handoff (Investigation & Test Specification Complete)  

---

## 1. Observation

### 1.1 Existing Test Suite Baseline
Execution of `flutter test` from `C:\Projeler\PrepMaster\mobile` yielded:
```
00:00 +0: loading C:/Projeler/PrepMaster/mobile/test/dataset_integrity_test.dart
00:00 +0: C:/Projeler/PrepMaster/mobile/test/dataset_integrity_test.dart: Dataset Integrity Tests for 105 Questions, 110 Vocab, 4 Listening Questions JSON loads and parses all 105 items with valid fields
00:00 +1: C:/Projeler/PrepMaster/mobile/test/dataset_integrity_test.dart: Dataset Integrity Tests for 105 Questions, 110 Vocab, 4 Listening Vocabulary JSON loads and parses all 110 items with valid fields
00:00 +2: C:/Projeler/PrepMaster/mobile/test/dataset_integrity_test.dart: Dataset Integrity Tests for 105 Questions, 110 Vocab, 4 Listening Listening JSON loads and parses all 4 tracks with questions
00:00 +3: C:/Projeler/PrepMaster/mobile/test/listening_writing_test.dart: Listening & Writing Evaluation Tests ListeningTrack fromJson parses correctly
00:00 +4: C:/Projeler/PrepMaster/mobile/test/listening_writing_test.dart: Listening & Writing Evaluation Tests Offline AI Essay Evaluation produces accurate score and CEFR
00:00 +5: C:/Projeler/PrepMaster/mobile/test/listening_writing_test.dart: Listening & Writing Evaluation Tests SpeakingTask parses from JSON and Offline AI Speaking Evaluation scores accurately
00:00 +6: C:/Projeler/PrepMaster/mobile/test/listening_writing_test.dart: Listening & Writing Evaluation Tests Mock Exam generator and Report Summary return valid structured payloads
00:00 +7: C:/Projeler/PrepMaster/mobile/test/widget_test.dart: PrepMasterApp smoke test
00:00 +8: All tests passed!
```

### 1.2 `mobile/test/dataset_integrity_test.dart` Hardcoded Limits
In `C:\Projeler\PrepMaster\mobile\test\dataset_integrity_test.dart`:
- **Line 9**: `group('Dataset Integrity Tests for 105 Questions, 110 Vocab, 4 Listening', () {`
- **Line 49**: `test('Listening JSON loads and parses all 4 tracks with questions', () {`
- **Line 56**: `expect(jsonList.length, 4);`
- **Lines 58–65**:
  ```dart
  for (var i = 0; i < jsonList.length; i++) {
    final item = jsonList[i];
    final track = ListeningTrack.fromJson(item);
    expect(track.id.isNotEmpty, isTrue, reason: 'Track $i missing id');
    expect(track.title.isNotEmpty, isTrue, reason: 'Track $i missing title');
    expect(track.audioScript.isNotEmpty, isTrue, reason: 'Track $i missing audio script');
    expect(track.questions.length, greaterThan(0), reason: 'Track $i has no questions');
  }
  ```
The existing test only asserts 4 superficial fields (`id`, `title`, `audioScript`, `questions.length > 0`). It does not validate:
1. `university_id` membership (`boun`, `itu`, `metu`, `bilkent`)
2. `level` membership (`B1`, `B2`, `C1`, `C2`)
3. `type` membership (`note_taking`, `while_listening`)
4. Presence of `subtitle`, `target_university`, `duration_minutes`, `lecture_duration_seconds`, `instructions_tr`, `suggested_notes_tr`
5. Integrity of `questions`: question text, option counts (A, B, C, D), correct answer match within options, non-empty Turkish explanations
6. Uniqueness of track IDs and question IDs across the entire dataset
7. Equal representation across universities (2 tracks each) and formats (4 note-taking, 4 while-listening)
8. Dual-platform asset synchronization between `data/listening.json` and `mobile/assets/data/listening.json`.

### 1.3 `mobile/test/listening_writing_test.dart` Coverage Gap
In `C:\Projeler\PrepMaster\mobile\test\listening_writing_test.dart` (lines 8–41):
- `ListeningTrack fromJson parses correctly` uses an artificial mock JSON map and only asserts `track.id`, `track.type`, `track.questions.length`, and `track.questions.first.correctAnswer`.
- It does not assert all 13 model properties (`universityId`, `level`, `title`, `subtitle`, `targetUniversity`, `durationMinutes`, `lectureDurationSeconds`, `instructionsTr`, `audioScript`, `suggestedNotesTr`).
- It does not test fallback default values when optional JSON keys are absent.
- It does not test offline filtering behavior of `ApiService().getListeningTracks()`.

### 1.4 Baseline Parity Check of Canonical Datasets
Running `Get-FileHash` across both files produced identical SHA-256 hashes:
```
Algorithm : SHA256
Hash      : 99D6A9A7867CE3488C6E608AAE6556405BA821337E01A91D7E7D1A6FB97A88C7
Path      : C:\Projeler\PrepMaster\data\listening.json

Algorithm : SHA256
Hash      : 99D6A9A7867CE3488C6E608AAE6556405BA821337E01A91D7E7D1A6FB97A88C7
Path      : C:\Projeler\PrepMaster\mobile\assets\data\listening.json
```

### 1.5 Synthesized 8-Track Inventory
Combining existing tracks with the specifications delivered by Explorer 1 (`.agents/teamwork/teamwork_preview_explorer_m1_1/handoff.md`) and Explorer 2 (`.agents/teamwork/teamwork_preview_explorer_m1_2/validate_tracks.py`):
| # | Track ID | University | Level | Type | Title | Questions | Source |
|---|----------|------------|-------|------|-------|-----------|--------|
| 1 | `lis_buept_01` | `boun` | C1 | `note_taking` | The Psychology of Cognitive Biases in Decision Making | 4 | Existing |
| 2 | `lis_itu_01` | `itu` | B2 | `while_listening` | Smart Electrical Grids and Renewable Energy Integration | 4 | Existing |
| 3 | `lis_odtu_01` | `metu` | C1 | `note_taking` | Bioclimatic Urban Architecture and Heat Island Mitigation | 4 | Existing |
| 4 | `lis_bilkent_01` | `bilkent` | B2 | `while_listening` | The Ethical Implications of Autonomous Medical AI | 3 | Existing |
| 5 | `lis_buept_02` | `boun` | C1 | `note_taking` | Epigenetics, Neuroplasticity, and Cognitive Aging | 4 | Explorer 1 |
| 6 | `lis_bilkent_02` | `bilkent` | B2 | `while_listening` | Behavioral Economics and Choice Architecture in Public Policy | 4 | Explorer 1 |
| 7 | `lis_odtu_02` | `metu` | C1 | `note_taking` | Circular Economy and Industrial Symbiosis in Resource-Constrained Economies | 4 | Explorer 2 |
| 8 | `lis_itu_02` | `itu` | B2 | `while_listening` | Composite Materials and Structural Health Monitoring in Aerospace Engineering | 4 | Explorer 2 |

**Totals**: Exactly 8 tracks, 31 total MCQs, 2 tracks per university (`boun`: 2, `itu`: 2, `metu`: 2, `bilkent`: 2), 4 `note_taking` (C1) and 4 `while_listening` (B2).

---

## 2. Logic Chain

1. **Immediate Failure upon Expansion**:
   Because `mobile/test/dataset_integrity_test.dart` line 56 specifies `expect(jsonList.length, 4);`, the moment Explorer 1 and Explorer 2's new tracks are merged into `listening.json`, `flutter test` will fail with `Expected: 4, Actual: 8`. Updating this line to `expect(jsonList.length, 8);` is mandatory.

2. **Semantic Description Synchronization**:
   To prevent confusing test output, the group title on line 9 and test title on line 49 must reflect `8 Listening Tracks` instead of `4 Listening`.

3. **Protection Against UI/Runtime Crashes**:
   In `mobile/lib/screens/listening_screen.dart` and `static/js/listening.js`, the UI relies on fields like `track.type`, `track.targetUniversity`, `track.lectureDurationSeconds`, and `track.suggestedNotesTr`. If any track lacks these fields, the app encounters `Null check operator used on a null value` or unhandled JSON key errors. Deep assertions across all 13 fields are required.

4. **Handling Question Count Asymmetry (`lis_bilkent_01`)**:
   Existing track `lis_bilkent_01` has 3 questions (`lis_bilkent_01_q1`, `q2`, `q3`), whereas all other 7 tracks have 4 questions. Therefore, the general track question count assertion must be `expect(track.questions.length, greaterThanOrEqualTo(3));`, or each track's expected question count must be verified. For the 4 new tracks (`lis_buept_02`, `lis_bilkent_02`, `lis_odtu_02`, `lis_itu_02`), they each have exactly 4 questions.

5. **Option Keys and Correct Answer Consistency**:
   Academic proficiency exams (BUEPT, EPE, İYS, COPE) standardly utilize 4 multiple-choice options: A, B, C, D. Every question must have options with keys `{'A', 'B', 'C', 'D'}` and `question.correctAnswer` must belong to that set.

6. **Dual-Platform Asset Parity Enforcement**:
   PrepMaster requires Web (served from `data/listening.json`) and Native Mobile (bundled from `mobile/assets/data/listening.json`) to have identical content. Integrating a direct byte comparison test in Dart ensures that any developer or CI run will flag any divergence between the two JSON files immediately.

---

## 3. Caveats

1. **Question Count Variance**:
   `lis_bilkent_01` has 3 questions, while all other tracks have 4 questions (31 questions total). The test suite must not assert `expect(track.questions.length, 4)` globally, as that would fail on track 4. It should assert `greaterThanOrEqualTo(3)` for all tracks, and `== 4` for the new tracks.
2. **Execution Directory for Relative Paths**:
   `flutter test` is executed with working directory `C:\Projeler\PrepMaster\mobile`. Therefore:
   - `File('assets/data/listening.json')` targets the mobile asset.
   - `File('../data/listening.json')` targets the root backend asset.
   In standalone mobile CI environments where `../data` might not be cloned, the parity test should verify `rootFile.existsSync()` before comparing bytes, maintaining portability without failing isolated mobile builds.
3. **Read-Only Scope**:
   Explorer 3 did not modify source or test files directly; the code below represents the definitive specification for the implementer agent.

---

## 4. Conclusion & Test Specification

### 4.1 Specification for `mobile/test/dataset_integrity_test.dart`

#### Target File: `C:\Projeler\PrepMaster\mobile\test\dataset_integrity_test.dart`

#### Contiguous Code Replacement (Lines 49–67):
Replace the existing test `test('Listening JSON loads and parses all 4 tracks with questions', ...)` with the following robust test implementation and add the dual-platform parity test:

```dart
    test('Listening JSON loads and parses all 8 tracks with valid fields and questions', () {
      final file = File('assets/data/listening.json');
      expect(file.existsSync(), isTrue, reason: 'assets/data/listening.json does not exist');

      final jsonStr = file.readAsStringSync();
      final List<dynamic> jsonList = jsonDecode(jsonStr);

      // 1. Exact track count assertion
      expect(jsonList.length, 8, reason: 'Expected exactly 8 academic listening tracks');

      const validUniversities = {'boun', 'itu', 'metu', 'bilkent'};
      const validLevels = {'B1', 'B2', 'C1', 'C2'};
      const validTypes = {'note_taking', 'while_listening'};

      final trackIds = <String>{};
      final uniTrackCounts = <String, int>{};
      final allQuestionIds = <String>{};

      for (var i = 0; i < jsonList.length; i++) {
        final item = jsonList[i] as Map<String, dynamic>;
        final track = ListeningTrack.fromJson(item);

        // Track Identity & Metadata
        expect(track.id.isNotEmpty, isTrue, reason: 'Track $i missing id');
        expect(trackIds.add(track.id), isTrue, reason: 'Duplicate track id: ${track.id}');

        expect(validUniversities.contains(track.universityId), isTrue,
            reason: 'Track ${track.id} has invalid university_id: ${track.universityId}');
        uniTrackCounts[track.universityId] = (uniTrackCounts[track.universityId] ?? 0) + 1;

        expect(validLevels.contains(track.level), isTrue,
            reason: 'Track ${track.id} has invalid level: ${track.level}');
        expect(validTypes.contains(track.type), isTrue,
            reason: 'Track ${track.id} has invalid type: ${track.type}');

        expect(track.title.isNotEmpty, isTrue, reason: 'Track ${track.id} missing title');
        expect(track.subtitle.isNotEmpty, isTrue, reason: 'Track ${track.id} missing subtitle');
        expect(track.targetUniversity.isNotEmpty, isTrue, reason: 'Track ${track.id} missing target_university');
        expect(track.durationMinutes, greaterThan(0), reason: 'Track ${track.id} invalid duration_minutes');
        expect(track.lectureDurationSeconds, greaterThan(0), reason: 'Track ${track.id} invalid lecture_duration_seconds');
        expect(track.instructionsTr.isNotEmpty, isTrue, reason: 'Track ${track.id} missing instructions_tr');
        expect(track.audioScript.isNotEmpty, isTrue, reason: 'Track ${track.id} missing audio_script');
        expect(track.audioScript.split(' ').length, greaterThanOrEqualTo(50),
            reason: 'Track ${track.id} audio_script too short');

        // Note-taking guidelines
        expect(track.suggestedNotesTr.isNotEmpty, isTrue,
            reason: 'Track ${track.id} missing suggested_notes_tr');
        for (var n = 0; n < track.suggestedNotesTr.length; n++) {
          expect(track.suggestedNotesTr[n].trim().isNotEmpty, isTrue,
              reason: 'Track ${track.id} note $n is empty');
        }

        // Questions validation (each track has >= 3 questions, new tracks have 4)
        expect(track.questions.length, greaterThanOrEqualTo(3),
            reason: 'Track ${track.id} has fewer than 3 questions');

        for (var q = 0; q < track.questions.length; q++) {
          final question = track.questions[q];
          expect(question.id.isNotEmpty, isTrue,
              reason: 'Track ${track.id} question $q missing id');
          expect(allQuestionIds.add(question.id), isTrue,
              reason: 'Duplicate question ID detected: ${question.id}');
          expect(question.question.isNotEmpty, isTrue,
              reason: 'Question ${question.id} missing question text');

          // Options validation (minimum 4 options A, B, C, D for academic MCQs)
          expect(question.options.length, greaterThanOrEqualTo(4),
              reason: 'Question ${question.id} has fewer than 4 options');

          final optionKeys = question.options.map((o) => o.key).toSet();
          expect(optionKeys.containsAll(['A', 'B', 'C', 'D']), isTrue,
              reason: 'Question ${question.id} options must include keys A, B, C, D');

          for (var opt in question.options) {
            expect(opt.key.isNotEmpty, isTrue,
                reason: 'Question ${question.id} has option with empty key');
            expect(opt.text.isNotEmpty, isTrue,
                reason: 'Question ${question.id} option ${opt.key} has empty text');
          }

          // Correct answer key must exist in options
          expect(optionKeys.contains(question.correctAnswer), isTrue,
              reason: 'Question ${question.id} correct_answer ${question.correctAnswer} not found in options');

          // Turkish explanation
          expect(question.explanationTr.isNotEmpty, isTrue,
              reason: 'Question ${question.id} missing explanation_tr');
        }
      }

      // Parity check across 4 universities: exactly 2 tracks per university
      for (var uni in ['boun', 'itu', 'metu', 'bilkent']) {
        expect(uniTrackCounts[uni], 2,
            reason: 'Expected exactly 2 tracks for university $uni, found ${uniTrackCounts[uni]}');
      }

      // Parity check across listening types: exactly 4 note_taking, 4 while_listening
      final noteTakingCount = jsonList.where((t) => t['type'] == 'note_taking').length;
      final whileListeningCount = jsonList.where((t) => t['type'] == 'while_listening').length;
      expect(noteTakingCount, 4, reason: 'Expected 4 note_taking tracks');
      expect(whileListeningCount, 4, reason: 'Expected 4 while_listening tracks');
    });

    test('Listening JSON assets in data/ and mobile/assets/data/ are 100% byte-identical', () {
      final mobileFile = File('assets/data/listening.json');
      final rootFile = File('../data/listening.json');

      expect(mobileFile.existsSync(), isTrue,
          reason: 'mobile/assets/data/listening.json must exist');

      if (rootFile.existsSync()) {
        final mobileBytes = mobileFile.readAsBytesSync();
        final rootBytes = rootFile.readAsBytesSync();
        expect(mobileBytes, equals(rootBytes),
            reason: 'data/listening.json and mobile/assets/data/listening.json must be byte-for-byte identical');
      }
    });
```

#### Line 9 Update:
Update the group description:
```dart
// Before:
  group('Dataset Integrity Tests for 105 Questions, 110 Vocab, 4 Listening', () {
// After:
  group('Dataset Integrity Tests for 105 Questions, 110 Vocab, 8 Listening Tracks', () {
```

---

### 4.2 Specification for `mobile/test/listening_writing_test.dart`

#### Target File: `C:\Projeler\PrepMaster\mobile\test\listening_writing_test.dart`

#### Lines 8–41 Update:
Enhance the unit test to verify all 13 model properties and add fallback default and offline filtering unit tests:

```dart
    test('ListeningTrack fromJson parses correctly with all 13 required fields', () {
      final jsonMap = {
        'id': 'test_lis_1',
        'university_id': 'boun',
        'level': 'C1',
        'type': 'note_taking',
        'title': 'Test Audio',
        'subtitle': 'Subtitle',
        'target_university': 'Boğaziçi',
        'duration_minutes': 15,
        'lecture_duration_seconds': 90,
        'instructions_tr': 'Not alınız',
        'audio_script': 'Hello students',
        'suggested_notes_tr': ['Note 1'],
        'questions': [
          {
            'id': 'q1',
            'question': 'What was said?',
            'options': [
              {'key': 'A', 'text': 'Option A'},
              {'key': 'B', 'text': 'Option B'},
              {'key': 'C', 'text': 'Option C'},
              {'key': 'D', 'text': 'Option D'},
            ],
            'correct_answer': 'A',
            'explanation_tr': 'Açıklama'
          }
        ]
      };

      final track = ListeningTrack.fromJson(jsonMap);
      expect(track.id, 'test_lis_1');
      expect(track.universityId, 'boun');
      expect(track.level, 'C1');
      expect(track.type, 'note_taking');
      expect(track.title, 'Test Audio');
      expect(track.subtitle, 'Subtitle');
      expect(track.targetUniversity, 'Boğaziçi');
      expect(track.durationMinutes, 15);
      expect(track.lectureDurationSeconds, 90);
      expect(track.instructionsTr, 'Not alınız');
      expect(track.audioScript, 'Hello students');
      expect(track.suggestedNotesTr, ['Note 1']);
      expect(track.questions.length, 1);
      expect(track.questions.first.id, 'q1');
      expect(track.questions.first.question, 'What was said?');
      expect(track.questions.first.options.length, 4);
      expect(track.questions.first.options.first.key, 'A');
      expect(track.questions.first.options.first.text, 'Option A');
      expect(track.questions.first.correctAnswer, 'A');
      expect(track.questions.first.explanationTr, 'Açıklama');
    });

    test('ListeningTrack fromJson handles missing optional fields with graceful defaults', () {
      final minimalJson = {
        'id': 'min_1',
        'title': 'Minimal Track',
      };
      final track = ListeningTrack.fromJson(minimalJson);
      expect(track.id, 'min_1');
      expect(track.title, 'Minimal Track');
      expect(track.type, 'while_listening');
      expect(track.durationMinutes, 10);
      expect(track.lectureDurationSeconds, 90);
      expect(track.questions, isEmpty);
      expect(track.suggestedNotesTr, isEmpty);
    });

    test('ApiService getListeningTracks filters 8 tracks correctly in offline mode', () async {
      TestWidgetsFlutterBinding.ensureInitialized();
      final allTracks = await ApiService().getListeningTracks();
      expect(allTracks.length, greaterThanOrEqualTo(8));

      final bounTracks = await ApiService().getListeningTracks(universityId: 'boun');
      expect(bounTracks.length, 2);
      expect(bounTracks.every((t) => t.universityId == 'boun'), isTrue);

      final metuTracks = await ApiService().getListeningTracks(universityId: 'metu');
      expect(metuTracks.length, 2);
      expect(metuTracks.every((t) => t.universityId == 'metu'), isTrue);

      final c1Tracks = await ApiService().getListeningTracks(level: 'C1');
      expect(c1Tracks.length, 4);

      final noteTaking = await ApiService().getListeningTracks(type: 'note_taking');
      expect(noteTaking.length, 4);
    });
```

---

### 4.3 Dual-Platform Parity Verification Protocol

To verify 100% synchronization between Web and Mobile assets, execute the following PowerShell command:

```powershell
$dataPath = "C:\Projeler\PrepMaster\data\listening.json"
$mobilePath = "C:\Projeler\PrepMaster\mobile\assets\data\listening.json"

$hash1 = (Get-FileHash -Path $dataPath -Algorithm SHA256).Hash
$hash2 = (Get-FileHash -Path $mobilePath -Algorithm SHA256).Hash

Write-Host "Canonical Data Hash: $hash1"
Write-Host "Mobile Asset   Hash: $hash2"

if ($hash1 -eq $hash2) {
    Write-Host "SUCCESS: Dual-platform listening assets are 100% IDENTICAL." -ForegroundColor Green
} else {
    Write-Error "PARITY FAILURE: listening.json files do NOT match!"
}
```

Git diff verification:
```powershell
git diff --no-index data/listening.json mobile/assets/data/listening.json
```
(Expected exit code: 0, no output).

---

## 5. Verification Method

### 5.1 Verification Commands
1. **Targeted Dataset Integrity Test**:
   ```powershell
   cd C:\Projeler\PrepMaster\mobile
   flutter test test/dataset_integrity_test.dart
   ```
   *Expected Result*: All tests pass (including 8 tracks and dual-file byte identity check).

2. **Listening & Writing Service Test**:
   ```powershell
   cd C:\Projeler\PrepMaster\mobile
   flutter test test/listening_writing_test.dart
   ```
   *Expected Result*: All 5 unit tests pass.

3. **Complete Mobile Test Suite**:
   ```powershell
   cd C:\Projeler\PrepMaster\mobile
   flutter test
   ```
   *Expected Result*: 100% pass rate across all test files.

4. **Flutter Static Analysis**:
   ```powershell
   cd C:\Projeler\PrepMaster\mobile
   flutter analyze
   ```
   *Expected Result*: `No issues found! (zero errors, zero warnings)`.

### 5.2 Invalidation Conditions
- Any track ID collision or deviation from the 8 prescribed IDs.
- Any track containing fewer than 3 questions (or new tracks containing fewer than 4 questions).
- Any MCQ missing option key `A`, `B`, `C`, or `D`, or having `correct_answer` not matching any option key.
- Mismatch between SHA-256 of `data/listening.json` and `mobile/assets/data/listening.json`.
