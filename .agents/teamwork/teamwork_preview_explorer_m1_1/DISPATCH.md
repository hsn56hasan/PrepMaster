# Dispatch: Milestone 1 - Explorer 1 (Boğaziçi & Bilkent Academic Listening Tracks)

## Context
- Working directory: C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_1
- Authoritative Request: C:\Projeler\PrepMaster\.agents\teamwork\ORIGINAL_REQUEST.md
- Scope Document: C:\Projeler\PrepMaster\.agents\teamwork\orchestrator_1\PROJECT.md
- Canonical Dataset: C:\Projeler\PrepMaster\data\listening.json

## Task
Design two authentic, university-standard academic listening tracks for:
1. **Boğaziçi University (BUEPT/BUEPT-PBT)**:
   - ID: `lis_buept_02`
   - University ID: `boun`
   - Level: `C1`
   - Type: `note_taking`
   - Subject: Advanced academic lecture (e.g., "Epigenetics, Neuroplasticity, and Cognitive Aging" or "Linguistic Relativity and Cognitive Framing in Modern Linguistics")
   - Full English audio script (rich, natural spoken academic lecture text, ~200-300 words)
   - Detailed Turkish note-taking guidelines (`suggested_notes_tr`: 4-6 bullet points covering main ideas and key evidence)
   - 4 Multiple Choice Questions (`lis_buept_02_q1` to `q4`) testing main idea, specific details, inferences, and speaker stance, each with 4 options (A-D), `correct_answer`, and clear Turkish explanation (`explanation_tr`).
2. **Bilkent University (COPE / PAE)**:
   - ID: `lis_bilkent_02`
   - University ID: `bilkent`
   - Level: `B2`
   - Type: `while_listening`
   - Subject: Contemporary academic lecture (e.g., "Behavioral Economics and Choice Architecture in Public Policy" or "Cyber-Physical Systems and Urban Resilience")
   - Full English audio script (~200-300 words)
   - Detailed Turkish listening guidelines (`suggested_notes_tr`)
   - 4 Multiple Choice Questions (`lis_bilkent_02_q1` to `q4`) with 4 options (A-D), `correct_answer`, and `explanation_tr`.

## Deliverable
Write your complete JSON objects and specification report to:
`C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_1\handoff.md`
Report back via `send_message`.

## 2026-10-14T10:08:41Z
[Message] timestamp=2026-10-14T10:08:41Z sender=d4d0cbdf-16eb-4100-bcd6-7f1e5ca40628 priority=MESSAGE_PRIORITY_HIGH content=You are Explorer 1 for Milestone 1 (Boğaziçi & Bilkent Listening Tracks).
Your working directory is: C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_1
Your dispatch instructions are at: C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_1\DISPATCH.md
Authoritative request: C:\Projeler\PrepMaster\.agents\teamwork\ORIGINAL_REQUEST.md
Scope document: C:\Projeler\PrepMaster\.agents\teamwork\orchestrator_1\PROJECT.md

Design the complete, authentic academic listening tracks for Boğaziçi (C1 note-taking, lis_buept_02) and Bilkent (B2 while-listening, lis_bilkent_02) conforming to the 13 required fields in ListeningTrack.fromJson with 4 multiple choice questions each, transcripts, and Turkish note guidelines.
Write your complete JSON objects and handoff report to:
C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_1\handoff.md
Send a completion message back to the orchestrator when done.
