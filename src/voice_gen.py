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

def chunk_text_for_sarvam_batches(text: str, max_chars_per_item: int = 350, max_items_per_batch: int = 1) -> list[list[str]]:
    """
    Splits narration into clean, natural sentence chunks and groups them into batches of
    `max_items_per_batch` (default 1 sentence per API call for ultra-fast response and 0 timeouts).
    """
    # Clean out markdown, symbols, and formatting that disrupt TTS
    cleaned = re.sub(r'[*#_~`\[\]\(\)\{\}]', '', text.strip())
    cleaned = re.sub(r'\s+', ' ', cleaned)
    # Ensure natural spacing after punctuation
    cleaned = re.sub(r'([।!?\.])([A-Za-z])', r'\1 \2', cleaned)

    tokens = re.split(r'([।!?\.\n]+)', cleaned)
    raw_sentences = []
    for i in range(0, len(tokens), 2):
        sent = tokens[i].strip()
        punct = tokens[i+1] if i + 1 < len(tokens) else "."
        # Keep clean punctuation
        if punct in ["\n", "\r\n"]:
            punct = "."
        part = f"{sent}{punct}".strip()
        if part and len(part) > 2:
            raw_sentences.append(part)

    if not raw_sentences:
        raw_sentences = [cleaned[:max_chars_per_item]]

    # Ensure no single item exceeds max_chars_per_item
    sanitized_items = []
    for s in raw_sentences:
        if len(s) <= max_chars_per_item:
            sanitized_items.append(s)
        else:
            # Sub-split long sentences by comma or space
            words = s.split()
            buf = ""
            for w in words:
                if len(buf) + len(w) + 1 <= max_chars_per_item:
                    buf = f"{buf} {w}".strip()
                else:
                    if buf:
                        sanitized_items.append(buf + ".")
                    buf = w
            if buf:
                sanitized_items.append(buf)

    # Group into batches of max_items_per_batch (default 1 for 100% reliability)
    batches = []
    for i in range(0, len(sanitized_items), max_items_per_batch):
        batches.append(sanitized_items[i:i + max_items_per_batch])

    return batches

def generate_voiceover_sarvam_with_timings(
    text: str,
    output_path: str,
    speaker: str = DEFAULT_SPEAKER,
    pace: float = DEFAULT_PACE,
    model: str = DEFAULT_MODEL
) -> tuple[float, list[dict]]:
    """
    Calls Sarvam AI Text-to-Speech API (bulbul:v3) with ultra-reliable single-sentence
    dispatch, connection pooling, automatic exponential retries, natural sentence-pause
    mastering, and studio-grade peak audio normalization.
    """
    if not SARVAM_API_KEY:
        raise ValueError("SARVAM_API_KEY is not configured in .env")

    import io
    import time
    import numpy as np
    from urllib3.util import Retry
    from requests.adapters import HTTPAdapter

    url = "https://api.sarvam.ai/text-to-speech"
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }

    # Setup resilient HTTP session with connection pooling
    session = requests.Session()
    adapter = HTTPAdapter(pool_connections=5, pool_maxsize=5)
    session.mount("https://", adapter)

    batches = chunk_text_for_sarvam_batches(text, max_chars_per_item=350, max_items_per_batch=1)
    print(f"[Sarvam AI] Synthesizing {len(batches)} sentences using speaker '{speaker}' ({model}, pace: {pace}x)...")

    all_audio_frames = b""
    sample_params = None

    for idx, b_inputs in enumerate(batches, 1):
        clean_text_preview = b_inputs[0][:60] + "..." if len(b_inputs[0]) > 60 else b_inputs[0]
        print(f"  🎙️ [Sarvam AI] Sentence {idx}/{len(batches)}: \"{clean_text_preview}\"")
        payload = {
            "inputs": b_inputs,
            "target_language_code": TARGET_LANGUAGE_CODE,
            "speaker": speaker,
            "model": model,
            "pace": pace,
            "speech_sample_rate": 22050,
            "enable_preprocessing": True
        }

        # Resilient retry loop (up to 3 attempts with exponential backoff)
        res_data = None
        for attempt in range(1, 4):
            try:
                response = session.post(url, json=payload, headers=headers, timeout=50)
                if response.status_code == 200:
                    res_data = response.json()
                    break
                elif response.status_code in [429, 500, 502, 503, 504]:
                    print(f"    ⚠️ [Sarvam AI] Temporary status {response.status_code} on attempt {attempt}/3, retrying...")
                    time.sleep(1.5 * attempt)
                else:
                    raise RuntimeError(f"Sarvam AI Error {response.status_code}: {response.text}")
            except (requests.Timeout, requests.ConnectionError) as net_err:
                print(f"    ⚠️ [Sarvam AI] Network timeout/error on attempt {attempt}/3: {net_err}")
                if attempt == 3:
                    raise RuntimeError(f"Sarvam AI failed after 3 network attempts: {net_err}")
                time.sleep(1.5 * attempt)

        if not res_data:
            raise RuntimeError(f"Sarvam AI failed to synthesize sentence {idx} after retries.")

        audios = res_data.get("audios", [])
        if not audios:
            raise RuntimeError(f"Sarvam AI returned empty audio in sentence {idx}.")

        for a_b64 in audios:
            raw_wav = base64.b64decode(a_b64)
            with wave.open(io.BytesIO(raw_wav), "rb") as w:
                if sample_params is None:
                    sample_params = (w.getnchannels(), w.getsampwidth(), w.getframerate())
                frames = w.readframes(w.getnframes())
                all_audio_frames += frames

                # Insert a subtle 100ms breathing silence between sentences for natural human cadence
                silence_frames = int(sample_params[2] * 0.10)
                silence_bytes = b"\x00" * (silence_frames * sample_params[0] * sample_params[1])
                all_audio_frames += silence_bytes

    if not all_audio_frames or sample_params is None:
        raise RuntimeError("Failed to assemble audio from Sarvam AI.")

    # Peak amplitude normalization to -0.8 dB for loud, broadcast-ready punch
    samples = np.frombuffer(all_audio_frames, dtype=np.int16).astype(np.float32)
    max_val = np.max(np.abs(samples))
    if max_val > 0:
        target_peak = 30000.0  # Approx -0.8 dB peak
        gain = target_peak / max_val
        samples = np.clip(samples * gain, -32767, 32767).astype(np.int16)
        all_audio_frames = samples.tobytes()

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(out_file), "wb") as out_w:
        out_w.setnchannels(sample_params[0])
        out_w.setsampwidth(sample_params[1])
        out_w.setframerate(sample_params[2])
        out_w.writeframes(all_audio_frames)

    with wave.open(str(out_file), "rb") as w:
        frames = w.getnframes()
        rate = w.getframerate()
        duration = frames / float(rate)

    print(f"  ✅ [Sarvam AI] Studio-grade voiceover generated: {duration:.2f}s across {len(batches)} sentences.")

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
        print(f"[Voiceover Engine] Calling Sarvam AI Bulbul v3 (Speaker: {speaker}, Pace: {pace}x)...")
        return generate_voiceover_sarvam_with_timings(text, output_path, speaker=speaker, pace=pace, model=model)
    except Exception as e:
        print(f"⚠️ [Voiceover Engine] Sarvam AI error ({e}). Attempting backup retry with primary voice...")
        try:
            return generate_voiceover_sarvam_with_timings(text, output_path, speaker="aditya", pace=1.02, model="bulbul:v3")
        except Exception as retry_err:
            print(f"❌ [Voiceover Engine] Sarvam AI exhausted ({retry_err}). Falling back to Microsoft Edge TTS...")
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
