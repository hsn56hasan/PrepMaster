# Dispatch: Milestone 1 - Explorer 2 (ODTÜ & İTÜ Academic Listening Tracks)

## Context
- Working directory: C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_2
- Authoritative Request: C:\Projeler\PrepMaster\.agents\teamwork\ORIGINAL_REQUEST.md
- Scope Document: C:\Projeler\PrepMaster\.agents\teamwork\orchestrator_1\PROJECT.md
- Canonical Dataset: C:\Projeler\PrepMaster\data\listening.json

## Task
Design two authentic, university-standard academic listening tracks for:
1. **Middle East Technical University (ODTÜ EPE)**:
   - ID: `lis_odtu_02`
   - University ID: `metu`
   - Level: `C1`
   - Type: `note_taking`
   - Subject: Rigorous engineering/environmental science lecture (e.g., "Circular Economy and Industrial Symbiosis in Resource-Constrained Economies" or "Desalination Technologies and Thermal Energy Storage")
   - Full English audio script (rich, natural spoken academic lecture text, ~200-300 words)
   - Detailed Turkish note-taking guidelines (`suggested_notes_tr`: 4-6 bullet points covering main thesis, mechanisms, and case study)
   - 4 Multiple Choice Questions (`lis_odtu_02_q1` to `q4`) testing thesis, quantitative/qualitative data points, causal reasoning, each with 4 options (A-D), `correct_answer`, and `explanation_tr`.
2. **Istanbul Technical University (İTÜ İYS)**:
   - ID: `lis_itu_02`
   - University ID: `itu`
   - Level: `B2`
   - Type: `while_listening`
   - Subject: Advanced technology & engineering lecture (e.g., "Autonomous Electric Vehicle Fleets and Decentralized Grid Integration" or "Composite Materials in Aerospace Structural Engineering")
   - Full English audio script (~200-300 words)
   - Detailed Turkish guidelines (`suggested_notes_tr`)
   - 4 Multiple Choice Questions (`lis_itu_02_q1` to `q4`) with 4 options (A-D), `correct_answer`, and `explanation_tr`.

## Deliverable
Write your complete JSON objects and specification report to:
`C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_2\handoff.md`
Report back via `send_message`.


## 2026-10-14T10:08:41Z
[Message] timestamp=2026-10-14T10:08:41Z sender=d4d0cbdf-16eb-4100-bcd6-7f1e5ca40628 priority=MESSAGE_PRIORITY_HIGH content=You are Explorer 2 for Milestone 1 (ODTÜ & İTÜ Listening Tracks).
Your working directory is: C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_2
Your dispatch instructions are at: C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_2\DISPATCH.md
Authoritative request: C:\Projeler\PrepMaster\.agents\teamwork\ORIGINAL_REQUEST.md
Scope document: C:\Projeler\PrepMaster\.agents\teamwork\orchestrator_1\PROJECT.md

Design the complete, authentic academic listening tracks for ODTÜ (C1 note-taking, lis_odtu_02) and İTÜ (B2 while-listening, lis_itu_02) conforming to the 13 required fields in ListeningTrack.fromJson with 4 multiple choice questions each, transcripts, and Turkish note guidelines.
Write your complete JSON objects and handoff report to:
C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_2\handoff.md
Send a completion message back to the orchestrator when done.
