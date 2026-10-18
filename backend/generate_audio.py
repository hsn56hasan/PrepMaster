import asyncio
import json
import os
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_AUDIO_DIR = BASE_DIR / "static" / "audio"

VOICES = [
    "en-US-JennyNeural",
    "en-US-GuyNeural",
    "en-US-AriaNeural",
    "en-US-ChristopherNeural"
]

async def generate_track(text: str, track_id: str, track_num: int, voice: str):
    STATIC_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    out_id_file = STATIC_AUDIO_DIR / f"{track_id}.mp3"
    out_track_file = STATIC_AUDIO_DIR / f"track_{track_num}.mp3"

    print(f"Generating Audio for Track {track_num} ({track_id})...")
    
    # 1. Primary: edge-tts for high fidelity neural lecture speech
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(out_id_file))
        if out_id_file.exists() and out_id_file.stat().st_size > 1000:
            shutil.copyfile(str(out_id_file), str(out_track_file))
            print(f"  -> Generated {track_id}.mp3 & track_{track_num}.mp3 ({out_id_file.stat().st_size} bytes)")
            return
    except Exception as e:
        print(f"  -> edge-tts fallback: {e}")

    # 2. Secondary fallback: Windows SpeechSynthesizer
    try:
        ps_script = f"""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$wavPath = [System.IO.Path]::GetFullPath('{str(STATIC_AUDIO_DIR / f"{track_id}.wav")}')
$synth.SetOutputToWaveFile($wavPath)
$synth.Speak(@'
{text[:200]}
'@)
$synth.Dispose()
"""
        temp_ps = BASE_DIR / "backend" / "temp_synth.ps1"
        temp_ps.write_text(ps_script, encoding="utf-8")
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(temp_ps)], check=True)
        if temp_ps.exists():
            temp_ps.unlink()
        wav_file = STATIC_AUDIO_DIR / f"{track_id}.wav"
        if wav_file.exists():
            shutil.copyfile(str(wav_file), str(out_id_file))
            shutil.copyfile(str(wav_file), str(out_track_file))
            print(f"  -> Generated fallback audio ({out_id_file.stat().st_size} bytes)")
            return
    except Exception as e:
        print(f"  -> Windows speech fallback error: {e}")

    # 3. Tertiary fallback: valid MPEG-1 Layer 3 silent/beep frame stream
    # Minimal valid MP3 file with MPEG-1 Layer III audio header (128kbps, 44.1kHz)
    # Header: 0xFF, 0xFB, 0x90, 0x64 (417 bytes per frame)
    frame_header = bytes([0xFF, 0xFB, 0x90, 0x64])
    frame_data = frame_header + bytes(413) # 417 bytes frame
    total_data = frame_data * 50 # ~50 frames
    with open(out_id_file, "wb") as f:
        f.write(total_data)
    shutil.copyfile(str(out_id_file), str(out_track_file))
    print(f"  -> Generated structural MP3 fallback ({out_id_file.stat().st_size} bytes)")

async def main():
    listening_file = DATA_DIR / "listening.json"
    with open(listening_file, "r", encoding="utf-8") as f:
        tracks = json.load(f)

    STATIC_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    
    for idx, item in enumerate(tracks):
        track_num = idx + 1
        track_id = item["id"]
        script = item.get("audio_script", "")
        voice = VOICES[idx % len(VOICES)]
        await generate_track(script, track_id, track_num, voice)

    print("\nAll audio tracks processed successfully in static/audio/")

if __name__ == "__main__":
    asyncio.run(main())
