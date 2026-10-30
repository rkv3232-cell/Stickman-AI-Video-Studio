"""
Visual Engine 2.0 for Raj Everyway Study.
Orchestrates backgrounds based on selected visual style:
- 'ai_cinematic': 100% Free AI Photorealistic Scene Art (Pollinations.ai Flux/Turbo) + Smooth Ken Burns Pan/Zoom!
- 'motion': Procedural 3D Cyberpunk, Neural Tunnel, Matrix Rain, IDE Terminal, Holographic Core.
- 'stock': Vertical Stock Video B-Roll (from assets/bg_videos or Pexels API).
- 'hybrid': Stock Video / AI Scene + Cyber HUD telemetry and scanline overlay.
"""

import os
import sys
import math
import random
import requests
from pathlib import Path
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Ensure root directory is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from moviepy import (
    VideoFileClip, VideoClip, CompositeVideoClip, concatenate_videoclips
)
from config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS,
    BG_VIDEOS_DIR, PEXELS_API_KEY
)
from src.motion_scenes import build_full_motion_background

# ══════════════════════════════════════════════════════════════
# 1. POLLINATIONS.AI FREE KEYLESS AI IMAGE GENERATOR
# ══════════════════════════════════════════════════════════════
def fetch_pollinations_ai_image(prompt: str, output_path: str, width: int = 1080, height: int = 1920) -> bool:
    """
    Downloads free AI photorealistic 9:16 artwork via Pollinations.ai (Flux/Turbo model).
    No API key required!
    """
    clean_prompt = f"{prompt}, cinematic lighting, photorealistic, 4k, hyper-detailed, vertical orientation 9:16, no text, no watermark"
    encoded = quote(clean_prompt[:400], safe="")
    
    # Try turbo first, fallback to flux
    models = ["turbo", "flux"]
    for model in models:
        url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&model={model}&nologo=true"
        try:
            r = requests.get(url, timeout=25)
            if r.status_code == 200 and len(r.content) > 10000:
                with open(output_path, "wb") as f:
                    f.write(r.content)
                # Verify valid image
                Image.open(output_path).verify()
                print(f"[Pollinations AI] Generated scene image: {Path(output_path).name} (model: {model})")
                return True
        except Exception as e:
            print(f"[Pollinations AI] Attempt with {model} failed: {e}")
            try:
                Path(output_path).unlink(missing_ok=True)
            except Exception:
                pass
    return False

# ══════════════════════════════════════════════════════════════
# 2. KEN BURNS MOTION EFFECT (Smooth Pan & Zoom on AI Images)
# ══════════════════════════════════════════════════════════════
def create_ken_burns_clip(image_path: str, duration: float, zoom_in: bool = True) -> VideoClip:
    """
    Converts a static 9:16 image into a dynamic, smooth Ken Burns motion video clip.
    """
    img = Image.open(image_path).convert("RGB")
    # Ensure exact dimensions
    if img.size != (VIDEO_WIDTH, VIDEO_HEIGHT):
        img = img.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.LANCZOS)
    
    img_np = np.array(img, dtype=np.uint8)
    h, w, _ = img_np.shape

    z_start = 1.00 if zoom_in else 1.15
    z_end = 1.15 if zoom_in else 1.00

    def make_frame(t):
        p = t / max(duration, 0.01)
        scale = z_start + (z_end - z_start) * p

        # Calculate crop window
        crop_w = int(w / scale)
        crop_h = int(h / scale)
        
        # Slight panning drift
        drift_x = int((w - crop_w) * (0.5 + 0.3 * math.sin(p * math.pi)))
        drift_y = int((h - crop_h) * (0.5 + 0.3 * math.cos(p * math.pi)))

        drift_x = max(0, min(drift_x, w - crop_w))
        drift_y = max(0, min(drift_y, h - crop_h))

        cropped = img_np[drift_y : drift_y + crop_h, drift_x : drift_x + crop_w]
        resized = Image.fromarray(cropped).resize((w, h), Image.Resampling.BILINEAR)
        return np.array(resized)

    return VideoClip(make_frame, duration=duration).with_fps(VIDEO_FPS)

def build_ai_cinematic_background(total_duration: float, visual_keywords: list[str]) -> tuple[VideoClip, list[float]]:
    """
    Generates 3 to 4 photorealistic AI images via Pollinations.ai and animates them with Ken Burns!
    """
    if not visual_keywords:
        visual_keywords = ["cyberpunk tech laboratory", "python code neural network", "holographic artificial intelligence", "youtube subscriber futuristic"]

    scene_count = min(len(visual_keywords), 4)
    scene_dur = total_duration / float(scene_count)
    clips = []
    transition_times = [0.0]
    curr_time = 0.0

    temp_img_dir = Path("assets/scenes")
    temp_img_dir.mkdir(parents=True, exist_ok=True)

    for i, kw in enumerate(visual_keywords[:scene_count]):
        img_file = temp_img_dir / f"ai_scene_{i+1}.jpg"
        this_dur = min(scene_dur, total_duration - curr_time)

        # Fetch image if not cached
        success = fetch_pollinations_ai_image(kw, str(img_file))
        if success:
            c = create_ken_burns_clip(str(img_file), this_dur, zoom_in=(i % 2 == 0))
            clips.append(c)
        else:
            # Fallback to procedural scene for this slot
            from src.motion_scenes import (
                create_modern_studio_scene, create_growth_infographic_scene,
                create_multi_industry_scene, create_cyber_subscribe_outro
            )
            fallbacks = [create_modern_studio_scene, create_growth_infographic_scene, create_multi_industry_scene, create_cyber_subscribe_outro]
            c = fallbacks[i % len(fallbacks)](this_dur)
            clips.append(c)

        curr_time += this_dur
        if curr_time < total_duration:
            transition_times.append(curr_time)

    final_bg = concatenate_videoclips(clips).with_duration(total_duration)
    return final_bg, transition_times

# ══════════════════════════════════════════════════════════════
# 3. PEXELS STOCK VIDEOS DOWNLOADER & FITTER
# ══════════════════════════════════════════════════════════════
def download_pexels_videos(keywords: list[str], target_dir: Path, max_videos: int = 3) -> list[Path]:
    """Downloads vertical (9:16 portrait) stock videos from Pexels API if PEXELS_API_KEY is available."""
    if not PEXELS_API_KEY:
        return []

    target_dir.mkdir(parents=True, exist_ok=True)
    headers = {"Authorization": PEXELS_API_KEY}
    downloaded = []

    for kw in keywords[:max_videos]:
        try:
            url = f"https://api.pexels.com/v1/videos/search?query={requests.utils.quote(kw)}&orientation=portrait&per_page=3"
            res = requests.get(url, headers=headers, timeout=12)
            if res.status_code == 200:
                data = res.json()
                videos = data.get("videos", [])
                for v in videos:
                    v_files = v.get("video_files", [])
                    hd_files = [f for f in v_files if f.get("width", 0) <= 1080 and f.get("link")]
                    if hd_files:
                        chosen = sorted(hd_files, key=lambda x: x.get("width", 0), reverse=True)[0]
                        v_name = f"pexels_{v['id']}.mp4"
                        v_path = target_dir / v_name
                        if not v_path.exists():
                            print(f"[Pexels Stock] Downloading: {v_name}...")
                            with requests.get(chosen["link"], stream=True, timeout=30) as r:
                                r.raise_for_status()
                                with open(v_path, "wb") as f:
                                    for chunk in r.iter_content(chunk_size=8192):
                                        f.write(chunk)
                        downloaded.append(v_path)
                        break
        except Exception as e:
            print(f"[Pexels Stock] Error: {e}")

    return downloaded

def fit_video_to_portrait(clip: VideoFileClip) -> VideoClip:
    """Resizes and center-crops any video clip to exact 1080x1920 (9:16 Shorts format)."""
    w, h = clip.size
    target_ratio = VIDEO_WIDTH / VIDEO_HEIGHT
    current_ratio = w / h

    if current_ratio > target_ratio:
        new_h = VIDEO_HEIGHT
        new_w = int(w * (new_h / h))
        resized = clip.resized(height=new_h)
        x_center = (new_w - VIDEO_WIDTH) // 2
        cropped = resized.cropped(x1=x_center, y1=0, x2=x_center + VIDEO_WIDTH, y2=VIDEO_HEIGHT)
    else:
        new_w = VIDEO_WIDTH
        new_h = int(h * (new_w / w))
        resized = clip.resized(width=new_w)
        y_center = (new_h - VIDEO_HEIGHT) // 2
        cropped = resized.cropped(x1=0, y1=y_center, x2=VIDEO_WIDTH, y2=y_center + VIDEO_HEIGHT)

    return cropped.with_fps(VIDEO_FPS)

def create_cyber_hud_overlay(duration: float) -> VideoClip:
    """Futuristic HUD telemetry overlay with glowing scanlines and corner brackets."""
    canvas = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    b_len = 40
    b_margin = 35
    w, h = VIDEO_WIDTH, VIDEO_HEIGHT
    b_color = (0, 240, 255, 120)

    draw.line([(b_margin, b_margin), (b_margin + b_len, b_margin)], fill=b_color, width=2)
    draw.line([(b_margin, b_margin), (b_margin, b_margin + b_len)], fill=b_color, width=2)
    draw.line([(w - b_margin - b_len, b_margin), (w - b_margin, b_margin)], fill=b_color, width=2)
    draw.line([(w - b_margin, b_margin), (w - b_margin, b_margin + b_len)], fill=b_color, width=2)
    draw.line([(b_margin, h - b_margin), (b_margin + b_len, h - b_margin)], fill=b_color, width=2)
    draw.line([(b_margin, h - b_margin), (b_margin, h - b_margin - b_len)], fill=b_color, width=2)
    draw.line([(w - b_margin - b_len, h - b_margin), (w - b_margin, h - b_margin)], fill=b_color, width=2)
    draw.line([(w - b_margin, h - b_margin), (w - b_margin, h - b_margin - b_len)], fill=b_color, width=2)

    hud_np = np.array(canvas)

    def make_frame(t):
        frame = hud_np.copy()
        if int(t * 15) % 2 == 0:
            frame[::6, :, 3] = np.clip(frame[::6, :, 3].astype(int) + 12, 0, 255)
        return frame

    return VideoClip(make_frame, duration=duration).with_fps(VIDEO_FPS)

# ══════════════════════════════════════════════════════════════
# 4. MASTER BACKGROUND BUILDER
# ══════════════════════════════════════════════════════════════
def build_background(
    total_duration: float,
    visual_style: str = "motion",
    visual_keywords: list[str] = None
) -> tuple[VideoClip, list[float]]:
    """
    Master background builder supporting:
    - 'ai_cinematic': Pollinations AI scene generation + Ken Burns
    - 'motion': Procedural 3D Cyberpunk
    - 'stock': Real Stock Videos (Pexels / local)
    - 'hybrid': Stock / AI + Cyber HUD
    """
    style = visual_style.lower()

    # 1. AI Cinematic Mode (Pollinations.ai)
    if style in ["ai_cinematic", "ai", "pollinations"]:
        print(f"[Visual Engine] Building AI Photorealistic Scenes via Pollinations.ai + Ken Burns...")
        return build_ai_cinematic_background(total_duration, visual_keywords)

    # 2. Stock Video Mode
    if style in ["stock", "hybrid"]:
        video_candidates = list(Path(BG_VIDEOS_DIR).glob("*.mp4")) + list(Path(BG_VIDEOS_DIR).glob("*.mov"))
        
        if not video_candidates and PEXELS_API_KEY and visual_keywords:
            print(f"[Visual Engine] Fetching stock videos for: {visual_keywords}...")
            video_candidates = download_pexels_videos(visual_keywords, BG_VIDEOS_DIR, max_videos=3)

        if video_candidates:
            print(f"[Visual Engine] Assembling {len(video_candidates)} Stock Video Clips...")
            clips = []
            transition_times = [0.0]
            curr_time = 0.0
            clip_dur = total_duration / float(min(len(video_candidates), 4))

            random.seed(42)
            selected_videos = video_candidates.copy()
            random.shuffle(selected_videos)

            for vid_path in selected_videos:
                if curr_time >= total_duration:
                    break
                try:
                    c = VideoFileClip(str(vid_path)).without_audio()
                    c_fit = fit_video_to_portrait(c)
                    this_dur = min(clip_dur, total_duration - curr_time)
                    if c_fit.duration < this_dur:
                        loops = math.ceil(this_dur / c_fit.duration)
                        c_fit = concatenate_videoclips([c_fit] * loops)
                    c_sub = c_fit.subclipped(0, this_dur)
                    clips.append(c_sub)
                    curr_time += this_dur
                    if curr_time < total_duration:
                        transition_times.append(curr_time)
                except Exception as e:
                    print(f"Error processing stock clip {vid_path}: {e}")

            if clips:
                stock_bg = concatenate_videoclips(clips).with_duration(total_duration)
                
                def darken_frame(im):
                    return (im * 0.72).astype(np.uint8)

                darkened_stock = stock_bg.image_transform(darken_frame)

                if style == "hybrid":
                    hud_overlay = create_cyber_hud_overlay(total_duration)
                    composite_bg = CompositeVideoClip([darkened_stock, hud_overlay], size=(VIDEO_WIDTH, VIDEO_HEIGHT))
                    return composite_bg, transition_times
                else:
                    return darkened_stock, transition_times

    # 3. Default: Full-Motion Cyberpunk
    print("[Visual Engine] Using Full-Motion Cyberpunk Procedural Scenes...")
    return build_full_motion_background(total_duration, scene_count=4)

# ══════════════════════════════════════════════════════════════
# 5. SCENE-WISE BACKGROUND BUILDER FOR STORYBOARD
# ══════════════════════════════════════════════════════════════
def create_sketch_notes_scene(duration: float, topic_cue: str = "") -> VideoClip:
    """
    Renders an educational Sketch-Notes card canvas:
    - Warm cream background (#F5F0E8)
    - Subtle pastel dot grid
    - Rounded white card frame with soft shadow
    - Hand-drawn decorative corner brackets
    """
    canvas_base = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (245, 240, 232))
    draw = ImageDraw.Draw(canvas_base)

    # Dot grid
    grid_gap = 48
    for gx in range(40, VIDEO_WIDTH - 40, grid_gap):
        for gy in range(160, VIDEO_HEIGHT - 300, grid_gap):
            draw.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=(210, 204, 195))

    # Main Card container
    card_x1, card_y1 = 60, 240
    card_x2, card_y2 = VIDEO_WIDTH - 60, VIDEO_HEIGHT - 380
    # Soft drop shadow
    draw.rounded_rectangle([card_x1 + 6, card_y1 + 8, card_x2 + 6, card_y2 + 8], radius=28, fill=(225, 218, 208))
    # Crisp white paper card
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=28, fill=(255, 255, 255), outline=(15, 23, 42), width=3)

    # Hand-drawn corner tape / doodle
    draw.rectangle([card_x1 + 40, card_y1 - 12, card_x1 + 100, card_y1 + 12], fill=(254, 240, 138)) # Yellow washi tape

    def make_frame(t):
        return np.array(canvas_base)

    return VideoClip(make_frame, duration=duration).with_fps(VIDEO_FPS)

def create_paper_collage_scene(duration: float, topic_cue: str = "") -> VideoClip:
    """
    Renders an artistic Paper Collage canvas:
    - Layered warm parchment background (#F4EEE2)
    - Cutout kraft paper and pastel sticky note layers with soft drop shadows
    - Tape accents and torn-paper organic edges
    """
    canvas = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (244, 238, 226))
    draw = ImageDraw.Draw(canvas)

    # Base kraft card
    card_x1, card_y1 = 70, 220
    card_x2, card_y2 = VIDEO_WIDTH - 70, VIDEO_HEIGHT - 360
    # Drop shadow
    draw.rounded_rectangle([card_x1 + 8, card_y1 + 10, card_x2 + 8, card_y2 + 10], radius=16, fill=(215, 206, 192))
    # Crisp textured paper
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=16, fill=(255, 252, 245), outline=(180, 168, 150), width=2)

    # Pastel Sticky Notes
    notes = [
        {"x": 100, "y": 280, "w": 280, "h": 120, "col": (254, 240, 138), "rot": -2},
        {"x": VIDEO_WIDTH - 380, "y": 420, "w": 260, "h": 130, "col": (187, 247, 208), "rot": 3},
        {"x": 120, "y": 580, "w": 300, "h": 120, "col": (191, 219, 254), "rot": -1}
    ]
    for n in notes:
        # Shadow
        draw.rounded_rectangle([n["x"] + 4, n["y"] + 6, n["x"] + n["w"] + 4, n["y"] + n["h"] + 6], radius=8, fill=(220, 212, 198))
        # Note
        draw.rounded_rectangle([n["x"], n["y"], n["x"] + n["w"], n["y"] + n["h"]], radius=8, fill=n["col"], outline=(160, 150, 130), width=1)
        # Washi tape strip
        draw.rectangle([n["x"] + 40, n["y"] - 10, n["x"] + 90, n["y"] + 10], fill=(245, 208, 115, 220))

    def make_frame(t):
        return np.array(canvas)

    return VideoClip(make_frame, duration=duration).with_fps(VIDEO_FPS)

def build_scene_background(scene: dict, visual_style: str = "motion") -> VideoClip:
    """
    Builds a standalone background clip tailored to a single storyboard scene:
    - AI Cinematic: Pollinations.ai Flux/Turbo artwork + Ken Burns pan/zoom
    - Sketch Notes: Educational card canvas (#F5F0E8) with dot grid
    - Paper Collage: Layered kraft paper & sticky notes (#F4EEE2)
    - Motion / Infographic / Futuristic / Educational: Modern studio, Indian AI growth curve, multi-industry sector cards
    - Stock / Hybrid: Stock B-roll or dark HUD
    """
    scene_id = scene.get("scene_id", 1)
    duration = float(scene.get("duration", 4.0))
    prompt = scene.get("visual_prompt", "cyberpunk futuristic tech room, 9:16 vertical 4k, no text")
    stage = scene.get("stage", "").lower()
    cam = scene.get("camera_movement", "zoom_in")

    style = visual_style.lower()

    # 1. Generate or load Scene Background Image via ProviderManager
    temp_img_dir = Path("assets/scenes")
    temp_img_dir.mkdir(parents=True, exist_ok=True)
    
    img_path_str = scene.get("image_path")
    if img_path_str and Path(img_path_str).exists():
        img_file = Path(img_path_str)
    else:
        img_file = temp_img_dir / f"scene_{scene_id}.jpg"
        if not img_file.exists():
            from src.provider_manager import provider_mgr
            success, provider_used = provider_mgr.generate_image_for_scene(prompt, str(img_file), scene_idx=scene_id)
            print(f"[Visual Engine] Scene {scene_id} Visual Provider: {provider_used}")

    if img_file.exists():
        zoom_in = (cam != "zoom_out" and scene_id % 2 == 1)
        return create_ken_burns_clip(str(img_file), duration, zoom_in=zoom_in)

    # 2. Sketch Notes Mode
    if style in ["sketch_notes", "sketchnote"]:
        return create_sketch_notes_scene(duration, topic_cue=scene.get("background_description", ""))

    # 3. Paper Collage Mode
    if style in ["paper_collage", "collage"]:
        return create_paper_collage_scene(duration, topic_cue=scene.get("background_description", ""))

    # 4. Motion / Infographic / Futuristic / Educational Modes (Procedural Narrative Scenes)
    from src.motion_scenes import (
        create_modern_studio_scene, create_growth_infographic_scene,
        create_multi_industry_scene, create_workspace_studio_scene,
        create_cyber_subscribe_outro
    )

    if "hook" in stage:
        return create_modern_studio_scene(duration)
    elif any(k in stage for k in ["growth", "disrupt", "market", "economy"]):
        return create_growth_infographic_scene(duration)
    elif any(k in stage for k in ["secret", "industry", "sectors", "healthcare", "agri"]):
        return create_multi_industry_scene(duration)
    elif any(k in stage for k in ["truth", "workspace", "desk", "coding", "insight"]):
        return create_workspace_studio_scene(duration)
    elif "cta" in stage or "outro" in stage or "elevation" in stage:
        return create_cyber_subscribe_outro(duration)
    else:
        # Alternating narrative scenes
        scenes_pool = [
            create_modern_studio_scene,
            create_growth_infographic_scene,
            create_multi_industry_scene,
            create_workspace_studio_scene,
            create_cyber_subscribe_outro
        ]
        return scenes_pool[(scene_id - 1) % len(scenes_pool)](duration)


