# Dispatch: Milestone 1 Worker - Academic Listening Expansion & Sync (R3)

## Identity & Context
- Role: Implementation Worker for Milestone 1
- Working directory: C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_worker_m1
- Authoritative Request: C:\Projeler\PrepMaster\.agents\teamwork\ORIGINAL_REQUEST.md
- Scope Document: C:\Projeler\PrepMaster\.agents\teamwork\orchestrator_1\PROJECT.md

## Exclusive Write Ownership
You exclusively own and may modify:
- `C:\Projeler\PrepMaster\data\listening.json`
- `C:\Projeler\PrepMaster\mobile\assets\data\listening.json`
- `C:\Projeler\PrepMaster\mobile\test\dataset_integrity_test.dart`
- `C:\Projeler\PrepMaster\mobile\test\listening_writing_test.dart`

Do NOT modify any other files.

## Source Materials & Exact Specifications
1. Explorer 1 findings (Boğaziçi `lis_buept_02` & Bilkent `lis_bilkent_02` JSON):
   `C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_1\handoff.md`
2. Explorer 2 findings (ODTÜ `lis_odtu_02` & İTÜ `lis_itu_02` JSON):
   `C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_2\handoff.md`
3. Explorer 3 findings (Test specifications & parity verification):
   `C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_3\handoff.md`

## Concrete Tasks
1. **Expand Listening Dataset**:
   - Merge the 4 new tracks (`lis_buept_02`, `lis_bilkent_02`, `lis_odtu_02`, `lis_itu_02`) into `data/listening.json` so that it contains all 8 complete tracks.
   - Synchronize `mobile/assets/data/listening.json` so it is 100% byte-for-byte identical to `data/listening.json`.
2. **Update Dataset Integrity Tests**:
   - In `mobile/test/dataset_integrity_test.dart`, update lines 9 and 49-67 per Explorer 3's specification to assert 8 tracks, deep 13-field validations, options completeness, and dual-platform asset parity.
3. **Enhance Listening Unit Tests**:
   - In `mobile/test/listening_writing_test.dart`, update the unit test to verify all 13 fields and offline filtering per Explorer 3's specification.
4. **Build & Test Verification**:
   - Run `flutter analyze` in `mobile/` (verify 0 errors, 0 warnings).
   - Run `flutter test` in `mobile/` (verify 100% pass rate).
   - Run PowerShell file hash comparison to prove `data/listening.json` and `mobile/assets/data/listening.json` are identical.

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Deliverable
Write your comprehensive implementation and verification report to:
`C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_worker_m1\handoff.md`
Report back via `send_message`.
