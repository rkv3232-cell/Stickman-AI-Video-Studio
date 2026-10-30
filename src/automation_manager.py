"""
Master Automation Manager & Lifecycle Orchestrator.
Manages the complete autonomous YouTube Shorts production pipeline:
Topic Discovery -> Source-Backed Research -> Viral Scripting -> Storyboard ->
AI Visuals & Video -> Articulated Stickman Rig -> Dual-Engine Voiceover ->
Word-Highlight Captions -> MoviePy Rendering -> Thumbnail & SEO -> 100-Pt QC ->
YouTube Publishing -> Analytics.

Uses persistent SQLite storage, enforces budget limits, and supports pause/resume/retry.
"""

import os
import sys
import uuid
import json
import shutil
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Ensure root dir on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import (
    OUTPUT_DIR, DEFAULT_SPEAKER, DEFAULT_PACE,
    DEFAULT_VISUAL_STYLE, CHANNEL_NAME
)
from src.database import (
    create_job, update_job_progress, complete_job_record, fail_job_record,
    get_job, list_jobs, get_setting, set_setting, count_jobs_today,
    get_next_topic_from_queue, add_to_publishing_queue, update_publishing_status
)
from src.topic_discovery import discover_and_populate_topics
from src.researcher import research_topic, export_research_report
from src.script_gen import get_script_for_input, format_script_for_voice
from src.voice_gen import generate_voiceover_with_timings
from src.storyboard_director import build_storyboard
from src.caption_engine import build_caption_phrase_groups, export_caption_groups_to_srt
from src.video_engine import build_short_video
from src.thumbnail_gen import generate_thumbnail
from src.seo_analyzer import audit_seo_score
from src.compliance import check_script_compliance
from src.quality_control import run_quality_control
from src.hinglish_normalizer import normalize_text_to_hinglish, enforce_storyboard_hinglish, validate_final_text_is_hinglish
from src.provider_manager import provider_mgr
from src.video_providers import video_provider_mgr
from src.youtube_uploader import youtube_uploader
from src.cost_manager import cost_mgr

class AutomationManager:
    def __init__(self):
        self.current_job_id: Optional[str] = None
        self._lock = threading.Lock()
        self._is_paused = False
        self._stop_requested = False

    def is_running(self) -> bool:
        return self.current_job_id is not None

    def pause(self):
        self._is_paused = True
        set_setting("automation_enabled", "false")

    def resume(self):
        self._is_paused = False
        set_setting("automation_enabled", "true")

    def stop(self):
        self._stop_requested = True
        self._is_paused = True
        set_setting("automation_enabled", "false")

    def start_production_job(
        self,
        topic: str,
        category: str = "AI Technology",
        is_auto: bool = False,
        speaker: str = DEFAULT_SPEAKER,
        pace: float = DEFAULT_PACE,
        visual_style: str = DEFAULT_VISUAL_STYLE,
        stickman_style: str = "modern_beanie",
        auto_publish: bool = True
    ) -> str:
        """Launches a full production job in a dedicated background daemon thread."""
        with self._lock:
            if self.is_running():
                raise RuntimeError(f"Job {self.current_job_id} is already in progress.")
            
            job_id = uuid.uuid4().hex[:8]
            self.current_job_id = job_id
            self._stop_requested = False
            self._is_paused = False

            create_job(job_id=job_id, topic=topic, category=category, is_auto=is_auto)

            thread = threading.Thread(
                target=self._run_job_lifecycle,
                args=(job_id, topic, category, speaker, pace, visual_style, stickman_style, auto_publish),
                daemon=True
            )
            thread.start()
            return job_id

    def _run_job_lifecycle(
        self,
        job_id: str,
        topic: str,
        category: str,
        speaker: str,
        pace: float,
        visual_style: str,
        stickman_style: str,
        auto_publish: bool
    ):
        try:
            print(f"\n[Automation Engine] Starting Job {job_id} on topic: '{topic}'...")

            # Clean topic title for directory and filenames
            raw_title = normalize_text_to_hinglish(topic)
            clean_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in raw_title).strip("_").lower()[:35]
            if not clean_title:
                clean_title = f"video_{job_id}"

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"{clean_title}_{timestamp}"
            project_dir = OUTPUT_DIR / base_name
            project_dir.mkdir(parents=True, exist_ok=True)

            # --- STAGE 1: SOURCE-BACKED RESEARCH & FACT VERIFICATION ---
            update_job_progress(job_id, "researching", "Fact Research", 10, "Conducting source-backed research & verification...")
            research_data = research_topic(raw_title, category=category)
            research_json_path = project_dir / "research.json"
            research_md_path = project_dir / "research_report.md"
            with open(research_json_path, "w", encoding="utf-8") as f:
                json.dump(research_data, f, ensure_ascii=False, indent=2)
            export_research_report(research_data, str(research_md_path))
            print(f"  ✅ Research completed (Verdict: {research_data.get('verdict')})")

            # --- STAGE 2: VIRAL HINGLISH SCRIPT GENERATION ---
            update_job_progress(job_id, "scripting", "Script Writing", 25, "Generating 100% Roman Hinglish storytelling script...")
            script_data = get_script_for_input(prompt=raw_title)
            script_text = format_script_for_voice(script_data)

            # Double-check Hinglish compliance
            script_text = normalize_text_to_hinglish(script_text)

            dest_script = project_dir / "script.txt"
            with open(dest_script, "w", encoding="utf-8") as f:
                f.write(f"TOPIC: {raw_title}\nCATEGORY: {category}\n\n")
                f.write(f"HOOK: {script_data.get('hook', '')}\n\n")
                for i, p in enumerate(script_data.get("points", []), 1):
                    f.write(f"POINT {i}: {p}\n")
                f.write(f"\nCTA: {script_data.get('cta', '')}\n\n")
                f.write(f"COMPLETE NARRATION (ROMAN HINGLISH):\n{script_text}\n")

            # --- STAGE 3: DUAL-ENGINE VOICEOVER GENERATION ---
            update_job_progress(job_id, "voiceover", "Voiceover Narration", 38, f"Generating natural voiceover with {speaker}...")
            audio_path = project_dir / "voiceover.wav"
            duration, word_timings = generate_voiceover_with_timings(
                text=script_text,
                output_path=str(audio_path),
                speaker=speaker,
                pace=pace
            )
            print(f"  ✅ Voiceover generated: {duration:.2f}s ({len(word_timings)} words)")

            # --- STAGE 4: STORYBOARD CHOREOGRAPHER & ADAPTIVE COMPOSITION ---
            update_job_progress(job_id, "storyboard", "Storyboard Choreography", 48, "Choreographing Stickman poses and kinetic typography...")
            storyboard_path = project_dir / "storyboard.json"
            storyboard = build_storyboard(
                topic=raw_title,
                script_data=script_data,
                total_duration=duration,
                visual_style=visual_style,
                output_path=str(storyboard_path)
            )

            # Enforce 0-Devanagari check on all storyboard captions
            storyboard = enforce_storyboard_hinglish({"scenes": storyboard})["scenes"]

            # --- STAGE 5: AI SCENE VISUAL GENERATION ---
            update_job_progress(job_id, "visual_gen", "AI Visual Generation", 60, "Generating scene backgrounds with Gemini / fallback...")
            scenes_dir = project_dir / "scenes"
            scenes_dir.mkdir(parents=True, exist_ok=True)

            for sc in storyboard:
                sc_id = sc.get("scene_id", 1)
                prompt = sc.get("visual_prompt", sc.get("background_description", "futuristic tech"))
                img_dest = scenes_dir / f"scene_{sc_id}.jpg"
                success, provider = provider_mgr.generate_image_for_scene(prompt, str(img_dest), scene_idx=sc_id)
                sc["image_path"] = str(img_dest)
                sc["image_provider"] = provider

            with open(storyboard_path, "w", encoding="utf-8") as f:
                json.dump(storyboard, f, ensure_ascii=False, indent=2)

            # --- STAGE 6: SYNCHRONIZED CAPTIONS & SRT ---
            update_job_progress(job_id, "captions", "Caption Engine", 70, "Synchronizing Roman Hinglish word-highlight subtitles...")
            srt_path = project_dir / "subtitles.srt"
            caption_groups = build_caption_phrase_groups(word_timings, duration, words_per_phrase=5)
            export_caption_groups_to_srt(caption_groups, str(srt_path))

            # --- STAGE 7: COMPOSITE VIDEO RENDERING ---
            update_job_progress(job_id, "rendering", "Video Rendering", 78, "Assembling 1080x1920 30FPS composite video with Stickman rig...")
            video_filename = f"{base_name}.mp4"
            final_video_dest = project_dir / "final_video.mp4"

            build_short_video(
                audio_path=str(audio_path),
                script_text=script_text,
                storyboard=storyboard,
                visual_style=visual_style,
                stickman_style=stickman_style,
                visual_keywords=script_data.get("visual_keywords", ["tech", "ai", "study"]),
                output_filename=str(final_video_dest),
                word_timings=word_timings
            )

            # Copy to global output dir for quick direct access
            shutil.copy2(final_video_dest, OUTPUT_DIR / video_filename)

            # --- STAGE 8: HIGH-CTR THUMBNAIL & SEO METADATA ---
            update_job_progress(job_id, "metadata", "Thumbnail & SEO", 90, "Generating portrait thumbnail and YouTube SEO launch kit...")
            thumb_dest = project_dir / "thumbnail.png"
            generate_thumbnail(
                title=script_data.get("seo", {}).get("youtube_title", raw_title),
                output_path=str(thumb_dest),
                is_portrait=True
            )
            shutil.copy2(thumb_dest, OUTPUT_DIR / f"{base_name}_thumb.png")

            seo = script_data.get("seo", {})
            y_title = seo.get("youtube_title", f"{raw_title} 🚀 #Shorts")
            y_desc = seo.get("description", f"{script_text}\n\nSubscribe to {CHANNEL_NAME} for more insights!")
            y_tags = seo.get("tags", f"{clean_title}, shorts, tech, ai, {CHANNEL_NAME.lower()}")
            audit_data = audit_seo_score(y_title, y_desc, y_tags, topic_keyword=raw_title, is_shorts=True)
            comp_data = check_script_compliance(script_text, raw_title)

            metadata_dest = project_dir / "metadata.json"
            metadata_obj = {
                "channel": CHANNEL_NAME,
                "topic": raw_title,
                "youtube_title": y_title,
                "description": y_desc,
                "hashtags": seo.get("hashtags", ["#shorts", "#tech", "#ai"]),
                "tags": y_tags,
                "seo_score": audit_data.get("total_score", 95),
                "monetization_status": comp_data.get("risk_level", "SAFE"),
                "duration_seconds": round(duration, 2),
                "resolution": "1080x1920",
                "aspect_ratio": "9:16",
                "fps": 30,
                "main_character": "Articulated 2D Stickman",
                "created_at": datetime.now().isoformat()
            }
            with open(metadata_dest, "w", encoding="utf-8") as f:
                json.dump(metadata_obj, f, ensure_ascii=False, indent=2)

            # --- STAGE 9: 100-POINT QUALITY CONTROL AUDIT ---
            update_job_progress(job_id, "qc", "Quality Control", 95, "Running automated technical, visual, and audio QC audit...")
            qc_dest = project_dir / "quality_report.md"
            qc_results = run_quality_control(
                video_path=str(final_video_dest),
                audio_path=str(audio_path),
                storyboard=storyboard,
                script_data=script_data,
                output_report_path=str(qc_dest)
            )

            # --- STAGE 10: COMPLETION & PUBLISHING QUEUE ---
            complete_job_record(
                job_id=job_id,
                output_dir=str(project_dir),
                video_filename=video_filename,
                thumb_filename=f"{base_name}_thumb.png",
                qc_score=qc_results["total_score"],
                qc_verdict=qc_results["verdict"],
                duration=duration
            )

            # Record cost
            cost_mgr.record_usage(
                provider="Studio Production",
                operation="Complete Short Render",
                units=1.0,
                cost_usd=0.01,
                job_id=job_id,
                details=f"Rendered {duration:.1f}s video with QC score {qc_results['total_score']}/100"
            )

            # Queue for publishing or direct upload
            privacy_setting = get_setting("default_privacy", "private")
            q_id = add_to_publishing_queue(
                job_id=job_id,
                title=y_title,
                description=y_desc,
                tags=y_tags,
                privacy=privacy_setting
            )

            if auto_publish and youtube_uploader.is_authenticated():
                print(f"[YouTube Publishing] Uploading video to authorized channel...")
                update_job_progress(job_id, "publishing", "YouTube Upload", 98, "Publishing video to YouTube...")
                success, up_res = youtube_uploader.upload_video(
                    video_path=str(final_video_dest),
                    title=y_title,
                    description=y_desc,
                    tags=[t.strip() for t in y_tags.split(",")],
                    privacy_status=privacy_setting
                )
                if success:
                    update_publishing_status(q_id, "uploaded", up_res.get("video_id"), up_res.get("video_url"))
                    print(f"  🎉 Published to YouTube: {up_res.get('video_url')}")
                else:
                    update_publishing_status(q_id, "failed", error=up_res.get("error"))
                    print(f"  ⚠️ YouTube upload error: {up_res.get('error')}")

            print(f"\n[Automation Engine] Job {job_id} successfully completed! Output: {project_dir}")

        except Exception as e:
            print(f"[Automation Engine ERROR in Job {job_id}]: {str(e)}")
            fail_job_record(job_id, str(e))
        finally:
            with self._lock:
                self.current_job_id = None

    def start_next_automated_job(self) -> Optional[str]:
        """Picks the next discovered topic from the queue and triggers production."""
        if self.is_running():
            return None

        # Check daily limit
        daily_limit = int(get_setting("daily_video_limit", "2"))
        today_jobs = count_jobs_today()
        if today_jobs >= daily_limit:
            print(f"[Scheduler] Daily target reached ({today_jobs}/{daily_limit} videos today).")
            return None

        # Check budget
        allowed, msg = cost_mgr.check_budget_allowance(0.05)
        if not allowed:
            print(f"[Scheduler] Budget check: {msg}")
            return None

        # Get topic from queue
        topic_item = get_next_topic_from_queue()
        if not topic_item:
            print("[Scheduler] Queue empty; triggering topic discovery radar...")
            discover_and_populate_topics()
            topic_item = get_next_topic_from_queue()

        if not topic_item:
            print("[Scheduler] No topics available.")
            return None

        return self.start_production_job(
            topic=topic_item["topic"],
            category=topic_item.get("category", "AI Technology"),
            is_auto=True
        )

automation_mgr = AutomationManager()

if __name__ == "__main__":
    print("Automation Manager Initialized!")
    print(" - Currently Running:", automation_mgr.is_running())

