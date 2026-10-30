"""
High-Retention Procedural Motion Scenes for Raj Everyway Study.
Provides dynamic, topic-driven backgrounds:
1. create_modern_studio_scene: 3D perspective floor grid receding into midnight horizon with ambient glowing lights.
2. create_growth_infographic_scene: Dynamic Indian AI $1 Trillion growth curve, rising economic bars, sector growth telemetry.
3. create_multi_industry_scene: 3D floating sector cards (Healthcare AI, Smart AgriTech, Developer Power).
4. create_workspace_studio_scene: Modern clean creator tech studio with ambient neon lighting.
5. create_cyber_subscribe_outro: Celebratory golden particle bursts & animated YouTube subscribe CTA.

Zero fake terminal code. Zero random matrix code rain.
100% focused on storytelling, clarity, and visual impact.
"""

import sys
import math
import random
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Ensure root directory is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from moviepy import VideoClip, concatenate_videoclips
from config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, CHANNEL_NAME

FONT_MAIN = "C:/Windows/Fonts/arial.ttf"
FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        try:
            return ImageFont.truetype(FONT_MAIN, size)
        except Exception:
            return ImageFont.load_default()

# =========================================================================
# 1. SCENE 1: MODERN PERSPECTIVE 3D STUDIO (Cinematic Midnight Depth)
# =========================================================================
def create_modern_studio_scene(duration: float) -> VideoClip:
    """
    Sleek studio with 3D perspective grid floor receding into horizon,
    ambient cyan/violet lighting, and gentle forward camera motion.
    """
    horizon_y = int(VIDEO_HEIGHT * 0.48)
    num_particles = 40
    np.random.seed(42)
    part_x = np.random.uniform(50, VIDEO_WIDTH - 50, num_particles)
    part_y = np.random.uniform(100, horizon_y, num_particles)
    part_speeds = np.random.uniform(10, 30, num_particles)

    def make_frame(t):
        # Deep midnight gradient
        img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (10, 16, 30))
        draw = ImageDraw.Draw(img)

        # Ambient background glow at horizon
        glow_r = int(320 + 20 * math.sin(t * 2.0))
        draw.ellipse(
            [VIDEO_WIDTH // 2 - glow_r, horizon_y - glow_r // 3, VIDEO_WIDTH // 2 + glow_r, horizon_y + glow_r // 3],
            fill=(20, 38, 70)
        )

        # 3D Perspective Grid Floor
        # Transverse horizontal lines with exponential perspective spacing
        grid_offset = (t * 40.0) % 50.0
        for i in range(16):
            p = (i * 35.0 + grid_offset) / 550.0
            if p > 0:
                y = horizon_y + int(math.pow(p, 1.7) * (VIDEO_HEIGHT - horizon_y))
                if y < VIDEO_HEIGHT:
                    alpha_bright = min(220, int(p * 220))
                    draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(15, alpha_bright // 3 + 20, alpha_bright // 2 + 40), width=max(1, int(p * 2)))

        # Perspective longitudinal lines vanishing at center horizon
        vanish_x, vanish_y = VIDEO_WIDTH // 2, horizon_y
        for x_floor in range(-VIDEO_WIDTH // 2, VIDEO_WIDTH + VIDEO_WIDTH // 2, 90):
            draw.line([(vanish_x, vanish_y), (x_floor, VIDEO_HEIGHT)], fill=(25, 45, 75), width=1)

        # Drifting ambient light orbs in the air
        for pi in range(num_particles):
            curr_py = (part_y[pi] - t * part_speeds[pi]) % (horizon_y - 80) + 80
            draw.ellipse([part_x[pi] - 2, curr_py - 2, part_x[pi] + 2, curr_py + 2], fill=(56, 189, 248, 180))

        return np.array(img)

    return VideoClip(make_frame, duration=duration).with_fps(VIDEO_FPS)

# =========================================================================
# 2. SCENE 2: INDIAN AI GROWTH INFOGRAPHIC SCENE ($1T Economy)
# =========================================================================
def create_growth_infographic_scene(duration: float) -> VideoClip:
    """
    Topic-matched Indian AI Growth visual:
    Upward growth trendline, rising metrics, Indian tech hub badges.
    """
    font_header = get_font(FONT_BOLD, 42)
    font_stat = get_font(FONT_BOLD, 56)
    font_sub = get_font(FONT_MAIN, 26)

    def make_frame(t):
        img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (8, 14, 28))
        draw = ImageDraw.Draw(img)

        # Top Banner: INDIA AI ECONOMY 2026
        banner_y = 200
        draw.rounded_rectangle([70, banner_y, VIDEO_WIDTH - 70, banner_y + 85], radius=16, fill=(15, 23, 42), outline=(56, 189, 248), width=2)
        draw.text((105, banner_y + 20), "INDIA AI FUTURE 2026", font=font_header, fill=(255, 255, 255))

        # Big Highlight Metric Card: $1 TRILLION GOAL
        card_y = 320
        card_pulse = 1.0 + 0.02 * math.sin(t * 3.0)
        draw.rounded_rectangle([70, card_y, VIDEO_WIDTH - 70, card_y + 200], radius=20, fill=(18, 30, 56), outline=(245, 158, 11), width=2)
        draw.text((105, card_y + 24), "PROJECTED MARKET IMPACT", font=font_sub, fill=(200, 215, 235))
        draw.text((105, card_y + 65), "$1 TRILLION", font=font_stat, fill=(245, 158, 11))
        draw.text((105, card_y + 140), "+35% CAGR Growth Across Healthcare & Agri", font=font_sub, fill=(56, 189, 248))

        # Upward Dynamic Growth Curve
        curve_start_x = 100
        curve_end_x = VIDEO_WIDTH - 100
        curve_base_y = 800
        curve_points = []
        progress = min(1.0, 0.3 + (t / max(duration, 0.1)) * 0.7)

        for step_i in range(25):
            frac = step_i / 24.0
            if frac <= progress:
                cx = int(curve_start_x + (curve_end_x - curve_start_x) * frac)
                cy = int(curve_base_y - math.pow(frac, 1.8) * 220)
                curve_points.append((cx, cy))

        if len(curve_points) > 1:
            for ci in range(len(curve_points) - 1):
                draw.line([curve_points[ci], curve_points[ci + 1]], fill=(0, 240, 255), width=4)
            # Leading glowing point
            lead_x, lead_y = curve_points[-1]
            draw.ellipse([lead_x - 8, lead_y - 8, lead_x + 8, lead_y + 8], fill=(255, 255, 255), outline=(0, 240, 255), width=2)

        # Tech Hub Chips at bottom
        hubs = ["Bengaluru", "Hyderabad", "NCR Hub", "Pune Tech"]
        chip_y = 850
        for hi, hub in enumerate(hubs):
            hx = 70 + hi * 230
            draw.rounded_rectangle([hx, chip_y, hx + 200, chip_y + 44], radius=12, fill=(20, 32, 54), outline=(71, 85, 105))
            draw.text((hx + 28, chip_y + 10), hub, font=font_sub, fill=(200, 220, 245))

        return np.array(img)

    return VideoClip(make_frame, duration=duration).with_fps(VIDEO_FPS)

# =========================================================================
# 3. SCENE 3: MULTI-INDUSTRY TRANSFORMATION SCENE (Healthcare, Agri, Tech)
# =========================================================================
def create_multi_industry_scene(duration: float) -> VideoClip:
    """
    3D floating cards representing real Indian AI sectors:
    Healthcare, Smart Agriculture, and Developer Power.
    """
    font_title = get_font(FONT_BOLD, 38)
    font_sub = get_font(FONT_MAIN, 26)

    cards = [
        {"title": "HEALTHCARE AI", "sub": "Instant Remote Diagnostics", "col": (239, 68, 68), "y": 280},
        {"title": "SMART AGRITECH", "sub": "Drone Crop Monitoring & Yield", "col": (34, 197, 94), "y": 480},
        {"title": "SOFTWARE & CODING", "sub": "10x Faster AI-Powered Devs", "col": (56, 189, 248), "y": 680}
    ]

    def make_frame(t):
        img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (10, 16, 28))
        draw = ImageDraw.Draw(img)

        # Ambient studio lighting
        draw.ellipse([VIDEO_WIDTH // 2 - 250, 400, VIDEO_WIDTH // 2 + 250, 900], fill=(16, 26, 48))

        # Floating Industry Cards with smooth floating physics
        for i, c in enumerate(cards):
            c_float = math.sin(t * 3.0 + i * 1.8) * 10.0
            cx1 = 80 + int(math.sin(t * 2.0 + i) * 6.0)
            cy1 = int(c["y"] + c_float)
            cx2 = VIDEO_WIDTH - 80
            cy2 = cy1 + 150

            # Glass card background
            draw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=18, fill=(18, 26, 44), outline=c["col"], width=2)
            # Glowing left accent bar
            draw.rounded_rectangle([cx1 + 6, cy1 + 6, cx1 + 18, cy2 - 6], radius=6, fill=c["col"])
            # Content
            draw.text((cx1 + 40, cy1 + 28), c["title"], font=font_title, fill=(255, 255, 255))
            draw.text((cx1 + 40, cy1 + 82), c["sub"], font=font_sub, fill=(180, 205, 230))

        return np.array(img)

    return VideoClip(make_frame, duration=duration).with_fps(VIDEO_FPS)

# =========================================================================
# 4. SCENE 4: WORKSPACE STUDIO SCENE (Clean Modern Tech Studio)
# =========================================================================
def create_workspace_studio_scene(duration: float) -> VideoClip:
    """
    Modern minimalist studio with ambient lighting and clean perspective depth.
    Ideal backdrop for Stickman thinking, sitting, and working.
    """
    def make_frame(t):
        img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (12, 18, 32))
        draw = ImageDraw.Draw(img)

        # Ambient lighting gradient
        for ring_i in range(3):
            rad = 280 + ring_i * 90
            draw.ellipse(
                [VIDEO_WIDTH // 2 - rad, 450 - rad, VIDEO_WIDTH // 2 + rad, 450 + rad],
                fill=(16 + ring_i * 4, 24 + ring_i * 6, 42 + ring_i * 8)
            )

        # Subtle vertical studio architectural pillars
        for px in [120, VIDEO_WIDTH - 120]:
            draw.line([(px, 150), (px, 950)], fill=(30, 41, 59), width=2)

        return np.array(img)

    return VideoClip(make_frame, duration=duration).with_fps(VIDEO_FPS)

# =========================================================================
# 5. SCENE 5: CELEBRATION OUTRO CTA SCENE (Golden Sparkles & Subscribe)
# =========================================================================
def create_cyber_subscribe_outro(duration: float) -> VideoClip:
    """
    Celebratory outro background with glowing particle sparkles,
    vibrant YouTube subscribe card, and channel branding.
    """
    font_cta = get_font(FONT_BOLD, 52)
    font_sub = get_font(FONT_MAIN, 36)

    def make_frame(t):
        img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (10, 16, 32))
        draw = ImageDraw.Draw(img)

        # Concentric golden energy rings
        for ring_i in range(4):
            ring_rad = int((t * 110 + ring_i * 85) % 400) + 70
            draw.ellipse(
                [VIDEO_WIDTH // 2 - ring_rad, 720 - ring_rad, VIDEO_WIDTH // 2 + ring_rad, 720 + ring_rad],
                outline=(245, 158, 11),
                width=max(1, 3 - ring_i)
            )

        # Pulsating Subscribe Card
        pulse = 1.0 + 0.04 * math.sin(t * 6.0)
        btn_w = int(520 * pulse)
        btn_h = int(120 * pulse)
        bx1 = (VIDEO_WIDTH - btn_w) // 2
        by1 = 720 - btn_h // 2
        bx2 = bx1 + btn_w
        by2 = by1 + btn_h

        # Crimson Red Subscribe Pill
        draw.rounded_rectangle([bx1, by1, bx2, by2], radius=32, fill=(220, 38, 38), outline=(255, 255, 255), width=3)
        draw.text((bx1 + int(50 * pulse), by1 + int(28 * pulse)), "SUBSCRIBE NOW", font=font_cta, fill=(255, 255, 255))

        # Channel text underneath
        draw.text((VIDEO_WIDTH // 2 - 210, 880), CHANNEL_NAME, font=font_sub, fill=(56, 189, 248))

        return np.array(img)

    return VideoClip(make_frame, duration=duration).with_fps(VIDEO_FPS)

def build_full_motion_background(total_duration: float, scene_count: int = 5) -> tuple[VideoClip, list[float]]:
    """
    Creates a multi-scene seamless full-motion 30 FPS video background.
    """
    scene_dur = total_duration / float(scene_count)
    print(f"Generating {scene_count} Full-Motion Animated Video Scenes (~{scene_dur:.1f}s each)...")

    scene_pool = [
        create_modern_studio_scene(scene_dur),
        create_growth_infographic_scene(scene_dur),
        create_multi_industry_scene(scene_dur),
        create_workspace_studio_scene(scene_dur),
        create_cyber_subscribe_outro(scene_dur)
    ]
    chosen = scene_pool[:scene_count]
    if scene_count >= 5:
        chosen[-1] = create_cyber_subscribe_outro(scene_dur)

    final_motion_bg = concatenate_videoclips(chosen).with_duration(total_duration)
    transition_times = [i * scene_dur for i in range(scene_count)]
    return final_motion_bg, transition_times

if __name__ == "__main__":
    print("Testing Updated Procedural Motion Scenes...")
    sc1 = create_modern_studio_scene(2.0)
    sc2 = create_growth_infographic_scene(2.0)
    print("Motion scenes created successfully without fake terminal or matrix code!")
