"""
Dual-Engine Voiceover Generator for Raj Everyway Study.
Supports:
1. Microsoft Edge TTS — 100% Free, Keyless, Unlimited Neural Voices with Millisecond WordBoundary Timings!
2. Sarvam AI (bulbul:v3) — Premium Desi Hindi Voices (aditya, shubh, priya, ritu, rahul, amit)
3. Automatic Fallback: If Sarvam fails or key is missing, auto-falls back to Edge-TTS!
4. Real-time Word Timings: Provides exact per-word start & end timestamps for Word Highlight Captions.
"""

import os
import sys
import json
import base64
import wave
import asyncio
import re
from pathlib import Path
import requests

# Ensure root directory is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import (
    SARVAM_API_KEY, DEFAULT_SPEAKER, DEFAULT_MODEL, DEFAULT_PACE, TARGET_LANGUAGE_CODE
)

# Edge TTS Voice mapping
EDGE_VOICES = {
    "edge_swara": "hi-IN-SwaraNeural",
    "edge_madhur": "hi-IN-MadhurNeural",
    "edge_neerja": "en-IN-NeerjaNeural",
    "edge_prabhat": "en-IN-PrabhatNeural"
}

def align_word_timings_heuristics(text: str, total_duration: float) -> list[dict]:
    """
    Computes natural, syllable-weighted word timings for audio when provider word
    boundaries are not natively streamed (e.g. Sarvam AI or external WAV).
    """
    words = text.strip().split()
    if not words or total_duration <= 0:
        return []

    # Assign weights based on character length and punctuation pauses
    weights = []
    for w in words:
        base_w = max(1.0, len(w) * 0.9)
        if any(w.endswith(p) for p in ["।", ".", "!", "?"]):
            base_w += 2.2  # Pause weight
        elif any(w.endswith(p) for p in [",", ";", ":"]):
            base_w += 1.2
        weights.append(base_w)

    total_weight = sum(weights)
    lead_in = 0.08
    effective_dur = max(0.5, total_duration - lead_in - 0.15)

    timings = []
    curr_t = lead_in
    for w, wt in zip(words, weights):
        w_dur = (wt / total_weight) * effective_dur
        # Cap unreasonable extremes
        w_dur = max(0.18, min(w_dur, 1.20))
        timings.append({
            "word": w,
            "start": round(curr_t, 3),
            "end": round(curr_t + w_dur, 3)
        })
        curr_t += w_dur

    return timings

def generate_voiceover_edge_with_timings(
    text: str,
    output_path: str,
    voice: str = "hi-IN-MadhurNeural",
    pace: float = 1.0
) -> tuple[float, list[dict]]:
    """
    Generates voiceover using Microsoft Edge TTS with hardware-precise WordBoundary events.
    Returns (duration, word_timings).
    """
    import edge_tts
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    rate_pct = int((pace - 1.0) * 100)
    rate_str = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"

    word_timings: list[dict] = []
    temp_mp3 = out_file.with_suffix(".temp.mp3")

    async def _run():
        communicate = edge_tts.Communicate(
            text.strip(),
            voice,
            rate=rate_str,
            boundary="WordBoundary"
        )
        with open(temp_mp3, "wb") as f_mp3:
            async for chunk in communicate.stream():
                ctype = chunk.get("type")
                if ctype == "audio":
                    f_mp3.write(chunk["data"])
                elif ctype == "WordBoundary":
                    start = chunk["offset"] / 10_000_000
                    dur = chunk["duration"] / 10_000_000
                    word_timings.append({
                        "word": chunk["text"],
                        "start": round(start, 3),
                        "end": round(start + dur, 3)
                    })

    asyncio.run(_run())

    # Convert mp3 to wav using moviepy
    from moviepy import AudioFileClip
    audio_clip = AudioFileClip(str(temp_mp3))
    audio_clip.write_audiofile(str(out_file), fps=22050, nbytes=2, logger=None)
    audio_clip.close()

    try:
        temp_mp3.unlink(missing_ok=True)
    except Exception:
        pass

    # Exact WAV duration
    with wave.open(str(out_file), "rb") as w:
        frames = w.getnframes()
        rate = w.getframerate()
        duration = frames / float(rate)

    # If edge-tts word count diverges or failed, fallback to heuristic alignment
    if not word_timings or len(word_timings) < len(text.split()) * 0.6:
        word_timings = align_word_timings_heuristics(text, duration)

    # Persist timings JSON
    timings_json_path = out_file.with_suffix(".timings.json")
    with open(timings_json_path, "w", encoding="utf-8") as f_json:
        json.dump(word_timings, f_json, ensure_ascii=False, indent=2)

    return duration, word_timings

def chunk_text_for_sarvam(text: str, max_chars: int = 400) -> list[str]:
    """Splits text into clean sentence chunks under max_chars so Sarvam 500-char limit is never exceeded."""
    tokens = re.split(r'([।!?\.])', text.strip())
    chunks = []
    current = ""
    for i in range(0, len(tokens), 2):
        sent = tokens[i].strip()
        punct = tokens[i+1] if i + 1 < len(tokens) else ""
        part = f"{sent}{punct}".strip()
        if not part:
            continue
        if len(current) + len(part) + 1 <= max_chars:
            current = f"{current} {part}".strip()
        else:
            if current:
                chunks.append(current)
            current = part
    if current:
        chunks.append(current)
    return chunks if chunks else [text.strip()[:max_chars]]

def generate_voiceover_sarvam_with_timings(
    text: str,
    output_path: str,
    speaker: str = DEFAULT_SPEAKER,
    pace: float = DEFAULT_PACE,
    model: str = DEFAULT_MODEL
) -> tuple[float, list[dict]]:
    """
    Calls Sarvam AI Text-to-Speech API (bulbul:v3) and generates high-fidelity word timings.
    """
    if not SARVAM_API_KEY:
        raise ValueError("SARVAM_API_KEY is not configured in .env")

    url = "https://api.sarvam.ai/text-to-speech"
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }

    text_chunks = chunk_text_for_sarvam(text, max_chars=400)
    print(f"[Sarvam AI] Sending {len(text_chunks)} chunks (total length: {len(text)} chars)...")

    payload = {
        "inputs": text_chunks,
        "target_language_code": TARGET_LANGUAGE_CODE,
        "speaker": speaker,
        "model": model,
        "pace": pace,
        "speech_sample_rate": 22050,
        "enable_preprocessing": True
    }

    response = requests.post(url, json=payload, headers=headers, timeout=35)
    if response.status_code != 200:
        raise RuntimeError(f"Sarvam AI TTS Error {response.status_code}: {response.text}")

    res_data = response.json()
    audios = res_data.get("audios", [])
    if not audios:
        raise RuntimeError("Sarvam AI did not return audio data.")

    audio_bytes = base64.b64decode(audios[0])
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "wb") as f:
        f.write(audio_bytes)

    with wave.open(str(out_file), "rb") as w:
        frames = w.getnframes()
        rate = w.getframerate()
        duration = frames / float(rate)

    word_timings = align_word_timings_heuristics(text, duration)

    timings_json_path = out_file.with_suffix(".timings.json")
    with open(timings_json_path, "w", encoding="utf-8") as f_json:
        json.dump(word_timings, f_json, ensure_ascii=False, indent=2)

    return duration, word_timings

def generate_voiceover_with_timings(
    text: str,
    output_path: str,
    speaker: str = DEFAULT_SPEAKER,
    pace: float = DEFAULT_PACE,
    model: str = DEFAULT_MODEL
) -> tuple[float, list[dict]]:
    """
    Master voice generator returning both audio duration and precise word-level timings.
    - If speaker starts with 'edge_', uses Edge TTS directly.
    - Otherwise tries Sarvam AI (Aditya, Shubh, Priya, etc.).
    - If Sarvam fails, automatically falls back to Edge TTS.
    """
    if speaker in EDGE_VOICES or speaker.startswith("edge_") or speaker.endswith("Neural"):
        voice_id = EDGE_VOICES.get(speaker, speaker)
        print(f"[Voiceover Engine] Using Microsoft Edge TTS with Word Boundaries ({voice_id})...")
        return generate_voiceover_edge_with_timings(text, output_path, voice=voice_id, pace=pace)

    try:
        print(f"[Voiceover Engine] Calling Sarvam AI (Speaker: {speaker}, Pace: {pace}x)...")
        return generate_voiceover_sarvam_with_timings(text, output_path, speaker=speaker, pace=pace, model=model)
    except Exception as e:
        print(f"[Voiceover Engine] Sarvam AI failed ({e}), falling back to Edge TTS...")
        fallback_voice = "hi-IN-MadhurNeural" if speaker in ["aditya", "shubh", "rahul", "amit"] else "hi-IN-SwaraNeural"
        return generate_voiceover_edge_with_timings(text, output_path, voice=fallback_voice, pace=pace)

def generate_voiceover(
    text: str,
    output_path: str,
    speaker: str = DEFAULT_SPEAKER,
    pace: float = DEFAULT_PACE,
    model: str = DEFAULT_MODEL
) -> float:
    """Legacy entrypoint returning duration in seconds."""
    duration, _ = generate_voiceover_with_timings(
        text=text,
        output_path=output_path,
        speaker=speaker,
        pace=pace,
        model=model
    )
    return duration
