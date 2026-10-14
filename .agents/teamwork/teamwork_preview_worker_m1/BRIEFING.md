# BRIEFING — 2026-10-14T10:18:00Z

## Mission
Implement Milestone 1: Academic Listening Expansion & Sync (F1, F2). Expand listening dataset from 4 to 8 tracks, enforce 100% byte parity between canonical and mobile assets, and enhance integrity and unit test suites.

## 🔒 My Identity
- Archetype: worker
- Roles: implementer, qa, specialist
- Working directory: C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_worker_m1
- Original parent: d4d0cbdf-16eb-4100-bcd6-7f1e5ca40628
- Milestone: Milestone 1 - Academic Listening Expansion & Sync

## 🔒 Key Constraints
- Exclusive write ownership:
  - C:\Projeler\PrepMaster\data\listening.json
  - C:\Projeler\PrepMaster\mobile\assets\data\listening.json
  - C:\Projeler\PrepMaster\mobile\test\dataset_integrity_test.dart
  - C:\Projeler\PrepMaster\mobile\test\listening_writing_test.dart
- Do not modify any other files in the project.
- No shortcuts or fake data: All 4 new tracks must be genuine, academic-grade, with 13 fields and valid MCQs.
- 100% byte parity between data/listening.json and mobile/assets/data/listening.json.
- flutter analyze must report 0 issues; flutter test must pass 100%.

## Current Parent
- Conversation ID: d4d0cbdf-16eb-4100-bcd6-7f1e5ca40628
- Updated: not yet

## Task Summary
- **What to build**: Merge 4 new tracks (lis_buept_02, lis_bilkent_02, lis_odtu_02, lis_itu_02) into listening.json; synchronize mobile/assets/data/listening.json; update dataset_integrity_test.dart to validate 8 tracks with all 13 fields and byte parity; update listening_writing_test.dart to test 13 fields, defaults, and ApiService offline filtering.
- **Success criteria**: 8 tracks parsed, all 13 fields valid, 100% test pass, flutter analyze clean, SHA-256 match.
- **Interface contracts**: PROJECT.md § 1. Academic Listening Contract
- **Code layout**: PROJECT.md § Code Layout

## Change Tracker
- **Files modified**:
  - [TBD] data/listening.json
  - [TBD] mobile/assets/data/listening.json
  - [TBD] mobile/test/dataset_integrity_test.dart
  - [TBD] mobile/test/listening_writing_test.dart
- **Build status**: pending
- **Pending issues**: none

## Quality Status
- **Build/test result**: pending
- **Lint status**: pending
- **Tests added/modified**: pending

## Loaded Skills
- None specified in dispatch.

## Key Decisions Made
- Use exact JSON specs authored by Explorer 1 and Explorer 2.
- Update tests per Explorer 3 specifications.
- Verify byte parity using SHA-256 and git diff.

## Artifact Index
- handoff.md — Final implementation and verification report
- progress.md — Real-time progress and liveness heartbeat
