import json
import re
import hashlib
import os

h1_path = r'C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_1\handoff.md'
h2_path = r'C:\Projeler\PrepMaster\.agents\teamwork\teamwork_preview_explorer_m1_2\handoff.md'
root_path = r'C:\Projeler\PrepMaster\data\listening.json'
mobile_path = r'C:\Projeler\PrepMaster\mobile\assets\data\listening.json'

with open(h1_path, encoding='utf-8') as f:
    tracks_h1 = [json.loads(b) for b in re.findall(r'```json\s*(\{.*?\})\s*```', f.read(), re.DOTALL)]

with open(h2_path, encoding='utf-8') as f:
    tracks_h2 = [json.loads(b) for b in re.findall(r'```json\s*(\{.*?\})\s*```', f.read(), re.DOTALL)]

with open(root_path, encoding='utf-8') as f:
    existing = json.load(f)

# Combine: 4 existing + 2 from Explorer 1 + 2 from Explorer 2
all_8 = existing + tracks_h1 + tracks_h2
assert len(all_8) == 8, f"Expected 8 tracks, got {len(all_8)}"

json_text = json.dumps(all_8, indent=2, ensure_ascii=False) + '\n'

# Write to root
with open(root_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(json_text)

# Write to mobile asset
with open(mobile_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(json_text)

# Verify SHA-256 byte parity
with open(root_path, 'rb') as f:
    bytes_root = f.read()
    hash_root = hashlib.sha256(bytes_root).hexdigest()

with open(mobile_path, 'rb') as f:
    bytes_mobile = f.read()
    hash_mobile = hashlib.sha256(bytes_mobile).hexdigest()

print(f"data/listening.json size: {len(bytes_root)} bytes, SHA-256: {hash_root}")
print(f"mobile/assets/data/listening.json size: {len(bytes_mobile)} bytes, SHA-256: {hash_mobile}")

assert bytes_root == bytes_mobile, "Byte mismatch!"
assert hash_root == hash_mobile, "Hash mismatch!"
print("100% BYTE PARITY CONFIRMED!")
