import os
import sys
import math
import random
import wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Ensure root directory is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from moviepy import (
    VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, VideoClip, concatenate_videoclips
)
from moviepy.audio.AudioClip import CompositeAudioClip
from config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS,
    BG_VIDEOS_DIR, BG_MUSIC_DIR, OUTPUT_DIR, FONT_PATH,
    CHANNEL_NAME, DEFAULT_VISUAL_STYLE
)
import json
from src.subtitle_gen import generate_subtitle_clips
from src.visual_engine import build_background, build_scene_background
from src.stickman_engine import create_stickman_clip, StickmanConfig
from src.composition_engine import get_composition_layout
from src.kinetic_typography import create_kinetic_typography_clip
from src.caption_engine import build_caption_phrase_groups, create_word_highlight_caption_clip
from src.voice_gen import align_word_timings_heuristics

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def create_channel_header() -> np.ndarray:
    """Creates a sleek channel header badge overlay for top of Shorts."""
    canvas = Image.new("RGBA", (VIDEO_WIDTH, 140), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    badge_text = CHANNEL_NAME
    try:
        font = ImageFont.truetype(FONT_PATH, 42)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), badge_text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    pill_w = tw + 80
    pill_h = th + 36
    px = (VIDEO_WIDTH - pill_w) // 2
    py = (140 - pill_h) // 2

    # Glowing dark pill container
    draw.rounded_rectangle(
        [px, py, px + pill_w, py + pill_h],
        radius=24,
        fill=(12, 18, 34, 230),
        outline=(0, 240, 255, 180),
        width=2
    )

    # Red live dot
    dot_r = 8
    dot_x = px + 28
    dot_y = py + pill_h // 2
    draw.ellipse([dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r], fill=(239, 68, 68, 255))
    draw.text((px + 52, py + (pill_h - th) // 2 - 2), badge_text, font=font, fill=(255, 255, 255, 255))
    return np.array(canvas)

def create_audio_spectrum_visualizer(audio_path: str, duration: float) -> VideoClip:
    """
    Renders 18 glowing neon equalizer bars that pulse in real-time to Sarvam voiceover frequencies!
    """
    try:
        with wave.open(audio_path, "rb") as w:
            sr = w.getframerate()
            raw = w.readframes(w.getnframes())
            audio_samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    except Exception as e:
        print(f"Visualizer audio read error: {e}")
        audio_samples = np.zeros(int(duration * 22050))
        sr = 22050

    num_bars = 18
    bar_w = 10
    gap = 6
    total_w = num_bars * bar_w + (num_bars - 1) * gap
    start_x = (VIDEO_WIDTH - total_w) // 2
    vis_h = 36

    def make_vis_frame(t):
        idx = int(t * sr)
        window = audio_samples[idx : idx + 1024]
        if len(window) < 1024:
            fft_vals = np.zeros(num_bars)
        else:
            fft = np.abs(np.fft.rfft(window * np.hanning(len(window))))
            indices = np.linspace(2, min(len(fft) - 1, 140), num_bars, dtype=int)
            fft_vals = np.clip(fft[indices] / 7.5, 0.08, 1.0)

        img = Image.new("RGBA", (VIDEO_WIDTH, vis_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        for i in range(num_bars):
            bx = start_x + i * (bar_w + gap)
            bh = max(4, int(fft_vals[i] * (vis_h - 4)))
            by1 = vis_h - bh
            by2 = vis_h
            draw.rounded_rectangle(
                [bx, by1, bx + bar_w, by2],
                radius=3,
                fill=(0, 240, 255, 200),
                outline=(255, 255, 255, 120),
                width=1
            )

        return np.array(img)

    return (
        VideoClip(make_vis_frame, duration=duration)
        .with_fps(VIDEO_FPS)
        .with_position(("center", VIDEO_HEIGHT - 70))
    )

def build_short_video(
    audio_path: str,
    script_text: str,
    storyboard: list[dict] = None,
    visual_style: str = DEFAULT_VISUAL_STYLE,
    stickman_style: str = "modern_beanie",
    visual_keywords: list[str] = None,
    output_filename: str = "final_short.mp4",
    bgm_volume: float = 0.06,
    progress_callback = None,
    word_timings: list[dict] = None
) -> str:
    """
    Master Shorts Video Engine 3.0 (Stickman AI Video Production Studio):
    - Scene-by-Scene Storyboard Choreography with Consistent Stickman Actor in 100% of Scenes
    - Adaptive Rule-of-Thirds Composition: Intelligent Alternation between Left and Right Framing
    - Bold Kinetic Typography: Oversized Hero Keywords, Editorial Tags, Spring-Pop Easing
    - Real-Time Word Highlight Captions: Exact Speech Synchronization in Shorts Safe Zone
    - Multi-mode Visual Background (Pollinations AI + Ken Burns / Procedural Cyberpunk / Sketch Notes / Stock)
    - Articulated Stickman Rig with Micro-animations (Breathing, Blinks, Speaking Mouth, Expressions, Props)
    - Live pulsing Audio Spectrum Visualizer
    - Channel branding badge (RAJ EVERYWAY STUDY)
    - Whoosh SFX at scene transitions
    - Studio BGM (ambient lo-fi beat) with audio ducking
    - Export to 1080x1920 30FPS MP4
    """
    def report(pct: int, msg: str):
        if progress_callback:
            progress_callback(pct, msg)
        print(f"[{pct}%] {msg}")

    report(10, "Loading audio and preparing duration...")
    voice_audio = AudioFileClip(audio_path)
    total_duration = voice_audio.duration
    print(f"Voiceover duration: {total_duration:.2f} seconds")

    # Load or resolve word timings for real-time word highlight captions
    if not word_timings:
        timings_json_path = Path(audio_path).with_suffix(".timings.json")
        if timings_json_path.exists():
            try:
                with open(timings_json_path, "r", encoding="utf-8") as f_json:
                    word_timings = json.load(f_json)
                print(f"[Video Engine] Loaded {len(word_timings)} word timings from {timings_json_path.name}")
            except Exception as e:
                print(f"[Video Engine] Failed to load timings JSON: {e}")

    if not word_timings:
        print("[Video Engine] Aligning word timings via heuristic rhythm model...")
        word_timings = align_word_timings_heuristics(script_text, total_duration)

    # 1. Multi-Scene Visual Assembly with Adaptive Stickman & Kinetic Typography
    transition_times = [0.0]
    if storyboard and len(storyboard) > 0:
        report(25, f"Assembling {len(storyboard)} scenes with Adaptive Stickman & Bold Kinetic Typography...")
        scene_clips = []
        curr_t = 0.0

        for idx, sc in enumerate(storyboard):
            s_dur = float(sc.get("duration", 4.0))
            pose = sc.get("stickman_pose", "explaining")
            emotion = sc.get("stickman_emotion", "confident")
            pos = sc.get("stickman_position", "left" if idx % 2 == 0 else "right")
            prop = sc.get("prop", "none")
            shot_type = sc.get("shot_type", "medium")
            typo_data = sc.get("typography", {})

            # Resolve adaptive composition layout
            layout = sc.get("composition")
            if not layout:
                layout = get_composition_layout(
                    scene_index=idx,
                    stickman_pos=pos,
                    typography_pos=typo_data.get("position", "right" if pos == "left" else "left"),
                    shot_type=shot_type,
                    primary_text=typo_data.get("primary_text", ""),
                    secondary_text=typo_data.get("secondary_text", "")
                )

            # A. Scene Background Layer
            s_bg = build_scene_background(sc, visual_style=visual_style)

            # B. Articulated Stickman Layer with Directional Acting & Positioning
            s_char_info = layout["stickman"]
            s_stickman = create_stickman_clip(
                duration=s_dur,
                pose=pose,
                emotion=emotion,
                position=s_char_info["position"],
                shot_type=shot_type,
                prop=prop,
                config=StickmanConfig(style=stickman_style),
                scale=s_char_info["scale"],
                target_x=s_char_info["x"],
                target_y=s_char_info["y"],
                facing=s_char_info["facing"]
            )

            # C. Bold Kinetic Typography Layer
            s_typo = create_kinetic_typography_clip(
                duration=s_dur,
                typo_data=typo_data,
                layout_info=layout
            )

            # D. Composite Scene (Background + Stickman + Kinetic Typography)
            s_comp = CompositeVideoClip([s_bg, s_stickman, s_typo], size=(VIDEO_WIDTH, VIDEO_HEIGHT)).with_duration(s_dur)
            scene_clips.append(s_comp)

            curr_t += s_dur
            if curr_t < total_duration:
                transition_times.append(curr_t)

        master_visual_track = concatenate_videoclips(scene_clips).with_duration(total_duration)
    else:
        report(25, f"Building background visuals (Style: {visual_style})...")
        master_visual_track, transition_times = build_background(
            total_duration=total_duration,
            visual_style=visual_style,
            visual_keywords=visual_keywords
        )

    # 2. Audio Spectrum Visualizer
    report(45, "Generating real-time audio spectrum visualizer...")
    visualizer_clip = create_audio_spectrum_visualizer(audio_path, total_duration)

    # 3. Synchronized Word-Highlight Captions Engine
    report(60, "Generating real-time word-highlight captions...")
    caption_groups = build_caption_phrase_groups(word_timings, total_duration, words_per_phrase=5)
    caption_clip = create_word_highlight_caption_clip(caption_groups, total_duration)

    # 4. Channel Header Badge
    report(70, "Adding channel header badge...")
    header_np = create_channel_header()
    header_clip = (
        ImageClip(header_np)
        .with_duration(total_duration)
        .with_position(("center", 180))
    )

    # 5. Multi-Track Audio (Voice + Whoosh SFX + Studio BGM)
    report(80, "Mixing multi-track audio and SFX...")
    audio_tracks = [voice_audio]

    whoosh_path = Path("assets/sfx/whoosh.wav")
    if whoosh_path.exists() and len(transition_times) > 1:
        for t_trans in transition_times[1:]:
            sfx = (
                AudioFileClip(str(whoosh_path))
                .with_start(max(0, t_trans - 0.15))
                .with_volume_scaled(0.20)
            )
            audio_tracks.append(sfx)

    # Select BGM
    bgm_candidates = list(Path(BG_MUSIC_DIR).glob("*.mp3")) + list(Path(BG_MUSIC_DIR).glob("*.wav"))
    if bgm_candidates:
        chosen_bgm = bgm_candidates[0]
        bgm = AudioFileClip(str(chosen_bgm)).with_duration(total_duration).with_volume_scaled(bgm_volume)
        audio_tracks.append(bgm)

    final_audio = CompositeAudioClip(audio_tracks)

    # 6. Composite All Visual Layers (Visuals + Audio Spectrum + Header + Word Highlight Captions)
    report(85, "Compositing visual layers with Stickman protagonist & kinetic typography...")
    all_layers = [master_visual_track, visualizer_clip, header_clip, caption_clip]
    final_video = CompositeVideoClip(all_layers, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
    final_video = final_video.with_duration(total_duration).with_audio(final_audio)

    # 7. Render Final MP4
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / output_filename
    report(90, f"Rendering 1080x1920 MP4 to {out_path.name}...")
    final_video.write_videofile(
        str(out_path),
        fps=VIDEO_FPS,
        codec="libx264",
        audio_codec="aac",
        preset="fast",
        threads=4
    )

    # Cleanup memory
    try:
        voice_audio.close()
        master_visual_track.close()
        final_video.close()
    except Exception:
        pass

    report(100, f"Video successfully rendered at: {out_path.name}!")
    return str(out_path)
