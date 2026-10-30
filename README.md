# 🎬 Raj Everyway Study — Stickman AI Video Production Studio 2.2
### Professional Automated AI Video Production System for YouTube Shorts

[![Format](https://img.shields.io/badge/Format-1080x1920%20(9:16)-blue?style=flat-square)](https://youtube.com)
[![FPS](https://img.shields.io/badge/FPS-30%20FPS-cyan?style=flat-square)](https://youtube.com)
[![Character](https://img.shields.io/badge/Protagonist-Consistent%20Stickman%20Rig-green?style=flat-square)](https://youtube.com)
[![Voice](https://img.shields.io/badge/TTS-Sarvam%20AI%20%2B%20Edge--TTS%20(Free)-orange?style=flat-square)](https://youtube.com)
[![QC](https://img.shields.io/badge/Quality%20Control-Automated%20Scorecard-success?style=flat-square)](https://youtube.com)

**Raj Everyway Study — Stickman AI Video Studio 2.2** is a fully automated, end-to-end AI video studio designed specifically for high-retention YouTube Shorts (1080×1920, 30 FPS, Hindi).

Unlike ordinary AI slideshow generators that output random morphed faces or abstract pulsing orbs, this studio guarantees that an **articulated, consistent Stickman character remains the main protagonist in 100% of scenes from Frame 0 to the finish**.

---

## 🌟 Core Pillars & Architectural Highlights

### 1. 🕺 Permanent Stickman Character Engine (`src/stickman_engine.py`)
- **100% Anatomical & Identity Continuity**: Powered by a mathematical vector rig with calibrated proportions (head, spine, articulated 2-segment arms and legs).
- **Fluid Micro-Animations**:
  - Sinusoidal natural breathing bob.
  - Periodic eye blinks every 2.8 seconds.
  - Articulated speaking mouth synchronized to speech audio.
  - Expressive eyebrows (curious raised eyebrow, shocked arch, confident smile).
- **11 Expressive Poses**:
  `EXPLAINING`, `POINTING_RIGHT`, `POINTING_LEFT`, `POINTING_UP`, `THINKING`, `SHOCKED`, `TALKING`, `CELEBRATING`, `WORRIED`, `WALKING`, `INTERACTING_SCREEN`.
- **6 Scene Props**:
  - `screen`: Floating holographic cyan glass UI with active glowing code lines.
  - `laptop`: Sleek workspace laptop on desk.
  - `lightbulb`: Radiating idea bulb with glowing light rays.
  - `warning`: Hazard exclamation alert badge for myth-busting scenes.
  - `books`: Multi-colored textbook stack for academic study topics.
  - `bell`: Animated ringing YouTube subscribe bell with motion vibration and red "SUB" badge.
- **3 Visual Character Styles**:
  - `Modern Beanie Zeke`: Yellow shirt, red beanie cap, black limbs.
  - `Classic Minimalist`: Monochrome hand-drawn linework.
  - `Cyber Neon`: Glowing cyan and magenta neon contours.

### 2. 📋 5-Stage Storyboard Director (`src/storyboard_director.py`)
Adapted from `stickman-video-director-main`:
- **Stage 1: Golden Hook (0–5s)** — High-curiosity paradox / shocker (Stickman shocked, warning badge).
- **Stage 2: Disrupt Assumptions (5–12s)** — Shatters popular myths (Stickman worried/warning).
- **Stage 3: Unveil Insider Secrets (12–25s)** — Reveals technical logic (Stickman thinking/screen).
- **Stage 4: Ultimate Truth (25–40s)** — Actionable solution (Stickman explaining with laptop/books).
- **Stage 5: Elevation & High-Engagement CTA (40–50s)** — Subscribe prompt (Stickman celebrating with bell).
- Enforces visual changes every 2–4 seconds (6–8 scenes per Short).

### 3. 🎨 Multi-Mode Visual Environments (`src/visual_engine.py`)
- **Full-Motion Cyberpunk**: 3D Neural Tunnel, IDE Terminal Editor, Matrix Rain, Sonar Outro.
- **AI Photorealistic Scenes**: Pollinations.ai 4K artwork with smooth Ken Burns Pan/Zoom (100% Free & Keyless).
- **Sketch Notes Mode**: Warm cream background (`#F5F0E8`), pastel graph paper grid, rounded card containers, and doodle washi tape.
- **Hybrid Pro**: Stock B-roll with dark Cyber HUD telemetry and audio spectrum overlay.

### 4. 🎙️ Dual-Engine Hindi Voiceover (`src/voice_gen.py`)
- **Sarvam AI (Bulbul v3)**: Natural Indian voices (`aditya`, `shubh`, `priya`, `ritu`, `rahul`, `amit`).
  - *Auto-Chunking*: Solves the 500-char API limit by splitting sentences (<400 chars) and stitching WAV segments seamlessly.
- **Microsoft Edge-TTS**: 100% Free, keyless and unlimited neural voices (`edge_madhur`, `edge_swara`, `edge_neerja`, `edge_prabhat`).

### 5. ✨ MoneyPrinter Bouncy Subtitles (`src/subtitle_gen.py`)
- High-contrast Devanagari Hindi text with thick black outline.
- Active words highlighted in Neon Yellow (`#FFE600`) and Cyan (`#00F5FF`).
- MoneyPrinterTurbo spring-bounce pop animation on appearance.
- Exports standard `.srt` subtitles.

### 6. 🛡️ Automatic Quality Control Engine (`src/quality_control.py`)
Performs 4-layer validation before marking any video complete:
- **Technical**: 1080x1920, 9:16 portrait, 30 FPS, H.264/AAC, audio/video duration sync.
- **Visual**: First frame hook check, freeze-frame detector, Stickman presence in 100% of scenes, pose variety.
- **Audio**: Speech loudness, RMS power, peak volume, no clipping.
- **Content**: YouTube advertiser-friendly compliance check.
- Exports `quality_report.md` with 0–100 Quality Score.

---

## 📦 The 7 Production Deliverables

Every production run packages 7 complete files in `output/{project_title}/`:

1. `final_video.mp4` — Ready-to-publish 1080×1920 30FPS MP4.
2. `thumbnail.png` — High-CTR portrait thumbnail with glowing typography and hook badge.
3. `script.txt` — Full Hindi script breakdown with Hook, Points, CTA, and voiceover text.
4. `storyboard.json` — Detailed scene-by-scene cinematography and choreography plan.
5. `subtitles.srt` — Standard YouTube-compatible SRT subtitle track.
6. `metadata.json` — YouTube Title, Description, Tags, Hashtags, SEO score.
7. `quality_report.md` — Complete QC audit scorecard with pass/fail itemization.

---

## ⚡ How to Run

### 1. Interactive Web Studio (Recommended)
Double-click `run_ui.bat` or run:
```powershell
.\.venv\Scripts\python.exe web_app.py
```
Open your browser at:
```
http://127.0.0.1:8000
```
- Click on any topic in the **Live Trend Radar** or enter your custom topic.
- Select your **Stickman Style** and **Background Mode**.
- Click **"RENDER 1080x1920 SHORT & THUMBNAIL"**.
- View your live video, thumbnail, storyboard, and QC score in the studio!

### 2. Command Line (CLI) 1-Click Automation
```powershell
# 1-Click Topic to Video:
.\.venv\Scripts\python.exe main.py --prompt "भारत में AI का भविष्य"

# Custom Voice & Style:
.\.venv\Scripts\python.exe main.py --prompt "Top 3 Student AI Tools" --speaker edge_madhur --style motion --stickman-style modern_beanie
```

---

## 📂 Project Directory Structure

```text
New folder/
├── web_app.py                 # FastAPI Web Application & Studio Server
├── main.py                    # Master CLI Pipeline Orchestrator
├── config.py                  # Global Configuration & Settings
├── run_ui.bat                 # 1-Click Web UI Launcher
├── run_cli.bat                # 1-Click CLI Launcher
├── requirements.txt           # Project Dependencies
├── ARCHITECTURE.md            # Complete System Architecture Document
├── INTEGRATION_REPORT.md      # Reference Repository Audit & Integration Report
├── CHANGELOG.md               # Version History & Release Notes
├── INSTALLATION.md            # Complete Setup & Installation Guide
├── TROUBLESHOOTING.md         # Diagnostic Guide & Solutions
├── web/                       # Modern Cyberpunk Frontend (HTML, CSS, JS)
│   ├── index.html
│   ├── style.css
│   └── app.js
├── src/
│   ├── stickman_engine.py     # Deterministic 2D Articulated Stickman Rig & Props
│   ├── storyboard_director.py # 5-Stage Heartbeat Scene Choreographer
│   ├── video_engine.py        # Master Video Layer Compositor & MP4 Renderer
│   ├── visual_engine.py       # Pollinations AI, Sketch Notes, Pexels Stock
│   ├── motion_scenes.py       # 3D Procedural Cyberpunk Scenes (Tunnel, IDE, Matrix)
│   ├── voice_gen.py           # Dual Voiceover Engine (Sarvam AI + Edge-TTS)
│   ├── subtitle_gen.py        # Spring-Bounce Subtitles & SRT Exporter
│   ├── thumbnail_gen.py       # High-CTR Thumbnail Designer (PNG/JPEG)
│   ├── quality_control.py     # Automated Technical & Visual QC Engine
│   ├── trends.py              # Live Trend Radar (Google Trends + Hacker News)
│   ├── seo_analyzer.py        # 100-Point SEO Audit & YouTube Autocomplete
│   ├── compliance.py          # Monetization & Safe Content Scanner
│   └── script_gen.py          # Script Resolver (AI + Curated Templates)
└── output/                    # Production Bundles (MP4, PNG, SRT, JSON, QC)
```

---

## 📜 Documentation Reference

- [Architecture Specification (ARCHITECTURE.md)](ARCHITECTURE.md)
- [Reference Repositories Integration Report (INTEGRATION_REPORT.md)](INTEGRATION_REPORT.md)
- [Installation Guide (INSTALLATION.md)](INSTALLATION.md)
- [Troubleshooting & FAQ (TROUBLESHOOTING.md)](TROUBLESHOOTING.md)
- [Changelog (CHANGELOG.md)](CHANGELOG.md)

---
Developed with ❤️ for **Raj Everyway Study**.
