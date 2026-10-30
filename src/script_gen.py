"""
Script Generator for Raj Everyway Study YouTube Shorts.
100% Roman Hinglish Edition.
Supports:
1. Dynamic Gemini AI Script Generation (Any topic or custom prompt in Roman Hinglish)
2. Curated Viral Templates (india_ai_future, ai_future, ai_study, ai_winter, deepseek_ai)
3. Custom Raw Script Text
"""

import sys
from pathlib import Path

# Ensure root directory is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.ai_script import generate_ai_script, get_fallback_script
from src.hinglish_normalizer import normalize_text_to_hinglish

SAMPLE_TEMPLATES = {
    "india_ai_future": {
        "title": "Future of AI in India 2026",
        "hook": "Kya 2026 tak Artificial Intelligence Bharat ka future puri tarah badal dega?",
        "points": [
            "Healthcare mein AI doctors ki help se serious diseases seconds mein detect ho rahi hain.",
            "Indian farming mein smart drones aur AI sensors fasal ki paidaawar 3 guna badha rahe hain.",
            "Software aur coding mein Indian developers AI tools se 10X tezi se naye systems build kar rahe hain.",
            "Sach to yeh hai ki AI jobs nahi chheenega, balki AI seekhne wale log desh ka future decide karenge."
        ],
        "cta": "Isliye aaj hi nayi AI skills seekhna shuru kijiye aur Raj Everyway Study ko abhi subscribe kijiye!",
        "seo": {
            "youtube_title": "Future of AI in India 2026 🇮🇳🤖 | Reality Dekh Kar Shock Ho Jaoge! #Shorts",
            "description": "Kya Bharat AI ki duniya mein superpower banne wala hai? Janiye Bharat mein AI ke future ki puri sachhai!\n\nSubscribe to Raj Everyway Study for daily tech and AI insights.",
            "hashtags": ["#shorts", "#aiinindia", "#futureofai", "#artificialintelligence", "#rajeverywaystudy", "#techtrends", "#indiangrowth", "#upskilling"],
            "tags": "future of ai in india, india ai 2026, artificial intelligence india, ai jobs india, raj everyway study"
        },
        "visual_keywords": [
            "futuristic Indian cyber tech hub with glowing neon networks, 9:16 vertical",
            "advanced AI medical diagnostics holographic interface in hospital, 9:16 vertical",
            "smart agricultural drone flying over Indian farming fields at golden hour, 9:16 vertical",
            "high tech Indian coder workspace with holographic code streams, 9:16 vertical"
        ]
    },
    "ai_future": {
        "title": "Will AI Replace Programmers?",
        "hook": "Kya Artificial Intelligence sach mein humans ki jobs khatam kar dega?",
        "points": [
            "Reality yeh hai ki AI humans ko replace nahi karega, balki AI use karne wale log unhe replace karenge jo AI nahi seekhte.",
            "Aaj AI coding, writing aur designing ko 10 guna fast bana raha hai.",
            "Isliye darne ke bajay, naye AI tools ko seekhna shuru kijiye."
        ],
        "cta": "AI ki duniya mein updated rehne ke liye Raj Everyway Study ko follow karein!",
        "seo": {
            "youtube_title": "Will AI Replace Programmers in 2026? 🤖 #Shorts",
            "description": "Will AI take our jobs? Watch this reality check on AI vs Programmers!\n\nSubscribe to Raj Everyway Study for daily tech and AI insights.",
            "hashtags": ["#shorts", "#ai", "#coding", "#futuretech", "#rajeverywaystudy", "#programming", "#techtrends"],
            "tags": "ai replace programmers, future of coding, artificial intelligence, raj everyway study"
        },
        "visual_keywords": ["robot thinking cyber lab", "programmer coding multi monitor", "futuristic tech city", "subscribe button bell"]
    },
    "ai_study": {
        "title": "Top 3 AI Tools for Students in 2026",
        "hook": "Kya aap bhi ghanton baithkar manual notes banane mein time waste kar rahe hain?",
        "points": [
            "Number one: Perplexity AI, jo aapke kisi bhi difficult question ka verified sources ke sath answer deta hai.",
            "Number two: NotebookLM, isme apni PDF book upload kijiye aur yeh aapko 5-minute ka audio podcast bana kar explain kar dega.",
            "Number three: Gamma App, jo sirf ek topic likhte hi 1 minute mein beautiful presentation generate kar deta hai."
        ],
        "cta": "Agar aap bhi smart study karna chahte hain, to Raj Everyway Study ko abhi subscribe karein!",
        "seo": {
            "youtube_title": "Top 3 AI Tools Every Student Must Use 📚🚀 #Shorts",
            "description": "Stop wasting hours taking manual notes! Top 3 game-changing AI tools for smart students.\n\nSubscribe to Raj Everyway Study for student hacks.",
            "hashtags": ["#shorts", "#students", "#studyhacks", "#aitools", "#notebooklm", "#perplexity", "#rajeverywaystudy"],
            "tags": "student ai tools, best ai for study, notebooklm, perplexity ai, study hacks"
        },
        "visual_keywords": ["student studying laptop neon", "ai technology brain hologram", "digital glowing book", "subscribe bell"]
    },
    "ai_winter": {
        "title": "What is AI Winter?",
        "hook": "Kya aap jaante hain ki AI ki history mein ek aisa daur aaya tha jab AI poori tarah band hone ki kagaar par tha?",
        "points": [
            "Ise kaha jata hai AI Winter, jab 1970 aur 1980s mein hype bahut badh gayi par computers utne powerful nahi the.",
            "Governments aur companies ne AI projects ki funding band kar di thi.",
            "Lekin aaj Deep Learning aur GPUs ki wajah se AI apne sabse golden era mein hai."
        ],
        "cta": "Aisi hi tech aur AI history jaan-ne ke liye Raj Everyway Study ko subscribe zaroor karein!",
        "seo": {
            "youtube_title": "The Dark History of AI Winter ❄️🤖 #Shorts",
            "description": "Did you know AI almost died in the 1980s? The fascinating story of AI Winter explained!\n\nSubscribe to Raj Everyway Study.",
            "hashtags": ["#shorts", "#aiwinter", "#historyofai", "#techhistory", "#deeplearning", "#rajeverywaystudy"],
            "tags": "what is ai winter, history of artificial intelligence, machine learning, tech facts"
        },
        "visual_keywords": ["retro computer laboratory vintage", "frozen ice matrix tech", "supercomputer gpu datacenter", "subscribe button"]
    },
    "deepseek_ai": {
        "title": "DeepSeek vs ChatGPT Reality",
        "hook": "Kya DeepSeek AI sach mein ChatGPT ko hamesha ke liye peeche chhod dega?",
        "points": [
            "Pehla reason: DeepSeek ka open-source model ChatGPT se lagbhag 90% kam cost mein train kiya gaya hai.",
            "Doosra reason: Yeh coding aur math reasoning mein world ke sabse expensive models ko takkar de raha hai.",
            "Teesra reason: Ab worldwide developers DeepSeek ko locally apne system par run kar rahe hain."
        ],
        "cta": "AI ki sabse fast updates ke liye Raj Everyway Study ko abhi subscribe karein!",
        "seo": {
            "youtube_title": "DeepSeek vs ChatGPT: Which AI is Better? 🔥🤖 #Shorts",
            "description": "DeepSeek shockwaves in the AI world! Can it beat ChatGPT?\n\nSubscribe to Raj Everyway Study for daily tech breakdown.",
            "hashtags": ["#shorts", "#deepseek", "#chatgpt", "#opensource", "#aiwars", "#rajeverywaystudy"],
            "tags": "deepseek vs chatgpt, deepseek r1, open source ai, artificial intelligence, raj everyway study"
        },
        "visual_keywords": ["cyber warfare ai arena", "neural network glowing connections", "deepseek vs openai logo matrix", "subscribe bell"]
    }
}

def get_script_narration_text(script_data: dict) -> str:
    """Returns the full combined text for TTS."""
    if "narration_text" in script_data and script_data["narration_text"]:
        return normalize_text_to_hinglish(script_data["narration_text"])
    parts = [script_data.get("hook", "")]
    parts.extend(script_data.get("points", []))
    parts.append(script_data.get("cta", ""))
    combined = " ".join(p.strip() for p in parts if p.strip())
    return normalize_text_to_hinglish(combined)

format_script_for_voice = get_script_narration_text

def get_script_by_key(key: str) -> dict:
    """Returns static template or falls back to ai_future."""
    return SAMPLE_TEMPLATES.get(key, SAMPLE_TEMPLATES["ai_future"])

def list_available_topics() -> list:
    """Returns list of curated template keys."""
    return list(SAMPLE_TEMPLATES.keys())

def get_script_for_input(topic_key: str = None, prompt: str = None, custom_text: str = None) -> dict:
    """
    Intelligent master script resolver:
    1. If prompt is given -> calls Gemini (3.5 Flash Lite) to generate dynamic Roman Hinglish script + SEO.
    2. If custom_text is given -> normalizes to Roman Hinglish and creates minimal wrapper.
    3. If topic_key is given -> uses curated Roman Hinglish template or generates on the fly.
    """
    if prompt:
        print(f"[AI Script Engine] Generating dynamic Roman Hinglish script with Gemini for prompt: '{prompt}'...")
        script = generate_ai_script(prompt)
    elif custom_text:
        clean_text = normalize_text_to_hinglish(custom_text.strip())
        script = {
            "title": "Custom Short",
            "hook": clean_text[:60] + "...",
            "points": [],
            "cta": f"Subscribe to Raj Everyway Study!",
            "narration_text": clean_text,
            "seo": {
                "youtube_title": f"Viral Tech Insight 🚀 #Shorts",
                "description": f"{clean_text}\n\nSubscribe to Raj Everyway Study!",
                "hashtags": ["#shorts", "#tech", "#rajeverywaystudy", "#education"],
                "tags": "shorts, tech, education, raj everyway study"
            },
            "visual_keywords": ["technology lab neon", "code terminal 9:16", "cyberpunk visual 9:16", "subscribe button"]
        }
    elif topic_key in SAMPLE_TEMPLATES:
        script = SAMPLE_TEMPLATES[topic_key]
    elif topic_key:
        print(f"[AI Script Engine] Generating dynamic Roman Hinglish script with Gemini for topic: '{topic_key}'...")
        script = generate_ai_script(topic_key)
    else:
        script = SAMPLE_TEMPLATES["india_ai_future"]

    # Guarantee 100% Roman Hinglish on every field
    script["title"] = normalize_text_to_hinglish(script.get("title", ""))
    script["hook"] = normalize_text_to_hinglish(script.get("hook", ""))
    script["cta"] = normalize_text_to_hinglish(script.get("cta", ""))
    script["narration_text"] = normalize_text_to_hinglish(script.get("narration_text", ""))
    if "points" in script and isinstance(script["points"], list):
        script["points"] = [normalize_text_to_hinglish(p) for p in script["points"]]

    return script
