# 📝 CHANGELOG
## Raj Everyway Study — Stickman AI Video Production Studio

All notable changes, upgrades, and architecture improvements are documented in this file.

---

### [2.2.0] — 2026-10-30
#### 🚀 Major Upgrade: Transformation into Stickman AI Video Production Studio

#### Added
- **Permanent Stickman Character Rig (`src/stickman_engine.py`)**:
  - Built a deterministic 2D vector/canvas rig guaranteeing 100% anatomical and character consistency across 100% of scenes.
  - 11 expressive dynamic poses: `EXPLAINING`, `POINTING_RIGHT`, `POINTING_LEFT`, `POINTING_UP`, `THINKING`, `SHOCKED`, `TALKING`, `CELEBRATING`, `WORRIED`, `WALKING`, `INTERACTING_SCREEN`.
  - 6 interactive scene props:
    - `screen`: Floating holographic glass UI card with header buttons and animated glowing code lines.
    - `laptop`: Sleek workspace laptop with keyboard and glowing screen.
    - `lightbulb`: Radiating idea bulb above character's head with glowing light rays.
    - `warning`: Exclamation alert hazard badge for myth-busting and tension scenes.
    - `books`: Multi-colored academic textbook stack for educational study topics.
    - `bell`: Animated ringing YouTube subscribe bell with motion tilt and red "SUB" button.
  - Micro-animations:
    - Natural sinusoidal breathing bob (`math.sin(t * 3.5) * 4.0`)
    - Eye blink cycle every 2.8 seconds
    - Articulated speaking mouth synchronized to speech
    - Eyebrow articulation (curious raised eyebrow, shocked arch, confident smile)
  - 3 Character Styles: `modern_beanie` (Yellow shirt, Red beanie), `classic` (Monochrome minimalist), and `cyber_neon` (Cyan/magenta contours).

- **AI Storyboard Director (`src/storyboard_director.py`)**:
  - Implemented the 5-Stage High-Completion Heartbeat Arc (Golden Hook → Disrupt Assumptions → Unveil Secrets → Ultimate Truth → CTA).
  - Automatically divides scripts into 6–8 chronological scenes (2–4 seconds per visual shift).
  - Assigns scene ID, narration chunk, duration, stickman pose, emotion, position, prop, camera movement, background prompt, and subtitle chunk.
  - Outputs `storyboard.json`.

- **Automatic Quality Control Engine (`src/quality_control.py`)**:
  - Technical validation: Resolution (1080x1920), 9:16 portrait ratio, 30 FPS, H.264/AAC codec, duration synchronization.
  - Visual validation: First-frame hook check (no black opening frame), freeze-frame detector, Stickman presence in 100% of scenes, pose diversity.
  - Audio validation: Audio presence, RMS loudness, peak volume, no clipping.
  - Content validation: Scans against YouTube monetization and advertiser guidelines.
  - Exports comprehensive `quality_report.md` with 0–100 Quality Score and verdict (`PASSED`, `APPROVED`).

- **Sketch Notes Visual Mode (`src/visual_engine.py`)**:
  - Added warm cream canvas (`#F5F0E8`) with subtle pastel graph grid, rounded paper cards, drop shadows, and hand-drawn washi tape accents inspired by `insta-card-shorts-generator-main`.

- **7-Deliverable Production Packaging (`main.py`)**:
  - Every production run packages:
    1. `final_video.mp4`
    2. `thumbnail.png`
    3. `script.txt`
    4. `storyboard.json`
    5. `subtitles.srt`
    6. `metadata.json`
    7. `quality_report.md`
  - Saves in dedicated project bundle directory `output/{project_title}/` for 1-click archiving.

- **Web Application Upgrade (`web_app.py`, `web/*`)**:
  - Added Stickman Character Style selector cards.
  - Added Storyboard Plan inspector tab.
  - Added Quality Control scorecard tab.
  - Added 7-deliverable download action grid.

#### Fixed
- **Virtual Environment Path Corruption**: Fixed `pyvenv.cfg` which pointed to non-existent `C:\Users\lenovo` path; rebound to host Python 3.12.
- **Windows Terminal Unicode Encoding**: Fixed `UnicodeEncodeError: 'charmap'` when printing Hindi Devanagari and emojis by adding `sys.stdout.reconfigure(encoding='utf-8')`.
- **Sarvam AI TTS 400 Bad Request**: Fixed 500-character payload limit in Sarvam AI Bulbul v3 API by implementing sentence chunking (`chunk_text_for_sarvam(max_chars=400)`) with automatic WAV segment concatenation.
- **Fallback Voice Engine**: Integrated Microsoft Edge-TTS keyless fallback (`edge_swara`, `edge_madhur`) for 100% offline/free voiceover generation.
- **Thumbnail Format Compatibility**: Fixed thumbnail generator saving JPEG headers to `.png` paths; now properly detects format extension.
- **PV-Tool License Protection**: Preserved commercial monetization safety by strictly omitting non-commercial licensed code from `pv-tool-main`.

---

### [2.1.0] — 2026-10-30
- Initial AI Shorts Studio overhaul.
- Added live Trend Radar (`src/trends.py`).
- Added 100-Point SEO Findability Audit (`src/seo_analyzer.py`).
- Added Monetization Compliance Auditor (`src/compliance.py`).
- Added Multi-Style Thumbnail Generator (`src/thumbnail_gen.py`).
- Added Pollinations.ai 4K scene generator + Ken Burns Pan/Zoom (`src/visual_engine.py`).
