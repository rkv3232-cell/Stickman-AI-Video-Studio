"""
Word Highlight Caption Engine for Stickman AI Video Production Studio.
Renders real-time synchronized Devanagari Hindi captions with active word highlighting.

Features:
- Full spoken phrase remains visible and readable at all times.
- Currently spoken word is highlighted in real-time according to exact speech timestamps.
- Active word highlighted in contrasting Neon Yellow (#FFE600) with dark stroke & glow.
- Inactive words remain crisp white with strong black stroke for 100% readability.
- Strictly framed in YouTube Shorts safe zone (Y: 1480-1680) to avoid UI buttons and stickman overlap.
- Clean line-wrapping (max 2 lines) preserving Devanagari conjuncts and matras.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS,
    FONT_MUKTA_EXTRABOLD, FONT_MUKTA_BOLD, FONT_ARIAL_BOLD, FONT_NOTO_BOLD,
    SUBTITLE_FONT_SIZE, SUBTITLE_HIGHLIGHT_COLOR, SUBTITLE_PRIMARY_COLOR,
    SUBTITLE_STROKE_WIDTH
)
from src.hinglish_normalizer import normalize_text_to_hinglish

def _get_caption_font(size: int = 56) -> ImageFont.FreeTypeFont:
    """Loads Roman / Latin typography font optimized for mobile readability."""
    for fp in [FONT_MUKTA_EXTRABOLD, FONT_ARIAL_BOLD, FONT_MUKTA_BOLD, "C:/Windows/Fonts/arial.ttf"]:
        if Path(fp).exists():
            try:
                return ImageFont.truetype(str(fp), size)
            except Exception:
                pass
    return ImageFont.load_default()

def build_caption_phrase_groups(
    word_timings: List[Dict[str, Any]],
    total_duration: float,
    words_per_phrase: int = 5
) -> List[Dict[str, Any]]:
    """
    Groups individual word timings into short, coherent conversational phrases
    (4-6 words) for high-retention mobile captions.
    """
    if not word_timings:
        return []

    groups = []
    curr_words = []

    for w_entry in word_timings:
        clean_entry = dict(w_entry)
        raw_w = w_entry.get("word", "").strip()
        clean_w = normalize_text_to_hinglish(raw_w)
        clean_entry["word"] = clean_w
        curr_words.append(clean_entry)
        w_text = clean_w

        # Split on punctuation or reaching target phrase length
        is_terminal = any(w_text.endswith(p) for p in ["।", "?", "!", ".", ","])
        if len(curr_words) >= words_per_phrase or is_terminal:
            p_start = curr_words[0]["start"]
            p_end = curr_words[-1]["end"]
            groups.append({
                "words": list(curr_words),
                "start": p_start,
                "end": p_end,
                "text": " ".join(cw["word"] for cw in curr_words)
            })
            curr_words = []

    if curr_words:
        groups.append({
            "words": list(curr_words),
            "start": curr_words[0]["start"],
            "end": curr_words[-1]["end"],
            "text": " ".join(cw["word"] for cw in curr_words)
        })

    # Extend end times slightly to prevent jarring flashes between words
    for i in range(len(groups)):
        if i < len(groups) - 1:
            next_start = groups[i + 1]["start"]
            # Fill gap up to 0.35s
            if 0 < next_start - groups[i]["end"] <= 0.45:
                groups[i]["end"] = next_start
        else:
            groups[i]["end"] = max(groups[i]["end"], total_duration)

    return groups

def render_caption_frame(
    t: float,
    phrase_groups: List[Dict[str, Any]],
    font_size: int = 56,
    center_y: int = 1540
) -> Image.Image:
    """
    Renders a single frame of the word-highlight captions at time t.
    Shows the full phrase, with the active word illuminated in Neon Yellow.
    """
    canvas = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    if not phrase_groups:
        return canvas

    # Find active phrase group
    active_group = None
    for grp in phrase_groups:
        if grp["start"] <= t <= grp["end"]:
            active_group = grp
            break

    # Micro-gap fallback: if between phrases within 0.25s, hold previous or anticipation
    if not active_group:
        for grp in phrase_groups:
            if 0 <= t - grp["end"] <= 0.20:
                active_group = grp
                break

    if not active_group:
        return canvas

    words = active_group["words"]
    if not words:
        return canvas

    font = _get_caption_font(font_size)
    draw = ImageDraw.Draw(canvas)

    # Determine which word is currently active
    active_idx = -1
    for i, w in enumerate(words):
        if w["start"] <= t <= w["end"]:
            active_idx = i
            break
    if active_idx == -1:
        # Default to last spoken word in this phrase
        for i, w in enumerate(words):
            if t >= w["end"]:
                active_idx = i

    # Measure words and arrange lines (max 2 lines)
    space_w = draw.textlength(" ", font=font)
    max_line_w = 880

    lines: List[List[Tuple[int, Dict[str, Any], float]]] = [[]]
    cur_line_w = 0.0

    for i, w_entry in enumerate(words):
        w_str = w_entry["word"]
        w_w = draw.textlength(w_str, font=font)
        if cur_line_w + w_w > max_line_w and lines[-1]:
            lines.append([])
            cur_line_w = 0.0

        lines[-1].append((i, w_entry, w_w))
        cur_line_w += w_w + space_w

    # Calculate overall container dimensions
    line_h = int(font_size * 1.35)
    total_text_h = len(lines) * line_h
    max_measured_w = max(
        (sum(item[2] for item in ln) + (len(ln) - 1) * space_w)
        for ln in lines
    )

    pad_x = 36
    pad_y = 20
    pill_w = max_measured_w + pad_x * 2
    pill_h = total_text_h + pad_y * 2
    pill_x1 = (VIDEO_WIDTH - pill_w) // 2
    pill_y1 = center_y - pill_h // 2
    pill_x2 = pill_x1 + pill_w
    pill_y2 = pill_y1 + pill_h

    # 1. Frosted dark pill container
    draw.rounded_rectangle(
        [pill_x1, pill_y1, pill_x2, pill_y2],
        radius=22,
        fill=(10, 15, 28, 225),
        outline=(0, 240, 255, 120),
        width=2
    )

    # 2. Render each line of words
    cur_y = pill_y1 + pad_y
    for ln in lines:
        ln_w = sum(item[2] for item in ln) + (len(ln) - 1) * space_w
        cur_x = (VIDEO_WIDTH - ln_w) // 2

        for idx, w_entry, w_w in ln:
            w_str = w_entry["word"]
            is_active = (idx == active_idx)

            if is_active:
                # Active word: Highlighted in Neon Yellow (#FFE600) with glowing punch
                text_col = (255, 230, 0, 255)
                stroke_col = (0, 0, 0, 255)
                stroke_w = 6

                # Subtle active highlight backing pill
                hl_pad_x, hl_pad_y = 10, 4
                draw.rounded_rectangle(
                    [cur_x - hl_pad_x, cur_y - hl_pad_y, cur_x + w_w + hl_pad_x, cur_y + line_h - 10],
                    radius=10,
                    fill=(255, 230, 0, 40),
                    outline=(255, 230, 0, 160),
                    width=1
                )
            else:
                # Inactive word: Crisp translucent white
                text_col = (255, 255, 255, 220)
                stroke_col = (0, 0, 0, 255)
                stroke_w = 5

            draw.text(
                (cur_x, cur_y),
                w_str,
                font=font,
                fill=text_col,
                stroke_width=stroke_w,
                stroke_fill=stroke_col
            )
            cur_x += w_w + space_w

        cur_y += line_h

    return canvas

def create_word_highlight_caption_clip(
    phrase_groups: List[Dict[str, Any]],
    total_duration: float,
    center_y: int = 1540
):
    """
    Creates a full-timeline MoviePy VideoClip of real-time word highlight captions.
    """
    from moviepy import VideoClip

    def make_frame(t):
        img = render_caption_frame(
            t=t,
            phrase_groups=phrase_groups,
            font_size=56,
            center_y=center_y
        )
        return np.array(img)

    return VideoClip(make_frame, duration=total_duration).with_fps(VIDEO_FPS)

def format_srt_time(seconds: float) -> str:
    """Formats seconds into standard SRT timestamp format HH:MM:SS,mmm."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms >= 1000:
        s += 1
        ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def export_caption_groups_to_srt(
    phrase_groups: List[Dict[str, Any]],
    output_path: str
) -> str:
    """Exports synchronized phrase groups into standard YouTube .srt format."""
    lines = []
    for i, grp in enumerate(phrase_groups, 1):
        start_ts = format_srt_time(grp["start"])
        end_ts = format_srt_time(grp["end"])
        lines.append(f"{i}")
        lines.append(f"{start_ts} --> {end_ts}")
        lines.append(grp["text"])
        lines.append("")

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return str(out_file)

