"""
AI Storyboard Director & Stickman Animation Choreographer for Raj Everyway Study.
Translates topics, research briefs, and scripts into a structured multi-scene storyboard.
100% Roman Hinglish Edition.

Enforces:
1. Primary Character Continuity: Consistent Stickman protagonist (Beanie Zeke) across 100% of scenes.
2. Adaptive Composition: Intelligent alternation between Left and Right character thirds.
3. Bold Roman Hinglish Kinetic Typography Integration: Hero keyword, secondary subtitle, and styling per scene.
4. 5-Stage High-Completion Heartbeat Arc:
   - Stage 1: Golden Hook (0-5s) -> High curiosity, Stickman on Left, Hero Typography on Right.
   - Stage 2: Healthcare & Diagnostics (5-12s) -> Stickman on Right, Typography on Left.
   - Stage 3: Smart Agriculture & Drones (12-22s) -> Stickman on Left (walking/waving), Typography on Right.
   - Stage 4: Technology & Coding (22-34s) -> Stickman on Right (seated at IDE workstation), Typography on Left.
   - Stage 5: Ultimate Truth & Future (34-44s) -> Stickman on Left (explaining with confidence), Typography on Right.
   - Stage 6: Elevation & CTA (44-50s) -> Stickman on Right (joyous celebration leap), Subscribe Typography on Left.
5. Fast Pacing: Visual changes every 3-6 seconds.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Tuple, Dict, Any, List

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure root directory is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import GEMINI_API_KEY, CHANNEL_NAME
from src.stickman_engine import StickmanPose, StickmanEmotion, ShotType
from src.composition_engine import get_composition_layout
from src.hinglish_normalizer import normalize_text_to_hinglish, has_devanagari

STORYBOARD_PROMPT_TEMPLATE = """
You are the world-class AI Storyboard Director & Kinetic Typography Choreographer for "{channel_name}".

You are given a viral Roman Hinglish YouTube Short script for topic: "{topic}".
Total Narration Audio Duration: {total_duration:.2f} seconds.

SCRIPT:
Hook: {hook}
Points:
{points_str}
CTA: {cta}
Full Narration: {narration_text}

Choreograph a 6-scene storyboard where:
1. A consistent STICKMAN CHARACTER (Beanie Zeke) is the central protagonist throughout the ENTIRE video.
2. ADAPTIVE COMPOSITION: Stickman position MUST ALTERNATE between "left" and "right" across scenes.
3. KINETIC TYPOGRAPHY: Each scene MUST have bold ROMAN HINGLISH typography placed in the opposite negative space.
4. ABSOLUTELY ZERO DEVANAGARI CHARACTERS! All text must be in the English alphabet (Roman Hinglish).

Available Stickman Poses:
- "explaining" (pointing forward, conversational gestures)
- "pointing_right" (pointing to right side at typography/charts)
- "pointing_left" (pointing to left side at typography/charts)
- "pointing_up" (pointing up to headline)
- "thinking" (hand on chin, curious eyebrow)
- "shocked" (hands clutching cheeks, wide open eyes)
- "talking" (conversational gestures)
- "celebrating" (arms raised high in triumph)
- "walking" (true horizontal locomotion across frame)
- "jumping" (parabolic airborne leap)
- "sitting" (seated on studio stool at workstation desk)
- "interacting_screen" (tapping floating holographic glass UI)

Available Shot Types: "close_up", "medium", "wide"
Available Stickman Emotions: "confident", "curious", "happy", "shocked", "worried", "neutral"
Available Props: "chart", "industry_cards", "laptop", "screen", "lightbulb", "warning", "bell", "none"
Available Camera Movements: "zoom_in", "pan_right", "pan_left", "static"

Typography Styles:
- "oversized_bold" (130-160px hero word with spring bounce)
- "editorial" (category badge + hero word + secondary line)
- "kinetic_reveal" (sequential word reveal synchronized to voice)
- "emphasis_impact" (high contrast scale punch and color flash)

The sum of all scene durations MUST equal exactly {total_duration:.2f} seconds.

Output ONLY a JSON array of scene objects with this exact structure:
[
  {{
    "scene_id": 1,
    "stage": "golden_hook",
    "narration": "Roman Hinglish narration line for this scene",
    "duration": 5.0,
    "stickman_pose": "look_and_shock",
    "stickman_emotion": "shocked",
    "stickman_position": "left",
    "shot_type": "medium",
    "prop": "none",
    "typography": {{
      "primary_text": "AI KA FUTURE",
      "secondary_text": "Bharat Badalne Wala Hai",
      "category_tag": "AI REVOLUTION",
      "position": "right",
      "style": "editorial",
      "highlight_color": "#FFE600"
    }},
    "camera_movement": "zoom_in",
    "background_description": "Bengaluru Indian tech city street with elevated metro and futuristic glowing ai spire",
    "visual_prompt": "bengaluru indian modern tech city street with elevated metro and futuristic glowing ai spire, vertical 9:16, 4k photorealistic, no text",
    "transition": "cut",
    "subtitle_segment": "Roman Hinglish subtitle text for this scene"
  }}
]
"""

def extract_primary_and_secondary_words(narration: str) -> Tuple[str, str]:
    """Extracts a strong hero keyword and secondary phrase in Roman Hinglish."""
    cleaned_narr = normalize_text_to_hinglish(narration)
    words = [w.strip() for w in cleaned_narr.split() if w.strip()]
    if not words:
        return ("AI FUTURE", "Bharat Revolution")

    # Clean punctuation
    cleaned = [re.sub(r'[।!?.,\'":;]', '', w) for w in words]
    if len(cleaned) == 1:
        return (cleaned[0].upper(), "")
    elif len(cleaned) <= 3:
        return (cleaned[0].upper(), " ".join(cleaned[1:]).title())
    else:
        # Find strongest tech or topic keyword
        skip_words = {"aur", "ka", "ki", "ke", "ko", "mein", "se", "hai", "hain", "to", "bhi", "par", "kya", "the", "is", "a", "an"}
        hero_candidates = [w for w in cleaned if len(w) >= 3 and w.lower() not in skip_words]
        hero = hero_candidates[0] if hero_candidates else cleaned[0]
        rem = [w for w in cleaned if w != hero][:3]
        sec = " ".join(rem)
        return (hero.upper(), sec.title())

def generate_deterministic_storyboard(
    script_data: dict,
    total_duration: float,
    visual_style: str = "ai_cinematic"
) -> List[Dict[str, Any]]:
    """
    Creates a mathematically balanced 6-scene storyboard matching the 5-stage heartbeat arc.
    100% Roman Hinglish with alternating Left/Right adaptive framing.
    """
    hook = normalize_text_to_hinglish(script_data.get("hook", "").strip())
    points = [normalize_text_to_hinglish(p.strip()) for p in script_data.get("points", []) if p.strip()]
    cta = normalize_text_to_hinglish(script_data.get("cta", "").strip())

    segments = []

    # Scene 1: Golden Hook -> Stickman LEFT, Typography RIGHT
    if hook:
        p_word, s_phrase = extract_primary_and_secondary_words(hook)
        segments.append({
            "stage": "golden_hook_city",
            "narration": hook,
            "pose": StickmanPose.LOOK_AND_SHOCK,
            "emotion": StickmanEmotion.SHOCKED,
            "shot_type": ShotType.MEDIUM,
            "position": "left",
            "prop": "none",
            "cam": "zoom_in",
            "bg_desc": "Bengaluru Indian tech city with elevated metro and towering AI spire",
            "prompt": "bengaluru indian modern tech city street with elevated metro and futuristic glowing ai spire, vertical 9:16, 4k photorealistic, no text",
            "typo": {
                "primary_text": "AI KA FUTURE",
                "secondary_text": "Bharat Badalne Wala Hai",
                "category_tag": "AI REVOLUTION",
                "position": "right",
                "style": "editorial",
                "highlight_color": "#FFE600"
            }
        })

    # Core Points with Alternating Left / Right Framing
    for i, pt in enumerate(points):
        p_word, s_phrase = extract_primary_and_secondary_words(pt)
        if i == 0:
            # Scene 2: Healthcare -> Stickman RIGHT, Typography LEFT
            stage = "healthcare_ai"
            pose = StickmanPose.POINT_AND_EXPLAIN
            emotion = StickmanEmotion.CONFIDENT
            shot_type = ShotType.MEDIUM
            prop = "none"
            pos = "right"
            cam = "zoom_in"
            bg = "Modern hospital diagnostic ICU with holographic AI brain scan and telemetry"
            prmpt = "modern hospital ICU diagnostics room with floating holographic brain scan and patient monitors, vertical 9:16, 4k photorealistic, no text"
            typo = {
                "primary_text": "AI HEALTHCARE",
                "secondary_text": "Fast Disease Detection",
                "category_tag": "SMART MEDICINE",
                "position": "left",
                "style": "oversized_bold",
                "highlight_color": "#00F5FF"
            }
        elif i == 1:
            # Scene 3: Agriculture -> Stickman LEFT, Typography RIGHT
            stage = "agriculture_drones"
            pose = StickmanPose.WALK_AND_WAVE
            emotion = StickmanEmotion.HAPPY
            shot_type = ShotType.WIDE
            prop = "none"
            pos = "left"
            cam = "pan_left"
            bg = "Lush Indian agricultural farm field with autonomous drone scanning crops"
            prmpt = "lush green indian farm field with autonomous agricultural drone scanning crops with laser grid, vertical 9:16, 4k photorealistic, no text"
            typo = {
                "primary_text": "SMART FARMING",
                "secondary_text": "3X Crop Yield with Drones",
                "category_tag": "AGRI TECH",
                "position": "right",
                "style": "kinetic_reveal",
                "highlight_color": "#22C55E"
            }
        elif i == 2:
            # Scene 4: Coding Workstation -> Stickman RIGHT, Typography LEFT
            stage = "technology_coding"
            pose = StickmanPose.SIT_AND_EXPLAIN
            emotion = StickmanEmotion.CONFIDENT
            shot_type = ShotType.MEDIUM
            prop = "none"
            pos = "right"
            cam = "static"
            bg = "Modern developer workstation with dual monitors and Python IDE code"
            prmpt = "software developer modern workstation desk with glowing dual monitors and python code editor, vertical 9:16, 4k photorealistic, no text"
            typo = {
                "primary_text": "10X SPEED",
                "secondary_text": "AI Tools & Coding Power",
                "category_tag": "DEV REVOLUTION",
                "position": "left",
                "style": "emphasis_impact",
                "highlight_color": "#FFE600"
            }
        else:
            # Scene 5: Future & Challenges -> Stickman LEFT, Typography RIGHT
            stage = "future_and_challenges"
            pose = StickmanPose.POINT_AND_EXPLAIN
            emotion = StickmanEmotion.CONFIDENT
            shot_type = ShotType.MEDIUM
            prop = "none"
            pos = "left"
            cam = "zoom_in"
            bg = "Futuristic Indian AI innovation campus atrium with holographic network"
            prmpt = "futuristic indian ai innovation campus atrium with floating holographic global network, vertical 9:16, 4k photorealistic, no text"
            typo = {
                "primary_text": "AI SKILLS",
                "secondary_text": "Desh Ka Future Banenge",
                "category_tag": "CAREER TRUTH",
                "position": "right",
                "style": "oversized_bold",
                "highlight_color": "#FF2D55"
            }

        segments.append({
            "stage": stage,
            "narration": pt,
            "pose": pose,
            "emotion": emotion,
            "shot_type": shot_type,
            "position": pos,
            "prop": prop,
            "cam": cam,
            "bg_desc": bg,
            "prompt": prmpt,
            "typo": typo
        })

    # Scene 6: Ending & CTA -> Stickman RIGHT, Typography LEFT
    if cta:
        p_word, s_phrase = extract_primary_and_secondary_words(cta)
        segments.append({
            "stage": "elevation_cta",
            "narration": cta,
            "pose": StickmanPose.CELEBRATE_AND_CTA,
            "emotion": StickmanEmotion.HAPPY,
            "shot_type": ShotType.WIDE,
            "position": "right",
            "prop": "none",
            "cam": "zoom_in",
            "bg_desc": "Warm aesthetic YouTube creator studio with camera and soft amber lighting",
            "prompt": "warm aesthetic youtube creator studio with camera on tripod, amber backlighting, vertical 9:16, 4k photorealistic, no text",
            "typo": {
                "primary_text": "SUBSCRIBE NOW",
                "secondary_text": "Raj Everyway Study",
                "category_tag": "JOIN COMMUNITY",
                "position": "left",
                "style": "editorial",
                "highlight_color": "#FFE600"
            }
        })

    # Ensure at least 6 scenes
    if len(segments) < 6:
        extra_scenes = []
        for s in segments:
            extra_scenes.append(s)
            if len(extra_scenes) + (len(segments) - len(extra_scenes)) < 6 and len(s["narration"]) > 35:
                words = s["narration"].split()
                if len(words) >= 6:
                    mid = len(words) // 2
                    s["narration"] = " ".join(words[:mid])
                    s2 = s.copy()
                    s2["stage"] += "_part2"
                    s2["narration"] = " ".join(words[mid:])
                    s2["position"] = "right" if s["position"] == "left" else "left"
                    s2["pose"] = StickmanPose.POINT_AND_EXPLAIN
                    s2["typo"] = {
                        "primary_text": s["typo"]["primary_text"],
                        "secondary_text": "Key Insights Inside",
                        "category_tag": "KEY POINT",
                        "position": "left" if s2["position"] == "right" else "right",
                        "style": "oversized_bold",
                        "highlight_color": "#00F5FF"
                    }
                    extra_scenes.append(s2)
        if len(extra_scenes) >= 6:
            segments = extra_scenes

    # Allocate duration proportional to word count
    total_words = sum(max(1, len(s["narration"].split())) for s in segments)
    allocated_scenes = []
    accumulated_dur = 0.0

    for i, s in enumerate(segments):
        words_count = max(1, len(s["narration"].split()))
        if i == len(segments) - 1:
            dur = round(total_duration - accumulated_dur, 2)
        else:
            dur = round((words_count / total_words) * total_duration, 2)
            accumulated_dur += dur

        pos = s.get("position", "left" if i % 2 == 0 else "right")
        typo_info = s.get("typo", {})
        typo_pos = typo_info.get("position", "right" if pos == "left" else "left")

        # Resolve exact layout coordinates and collision checks
        layout = get_composition_layout(
            scene_index=i,
            stickman_pos=pos,
            typography_pos=typo_pos,
            shot_type=s.get("shot_type", ShotType.MEDIUM),
            primary_text=typo_info.get("primary_text", ""),
            secondary_text=typo_info.get("secondary_text", "")
        )

        scene_obj = {
            "scene_id": i + 1,
            "stage": s["stage"],
            "narration": s["narration"],
            "duration": max(2.5, dur),
            "stickman_pose": s["pose"],
            "stickman_emotion": s["emotion"],
            "stickman_position": pos,
            "shot_type": s.get("shot_type", ShotType.MEDIUM),
            "prop": s["prop"],
            "camera_movement": s["cam"],
            "background_description": s["bg_desc"],
            "visual_prompt": s["prompt"],
            "transition": "whoosh" if i > 0 else "cut",
            "subtitle_segment": s["narration"],
            "typography": typo_info,
            "composition": layout
        }
        allocated_scenes.append(scene_obj)

    # Normalize durations so sum equals total_duration exactly
    sum_dur = sum(sc["duration"] for sc in allocated_scenes)
    diff = total_duration - sum_dur
    if allocated_scenes:
        allocated_scenes[-1]["duration"] = round(allocated_scenes[-1]["duration"] + diff, 2)

    return allocated_scenes

def build_storyboard(
    topic: str,
    script_data: dict,
    total_duration: float,
    visual_style: str = "ai_cinematic",
    output_path: str = None
) -> List[Dict[str, Any]]:
    """
    Main Storyboard Director Entrypoint:
    Tries Gemini (3.5 Flash Lite / 3.5 Flash) for nuanced scene choreography; falls back to deterministic engine.
    Guarantees 100% Roman Hinglish with 0 Devanagari characters.
    """
    hook = normalize_text_to_hinglish(script_data.get("hook", ""))
    points = [normalize_text_to_hinglish(p) for p in script_data.get("points", [])]
    cta = normalize_text_to_hinglish(script_data.get("cta", ""))
    narration_text = normalize_text_to_hinglish(script_data.get("narration_text", ""))

    points_str = "\n".join(f"- {p}" for p in points)
    storyboard = None

    if GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            prompt = STORYBOARD_PROMPT_TEMPLATE.format(
                channel_name=CHANNEL_NAME,
                topic=topic,
                total_duration=total_duration,
                hook=hook,
                points_str=points_str,
                cta=cta,
                narration_text=narration_text
            )

            models_to_try = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-flash-latest"]
            for m in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=m,
                        contents=prompt
                    )
                    raw = response.text.strip()
                    if "```" in raw:
                        m_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
                        if m_match:
                            raw = m_match.group(1).strip()

                    parsed = json.loads(raw)
                    if isinstance(parsed, list) and len(parsed) >= 4:
                        storyboard = parsed
                        print(f"[Storyboard Director] Successfully choreographed {len(storyboard)} scenes via Gemini ({m})!")
                        break
                except Exception:
                    continue
        except Exception as e:
            print(f"[Storyboard Director] Gemini choreography notice: {e}")

    # Fallback to deterministic choreographer
    if not storyboard:
        print("[Storyboard Director] Using deterministic 6-scene adaptive Roman Hinglish choreography engine...")
        storyboard = generate_deterministic_storyboard(script_data, total_duration, visual_style=visual_style)

    # Post-process to ensure all scenes have composition layouts, typography & 100% Roman Hinglish
    for i, sc in enumerate(storyboard):
        sc["narration"] = normalize_text_to_hinglish(sc.get("narration", ""))
        sc["subtitle_segment"] = normalize_text_to_hinglish(sc.get("subtitle_segment", sc["narration"]))
        
        pos = sc.get("stickman_position", "left" if i % 2 == 0 else "right")
        sc["stickman_position"] = pos

        typo = sc.get("typography")
        if not typo:
            p_word, s_phrase = extract_primary_and_secondary_words(sc.get("narration", ""))
            typo = {
                "primary_text": p_word,
                "secondary_text": s_phrase,
                "category_tag": "AI REPORT",
                "position": "right" if pos == "left" else "left",
                "style": "editorial" if i % 2 == 0 else "oversized_bold",
                "highlight_color": "#FFE600" if i % 2 == 0 else "#00F5FF"
            }
            sc["typography"] = typo
        else:
            typo["primary_text"] = normalize_text_to_hinglish(typo.get("primary_text", ""))
            typo["secondary_text"] = normalize_text_to_hinglish(typo.get("secondary_text", ""))
            typo["category_tag"] = normalize_text_to_hinglish(typo.get("category_tag", "AI REPORT"))

        typo_pos = typo.get("position", "right" if pos == "left" else "left")
        layout = get_composition_layout(
            scene_index=i,
            stickman_pos=pos,
            typography_pos=typo_pos,
            shot_type=sc.get("shot_type", "medium"),
            primary_text=typo.get("primary_text", ""),
            secondary_text=typo.get("secondary_text", "")
        )
        sc["composition"] = layout

    # Save to file if output_path specified
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(storyboard, f, ensure_ascii=False, indent=2)
        print(f"[Storyboard Director] Saved storyboard to {output_path}")

    return storyboard
