import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, VideoClip
from config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, FONT_PATH,
    SUBTITLE_FONT_SIZE, SUBTITLE_STROKE_WIDTH
)

def get_spring_scale(progress: float) -> float:
    """MoneyPrinterTurbo damped harmonic spring scale formula."""
    if progress >= 1.0:
        return 1.0
    scale = 1.0 - math.exp(-6.0 * progress) * math.cos(2.5 * math.pi * progress)
    return max(0.05, min(scale, 1.30))

def create_styled_subtitle_card(chunk_text: str, is_highlight: bool = False) -> Image.Image:
    """
    Renders high-energy modern Shorts subtitles:
    - Glowing dark frosted pill container
    - Vibrant colors: Active word in Neon Yellow (#FFE600), rest in White
    - Thick 6px black stroke for maximum contrast
    """
    card_w = VIDEO_WIDTH
    card_h = 240
    img = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font = None
    for fp in [FONT_PATH, "C:/Windows/Fonts/nirmala.ttf", "C:/Windows/Fonts/Nirmala.ttc", "C:/Windows/Fonts/arial.ttf"]:
        if Path(fp).exists():
            try:
                font = ImageFont.truetype(fp, 68)
                break
            except Exception:
                pass
    if font is None:
        font = ImageFont.load_default()

    words = chunk_text.strip().split()
    if not words:
        return img

    # Calculate word positions
    space_w = draw.textlength(" ", font=font)
    word_widths = [draw.textlength(w, font=font) for w in words]
    total_text_w = sum(word_widths) + (len(words) - 1) * space_w

    # Center horizontally and vertically
    start_x = (card_w - total_text_w) // 2
    y_pos = (card_h - 75) // 2

    # Draw frosted glass container pill
    pad_x = 36
    pad_y = 16
    pill_box = [
        start_x - pad_x,
        y_pos - pad_y,
        start_x + total_text_w + pad_x,
        y_pos + 75 + pad_y
    ]
    # Dark translucent pill with subtle cyan/neon outline
    draw.rounded_rectangle(
        pill_box,
        radius=20,
        fill=(10, 15, 28, 225),
        outline=(0, 240, 255, 140) if is_highlight else (255, 255, 255, 50),
        width=3 if is_highlight else 2
    )

    # Render each word
    curr_x = start_x
    for i, word in enumerate(words):
        # Color coding: First word neon yellow (#FFE600), remaining white
        if i == 0 or is_highlight:
            text_color = (255, 230, 0, 255) # Neon Yellow
        elif "?" in word or "!" in word:
            text_color = (0, 245, 255, 255) # Neon Cyan
        else:
            text_color = (255, 255, 255, 255) # Crisp White

        # Draw with thick black stroke
        draw.text(
            (curr_x, y_pos),
            word,
            font=font,
            fill=text_color,
            stroke_width=6,
            stroke_fill=(0, 0, 0, 255)
        )
        curr_x += word_widths[i] + space_w

    return img

def create_bouncy_subtitle_clip(chunk_text: str, duration: float, is_highlight: bool = False) -> VideoClip:
    """
    Creates a VideoClip for a subtitle chunk with MoneyPrinterTurbo spring bounce pop on appearance.
    """
    base_card = create_styled_subtitle_card(chunk_text, is_highlight)
    w, h = base_card.size
    anim_duration = min(0.20, duration * 0.5)

    def make_frame(t):
        if t >= anim_duration:
            return np.array(base_card)

        progress = t / max(anim_duration, 0.01)
        scale = get_spring_scale(progress)

        scaled_w = max(1, int(w * scale))
        scaled_h = max(1, int(h * scale))

        scaled_card = base_card.resize((scaled_w, scaled_h), Image.Resampling.BILINEAR)

        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ox = (w - scaled_w) // 2
        oy = (h - scaled_h) // 2
        canvas.paste(scaled_card, (ox, oy))
        return np.array(canvas)

    return VideoClip(make_frame, duration=duration).with_fps(30)

def split_into_punchy_chunks(text: str, max_words_per_chunk: int = 3) -> list[str]:
    """Splits text into short 2 to 3 word punchy chunks for fast viral pacing."""
    words = text.strip().split()
    chunks = []
    current = []

    for word in words:
        current.append(word)
        if len(current) >= max_words_per_chunk or word.endswith(("?", "!", "।", ".")):
            chunks.append(" ".join(current))
            current = []

    if current:
        chunks.append(" ".join(current))
    return chunks

def generate_subtitle_clips(script_text: str, total_duration: float) -> list[VideoClip]:
    """
    Generates word-chunked bouncy subtitles positioned at lower-center of 9:16 Shorts.
    """
    chunks = split_into_punchy_chunks(script_text, max_words_per_chunk=3)
    if not chunks:
        return []

    total_words = sum(len(c.split()) for c in chunks)
    time_per_word = total_duration / max(total_words, 1)

    clips = []
    current_time = 0.0

    for i, chunk in enumerate(chunks):
        word_count = len(chunk.split())
        chunk_dur = word_count * time_per_word
        is_hl = ("?" in chunk or "!" in chunk or i % 3 == 0)

        sub_clip = (
            create_bouncy_subtitle_clip(chunk, chunk_dur, is_highlight=is_hl)
            .with_start(current_time)
            .with_duration(chunk_dur)
            .with_position(("center", VIDEO_HEIGHT - 440))
        )
        clips.append(sub_clip)
        current_time += chunk_dur

    return clips

def format_srt_time(seconds: float) -> str:
    """Formats seconds into standard SRT timestamp HH:MM:SS,mmm."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms >= 1000:
        s += 1
        ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def export_subtitles_to_srt(script_text: str, total_duration: float, output_path: str) -> str:
    """
    Exports synchronized Hindi subtitle chunks into a standard .srt subtitle file.
    """
    chunks = split_into_punchy_chunks(script_text, max_words_per_chunk=4)
    if not chunks:
        chunks = [script_text.strip()]

    total_words = sum(len(c.split()) for c in chunks)
    time_per_word = total_duration / max(total_words, 1)

    lines = []
    current_time = 0.0

    for i, chunk in enumerate(chunks, 1):
        word_count = len(chunk.split())
        chunk_dur = word_count * time_per_word
        start_ts = format_srt_time(current_time)
        end_ts = format_srt_time(current_time + chunk_dur)

        lines.append(f"{i}")
        lines.append(f"{start_ts} --> {end_ts}")
        lines.append(chunk.strip())
        lines.append("")

        current_time += chunk_dur

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[Subtitle Engine] Exported subtitles to: {out_file.name}")
    return str(out_file)

