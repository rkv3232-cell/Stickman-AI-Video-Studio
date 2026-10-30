# Integration Report: AI Video Maker to Professional Stickman AI Studio

## 1. Executive Summary

This report documents the architectural audit of the current AI Video Maker project and the 7 local reference repositories downloaded in the workspace. It specifies the reusable patterns, licenses, dependency considerations, and integration roadmap to transform the existing tool into a **Professional Stickman-Driven AI Video Production Studio**.

---

## 2. Audit of Existing Codebase (`New folder/`)

| Component | Current Implementation | Status | Upgrade Needed |
| :--- | :--- | :--- | :--- |
| **Main Character** | Procedural abstract canvas (tunnels, code terminal) | ⚠️ Missing | **Build permanent deterministic Stickman Rig** |
| **Script Generation** | Gemini 2.5 Flash (`src/ai_script.py`) | ✅ Working | Upgrade to 5-stage high-completion storytelling |
| **Voiceover Engine** | Sarvam AI (Bulbul v3) + Edge-TTS fallback | ✅ Working | Keep dual engine, integrate scene timestamps |
| **Subtitles** | Spring-pop word chunks (`src/subtitle_gen.py`) | ✅ Working | Add SRT exporter, safe zone verification |
| **Video Composition** | MoviePy 2.2 composite (`src/video_engine.py`) | ✅ Working | Add multi-layer Stickman actor compositing |
| **Web UI** | FastAPI + HTML5/CSS/JS (`web_app.py`) | ✅ Working | Add Storyboard Inspector, QC Report, Stickman Mode |
| **SEO & Thumbnail** | Multi-style thumbnail (`src/thumbnail_gen.py`) | ✅ Working | Standardize output bundle naming |
| **Quality Control** | Basic checks in console | ⚠️ Partial | **Build formal Automated QC Engine** |

---

## 3. Reference Repositories Analysis & Reusable Matrix

### A. `stickman-video-director-main` (Priority Reference)
- **Core Value**: Directing stickman storytelling, 5-stage heartbeat narrative arc, character identity standards (Beanie Zeke, Classic Minimalist), scene pacing (2–4 second dynamic beats), and prompt contract.
- **License**: MIT
- **Adapted Features**:
  1. 5-Stage Story Arc: Golden Hook → Disrupting Assumptions → Unveiling Secrets → Ultimate Truth → High-Engagement CTA.
  2. Character design constraints: 2D vector stickman, stable proportions, no bug-eye deformation, expressive hand/limb poses.
  3. Shot rhythm: Visual change every 2–4 seconds (6–10 scenes per Short).

### B. `vox-director-main`
- **Core Value**: Editorial paper-collage aesthetics, narrative beat map (`beats.json`), camera pans/zooms, and audio ducking.
- **License**: MIT
- **Adapted Features**:
  1. Storyboard schema with structured scene beats.
  2. Paper Collage / Editorial visual mode around the Stickman.
  3. Ken Burns micro-camera movements.

### C. `insta-card-shorts-generator-main`
- **Core Value**: Sketch-note style, warm cream palette (`#F5F0E8`), 7-card storytelling structure.
- **License**: MIT
- **Adapted Features**:
  1. Sketch Notes visual mode for educational / tech explainers.
  2. Card-based visual framing behind the stickman.

### D. `the-generator-main`
- **Core Value**: Complete workflow, keyless Pollinations.ai AI images, Microsoft Edge-TTS integration, compliance scanning.
- **License**: MIT
- **Adapted Features**:
  1. Keyless AI photorealistic scene background generation.
  2. Edge-TTS neural voices fallback.
  3. YouTube monetization compliance rules.

### E. `youtube-agentic-ai-studio-main` (YAAS)
- **Core Value**: Multi-agent pipeline, live Google Trends / Hacker News radar, YouTube autocomplete keyword ideas, 100-point SEO score.
- **License**: MIT
- **Adapted Features**:
  1. Real-time trend radar for automatic topic inspiration.
  2. 100-point SEO findability scoring.
  3. Autocomplete keyword suggestions.

### F. `MoneyPrinterTurbo`
- **Core Value**: Multi-track audio mixing, FFmpeg processing, material management.
- **License**: Apache-2.0
- **Adapted Features**:
  1. Studio beat audio ducking algorithms.
  2. Multi-threaded fast video rendering.

### G. `pv-tool-main`
- **Core Value**: Kinetic typography, Japanese PV music video overlays, PixiJS Canvas effects.
- **License**: Non-Commercial License (effective 2026/03/24)
- **Adoption Strategy**: To ensure 100% commercial and YouTube monetization safety, **NO code or assets are copied from PV Tool**. Only general open-domain mathematical vector drawing concepts (pure Canvas lines and angles) are implemented cleanly in Python.

---

## 4. Key Architectural Decision: Deterministic Stickman Rig

To fulfill the primary mandate—**Stickman must remain the consistent protagonist throughout every video**:
1. Generative AI redraws the character differently every frame if used directly for the character.
2. Therefore, the primary Stickman actor is rendered via a **Deterministic Vector Rig** (`src/stickman_engine.py`) using anti-aliased mathematical geometry.
3. The Stickman has consistent proportions, customizable expressions (neutral, happy, thinking, shocked, explaining, determined), and a library of 10+ dynamic poses and animations.
4. Background environments (Cyber Studio, Paper Collage, Sketch Notes, AI Photorealistic) are rendered as the context layer, while the Stickman acts in the foreground.

---

## 5. Standard Output Bundle Definition

Every video generation produces 7 standardized files in `output/{project_id}/`:
1. `final_video.mp4` — 1080×1920 30FPS H.264/AAC
2. `thumbnail.png` — High-CTR 1080×1920 & 1280×720 cover
3. `script.txt` — Full narration and hook breakdown
4. `storyboard.json` — Detailed scene-by-scene director plan
5. `subtitles.srt` — Standard timed subtitle sidecar
6. `metadata.json` — YouTube Title, Description, Hashtags, and Tags
7. `quality_report.md` — Formal Quality Control audit report
