"""
FastAPI Web Application — Stickman AI Video Production Studio (Raj Everyway Study).
Provides an interactive modern web UI for 1-click topic to broadcast-grade Shorts production.
"""

import os
import sys
import re
import uuid
import threading
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure root directory is on sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

from config import (
    OUTPUT_DIR, DEFAULT_SPEAKER, DEFAULT_PACE,
    AVAILABLE_SPEAKERS, VISUAL_STYLES, DEFAULT_VISUAL_STYLE,
    CHANNEL_NAME
)
from src.ai_script import generate_ai_script
from src.script_gen import get_script_for_input
from src.voice_gen import generate_voiceover, generate_voiceover_with_timings
from src.storyboard_director import build_storyboard
from src.subtitle_gen import export_subtitles_to_srt
from src.caption_engine import build_caption_phrase_groups, export_caption_groups_to_srt
from src.video_engine import build_short_video
from src.thumbnail_gen import generate_thumbnail
from src.seo_analyzer import audit_seo_score, get_youtube_suggestions
from src.compliance import check_script_compliance
from src.quality_control import run_quality_control
from src.trends import get_all_trending_topics
from main import export_production_bundle

app = FastAPI(
    title=f"{CHANNEL_NAME} — Stickman AI Video Production Studio",
    version="2.2.0"
)

# Mount static web assets
web_dir = root_dir / "web"
app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

TASKS: Dict[str, Dict[str, Any]] = {}

class ScriptRequest(BaseModel):
    prompt: str

class VideoRequest(BaseModel):
    title: str = "Short Video"
    hook: str = ""
    points: List[str] = []
    cta: str = ""
    narration_text: str = ""
    speaker: str = DEFAULT_SPEAKER
    pace: float = DEFAULT_PACE
    visual_style: str = DEFAULT_VISUAL_STYLE
    stickman_style: str = "modern_beanie"
    seo: Optional[Dict[str, Any]] = None
    visual_keywords: Optional[List[str]] = None

class SeoAuditRequest(BaseModel):
    title: str
    description: str = ""
    tags: str = ""
    keyword: str = ""

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = web_dir / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/providers")
async def get_providers():
    from src.provider_manager import provider_mgr
    return {
        "diagnostics": provider_mgr.diagnostics,
        "status_report": provider_mgr.get_status_report()
    }

@app.get("/api/config")
async def get_config():
    styles = VISUAL_STYLES.copy()
    styles["sketch_notes"] = "Sketch Notes Mode (Warm Cream #F5F0E8 + Educational Doodles)"
    return {
        "channel_name": CHANNEL_NAME,
        "speakers": AVAILABLE_SPEAKERS,
        "visual_styles": styles,
        "stickman_styles": {
            "modern_beanie": "Modern Beanie Zeke (Yellow shirt, Red beanie)",
            "classic": "Classic Minimalist (Monochrome hand-drawn rig)",
            "cyber_neon": "Cyber Neon (Glowing cyan HUD accents)"
        },
        "default_speaker": DEFAULT_SPEAKER,
        "default_pace": DEFAULT_PACE,
        "default_style": DEFAULT_VISUAL_STYLE,
        "default_stickman_style": "modern_beanie"
    }

@app.get("/api/trends")
async def api_get_trends():
    trends = get_all_trending_topics(geo="IN")
    return {"trends": trends}

@app.post("/api/audit-seo")
async def api_audit_seo(req: SeoAuditRequest):
    audit = audit_seo_score(req.title, req.description, req.tags, req.keyword, is_shorts=True)
    return audit

@app.post("/api/generate-script")
async def api_generate_script(req: ScriptRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    try:
        script_data = generate_ai_script(req.prompt.strip())
        seo = script_data.get("seo", {})
        audit = audit_seo_score(
            seo.get("youtube_title", script_data.get("title", "")),
            seo.get("description", ""),
            seo.get("tags", ""),
            topic_keyword=script_data.get("title", ""),
            is_shorts=True
        )
        compliance = check_script_compliance(script_data.get("narration_text", ""), script_data.get("title", ""))
        
        script_data["audit"] = audit
        script_data["compliance"] = compliance
        return script_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate script: {str(e)}")

def run_video_generation_thread(task_id: str, payload: VideoRequest):
    task = TASKS[task_id]
    task["status"] = "running"
    task["percent"] = 5
    task["message"] = "Preparing script and project directory..."

    try:
        # 1. Narration Text
        narration = payload.narration_text.strip()
        if not narration:
            parts = [payload.hook] + payload.points + [payload.cta]
            narration = " ".join(p.strip() for p in parts if p.strip())

        raw_title = payload.title or "short_video"
        clean_title = re.sub(r'[^\w\-]', '_', raw_title).strip('_').lower()[:35]
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"{clean_title}_{timestamp}.mp4"
        base_name = Path(filename).stem

        # 2. Dual-Engine Voiceover
        task["percent"] = 15
        task["message"] = f"Generating voiceover with {payload.speaker}..."
        audio_temp = OUTPUT_DIR / f"{base_name}_voice.wav"

        duration, word_timings = generate_voiceover_with_timings(
            text=narration,
            output_path=str(audio_temp),
            speaker=payload.speaker,
            pace=payload.pace
        )
        task["percent"] = 30
        task["message"] = f"Voiceover generated! Duration: {duration:.2f}s ({len(word_timings)} words)"

        # 3. Choreograph 5-Stage Storyboard & Stickman Poses
        task["percent"] = 40
        task["message"] = "Choreographing 5-stage storyboard with Stickman character..."
        script_dict = {
            "title": payload.title,
            "hook": payload.hook,
            "points": payload.points,
            "cta": payload.cta,
            "narration_text": narration,
            "seo": payload.seo or {
                "youtube_title": f"{payload.title} 🚀 #Shorts",
                "description": f"{narration}\n\nSubscribe to {CHANNEL_NAME} for more smart tech insights!",
                "hashtags": ["#shorts", "#tech", "#ai", "#studyhacks", "#rajeverywaystudy"],
                "tags": f"{clean_title}, shorts, ai tech, raj everyway study"
            }
        }
        sb_path = OUTPUT_DIR / f"{base_name}_storyboard.json"
        storyboard = build_storyboard(
            topic=raw_title,
            script_data=script_dict,
            total_duration=duration,
            visual_style=payload.visual_style,
            output_path=str(sb_path)
        )
        task["storyboard"] = storyboard

        # 4. Generate Subtitles SRT
        task["percent"] = 50
        task["message"] = "Generating synchronized Devanagari word-highlight SRT subtitles..."
        srt_temp = OUTPUT_DIR / f"{base_name}_subtitles.srt"
        caption_groups = build_caption_phrase_groups(word_timings, duration, words_per_phrase=5)
        export_caption_groups_to_srt(caption_groups, str(srt_temp))

        # 5. Assemble and Render Video
        def progress_cb(pct: int, msg: str):
            scaled_pct = int(50 + (pct * 0.35))
            task["percent"] = min(scaled_pct, 88)
            task["message"] = msg

        final_path = build_short_video(
            audio_path=str(audio_temp),
            script_text=narration,
            storyboard=storyboard,
            visual_style=payload.visual_style,
            stickman_style=payload.stickman_style,
            visual_keywords=payload.visual_keywords or ["tech", "ai", "study"],
            output_filename=filename,
            progress_callback=progress_cb,
            word_timings=word_timings
        )

        # 6. Generate Thumbnail
        task["percent"] = 90
        task["message"] = "Generating high-CTR YouTube thumbnail..."
        thumb_path = OUTPUT_DIR / f"{base_name}_thumb.png"
        generate_thumbnail(
            title=payload.seo.get("youtube_title", payload.title) if payload.seo else payload.title,
            output_path=str(thumb_path),
            is_portrait=True
        )

        # 7. Audit SEO & Run Automatic Quality Control
        task["percent"] = 94
        task["message"] = "Running automatic Quality Control & SEO audit..."
        y_title = script_dict["seo"].get("youtube_title", payload.title)
        y_desc = script_dict["seo"].get("description", "")
        y_tags = script_dict["seo"].get("tags", "")
        audit = audit_seo_score(y_title, y_desc, y_tags, topic_keyword=payload.title, is_shorts=True)
        comp = check_script_compliance(narration, payload.title)

        qc_report_path = OUTPUT_DIR / f"{base_name}_quality_report.md"
        qc_results = run_quality_control(
            video_path=final_path,
            audio_path=str(audio_temp),
            storyboard=storyboard,
            script_data=script_dict,
            output_report_path=str(qc_report_path)
        )

        # 8. Package 7 Deliverables
        task["percent"] = 98
        task["message"] = "Exporting 7 production deliverables..."
        project_folder = OUTPUT_DIR / f"{clean_title}_{timestamp}"
        bundle = export_production_bundle(
            project_dir=project_folder,
            base_name=base_name,
            final_video_path=final_path,
            thumb_path=str(thumb_path),
            script_data=script_dict,
            storyboard=storyboard,
            srt_path=str(srt_temp),
            audit_data=audit,
            comp_data=comp,
            qc_results=qc_results,
            total_duration=duration
        )

        # Task complete
        task["percent"] = 100
        task["status"] = "completed"
        task["message"] = f"Production complete! Quality Score: {qc_results['total_score']}/100 ({qc_results['verdict']})"
        task["filename"] = filename
        task["video_url"] = f"/api/video/{filename}"
        task["thumb_url"] = f"/api/thumbnail/{base_name}_thumb.png"
        task["qc_score"] = qc_results["total_score"]
        task["qc_verdict"] = qc_results["verdict"]
        task["bundle"] = bundle

    except Exception as e:
        task["status"] = "failed"
        task["error"] = str(e)
        task["message"] = f"Error during rendering: {str(e)}"
        print(f"[Render Thread Error]: {e}")

@app.post("/api/generate-video")
async def api_generate_video(req: VideoRequest):
    task_id = uuid.uuid4().hex[:8]
    TASKS[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "percent": 0,
        "message": "Queued for render...",
        "video_url": None,
        "thumb_url": None,
        "filename": None,
        "error": None
    }

    t = threading.Thread(target=run_video_generation_thread, args=(task_id, req), daemon=True)
    t.start()

    return {"task_id": task_id, "status": "queued"}

@app.get("/api/task-status/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task ID not found")
    return TASKS[task_id]

@app.get("/api/videos")
async def list_videos():
    videos = []
    if not OUTPUT_DIR.exists():
        return []

    for f in sorted(OUTPUT_DIR.glob("*.mp4"), key=os.path.getmtime, reverse=True):
        size_mb = round(f.stat().st_size / (1024 * 1024), 2)
        mod_time = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        base_name = f.stem
        has_seo = (OUTPUT_DIR / f"{base_name}_SEO.txt").exists()
        has_thumb = (OUTPUT_DIR / f"{base_name}_thumb.png").exists() or (OUTPUT_DIR / f"{base_name}_thumb.jpg").exists()
        has_qc = (OUTPUT_DIR / f"{base_name}_quality_report.md").exists()

        thumb_ext = "png" if (OUTPUT_DIR / f"{base_name}_thumb.png").exists() else "jpg"

        videos.append({
            "filename": f.name,
            "base_name": base_name,
            "size_mb": size_mb,
            "modified": mod_time,
            "has_seo": has_seo,
            "has_thumb": has_thumb,
            "has_qc": has_qc,
            "thumb_url": f"/api/thumbnail/{base_name}_thumb.{thumb_ext}" if has_thumb else None
        })
    return videos

@app.get("/api/video/{filename}")
async def get_video(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    return FileResponse(str(file_path), media_type="video/mp4", filename=filename)

@app.get("/api/thumbnail/{filename}")
async def get_thumbnail(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        # check if .jpg exists instead
        if filename.endswith(".png"):
            file_path = OUTPUT_DIR / filename.replace(".png", ".jpg")
        elif filename.endswith(".jpg"):
            file_path = OUTPUT_DIR / filename.replace(".jpg", ".png")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail file not found")
    media_t = "image/png" if file_path.suffix == ".png" else "image/jpeg"
    return FileResponse(str(file_path), media_type=media_t, filename=file_path.name)

@app.get("/api/file/{filename}")
async def get_output_file(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(file_path), filename=filename)

def start_server(host: str = "127.0.0.1", port: int = 8000):
    print("=" * 65)
    print(f"   RAJ EVERYWAY STUDY — STICKMAN AI VIDEO STUDIO")
    print(f"   Opening Web UI at: http://{host}:{port}")
    print("=" * 65)
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()
