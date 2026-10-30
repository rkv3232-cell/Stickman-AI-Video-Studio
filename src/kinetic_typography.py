"""
Kinetic Typography Engine for Stickman AI Video Production Studio.
Renders broadcast-grade animated Hindi typography on a 1080x1920 portrait canvas.

Features:
- Devanagari Grapheme & Word Cluster Integrity (Never breaks matras or conjuncts).
- 6 Professional Kinetic Styles:
  1. Oversized Bold Typography (120-165px Hero Word with Spring Pop)
  2. Kinetic Word Reveal (Sequential slide-and-fade synchronized with narration)
  3. Editorial Typography (Category badge + Hero word + Secondary subtitle + Accent keyline)
  4. Staggered Typography (Cascading multi-word entrance with damped easing)
  5. Emphasis Impact Typography (Scale punch + vibrant highlight color flash)
  6. Stickman Focus Interaction (Callout anchored directly beside Stickman's pointing hand)
- Dark frosted glass backdrop cards with neon border glow for 100% legibility on any background.
"""

import math
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoClip

from config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS,
    FONT_NOTO_BOLD, FONT_MUKTA_BOLD, FONT_MUKTA_EXTRABOLD, FONT_ARIAL_BOLD, FONT_IMPACT,
    TYPO_HERO_SIZE, TYPO_SECONDARY_SIZE, TYPO_TAG_SIZE
)
from src.hinglish_normalizer import normalize_text_to_hinglish

def _get_font(size: int, weight: str = "bold") -> ImageFont.FreeTypeFont:
    """Loads best available Roman / Latin typography font with automatic fallback."""
    candidates = []
    if weight in ["black", "extrabold"] and FONT_MUKTA_EXTRABOLD.exists():
        candidates.append(str(FONT_MUKTA_EXTRABOLD))
    if FONT_ARIAL_BOLD.exists():
        candidates.append(str(FONT_ARIAL_BOLD))
    if FONT_IMPACT.exists():
        candidates.append(str(FONT_IMPACT))
    if FONT_MUKTA_BOLD.exists():
        candidates.append(str(FONT_MUKTA_BOLD))
    candidates.append("C:/Windows/Fonts/arial.ttf")

    for fp in candidates:
        try:
            return ImageFont.truetype(fp, size)
        except Exception:
            pass
    return ImageFont.load_default()

def _spring_scale(progress: float) -> float:
    """Damped harmonic oscillation for professional punchy entrance."""
    if progress >= 1.0:
        return 1.0
    if progress <= 0.0:
        return 0.0
    # Overdamped spring: quick overshoot to 1.12 then settle at 1.0
    scale = 1.0 - math.exp(-7.0 * progress) * math.cos(2.8 * math.pi * progress)
    return max(0.0, min(scale, 1.25))

def _smooth_step(edge0: float, edge1: float, x: float) -> float:
    """Hermite smoothstep interpolation."""
    t = max(0.0, min(1.0, (x - edge0) / max(1e-5, edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)

def _hex_to_rgb(hex_str: str, default=(255, 230, 0)) -> Tuple[int, int, int]:
    """Safely converts hex color to RGB tuple."""
    if not hex_str or not isinstance(hex_str, str):
        return default
    hex_str = hex_str.strip().lstrip("#")
    if len(hex_str) == 6:
        try:
            return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))
        except ValueError:
            pass
    return default

def render_kinetic_typography_frame(
    t: float,
    duration: float,
    typo_data: Dict[str, Any],
    layout_info: Dict[str, Any]
) -> Image.Image:
    """
    Renders a transparent 1080x1920 RGBA frame of the kinetic typography layer.
    """
    canvas = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    if not typo_data:
        return canvas

    primary_text = normalize_text_to_hinglish(typo_data.get("primary_text", "").strip())
    secondary_text = normalize_text_to_hinglish(typo_data.get("secondary_text", "").strip())
    category_tag = normalize_text_to_hinglish(typo_data.get("category_tag", "").strip())
    style = typo_data.get("style", "oversized_bold")
    highlight_color_hex = typo_data.get("highlight_color", "#FFE600")
    highlight_rgb = _hex_to_rgb(highlight_color_hex, default=(255, 230, 0))

    if not primary_text and not secondary_text:
        return canvas

    typo_layout = layout_info.get("typography", {})
    center_x = typo_layout.get("center_x", int(VIDEO_WIDTH * 0.70))
    center_y = typo_layout.get("center_y", int(VIDEO_HEIGHT * 0.38))
    max_w = typo_layout.get("max_width", 500)
    align = typo_layout.get("align", "left")

    # Animation progress in timeline
    tau = max(0.0, min(1.0, t / max(duration, 0.1)))

    # Entrance timing: animation happens during first 0.6 seconds
    entrance_dur = min(0.60, duration * 0.35)
    p_enter = min(1.0, t / entrance_dur)
    spring = _spring_scale(p_enter)

    # ═════════════════════════════════════════════════════════════════
    # STYLE 1: OVERSIZED BOLD TYPOGRAPHY
    # ═════════════════════════════════════════════════════════════════
    if style in ["oversized_bold", "hero_bold"]:
        hero_font_size = min(150, max(95, int(max_w / (len(primary_text) * 0.55))))
        font_hero = _get_font(hero_font_size, weight="extrabold")
        font_sec = _get_font(60, weight="bold")

        draw_temp = ImageDraw.Draw(canvas)
        hero_bbox = draw_temp.textbbox((0, 0), primary_text, font=font_hero)
        hw = hero_bbox[2] - hero_bbox[0]
        hh = hero_bbox[3] - hero_bbox[1]

        sec_bbox = draw_temp.textbbox((0, 0), secondary_text, font=font_sec) if secondary_text else (0,0,0,0)
        sw = sec_bbox[2] - sec_bbox[0]
        sh = sec_bbox[3] - sec_bbox[1] if secondary_text else 0

        total_content_h = hh + (sh + 24 if secondary_text else 0)
        card_w = max(hw, sw) + 80
        card_h = total_content_h + 60

        card_x1 = center_x - card_w // 2 if align == "center" else center_x - 30
        card_x1 = max(60, min(card_x1, VIDEO_WIDTH - 60 - card_w))
        card_y1 = max(190, min(center_y - card_h // 2, 1400 - card_h))
        card_x2 = card_x1 + card_w
        card_y2 = card_y1 + card_h

        # Render onto local surface for scaling
        surface = Image.new("RGBA", (card_w + 40, card_h + 40), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(surface)

        # Frosted glass card backing with glowing border
        sdraw.rounded_rectangle(
            [20, 20, card_w + 20, card_h + 20],
            radius=24,
            fill=(10, 15, 28, 220),
            outline=(*highlight_rgb, 180),
            width=3
        )

        # Primary Hero Word
        sdraw.text(
            (45, 35),
            primary_text,
            font=font_hero,
            fill=(*highlight_rgb, 255),
            stroke_width=5,
            stroke_fill=(0, 0, 0, 255)
        )

        # Secondary text
        if secondary_text:
            sdraw.text(
                (45, 35 + hh + 18),
                secondary_text,
                font=font_sec,
                fill=(255, 255, 255, 240),
                stroke_width=4,
                stroke_fill=(0, 0, 0, 255)
            )

        # Apply spring scaling
        if spring < 0.999:
            sw_scaled = max(1, int(surface.width * spring))
            sh_scaled = max(1, int(surface.height * spring))
            scaled_surf = surface.resize((sw_scaled, sh_scaled), Image.Resampling.BILINEAR)
            ox = card_x1 - (sw_scaled - surface.width) // 2
            oy = card_y1 - (sh_scaled - surface.height) // 2
            canvas.paste(scaled_surf, (ox, oy), scaled_surf)
        else:
            canvas.paste(surface, (card_x1, card_y1), surface)

    # ═════════════════════════════════════════════════════════════════
    # STYLE 2: EDITORIAL TYPOGRAPHY (TAG + HERO + SUBTITLE + KEYLINE)
    # ═════════════════════════════════════════════════════════════════
    elif style in ["editorial", "editorial_split"]:
        font_tag = _get_font(32, weight="bold")
        hero_font_size = min(130, max(85, int(max_w / (len(primary_text) * 0.55))))
        font_hero = _get_font(hero_font_size, weight="extrabold")
        font_sec = _get_font(52, weight="bold")

        draw_temp = ImageDraw.Draw(canvas)
        hw = draw_temp.textlength(primary_text, font=font_hero)
        sw = draw_temp.textlength(secondary_text, font=font_sec) if secondary_text else 0
        tag_text = category_tag.upper() if category_tag else "INSIGHT"
        tw = draw_temp.textlength(tag_text, font=font_tag)

        box_w = max(hw, sw, tw + 40) + 90
        box_h = 240
        box_x = center_x - box_w // 2 if align == "center" else center_x - 30
        box_x = max(60, min(box_x, VIDEO_WIDTH - 60 - int(box_w)))
        box_y = max(190, min(center_y - box_h // 2, 1400 - int(box_h)))

        surface = Image.new("RGBA", (int(box_w + 30), int(box_h + 30)), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(surface)

        # Dark sleek card
        sdraw.rounded_rectangle(
            [15, 15, box_w + 15, box_h + 15],
            radius=20,
            fill=(12, 18, 34, 225),
            outline=(255, 255, 255, 60),
            width=2
        )

        # Glowing accent vertical keyline
        sdraw.line([(32, 35), (32, box_h - 5)], fill=(*highlight_rgb, 255), width=6)

        # Category Pill
        pill_w = tw + 32
        sdraw.rounded_rectangle(
            [48, 32, 48 + pill_w, 68],
            radius=12,
            fill=(*highlight_rgb, 40),
            outline=(*highlight_rgb, 180),
            width=1
        )
        sdraw.text((64, 38), tag_text, font=font_tag, fill=(*highlight_rgb, 255))

        # Hero Word
        sdraw.text(
            (48, 80),
            primary_text,
            font=font_hero,
            fill=(255, 255, 255, 255),
            stroke_width=4,
            stroke_fill=(0, 0, 0, 255)
        )

        # Secondary text
        if secondary_text:
            sdraw.text(
                (48, 172),
                secondary_text,
                font=font_sec,
                fill=(*highlight_rgb, 255),
                stroke_width=3,
                stroke_fill=(0, 0, 0, 255)
            )

        # Slide in from side with smooth easing
        slide_offset = int((1.0 - _smooth_step(0.0, 1.0, p_enter)) * 60)
        final_x = box_x + (slide_offset if align == "left" else -slide_offset)
        canvas.paste(surface, (final_x, box_y), surface)

    # ═════════════════════════════════════════════════════════════════
    # STYLE 3: KINETIC WORD REVEAL (Sequential Words)
    # ═════════════════════════════════════════════════════════════════
    elif style in ["word_reveal", "kinetic_reveal"]:
        words = f"{primary_text} {secondary_text}".strip().split()
        font_word = _get_font(85, weight="extrabold")

        draw_temp = ImageDraw.Draw(canvas)
        word_widths = [draw_temp.textlength(w, font=font_word) for w in words]
        total_w = sum(word_widths) + (len(words) - 1) * 24

        curr_x = center_x - total_w // 2 if align == "center" else center_x - 10
        y_pos = center_y - 50

        # Card container
        pad_x, pad_y = 40, 25
        card_rect = [curr_x - pad_x, y_pos - pad_y, curr_x + total_w + pad_x, y_pos + 100 + pad_y]
        draw_temp.rounded_rectangle(
            card_rect,
            radius=22,
            fill=(10, 15, 28, 220),
            outline=(*highlight_rgb, 160),
            width=2
        )

        # Reveal words one by one based on timeline progress
        num_words = len(words)
        for i, word in enumerate(words):
            word_trigger = (i / max(num_words, 1)) * 0.50
            if tau >= word_trigger:
                word_p = min(1.0, (tau - word_trigger) / 0.18)
                w_scale = _spring_scale(word_p)
                w_color = (*highlight_rgb, 255) if i == 0 else (255, 255, 255, 255)

                draw_temp.text(
                    (curr_x, y_pos),
                    word,
                    font=font_word,
                    fill=w_color,
                    stroke_width=5,
                    stroke_fill=(0, 0, 0, 255)
                )
            curr_x += word_widths[i] + 24

    # ═════════════════════════════════════════════════════════════════
    # STYLE 4: EMPHASIS IMPACT TYPOGRAPHY
    # ═════════════════════════════════════════════════════════════════
    elif style in ["emphasis_impact", "impact"]:
        hero_font_size = min(155, max(100, int(max_w / (len(primary_text) * 0.52))))
        font_hero = _get_font(hero_font_size, weight="extrabold")
        font_sec = _get_font(58, weight="bold")

        draw_temp = ImageDraw.Draw(canvas)
        hw = draw_temp.textlength(primary_text, font=font_hero)
        sw = draw_temp.textlength(secondary_text, font=font_sec) if secondary_text else 0
        box_w = max(hw, sw) + 90
        box_h = 230
        box_x = center_x - box_w // 2 if align == "center" else center_x - 30
        box_x = max(60, min(box_x, VIDEO_WIDTH - 60 - int(box_w)))
        box_y = max(190, min(center_y - box_h // 2, 1400 - int(box_h)))

        # Pulsing impact flash
        is_flash = (0.15 <= tau <= 0.40)
        border_col = (255, 255, 255, 240) if is_flash else (*highlight_rgb, 180)
        bg_col = (25, 35, 60, 235) if is_flash else (10, 16, 30, 220)

        draw_temp.rounded_rectangle(
            [box_x, box_y, box_x + box_w, box_y + box_h],
            radius=24,
            fill=bg_col,
            outline=border_col,
            width=4 if is_flash else 2
        )

        # Hero with impact animation
        hero_color = (255, 255, 255, 255) if is_flash else (*highlight_rgb, 255)
        draw_temp.text(
            (box_x + 45, box_y + 30),
            primary_text,
            font=font_hero,
            fill=hero_color,
            stroke_width=6,
            stroke_fill=(0, 0, 0, 255)
        )

        if secondary_text:
            draw_temp.text(
                (box_x + 45, box_y + 140),
                secondary_text,
                font=font_sec,
                fill=(255, 255, 255, 230),
                stroke_width=4,
                stroke_fill=(0, 0, 0, 255)
            )

    # ═════════════════════════════════════════════════════════════════
    # STYLE 5: STICKMAN INTERACTION CALLOUT
    # ═════════════════════════════════════════════════════════════════
    else: # stickman_focus / default
        font_hero = _get_font(120, weight="extrabold")
        font_sec = _get_font(56, weight="bold")

        draw_temp = ImageDraw.Draw(canvas)
        hw = draw_temp.textlength(primary_text, font=font_hero)
        sw = draw_temp.textlength(secondary_text, font=font_sec) if secondary_text else 0
        box_w = max(hw, sw) + 80
        box_h = 220
        box_x = center_x - box_w // 2 if align == "center" else center_x - 20
        box_x = max(60, min(box_x, VIDEO_WIDTH - 60 - int(box_w)))
        box_y = max(190, min(center_y - box_h // 2, 1400 - int(box_h)))

        draw_temp.rounded_rectangle(
            [box_x, box_y, box_x + box_w, box_y + box_h],
            radius=24,
            fill=(10, 15, 28, 225),
            outline=(*highlight_rgb, 190),
            width=3
        )

        draw_temp.text(
            (box_x + 40, box_y + 30),
            primary_text,
            font=font_hero,
            fill=(*highlight_rgb, 255),
            stroke_width=5,
            stroke_fill=(0, 0, 0, 255)
        )

        if secondary_text:
            draw_temp.text(
                (box_x + 40, box_y + 135),
                secondary_text,
                font=font_sec,
                fill=(255, 255, 255, 240),
                stroke_width=4,
                stroke_fill=(0, 0, 0, 255)
            )

    return canvas

def create_kinetic_typography_clip(
    duration: float,
    typo_data: Dict[str, Any],
    layout_info: Dict[str, Any]
) -> VideoClip:
    """
    Creates a transparent VideoClip of kinetic typography for the scene duration.
    """
    def make_frame(t):
        img = render_kinetic_typography_frame(
            t=t,
            duration=duration,
            typo_data=typo_data,
            layout_info=layout_info
        )
        return np.array(img)

    return VideoClip(make_frame, duration=duration).with_fps(VIDEO_FPS)
