# 🏗️ ARCHITECTURE SPECIFICATION
## Stickman AI Video Production Studio (Raj Everyway Study)

**System Target**: 1080 × 1920, 9:16 Vertical, 30 FPS, YouTube Shorts  
**Narration Language**: Natural Conversational Hindi (Devanagari)  
**Main Character**: 100% Consistent Articulated 2D Vector/Rig Stickman Protagonist throughout all scenes

---

## 1. Architectural Philosophy & Core Decisions

### Non-Negotiable Rule: Stickman Character Permanence
Generative video diffusion models (Sora, Runway, Pexels, Midjourney) fail at temporal character consistency: characters morph in face, limbs, height, and clothing from scene to scene.
To solve this permanently, our system uses a **Deterministic 2D Articulated Rig Layer** (`src/stickman_engine.py`):
1. The Stickman is mathematically drawn on a transparent high-resolution canvas with exact anatomical proportions (head, spine, 2-segment articulated arms, 2-segment legs).
2. The character includes fluid micro-animations:
   - Natural sinusoidal breathing bob (`math.sin(t * 3.5)`)
   - Eye blinks every 2.8 seconds
   - Articulated speaking mouth synchronized to speech
   - 11 expressive poses (`explaining`, `pointing_right/left/up`, `thinking`, `shocked`, `talking`, `celebrating`, `worried`, `walking`, `interacting_screen`)
   - 6 dynamic props (`screen`, `laptop`, `lightbulb`, `warning`, `books`, `bell`)
3. The Stickman appears from **Frame 0 (0.0s)** and remains the primary visual actor until the final frame.
4. AI-generated and procedural visuals (`src/visual_engine.py`) serve as the **background layer**, allowing cinematic environments while the character remains 100% stable.

---

## 2. Multi-Stage Pipeline Architecture

```
                  ┌────────────────────────────────────────┐
                  │          USER INPUT: TOPIC             │
                  │     e.g., "भारत में AI का भविष्य"       │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
             [STAGE 1: RESEARCH & TREND RADAR] ─── (src/trends.py)
             Google Trends (IN) + Hacker News + Fact-Checking
                                      │
                                      ▼
             [STAGE 2: VIRAL HINDI SCRIPT] ─────── (src/ai_script.py / script_gen.py)
             Gemini 2.5 Flash / Curated Templates: Hook -> Points -> CTA
                                      │
                                      ▼
             [STAGE 3: DUAL-ENGINE HINDI VO] ───── (src/voice_gen.py)
             Sarvam AI (Bulbul v3) or Microsoft Edge-TTS (Swara / Madhur)
             -> Measures exact total_duration in seconds
                                      │
                                      ▼
             [STAGE 4: AI STORYBOARD DIRECTOR] ─── (src/storyboard_director.py)
             5-Stage Heartbeat Arc (Hook, Disrupt, Unveil, Truth, CTA)
             -> Outputs 6–8 scenes with Stickman poses, props, cameras
                                      │
                                      ▼
             [STAGE 5: SUBTITLE & SRT ENGINE] ──── (src/subtitle_gen.py)
             Devanagari text chunking + Spring Pop + Subtitles.srt
                                      │
                                      ▼
             [STAGE 6: STICKMAN VIDEO ENGINE] ──── (src/video_engine.py)
             Composite [Background + Stickman Actor] per scene
             + Pulse Spectrum + Header Badge + SFX + Ducked BGM
             -> 1080x1920 30FPS H.264/AAC final_video.mp4
                                      │
                                      ▼
             [STAGE 7: AUTOMATIC QC ENGINE] ────── (src/quality_control.py)
             Technical, Visual, Audio, Compliance checks -> quality_report.md
                                      │
                                      ▼
             [STAGE 8: PRODUCTION BUNDLE] ──────── (main.py: export_production_bundle)
             Exports all 7 deliverables to output/{project_id}/
```

---

## 3. Logical Module Inventory

| Module | File Path | Core Functionality |
|---|---|---|
| **Stickman Character Rig** | `src/stickman_engine.py` | Articulated 2D vector stickman, 11 poses, 6 props, styles (`modern_beanie`, `classic`, `cyber_neon`), micro-animations. |
| **Storyboard Director** | `src/storyboard_director.py` | 5-stage heartbeat scene choreographer; parses script into 6-8 scenes; assigns poses, emotions, and camera movements. |
| **Video Production Engine** | `src/video_engine.py` | Composite scene assembler, multi-track audio mixer (voice + whoosh SFX + BGM ducking), 1080x1920 30FPS MP4 renderer. |
| **Visual Backgrounds** | `src/visual_engine.py` | Pollinations.ai free 4K scene art + Ken Burns pan/zoom, Sketch Notes mode (`#F5F0E8`), Pexels stock video adapter. |
| **Procedural Motion** | `src/motion_scenes.py` | 3D procedural cyberpunk scenes: Neural Tunnel, Terminal IDE, Matrix Digital Rain, Sonar CTA. |
| **Dual Voice Engine** | `src/voice_gen.py` | Sarvam AI Bulbul v3 + Microsoft Edge-TTS keyless fallback, sentence chunking (<400 chars). |
| **Subtitle Engine** | `src/subtitle_gen.py` | MoneyPrinter spring-pop animated Devanagari subtitles + `export_subtitles_to_srt`. |
| **Thumbnail Designer** | `src/thumbnail_gen.py` | High-CTR 1080x1920 portrait thumbnails with glowing typography, hook badges, PNG/JPEG export. |
| **Quality Control** | `src/quality_control.py` | Automated technical, visual, audio, and compliance validation; generates `quality_report.md` (0-100 score). |
| **Trend Radar** | `src/trends.py` | Live trend aggregator from Google Trends (India/Global) and Hacker News. |
| **SEO Analyzer** | `src/seo_analyzer.py` | 100-point YouTube findability audit + autocomplete search term retriever. |
| **Monetization Compliance**| `src/compliance.py` | Scans scripts against YouTube advertiser guidelines to prevent demonetization. |
| **Web Studio** | `web_app.py`, `web/*` | Interactive FastAPI modern web interface with live player, storyboard viewer, QC viewer, and download links. |

---

## 4. The 5-Stage Storytelling Arc (Heartbeat Engine)

Adapted from `stickman-video-director-main`:
1. **Stage 1: Golden Hook (0–5s)**
   - Instant curiosity trigger or counter-intuitive paradox.
   - Stickman Pose: `shocked` or `pointing_up` with `warning` or `lightbulb` prop.
   - Stickman appears in Frame 0. No empty intros.
2. **Stage 2: Disrupting Assumptions (5–12s)**
   - Shatters a common misconception to build cognitive conflict.
   - Stickman Pose: `worried` or `pointing_left`.
3. **Stage 3: Unveiling Insider Secrets (12–25s)**
   - Reveals hidden mechanics and technical logic.
   - Stickman Pose: `thinking` or `interacting_screen` with holographic floating glass UI.
4. **Stage 4: Ultimate Truth (25–40s)**
   - Delivers the core solution or actionable principle.
   - Stickman Pose: `explaining` or `talking` with `laptop` or `books` prop.
5. **Stage 5: Elevation & High-Engagement CTA (40–50s)**
   - Discussion prompt and subscribe callout.
   - Stickman Pose: `celebrating` with animated ringing gold `bell` prop and "SUB" badge.

---

## 5. Output Specifications (The 7 Deliverables)

Every production run generates these 7 standardized deliverables inside `output/{project_title}/`:

1. `final_video.mp4`: 1080 × 1920 portrait, 30 FPS, H.264 video, AAC audio, containing the animated Stickman in 100% of scenes.
2. `thumbnail.png`: High-CTR portrait thumbnail with glowing typography, hook badge, and channel branding.
3. `script.txt`: Complete structured Hindi script (Hook, Points, CTA, Word Count, TTS voiceover block).
4. `storyboard.json`: Chronological scene-by-scene cinematography plan with poses, emotions, camera moves, and background prompts.
5. `subtitles.srt`: Standard SRT subtitle track formatted for YouTube Shorts upload.
6. `metadata.json`: YouTube title, description, hashtags, tags, SEO audit score, and duration.
7. `quality_report.md`: Automated technical, visual, audio, and compliance scorecard.
