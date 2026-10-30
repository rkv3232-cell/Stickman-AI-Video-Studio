"""
Multi-Style YouTube Thumbnail Designer for Raj Everyway Study.
Generates high-CTR thumbnails in 1080x1920 (Shorts) and 1280x720 (Standard 16:9).
Styles:
- 'impact': Huge outlined text with active word highlight & shock badge.
- 'cinematic': Moody dark gradient letterbox with sleek glowing typography.
- 'studio': Cyberpunk card with channel badge and neon audio spectrum bars.
"""

import os
import sys
import re
import math
from pathlib import Path

# Ensure root directory is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config import VIDEO_WIDTH, VIDEO_HEIGHT, FONT_PATH, CHANNEL_NAME

FONT_BOLD = "C:/Windows/Fonts/impact.ttf"
FONT_FALLBACK = "C:/Windows/Fonts/arialbd.ttf"
FONT_HINDI = "C:/Windows/Fonts/nirmala.ttf"

_HOOK_BADGES = ["SECRET", "TRUTH", "SHOCKING", "NEW AI", "ALERT", "2026", "MUST WATCH", "VIRAL"]

def _get_font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        try:
            return ImageFont.truetype(FONT_FALLBACK, size)
        except Exception:
            return ImageFont.load_default()

def _pick_hook_badge(title: str) -> str:
    upper = title.upper()
    for b in _HOOK_BADGES:
        if b in upper:
            return b
    return "NEW AI"

def generate_thumbnail(
    title: str,
    output_path: str,
    bg_image_path: str = None,
    style: str = "studio",
    is_portrait: bool = True
) -> str:
    """
    Renders high-converting YouTube thumbnail and saves as JPG.
    Returns the file path.
    """
    from src.hinglish_normalizer import normalize_text_to_hinglish
    title = normalize_text_to_hinglish(title)
    w = VIDEO_WIDTH if is_portrait else 1280
    h = VIDEO_HEIGHT if is_portrait else 720

    # 1. Base Canvas
    if bg_image_path and os.path.exists(bg_image_path):
        try:
            base = Image.open(bg_image_path).convert("RGB")
            # Fit and crop to w, h
            bw, bh = base.size
            scale = max(w / bw, h / bh)
            nw, nh = int(bw * scale), int(bh * scale)
            base = base.resize((nw, nh), Image.Resampling.LANCZOS)
            x_off = (nw - w) // 2
            y_off = (nh - h) // 2
            canvas = base.crop((x_off, y_off, x_off + w, y_off + h))
            # Darken slightly for readability
            canvas = Image.eval(canvas, lambda c: int(c * 0.70))
        except Exception:
            canvas = Image.new("RGB", (w, h), (10, 14, 26))
    else:
        # High-tech cyber gradient background
        canvas = Image.new("RGB", (w, h), (8, 12, 24))
        draw_bg = ImageDraw.Draw(canvas)
        # Gradient effect
        for y in range(h):
            ratio = y / float(h)
            r = int(8 + ratio * 15)
            g = int(12 + ratio * 20)
            b = int(24 + ratio * 45)
            draw_bg.line([(0, y), (w, y)], fill=(r, g, b))

    draw = ImageDraw.Draw(canvas)

    # 2. Channel Branding Badge (Top)
    font_brand = _get_font(FONT_HINDI, 38 if is_portrait else 28)
    badge_text = CHANNEL_NAME
    bbox = draw.textbbox((0, 0), badge_text, font=font_brand)
    bw_text = bbox[2] - bbox[0]
    bh_text = bbox[3] - bbox[1]
    
    pill_w = bw_text + 70
    pill_h = bh_text + 28
    px = (w - pill_w) // 2
    py = 100 if is_portrait else 40

    draw.rounded_rectangle([px, py, px + pill_w, py + pill_h], radius=18, fill=(12, 18, 36, 230), outline=(0, 240, 255, 200), width=2)
    draw.ellipse([px + 22 - 6, py + pill_h // 2 - 6, px + 22 + 6, py + pill_h // 2 + 6], fill=(239, 68, 68))
    draw.text((px + 44, py + (pill_h - bh_text) // 2 - 2), badge_text, font=font_brand, fill=(255, 255, 255))

    # 3. Clean Title & Extract Hook Words
    clean_title = re.sub(r'#\w+', '', title).strip()
    words = clean_title.split()
    if len(words) > 7:
        short_title = " ".join(words[:6]) + "..."
    else:
        short_title = clean_title

    # 4. Draw Style-Specific Elements
    font_title = _get_font(FONT_BOLD, 74 if is_portrait else 56)

    # Split into 2-3 lines
    lines = []
    curr_line = []
    for word in words[:8]:
        curr_line.append(word)
        if len(" ".join(curr_line)) > (18 if is_portrait else 24):
            lines.append(" ".join(curr_line))
            curr_line = []
    if curr_line:
        lines.append(" ".join(curr_line))

    # Center placement
    line_h = 95 if is_portrait else 75
    total_text_h = len(lines) * line_h
    start_y = (h // 2) - (total_text_h // 2) + (60 if is_portrait else 20)

    # Dark backdrop card for text
    card_margin = 50
    card_box = [card_margin, start_y - 30, w - card_margin, start_y + total_text_h + 30]
    draw.rounded_rectangle(card_box, radius=24, fill=(8, 12, 22, 220), outline=(0, 240, 255, 140), width=3)

    for i, line in enumerate(lines):
        line_bbox = draw.textbbox((0, 0), line, font=font_title)
        lw = line_bbox[2] - line_bbox[0]
        lx = (w - lw) // 2
        ly = start_y + i * line_h

        # Accent coloring
        line_color = (255, 230, 0) if i == 0 else ((0, 245, 255) if i == len(lines) - 1 else (255, 255, 255))

        # Thick black outline
        stroke_w = 6
        for dx in range(-stroke_w, stroke_w + 1):
            for dy in range(-stroke_w, stroke_w + 1):
                if dx * dx + dy * dy <= stroke_w * stroke_w:
                    draw.text((lx + dx, ly + dy), line, font=font_title, fill=(0, 0, 0))
        draw.text((lx, ly), line, font=font_title, fill=line_color)

    # 5. Hook Badge in Top Right Corner
    badge_label = _pick_hook_badge(title)
    font_badge = _get_font(FONT_BOLD, 36 if is_portrait else 28)
    bbox_b = draw.textbbox((0, 0), badge_label, font=font_badge)
    bw_badge = bbox_b[2] - bbox_b[0] + 40
    bh_badge = bbox_b[3] - bbox_b[1] + 20
    bx = w - bw_badge - 40
    by = 95 if is_portrait else 35

    draw.rounded_rectangle([bx, by, bx + bw_badge, by + bh_badge], radius=12, fill=(220, 38, 38), outline=(255, 255, 255), width=2)
    draw.text((bx + 20, by + 10), badge_label, font=font_badge, fill=(255, 255, 255))

    # 6. Save as PNG or JPG
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    if out_file.suffix.lower() == ".png":
        canvas.save(out_file, "PNG")
    else:
        canvas.save(out_file, "JPEG", quality=95)
    print(f"[Thumbnail Generated] -> {out_file.name} ({w}x{h})")
    return str(out_file)

if __name__ == "__main__":
    out = generate_thumbnail(
        title="DeepSeek vs ChatGPT Reality 🤖",
        output_path="output/test_thumb.jpg",
        is_portrait=True
    )
    print("Done:", out)
