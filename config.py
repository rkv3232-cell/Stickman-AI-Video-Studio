import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR

# API Keys
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# Directory Paths
ASSETS_DIR = BASE_DIR / "assets"
BG_VIDEOS_DIR = ASSETS_DIR / "bg_videos"
BG_MUSIC_DIR = ASSETS_DIR / "bg_music"
FONTS_DIR = ASSETS_DIR / "fonts"
SFX_DIR = ASSETS_DIR / "sfx"
SCENES_DIR = ASSETS_DIR / "scenes"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure directories exist
for d in [ASSETS_DIR, BG_VIDEOS_DIR, BG_MUSIC_DIR, FONTS_DIR, SFX_DIR, SCENES_DIR, OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Video Settings (YouTube Shorts format 9:16)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30

# Channel Identity
CHANNEL_NAME = "RAJ EVERYWAY STUDY"
CHANNEL_TAGLINE = "Study Smart · Tech · AI"

# Voice Settings (Dual Engine: Sarvam AI + Free Microsoft Edge-TTS)
AVAILABLE_SPEAKERS = {
    # Sarvam AI Bulbul v3 (Desi Hindi Natural Voices)
    "aditya": {"name": "Aditya", "engine": "Sarvam AI", "gender": "Male", "desc": "Energetic, Confident Tech Voice"},
    "shubh": {"name": "Shubh", "engine": "Sarvam AI", "gender": "Male", "desc": "Deep, Authoritative Narrative Voice"},
    "priya": {"name": "Priya", "engine": "Sarvam AI", "gender": "Female", "desc": "Warm, Engaging Educational Voice"},
    "ritu": {"name": "Ritu", "engine": "Sarvam AI", "gender": "Female", "desc": "Clear, Professional & Crisp Voice"},
    "rahul": {"name": "Rahul", "engine": "Sarvam AI", "gender": "Male", "desc": "Friendly, Conversational Desi Voice"},
    "amit": {"name": "Amit", "engine": "Sarvam AI", "gender": "Male", "desc": "Calm, Storytelling Voice"},
    # Microsoft Edge TTS (100% Free, Keyless & Unlimited)
    "edge_swara": {"name": "Swara (Free)", "engine": "Edge-TTS", "gender": "Female", "desc": "Natural Hindi Female Voice"},
    "edge_madhur": {"name": "Madhur (Free)", "engine": "Edge-TTS", "gender": "Male", "desc": "Deep Hindi Male Voice"},
    "edge_neerja": {"name": "Neerja (Free)", "engine": "Edge-TTS", "gender": "Female", "desc": "Indian English Female Voice"},
    "edge_prabhat": {"name": "Prabhat (Free)", "engine": "Edge-TTS", "gender": "Male", "desc": "Indian English Male Voice"},
}
DEFAULT_SPEAKER = "aditya"
DEFAULT_MODEL = "bulbul:v3"
DEFAULT_PACE = 1.05
TARGET_LANGUAGE_CODE = "hi-IN"

# Subtitle & Typography Fonts (Roman Hinglish & Multi-Script Support)
FONT_MUKTA_EXTRABOLD = FONTS_DIR / "Mukta-ExtraBold.ttf"
FONT_MUKTA_BOLD = FONTS_DIR / "Mukta-Bold.ttf"
FONT_ARIAL_BOLD = Path("C:/Windows/Fonts/arialbd.ttf")
FONT_IMPACT = Path("C:/Windows/Fonts/impact.ttf")
FONT_NOTO_BOLD = FONTS_DIR / "NotoSansDevanagari-Bold.ttf"

if FONT_MUKTA_EXTRABOLD.exists():
    FONT_PATH = str(FONT_MUKTA_EXTRABOLD)
elif FONT_ARIAL_BOLD.exists():
    FONT_PATH = str(FONT_ARIAL_BOLD)
elif FONT_MUKTA_BOLD.exists():
    FONT_PATH = str(FONT_MUKTA_BOLD)
else:
    FONT_PATH = "C:/Windows/Fonts/arial.ttf"

FALLBACK_FONT_PATH = str(FONT_ARIAL_BOLD) if FONT_ARIAL_BOLD.exists() else "C:/Windows/Fonts/arial.ttf"

# Typography Hierarchy
TYPO_HERO_SIZE = 135
TYPO_SECONDARY_SIZE = 75
TYPO_TAG_SIZE = 34
SUBTITLE_FONT_SIZE = 56
SUBTITLE_PRIMARY_COLOR = (255, 255, 255)
SUBTITLE_HIGHLIGHT_COLOR = (255, 230, 0)
SUBTITLE_CYAN_COLOR = (0, 245, 255)
SUBTITLE_ACCENT_COLOR = (255, 45, 85)
SUBTITLE_STROKE_COLOR = (0, 0, 0)
SUBTITLE_STROKE_WIDTH = 5

# Visual Styles (Expanded with Pollinations.ai Keyless Artwork)
VISUAL_STYLES = {
    "motion": "Full-Motion Cyberpunk (3D Neural Tunnel, IDE, Matrix, Sonar)",
    "ai_cinematic": "AI Photorealistic Scenes (Pollinations.ai + Ken Burns Pan/Zoom) [Free]",
    "hybrid": "Hybrid Pro (Stock Video + Cyber HUD & Spectrum Overlay)",
    "stock": "Cinematic Stock Videos (Curated Tech & Study B-Roll)"
}
DEFAULT_VISUAL_STYLE = "ai_cinematic"
