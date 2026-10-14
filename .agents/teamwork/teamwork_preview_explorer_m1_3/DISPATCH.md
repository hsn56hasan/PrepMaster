# Dispatch: Milestone 1 - Explorer 3 (Test Suite & Parity Validation Strategy)

## Context
- Working directory: C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_3
- Authoritative Request: C:\Projeler\PrepMaster\.agents\teamwork\ORIGINAL_REQUEST.md
- Scope Document: C:\Projeler\PrepMaster\.agents\teamwork\orchestrator_1\PROJECT.md
- Test File: C:\Projeler\PrepMaster\mobile\test\dataset_integrity_test.dart
- Dataset paths: C:\Projeler\PrepMaster\data\listening.json and C:\Projeler\PrepMaster\mobile\assets\data\listening.json

## Task
1. Examine `mobile/test/dataset_integrity_test.dart` and `mobile/test/listening_writing_test.dart` to specify exact test updates required when `listening.json` expands from 4 to 8 tracks.
2. Verify all assertions in `dataset_integrity_test.dart` (track IDs, university IDs, questions count, options count, valid keys).
3. Specify the exact test assertion changes needed (e.g. line 56: `expect(jsonList.length, 8);` or `expect(jsonList.length, greaterThanOrEqualTo(8));`, group description updates, etc.).
4. Define the verification commands and dual-platform file hash comparison method to ensure 100% parity.

## Deliverable
Write your test update specification and verification guide to:
`C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_3\handoff.md`
Report back via `send_message`.


## 2026-10-14T10:08:41Z
You are Explorer 3 for Milestone 1 (Listening Test & Parity Explorer).
Your working directory is: C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_3
Your dispatch instructions are at: C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_3\DISPATCH.md
Authoritative request: C:\Projeler\PrepMaster\.agents\teamwork\ORIGINAL_REQUEST.md
Scope document: C:\Projeler\PrepMaster\.agents\teamwork\orchestrator_1\PROJECT.md

Examine mobile/test/dataset_integrity_test.dart and listening_writing_test.dart. Formulate the exact test assertion changes and parity check protocol required for the 8 tracks expansion.
Write your test update specification and handoff report to:
C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_3\handoff.md
Send a completion message back to the orchestrator when done.
