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

# Automation & Platform Services
from src.database import (
    get_job, list_jobs, get_all_settings, set_setting, get_setting,
    list_topic_queue, add_topic_to_queue, list_publishing_queue, update_publishing_status
)
from src.automation_manager import automation_mgr
from src.scheduler import scheduler
from src.topic_discovery import discover_and_populate_topics
from src.video_providers import video_provider_mgr
from src.youtube_uploader import youtube_uploader
from src.youtube_analytics import get_channel_analytics_summary
from src.cost_manager import cost_mgr

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

# ══════════════════════════════════════════════════════════
# AUTOMATION, TOPICS, YOUTUBE & STUDIO APIs
# ══════════════════════════════════════════════════════════

class SettingsUpdateRequest(BaseModel):
    settings: Dict[str, str]

class TopicAddRequest(BaseModel):
    topic: str
    category: str = "AI Technology"

class AutoJobRequest(BaseModel):
    topic: Optional[str] = None
    category: str = "AI Technology"
    speaker: str = DEFAULT_SPEAKER
    pace: float = DEFAULT_PACE
    visual_style: str = DEFAULT_VISUAL_STYLE
    stickman_style: str = "modern_beanie"
    auto_publish: bool = True

@app.on_event("startup")
async def on_startup():
    scheduler.start()

@app.get("/api/automation/status")
async def get_automation_status():
    status = scheduler.get_status()
    active_job = None
    if status.get("active_job_id"):
        active_job = get_job(status["active_job_id"])
    return {
        "scheduler": status,
        "active_job": active_job
    }

@app.post("/api/automation/toggle")
async def toggle_automation():
    current = get_setting("automation_enabled", "false").lower() == "true"
    new_state = "false" if current else "true"
    set_setting("automation_enabled", new_state)
    return {"automation_enabled": new_state == "true"}

@app.post("/api/automation/pause")
async def pause_automation():
    automation_mgr.pause()
    return {"status": "paused", "automation_enabled": False}

@app.post("/api/automation/resume")
async def resume_automation():
    automation_mgr.resume()
    return {"status": "resumed", "automation_enabled": True}

@app.post("/api/automation/stop")
async def stop_automation():
    automation_mgr.stop()
    return {"status": "stopped"}

@app.post("/api/automation/generate-now")
async def api_generate_now(req: AutoJobRequest):
    if automation_mgr.is_running():
        raise HTTPException(status_code=409, detail=f"Job {automation_mgr.current_job_id} is already in progress.")

    target_topic = req.topic.strip() if req.topic and req.topic.strip() else None
    if target_topic:
        job_id = automation_mgr.start_production_job(
            topic=target_topic,
            category=req.category,
            is_auto=False,
            speaker=req.speaker,
            pace=req.pace,
            visual_style=req.visual_style,
            stickman_style=req.stickman_style,
            auto_publish=req.auto_publish
        )
    else:
        job_id = automation_mgr.start_next_automated_job()
        if not job_id:
            raise HTTPException(status_code=400, detail="No topic available in queue. Add a topic or click Discover Trends.")

    return {"job_id": job_id, "status": "started"}

@app.get("/api/jobs")
async def api_list_jobs(limit: int = 50):
    return {"jobs": list_jobs(limit=limit)}

@app.get("/api/jobs/{job_id}")
async def api_get_job(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.post("/api/jobs/{job_id}/retry")
async def api_retry_job(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if automation_mgr.is_running():
        raise HTTPException(status_code=409, detail="Another job is currently running.")

    new_job_id = automation_mgr.start_production_job(
        topic=job["topic"],
        category=job["category"],
        is_auto=False
    )
    return {"old_job_id": job_id, "new_job_id": new_job_id, "status": "started"}

@app.get("/api/topics/queue")
async def api_get_topic_queue():
    return {"queue": list_topic_queue(limit=50)}

@app.post("/api/topics/discover")
async def api_discover_topics():
    discovered = discover_and_populate_topics(limit_per_run=10)
    return {"discovered_count": len(discovered), "new_topics": discovered}

@app.post("/api/topics/add")
async def api_add_topic(req: TopicAddRequest):
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    from src.topic_discovery import calculate_relevance_score
    cat, score = calculate_relevance_score(req.topic.strip())
    added = add_topic_to_queue(
        topic=req.topic.strip(),
        category=req.category or cat,
        source="Manual Creator Input",
        relevance=score,
        reason="Added by creator via Studio Dashboard"
    )
    return {"added": added, "topic": req.topic.strip(), "category": req.category, "score": score}

@app.get("/api/research/{job_id}")
async def api_get_research(job_id: str):
    job = get_job(job_id)
    if not job or not job.get("output_dir"):
        raise HTTPException(status_code=404, detail="Research report not found for job")
    r_json = Path(job["output_dir"]) / "research.json"
    if not r_json.exists():
        raise HTTPException(status_code=404, detail="research.json file does not exist")
    with open(r_json, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/media-providers")
async def api_get_media_providers():
    from src.provider_manager import provider_mgr
    return {
        "text_and_image": {
            "diagnostics": provider_mgr.diagnostics,
            "status_report": provider_mgr.get_status_report()
        },
        "video_generation": video_provider_mgr.get_providers_status()
    }

@app.get("/api/youtube/status")
async def api_youtube_status():
    return youtube_uploader.get_channel_info()

@app.get("/api/youtube/auth-url")
async def api_youtube_auth_url():
    auth_url, err = youtube_uploader.get_authorization_url()
    if err:
        return {"configured": False, "error": err}
    return {"configured": True, "auth_url": auth_url}

@app.get("/api/youtube/oauth-callback")
async def api_youtube_oauth_callback(code: str):
    success, msg = youtube_uploader.handle_oauth_code(code)
    if not success:
        return HTMLResponse(f"<h3>YouTube Authorization Failed</h3><p>{msg}</p>")
    return HTMLResponse("<h3>YouTube Authorization Successful!</h3><p>You can close this tab and return to the Studio Dashboard.</p><script>window.opener && window.opener.location.reload(); window.close();</script>")

@app.get("/api/publishing/queue")
async def api_publishing_queue():
    return {"publishing_queue": list_publishing_queue()}

@app.post("/api/publishing/upload/{queue_id}")
async def api_manual_upload(queue_id: int):
    items = list_publishing_queue()
    target = next((item for item in items if item["id"] == queue_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Queue item not found")

    video_path = Path(target.get("output_dir", "")) / "final_video.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=400, detail="final_video.mp4 not found in project directory")

    success, res = youtube_uploader.upload_video(
        video_path=str(video_path),
        title=target["title"],
        description=target["description"],
        tags=[t.strip() for t in (target["tags"] or "").split(",")],
        privacy_status=target.get("privacy_status", "private")
    )
    if success:
        update_publishing_status(queue_id, "uploaded", res.get("video_id"), res.get("video_url"))
        return {"status": "uploaded", "youtube_id": res.get("video_id"), "video_url": res.get("video_url")}
    else:
        update_publishing_status(queue_id, "failed", error=res.get("error"))
        raise HTTPException(status_code=500, detail=res.get("error"))

@app.get("/api/analytics")
async def api_get_analytics():
    return get_channel_analytics_summary()

@app.get("/api/costs")
async def api_get_costs():
    return cost_mgr.get_cost_report()

@app.get("/api/settings")
async def api_get_settings():
    return {"settings": get_all_settings()}

@app.post("/api/settings")
async def api_update_settings(req: SettingsUpdateRequest):
    for k, v in req.settings.items():
        set_setting(k, v)
    return {"status": "updated", "settings": get_all_settings()}

def start_server(host: str = "127.0.0.1", port: int = 8000):
    print("=" * 65)
    print(f"   RAJ EVERYWAY STUDY — STICKMAN AI VIDEO STUDIO")
    print(f"   Opening Web UI at: http://{host}:{port}")
    print("=" * 65)
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()
