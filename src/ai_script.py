"""
Gemini AI Script & YouTube SEO Generator for Raj Everyway Study.
Generates viral Hinglish YouTube Shorts scripts (Hook -> Points -> CTA)
strictly written in Roman Hinglish (English Alphabet) with 0 Devanagari characters,
along with YouTube SEO metadata (Title, Description, Hashtags, Tags)
and visual matching prompts for 9:16 background generation.
"""

import os
import sys
import json
import re
from pathlib import Path

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

from google import genai
from config import GEMINI_API_KEY, CHANNEL_NAME
from src.hinglish_normalizer import normalize_text_to_hinglish, has_devanagari

def get_gemini_client():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in .env")
    return genai.Client(api_key=GEMINI_API_KEY)

PROMPT_TEMPLATE = """
You are the world-class YouTube Shorts Scriptwriter & SEO Strategist for the tech & educational YouTube channel "{channel_name}".

The user wants a viral 30-45 second YouTube Short on the following topic:
TOPIC: "{topic}"

CRITICAL REQUIREMENT:
The entire script MUST BE WRITTEN IN NATURAL ROMAN HINGLISH (Indian Hindi/English written strictly in the English alphabet, like WhatsApp / YouTube creator language).
NEVER OUTPUT ANY DEVANAGARI CHARACTERS! 
Examples of required Roman Hinglish style:
- "Kya 2026 tak AI Bharat ka future puri tarah badal dega?"
- "Healthcare mein AI doctors ki help se serious diseases seconds mein detect ho rahi hain."
- "Sach to yeh hai ki AI jobs nahi chheenega, balki AI seekhne wale log leader banenge!"

Structure requirements:
1. "title": Catchy YouTube Shorts Title in Roman Hinglish with 1-2 relevant emojis (under 60 characters).
2. "hook": 1 short magnetic opening question or myth buster in Roman Hinglish.
3. "points": An array of 3 or 4 punchy, high-value bullet points in Roman Hinglish. Keep each under 18 words.
4. "cta": A strong closing call-to-action in Roman Hinglish urging viewers to follow/subscribe to "{channel_name}".
5. "narration_text": The complete combined voiceover text (Hook + Points + CTA) formatted specifically for Text-To-Speech:
   - Absolutely NO markdown (no asterisks, no hashes, no bullet dashes).
   - NO emojis in narration_text.
   - Natural punctuation (periods and commas) for natural speaking rhythm.
6. "seo":
   - "youtube_title": Viral YouTube Title with #Shorts in Roman Hinglish.
   - "description": High-converting 2-paragraph YouTube description in Roman Hinglish with channel callout.
   - "hashtags": Array of 10-15 trending hashtags (e.g., ["#shorts", "#tech", "#aiinindia", "#futureofai", "#viral"]).
   - "tags": Comma-separated YouTube video tags.
7. "visual_keywords": Array of 4 English visual generation prompts matching each scene (e.g., ["futuristic Indian AI tech laboratory with neon hologram", "smart agriculture drone over lush farm field at sunrise", "high-tech coding workspace with glowing multiple monitors", "cinematic futuristic city skyline with digital networks"]).

Return ONLY a valid JSON object with these exact keys:
{{
  "title": "string",
  "hook": "string",
  "points": ["string", "string", "string"],
  "cta": "string",
  "narration_text": "string",
  "seo": {{
    "youtube_title": "string",
    "description": "string",
    "hashtags": ["string"],
    "tags": "string"
  }},
  "visual_keywords": ["string", "string", "string", "string"]
}}
"""

def generate_ai_script(topic: str) -> dict:
    """
    Calls Gemini (3.5 Flash Lite / 3.5 Flash) to generate a complete viral Roman Hinglish Short package.
    Guarantees 100% Roman Hinglish with 0 Devanagari characters.
    """
    client = get_gemini_client()
    formatted_prompt = PROMPT_TEMPLATE.format(
        channel_name=CHANNEL_NAME,
        topic=topic.strip()
    )

    models_to_try = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-flash-latest"]
    raw_text = None

    for m in models_to_try:
        try:
            response = client.models.generate_content(
                model=m,
                contents=formatted_prompt,
            )
            raw_text = response.text.strip()
            if raw_text:
                break
        except Exception as e:
            print(f"[Gemini AI Script] Model {m} error: {e}")
            continue

    if not raw_text:
        print("[Gemini AI Script] All models failed, using curated Roman Hinglish fallback.")
        return get_fallback_script(topic)

    try:
        # Clean potential markdown fences ```json ... ```
        if "```" in raw_text:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_text)
            if match:
                raw_text = match.group(1).strip()

        data = json.loads(raw_text)

        # Ensure narration_text is clean
        if "narration_text" not in data or not data["narration_text"]:
            parts = [data.get("hook", "")]
            parts.extend(data.get("points", []))
            parts.append(data.get("cta", ""))
            data["narration_text"] = " ".join(p.strip() for p in parts if p.strip())

        # Strip any accidental asterisks/emojis from narration text
        clean_narr = re.sub(r'[\*\_#`~]', '', data["narration_text"])
        data["narration_text"] = clean_narr.strip()

        # Enforce 100% Roman Hinglish on every field
        data["title"] = normalize_text_to_hinglish(data["title"], client)
        data["hook"] = normalize_text_to_hinglish(data["hook"], client)
        data["cta"] = normalize_text_to_hinglish(data["cta"], client)
        data["narration_text"] = normalize_text_to_hinglish(data["narration_text"], client)
        data["points"] = [normalize_text_to_hinglish(p, client) for p in data.get("points", [])]

        if "seo" in data and isinstance(data["seo"], dict):
            for k in ["youtube_title", "description", "tags"]:
                if k in data["seo"] and isinstance(data["seo"][k], str):
                    data["seo"][k] = normalize_text_to_hinglish(data["seo"][k], client)

        return data

    except Exception as e:
        print(f"[Gemini AI Script JSON Parse Error]: {e}")
        return get_fallback_script(topic)

def get_fallback_script(topic: str) -> dict:
    """Curated, high-retention Roman Hinglish fallback script."""
    return {
        "title": "Future of AI in India 2026",
        "hook": "Kya 2026 tak Artificial Intelligence Bharat ka future puri tarah badal dega?",
        "points": [
            "Healthcare mein AI doctors ki help se serious diseases seconds mein detect ho rahi hain.",
            "Indian farming mein smart drones aur AI sensors fasal ki paidaawar 3 guna badha rahe hain.",
            "Software aur coding mein Indian developers AI tools se 10X tezi se naye systems build kar rahe hain.",
            "Sach to yeh hai ki AI jobs nahi chheenega, balki AI seekhne wale log desh ka future decide karenge."
        ],
        "cta": "Isliye aaj hi nayi AI skills seekhna shuru kijiye aur Raj Everyway Study ko abhi subscribe kijiye!",
        "narration_text": "Kya 2026 tak Artificial Intelligence Bharat ka future puri tarah badal dega? Healthcare mein AI doctors ki help se serious diseases seconds mein detect ho rahi hain. Indian farming mein smart drones aur AI sensors fasal ki paidaawar 3 guna badha rahe hain. Software aur coding mein Indian developers AI tools se 10X tezi se naye systems build kar rahe hain. Sach to yeh hai ki AI jobs nahi chheenega, balki AI seekhne wale log desh ka future decide karenge. Isliye aaj hi nayi AI skills seekhna shuru kijiye aur Raj Everyway Study ko abhi subscribe kijiye!",
        "seo": {
            "youtube_title": "Future of AI in India 2026 🇮🇳🤖 | Reality Dekh Kar Shock Ho Jaoge! #Shorts",
            "description": "Kya Bharat AI ki duniya mein next superpower banne wala hai? Janiye Bharat mein AI ke future ki sachhai!\n\nSubscribe to Raj Everyway Study for daily tech and AI insights.",
            "hashtags": ["#shorts", "#aiinindia", "#futureofai", "#artificialintelligence", "#rajeverywaystudy", "#techtrends", "#indiangrowth", "#upskilling"],
            "tags": "future of ai in india, india ai 2026, artificial intelligence india, ai jobs india, raj everyway study"
        },
        "visual_keywords": [
            "futuristic Indian cyber tech hub with glowing neon networks, 9:16 vertical",
            "advanced AI medical diagnostics holographic interface in hospital, 9:16 vertical",
            "smart agricultural drone flying over Indian farming fields at golden hour, 9:16 vertical",
            "high tech Indian coder workspace with holographic code streams, 9:16 vertical"
        ]
    }
