import json
import re

h1_path = r'C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_1\handoff.md'
h2_path = r'C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_2\handoff.md'
existing_path = r'C:\Projeler\PrepMaster\data\listening.json'

with open(h1_path, encoding='utf-8') as f:
    tracks_h1 = [json.loads(b) for b in re.findall(r'```json\s*(\{.*?\})\s*```', f.read(), re.DOTALL)]

with open(h2_path, encoding='utf-8') as f:
    tracks_h2 = [json.loads(b) for b in re.findall(r'```json\s*(\{.*?\})\s*```', f.read(), re.DOTALL)]

with open(existing_path, encoding='utf-8') as f:
    existing = json.load(f)

all_8 = existing + tracks_h1 + tracks_h2
print(f'Total combined tracks: {len(all_8)}')

required_track_keys = [
    'id', 'university_id', 'level', 'type', 'title', 'subtitle',
    'target_university', 'duration_minutes', 'lecture_duration_seconds',
    'instructions_tr', 'audio_script', 'suggested_notes_tr', 'questions'
]

track_ids = set()
question_ids = set()
uni_counts = {}
type_counts = {}
level_counts = {}

for idx, t in enumerate(all_8):
    tid = t.get('id')
    assert tid, f'Track {idx} has no id'
    assert tid not in track_ids, f'Duplicate track id: {tid}'
    track_ids.add(tid)

    for k in required_track_keys:
        assert k in t, f'Track {tid} missing key {k}'
        assert t[k] is not None, f'Track {tid} key {k} is None'

    uni = t['university_id']
    assert uni in {'boun', 'itu', 'metu', 'bilkent'}, f'Invalid uni {uni}'
    uni_counts[uni] = uni_counts.get(uni, 0) + 1

    ttype = t['type']
    assert ttype in {'note_taking', 'while_listening'}, f'Invalid type {ttype}'
    type_counts[ttype] = type_counts.get(ttype, 0) + 1

    lvl = t['level']
    assert lvl in {'B1', 'B2', 'C1', 'C2'}, f'Invalid level {lvl}'
    level_counts[lvl] = level_counts.get(lvl, 0) + 1

    assert isinstance(t['suggested_notes_tr'], list) and len(t['suggested_notes_tr']) > 0
    assert len(t['questions']) >= 3, f'Track {tid} has < 3 questions'

    for q in t['questions']:
        qid = q.get('id')
        assert qid, f'Question missing id in {tid}'
        assert qid not in question_ids, f'Duplicate question id: {qid}'
        question_ids.add(qid)

        assert q.get('question'), f'Missing question text in {qid}'
        assert q.get('correct_answer'), f'Missing correct_answer in {qid}'
        assert q.get('explanation_tr'), f'Missing explanation_tr in {qid}'

        opts = q.get('options', [])
        assert len(opts) >= 4, f'Options count issue in {qid}'
        opt_keys = {o['key'] for o in opts}
        assert opt_keys == {'A', 'B', 'C', 'D'}, f'Keys not A,B,C,D in {qid}: {opt_keys}'
        assert q['correct_answer'] in opt_keys, f'Correct answer not in keys in {qid}'

print('Universities:', uni_counts)
print('Types:', type_counts)
print('Levels:', level_counts)
print('Question count total:', len(question_ids))
print('SUCCESS: All 8 tracks passed 100% of deep integrity checks!')
