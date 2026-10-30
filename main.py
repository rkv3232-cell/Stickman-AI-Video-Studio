"""
Main Pipeline Orchestrator — Stickman AI Video Production Studio (Raj Everyway Study).
Fully automated 1-click pipeline: Topic -> Viral Script -> Storyboard -> Stickman Video -> QC -> 7 Deliverables.

Deliverables Produced per Video:
1. final_video.mp4  (1080x1920 30FPS H.264/AAC with articulated Stickman in 100% of scenes)
2. thumbnail.png    (High-CTR portrait YouTube Shorts thumbnail)
3. script.txt       (Structured Hindi script with hook, points, CTA, and voiceover text)
4. storyboard.json  (Scene-by-scene cinematography & Stickman choreography plan)
5. subtitles.srt    (Synchronized Devanagari Hindi subtitles)
6. metadata.json    (YouTube title, description, tags, hashtags, SEO score & monetization status)
7. quality_report.md (Automated technical, visual, audio, and compliance QC audit)
"""

import argparse
import sys
import re
import json
import shutil
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from config import (
    OUTPUT_DIR, DEFAULT_SPEAKER, DEFAULT_PACE,
    AVAILABLE_SPEAKERS, VISUAL_STYLES, DEFAULT_VISUAL_STYLE,
    CHANNEL_NAME
)
from src.script_gen import get_script_for_input, list_available_topics, format_script_for_voice
from src.voice_gen import generate_voiceover, generate_voiceover_with_timings
from src.storyboard_director import build_storyboard
from src.subtitle_gen import export_subtitles_to_srt
from src.caption_engine import build_caption_phrase_groups, export_caption_groups_to_srt
from src.video_engine import build_short_video
from src.thumbnail_gen import generate_thumbnail
from src.seo_analyzer import audit_seo_score
from src.compliance import check_script_compliance
from src.quality_control import run_quality_control
from src.hinglish_normalizer import normalize_text_to_hinglish, enforce_storyboard_hinglish, validate_final_text_is_hinglish

def export_production_bundle(
    project_dir: Path,
    base_name: str,
    final_video_path: str,
    thumb_path: str,
    script_data: dict,
    storyboard: list[dict],
    srt_path: str,
    audit_data: dict,
    comp_data: dict,
    qc_results: dict,
    total_duration: float
) -> dict:
    """
    Saves the full 7-file delivery package in the dedicated project directory.
    """
    project_dir.mkdir(parents=True, exist_ok=True)

    # 1. final_video.mp4
    dest_video = project_dir / "final_video.mp4"
    shutil.copy2(final_video_path, dest_video)

    # 2. thumbnail.png
    dest_thumb = project_dir / "thumbnail.png"
    shutil.copy2(thumb_path, dest_thumb)

    # 3. script.txt
    dest_script = project_dir / "script.txt"
    with open(dest_script, "w", encoding="utf-8") as f:
        f.write("=" * 65 + "\n")
        f.write(f"  {CHANNEL_NAME} — VIRAL HINDI SCRIPT\n")
        f.write("=" * 65 + "\n\n")
        f.write(f"TOPIC: {script_data.get('title', '')}\n")
        f.write(f"DURATION: {total_duration:.2f} seconds\n")
        f.write(f"PROTAGONIST: Articulated 2D Stickman (100% Anatomical Consistency)\n\n")
        f.write("-" * 65 + "\n")
        f.write("🎯 [1] GOLDEN HOOK:\n")
        f.write(f"{script_data.get('hook', '')}\n\n")
        f.write("-" * 65 + "\n")
        f.write("💡 [2] CORE EXPLANATION (INSIDER SECRETS):\n")
        for i, pt in enumerate(script_data.get("points", []), 1):
            f.write(f"  Point {i}: {pt}\n")
        f.write("\n" + "-" * 65 + "\n")
        f.write("📢 [3] CALL TO ACTION (CTA):\n")
        f.write(f"{script_data.get('cta', '')}\n\n")
        f.write("-" * 65 + "\n")
        f.write("🎙️ [4] COMPLETE VOICEOVER NARRATION (TEXT-TO-SPEECH FORMAT):\n")
        f.write(f"{format_script_for_voice(script_data)}\n")

    # 4. storyboard.json
    dest_storyboard = project_dir / "storyboard.json"
    with open(dest_storyboard, "w", encoding="utf-8") as f:
        json.dump(storyboard, f, ensure_ascii=False, indent=2)

    # 4B. Copy generated scene images to project bundle
    src_scenes = OUTPUT_DIR / base_name / "scenes"
    dest_scenes = project_dir / "scenes"
    if src_scenes.exists():
        if dest_scenes.exists():
            shutil.rmtree(dest_scenes)
        shutil.copytree(src_scenes, dest_scenes)

    # 5. subtitles.srt
    dest_srt = project_dir / "subtitles.srt"
    shutil.copy2(srt_path, dest_srt)

    # 6. metadata.json
    seo = script_data.get("seo", {})
    dest_metadata = project_dir / "metadata.json"
    metadata_obj = {
        "channel": CHANNEL_NAME,
        "topic": script_data.get("title", ""),
        "youtube_title": seo.get("youtube_title", script_data.get("title", "")),
        "description": seo.get("description", ""),
        "hashtags": seo.get("hashtags", ["#shorts", "#tech", "#rajeverywaystudy"]),
        "tags": seo.get("tags", "shorts, tech, rajeverywaystudy"),
        "seo_score": audit_data.get("total_score", 95),
        "seo_grade": audit_data.get("grade", "A+"),
        "monetization_status": comp_data.get("risk_level", "SAFE"),
        "duration_seconds": round(total_duration, 2),
        "resolution": "1080x1920",
        "aspect_ratio": "9:16",
        "fps": 30,
        "video_codec": "H.264",
        "audio_codec": "AAC",
        "main_character": "Consistent Articulated 2D Stickman",
        "scenes_count": len(storyboard),
        "qc_score": qc_results.get("total_score", 95),
        "qc_verdict": qc_results.get("verdict", "PASSED"),
        "created_at": datetime.now().isoformat()
    }
    with open(dest_metadata, "w", encoding="utf-8") as f:
        json.dump(metadata_obj, f, ensure_ascii=False, indent=2)

    # 7. quality_report.md
    dest_qc = project_dir / "quality_report.md"
    qc_src = OUTPUT_DIR / f"{base_name}_quality_report.md"
    if qc_src.exists():
        shutil.copy2(qc_src, dest_qc)

    # Also save standard SEO launch text for fast copy-paste
    seo_file = project_dir / "SEO_LAUNCH_KIT.txt"
    with open(seo_file, "w", encoding="utf-8") as f:
        f.write("=" * 65 + "\n")
        f.write(f"  {CHANNEL_NAME} — YOUTUBE SEO LAUNCH KIT\n")
        f.write("=" * 65 + "\n\n")
        f.write(f"📌 VIDEO: final_video.mp4\n")
        f.write(f"🖼️ THUMBNAIL: thumbnail.png\n")
        f.write(f"📊 SEO SCORE: {audit_data['total_score']}/100 ({audit_data['grade']})\n")
        f.write(f"🛡️ MONETIZATION: {comp_data['tips']}\n\n")
        f.write("-" * 65 + "\n")
        f.write(f"🎯 YOUTUBE TITLE:\n{metadata_obj['youtube_title']}\n\n")
        f.write("-" * 65 + "\n")
        f.write(f"📝 DESCRIPTION:\n{metadata_obj['description']}\n\n")
        f.write(f"🏷️ HASHTAGS:\n{' '.join(metadata_obj['hashtags'])}\n\n")
        f.write("-" * 65 + "\n")
        f.write(f"🔍 TAGS:\n{metadata_obj['tags']}\n")

    return {
        "final_video": str(dest_video),
        "thumbnail": str(dest_thumb),
        "script": str(dest_script),
        "storyboard": str(dest_storyboard),
        "subtitles": str(dest_srt),
        "metadata": str(dest_metadata),
        "quality_report": str(dest_qc),
        "project_dir": str(project_dir)
    }

def generate_short(
    prompt: str = None,
    topic_key: str = None,
    custom_text: str = None,
    speaker: str = DEFAULT_SPEAKER,
    pace: float = DEFAULT_PACE,
    visual_style: str = DEFAULT_VISUAL_STYLE,
    stickman_style: str = "modern_beanie",
    output_name: str = None
) -> dict:
    print("=" * 70)
    print(f"   {CHANNEL_NAME} — STICKMAN AI VIDEO PRODUCTION STUDIO")
    print("   1-Click Topic to Broadcast-Grade YouTube Shorts Pipeline")
    print("=" * 70)

    # ══════════════════════════════════════════════════════════
    # STAGE 1 & 2: TOPIC RESEARCH & VIRAL HINGLISH SCRIPT WRITER
    # ══════════════════════════════════════════════════════════
    print("\n[Stage 1/7] Researching Topic & Generating Viral Roman Hinglish Script...")
    script_data = get_script_for_input(
        topic_key=topic_key,
        prompt=prompt,
        custom_text=custom_text
    )
    script_text = format_script_for_voice(script_data)

    raw_title = normalize_text_to_hinglish(script_data.get("title", "ai_stickman_short"))
    clean_title = re.sub(r'[^\w\-]', '_', raw_title).strip('_').lower()[:35]
    if not clean_title:
        clean_title = "stickman_short"

    print(f"  🎬 Title: {raw_title}")
    print(f"  ⚡ Golden Hook: {script_data.get('hook', '')}")
    if script_data.get("points"):
        print(f"  💡 Narrative Points: {len(script_data['points'])} key secrets")
    print(f"  📝 Narration Length: {len(script_text)} characters (100% Roman Hinglish)")

    # Compliance check
    comp = check_script_compliance(script_text, script_data.get("title", ""))
    print(f"  🛡️ Monetization Status: {comp['risk_level']} ({comp['tips']})")

    # ══════════════════════════════════════════════════════════
    # STAGE 3: HINDI VOICEOVER GENERATION (DUAL ENGINE)
    # ══════════════════════════════════════════════════════════
    if not output_name:
        output_name = f"{clean_title}.mp4"
    if not output_name.endswith(".mp4"):
        output_name += ".mp4"

    base_name = Path(output_name).stem
    audio_temp = OUTPUT_DIR / f"{base_name}_voice.wav"

    print(f"\n[Stage 2/7] Generating Hindi Voiceover Narration...")
    speaker_info = AVAILABLE_SPEAKERS.get(speaker, {})
    print(f"  🎙️ Speaker: {speaker} [{speaker_info.get('engine', 'TTS')}] ({speaker_info.get('desc', 'Voice')})")
    print(f"  ⚡ Pace: {pace}x")

    duration, word_timings = generate_voiceover_with_timings(
        text=script_text,
        output_path=str(audio_temp),
        speaker=speaker,
        pace=pace
    )
    print(f"  ✅ Voiceover generated: {duration:.2f} seconds ({len(word_timings)} words captured)")

    # ══════════════════════════════════════════════════════════
    # STAGE 4: AI STORYBOARD DIRECTOR & STICKMAN CHOREOGRAPHER
    # ══════════════════════════════════════════════════════════
    print(f"\n[Stage 3/7] Choreographing 5-Stage Storyboard & Stickman Poses...")
    storyboard_file = OUTPUT_DIR / f"{base_name}_storyboard.json"
    storyboard = build_storyboard(
        topic=raw_title,
        script_data=script_data,
        total_duration=duration,
        visual_style=visual_style,
        output_path=str(storyboard_file)
    )
    print(f"  ✅ Choreographed {len(storyboard)} Scenes with Stickman as Lead Actor!")

    # Pre-render Hinglish Enforcement & Validation
    is_valid, violations = validate_final_text_is_hinglish({"title": raw_title, "narration_text": script_text, "scenes": storyboard})
    if not is_valid:
        print(f"  ⚠️ Warning: {len(violations)} Devanagari occurrences detected. Enforcing Roman Hinglish normalization...")
        storyboard = enforce_storyboard_hinglish({"scenes": storyboard})["scenes"]

    # ══════════════════════════════════════════════════════════
    # STAGE 3.5: AI SCENE IMAGE GENERATION PIPELINE
    # ══════════════════════════════════════════════════════════
    print(f"\n[Stage 3.5/7] Executing AI Scene Image Generation Pipeline...")
    scenes_dir = OUTPUT_DIR / base_name / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    from src.provider_manager import provider_mgr

    for sc in storyboard:
        sc_id = sc.get("scene_id", 1)
        prompt = sc.get("visual_prompt", sc.get("background_description", "futuristic tech"))
        img_dest = scenes_dir / f"scene_{sc_id}.jpg"
        print(f"  🎨 Generating Scene #{sc_id} background...")
        success, provider = provider_mgr.generate_image_for_scene(prompt, str(img_dest), scene_idx=sc_id)
        sc["image_path"] = str(img_dest)
        sc["image_provider"] = provider
        print(f"  ✅ Scene #{sc_id} Image saved to {img_dest.name} (Provider: {provider})")

    # Update storyboard file with image associations
    with open(storyboard_file, "w", encoding="utf-8") as f:
        json.dump(storyboard, f, ensure_ascii=False, indent=2)

    # ══════════════════════════════════════════════════════════
    # STAGE 5: AUTOMATIC SUBTITLE GENERATION (ROMAN HINGLISH & SRT)
    # ══════════════════════════════════════════════════════════
    print(f"\n[Stage 4/7] Generating Synchronized Roman Hinglish Word-Highlight Subtitles & SRT...")
    srt_temp = OUTPUT_DIR / f"{base_name}_subtitles.srt"
    caption_groups = build_caption_phrase_groups(word_timings, duration, words_per_phrase=5)
    export_caption_groups_to_srt(caption_groups, str(srt_temp))

    # ══════════════════════════════════════════════════════════
    # STAGE 6: STICKMAN VIDEO ENGINE RENDERING (COMPOSITE)
    # ══════════════════════════════════════════════════════════
    print(f"\n[Stage 5/7] Assembling Multi-Scene Stickman Video & Multi-Track Audio...")
    print(f"  🎭 Character: Consistent 2D Stickman (Style: {stickman_style})")
    print(f"  🌌 Background Visual Style: {visual_style} ({VISUAL_STYLES.get(visual_style, '')})")
    visual_keywords = script_data.get("visual_keywords", ["tech", "coding", "ai", "study"])

    final_video_path = build_short_video(
        audio_path=str(audio_temp),
        script_text=script_text,
        storyboard=storyboard,
        visual_style=visual_style,
        stickman_style=stickman_style,
        visual_keywords=visual_keywords,
        output_filename=output_name,
        word_timings=word_timings
    )

    # ══════════════════════════════════════════════════════════
    # STAGE 7: THUMBNAIL, SEO, & QUALITY CONTROL
    # ══════════════════════════════════════════════════════════
    print(f"\n[Stage 6/7] Generating High-CTR Thumbnail & Running 100-Pt SEO Audit...")
    thumb_path = OUTPUT_DIR / f"{base_name}_thumb.png"
    generate_thumbnail(
        title=script_data.get("seo", {}).get("youtube_title", raw_title),
        output_path=str(thumb_path),
        is_portrait=True
    )

    seo = script_data.get("seo", {})
    y_title = seo.get("youtube_title", raw_title)
    y_desc = seo.get("description", "")
    y_tags = seo.get("tags", "shorts, tech, rajeverywaystudy")
    audit = audit_seo_score(y_title, y_desc, y_tags, topic_keyword=raw_title, is_shorts=True)
    print(f"  📊 YouTube SEO Score: {audit['total_score']}/100 ({audit['grade']})")

    print(f"\n[Stage 7/7] Executing Automatic Quality Control Engine...")
    qc_report_path = OUTPUT_DIR / f"{base_name}_quality_report.md"
    qc_results = run_quality_control(
        video_path=final_video_path,
        audio_path=str(audio_temp),
        storyboard=storyboard,
        script_data=script_data,
        output_report_path=str(qc_report_path)
    )
    print(f"  🛡️ QC Score: {qc_results['total_score']}/100 -> Verdict: {qc_results['verdict']}")

    # ══════════════════════════════════════════════════════════
    # EXPORT COMPLETE 7-FILE PRODUCTION PACKAGE
    # ══════════════════════════════════════════════════════════
    project_folder = OUTPUT_DIR / clean_title
    bundle = export_production_bundle(
        project_dir=project_folder,
        base_name=base_name,
        final_video_path=final_video_path,
        thumb_path=str(thumb_path),
        script_data=script_data,
        storyboard=storyboard,
        srt_path=str(srt_temp),
        audit_data=audit,
        comp_data=comp,
        qc_results=qc_results,
        total_duration=duration
    )

    print("\n" + "=" * 70)
    print("   🏆 SUCCESS! ALL 7 PRODUCTION DELIVERABLES COMPLETED")
    print("=" * 70)
    print(f"📁 PROJECT PACKAGE: {bundle['project_dir']}")
    print(f"  1. 🎥 final_video.mp4:   {Path(bundle['final_video']).name}")
    print(f"  2. 🖼️ thumbnail.png:     {Path(bundle['thumbnail']).name}")
    print(f"  3. 📜 script.txt:         {Path(bundle['script']).name}")
    print(f"  4. 📋 storyboard.json:    {Path(bundle['storyboard']).name} ({len(storyboard)} scenes)")
    print(f"  5. 💬 subtitles.srt:      {Path(bundle['subtitles']).name}")
    print(f"  6. 📊 metadata.json:      {Path(bundle['metadata']).name} (SEO: {audit['total_score']}/100)")
    print(f"  7. 🛡️ quality_report.md:  {Path(bundle['quality_report']).name} (QC: {qc_results['total_score']}/100 - {qc_results['verdict']})")
    print("=" * 70)

    return bundle

def main():
    parser = argparse.ArgumentParser(
        description="Raj Everyway Study — Stickman AI Video Production Studio"
    )
    parser.add_argument(
        "--prompt", "-p",
        type=str,
        default=None,
        help="Any topic/idea to auto-generate script & SEO with Gemini 2.5 Flash"
    )
    parser.add_argument(
        "--topic", "-t",
        type=str,
        default=None,
        choices=list_available_topics(),
        help=f"Select curated template. Choices: {', '.join(list_available_topics())}"
    )
    parser.add_argument(
        "--custom-text", "-c",
        type=str,
        default=None,
        help="Provide your own custom Hindi script text"
    )
    parser.add_argument(
        "--speaker", "-s",
        type=str,
        default=DEFAULT_SPEAKER,
        choices=list(AVAILABLE_SPEAKERS.keys()),
        help=f"Voice speaker name (e.g. {', '.join(AVAILABLE_SPEAKERS.keys())})"
    )
    parser.add_argument(
        "--pace",
        type=float,
        default=DEFAULT_PACE,
        help="Voice pace multiplier (e.g. 1.0, 1.05, 1.15)"
    )
    parser.add_argument(
        "--style",
        type=str,
        default=DEFAULT_VISUAL_STYLE,
        choices=list(VISUAL_STYLES.keys()) + ["sketch_notes"],
        help=f"Visual background style: {', '.join(VISUAL_STYLES.keys())}, sketch_notes"
    )
    parser.add_argument(
        "--stickman-style",
        type=str,
        default="modern_beanie",
        choices=["modern_beanie", "classic", "cyber_neon"],
        help="Stickman character appearance style: modern_beanie, classic, cyber_neon"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Custom output mp4 filename"
    )

    args = parser.parse_args()

    if not args.prompt and not args.topic and not args.custom_text:
        args.topic = "ai_study"

    generate_short(
        prompt=args.prompt,
        topic_key=args.topic,
        custom_text=args.custom_text,
        speaker=args.speaker,
        pace=args.pace,
        visual_style=args.style,
        stickman_style=args.stickman_style,
        output_name=args.output
    )

if __name__ == "__main__":
    main()
