# Dispatch: Survey 3 - Data Assets, Dual-Platform Parity & Test Infrastructure

## Identity & Context
- Role: Data & QA Explorer
- Working directory: C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_survey_3
- Authoritative Request: C:\Projeler\PrepMaster\.agents\teamwork\ORIGINAL_REQUEST.md
- Project root: C:\Projeler\PrepMaster

## Objective
Thoroughly explore data datasets, synchronization requirements, and test suites across `C:\Projeler\PrepMaster`:
1. Academic Listening Datasets (R3):
   - Inspect `data/listening.json` and `mobile/assets/data/listening.json`.
   - Analyze the current 4 tracks: JSON schema, keys (id, title, university, duration, audioUrl, noteTakingGuidelines, transcript, questions, options, correctIndex, explanation).
   - Check requirements for the 4 new university tracks (Boğaziçi, ODTÜ, İTÜ, Bilkent) with note-taking guidelines, transcripts, multiple choice questions.
   - Inspect `mobile/test/dataset_integrity_test.dart`: understand all validation checks, schema expectations, track count assertions.
2. Essay & Writing Datasets (R2):
   - Check where writing essays/exemplars currently live or should live for Web and Mobile.
   - Schema requirements for Band 85+ exemplars: essay types (Opinion, For & Against, Problem-Solution), annotations (thesis, topic sentences, CEFR breakdown, common pitfall analyses).
   - Offline availability mechanisms across Web and Flutter.
3. Git Status & Repository Hygiene:
   - Check git status, current branch, recent commits, untracked/modified files.
   - Verify build commands and dependencies across Flutter and Web.

## Deliverable
Write your comprehensive report and handoff to:
`C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_survey_3\handoff.md`
Report back via `send_message` with the report path and summary.
