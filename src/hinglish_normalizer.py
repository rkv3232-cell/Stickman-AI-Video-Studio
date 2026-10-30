"""
Hinglish Normalization and Enforcement Engine.
Ensures 100% Roman Hinglish compliance across:
- Narration script
- Subtitles & Word-Highlight Captions
- Bold Kinetic Typography
- On-Screen Badges & Category Labels
- YouTube SEO Metadata (Title, Description, Tags)

Rules:
1. Absolutely 0 Devanagari Unicode characters in rendered on-screen text.
2. Language-aware phonetics preserving technical terms (AI, Machine Learning, Technology, Python, Coding, Doctor, Healthcare, Developer, Jobs, Future, Students, Tools, Laptop).
3. Dual-mode translation: Gemini-powered contextual transliteration with a robust offline phonetic & dictionary fallback.
"""

import re
import sys
from typing import Dict, Any, List, Tuple
from google import genai
from config import GEMINI_API_KEY

DEVANAGARI_REGEX = re.compile(r'[\u0900-\u097F]+')

# Common Hindi to Natural Roman Hinglish dictionary mapping
COMMON_HINGLISH_DICT = {
    "भारत": "Bharat",
    "का": "Ka",
    "की": "Ki",
    "के": "Ke",
    "को": "Ko",
    "में": "Mein",
    "से": "Se",
    "पर": "Par",
    "और": "Aur",
    "या": "Ya",
    "है": "Hai",
    "हैं": "Hain",
    "था": "Tha",
    "थी": "Thi",
    "थे": "The",
    "होगा": "Hoga",
    "होगी": "Hogi",
    "होंगे": "Honge",
    "क्या": "Kya",
    "क्यों": "Kyun",
    "कैसे": "Kaise",
    "कहाँ": "Kahan",
    "कब": "Kab",
    "कौन": "Kaun",
    "भविष्य": "Future",
    "बदलने": "Badalne",
    "बदल": "Badal",
    "रहा": "Raha",
    "रही": "Rahi",
    "रहे": "Rahe",
    "सकता": "Sakta",
    "सकती": "Sakti",
    "सकते": "Sakte",
    "वाला": "Wala",
    "वाली": "Wali",
    "वाले": "Wale",
    "जिंदगी": "Life",
    "नौकरियां": "Jobs",
    "नौकरियों": "Jobs",
    "नौकरी": "Job",
    "काम": "Kaam",
    "अवसर": "Opportunity",
    "पैसा": "Paisa",
    "तेजी": "Tezi",
    "आगे": "Aage",
    "बढ़": "Badh",
    "इंसान": "Insaan",
    "इंसानों": "Insano",
    "लोग": "Log",
    "छात्र": "Students",
    "विद्यार्थी": "Students",
    "पढ़ाई": "Padhai",
    "स्मार्ट": "Smart",
    "सीखना": "Seekhna",
    "शुरू": "Shuru",
    "कीजिए": "Kijiye",
    "करें": "Karein",
    "सब्सक्राइब": "Subscribe",
    "लाइक": "Like",
    "शेयर": "Share",
    "घंटी": "Bell",
    "दबाइए": "Dabaiye",
    "आज": "Aaj",
    "कल": "Kal",
    "समय": "Time",
    "सवाल": "Sawaal",
    "जवाब": "Jawaab",
    "सच": "Sach",
    "सच्चाई": "Sacchai",
    "झूठ": "Jhooth",
    "क्रांति": "Kranti",
    "वादा": "Waada",
    "खतरा": "Khatra",
    "फायदा": "Faayda",
    "नुकसान": "Nuksan",
    "स्वास्थ्य": "Health",
    "कृषि": "Agriculture",
    "किसान": "Kisaan",
    "डॉक्टर": "Doctor",
    "अस्पताल": "Hospital",
    "दवा": "Medicine",
    "बीमारी": "Disease",
    "इलाज": "Treatment",
    "सुरक्षा": "Security",
    "देश": "Desh",
    "दुनिया": "Duniya",
    "नया": "Naya",
    "नई": "Nayi",
    "नए": "Naye",
    "पहला": "Pehla",
    "दूसरा": "Doosra",
    "तीसरा": "Teesra",
    "आर्टिफिशियल": "Artificial",
    "इंटेलिजेंस": "Intelligence",
    "तकनीक": "Technology",
    "तकनीकी": "Technical",
    "कौशल": "Skills",
    "लीडर": "Leader",
    "सुपरपावर": "Superpower",
    "तैयार": "Taiyar",
    "रहिए": "Rahiye",
    "जानकर": "Jaankar",
    "होश": "Hosh",
    "उड़": "Udd",
    "जाएंगे": "Jayenge",
    "बड़ा": "Bada",
    "बड़ी": "Badi",
    "बड़े": "Bade",
    "छोटा": "Chhota",
    "ज्यादा": "Zyada",
    "कम": "Kam",
    "बहुत": "Bahut",
    "सिर्फ": "Sirf",
    "केवल": "Keval",
    "जरूरी": "Zaroori",
    "महत्वपूर्ण": "Important",
    "आसान": "Aasan",
    "मुश्किल": "Mushkil",
    "तेज": "Tez",
    "धीमा": "Dheema",
    "पहचान": "Pehchan",
    "सेकंडों": "Seconds",
    "मिनटों": "Minutes",
    "घंटों": "Hours",
    "सालों": "Years"
}

def has_devanagari(text: str) -> bool:
    """Checks if string contains any Devanagari characters."""
    if not text:
        return False
    return bool(DEVANAGARI_REGEX.search(text))

def get_devanagari_chars(text: str) -> List[str]:
    """Returns list of all Devanagari substrings found in text."""
    if not text:
        return []
    return DEVANAGARI_REGEX.findall(text)

def transliterate_word_fallback(word: str) -> str:
    """
    Offline language-aware word transliteration for Devanagari word.
    Checks dictionary first, then applies phonetic mapping.
    """
    clean_w = word.strip("।,?!:;\"'()[]{}")
    if clean_w in COMMON_HINGLISH_DICT:
        return word.replace(clean_w, COMMON_HINGLISH_DICT[clean_w])
    
    # Syllabic / character phonetic table for Devanagari
    matras = {
        'ा': 'a', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo', 'ृ': 'ri',
        'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au', 'ं': 'n', 'ँ': 'n', 'ः': 'h', '्': ''
    }
    vowels = {
        'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
        'ऋ': 'ri', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au'
    }
    consonants = {
        'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
        'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
        'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
        'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
        'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
        'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v',
        'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h',
        'क़': 'q', 'ख़': 'kh', 'ग़': 'gh', 'ज़': 'z', 'ड़': 'd', 'ढ़': 'dh', 'फ़': 'f'
    }
    
    res = []
    i = 0
    w_len = len(clean_w)
    while i < w_len:
        ch = clean_w[i]
        next_ch = clean_w[i+1] if i + 1 < w_len else None
        
        if ch in vowels:
            res.append(vowels[ch])
        elif ch in consonants:
            c_val = consonants[ch]
            if next_ch and next_ch in matras:
                res.append(c_val + matras[next_ch])
                i += 1
            elif next_ch == '्': # Halant
                res.append(c_val)
                i += 1
            else:
                # Inherent 'a' except at end of word
                if i == w_len - 1:
                    res.append(c_val)
                else:
                    res.append(c_val + 'a')
        elif ch in matras:
            res.append(matras[ch])
        else:
            res.append(ch)
        i += 1
        
    translit = "".join(res).capitalize()
    return word.replace(clean_w, translit)

def convert_devanagari_to_hinglish_gemini(text: str, client: Any = None) -> str:
    """
    Uses Gemini (3.5 Flash or 3.5 Flash Lite) to translate/transliterate
    Devanagari text into natural, viral, colloquial Roman Hinglish.
    Preserves English tech terms natively.
    """
    if not text or not has_devanagari(text):
        return text

    if client is None:
        if not GEMINI_API_KEY:
            return convert_devanagari_to_hinglish_offline(text)
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
        except Exception:
            return convert_devanagari_to_hinglish_offline(text)

    prompt = f"""
Translate and transliterate this Hindi/Devanagari text into natural, viral Roman Hinglish (colloquial Indian English/Hindi, written strictly in the English alphabet).

Rules:
1. Output MUST BE 100% Roman characters. NEVER output Devanagari characters.
2. Keep all English/Tech words in standard English (AI, Machine Learning, Technology, Python, Coding, Doctor, Healthcare, Developer, Jobs, Future, Students, Tools, Laptop, Subscribe, Opportunity, Revolution).
3. Sound conversational, magnetic, and modern (e.g. "Kya AI Hamari Life Badal Dega?", "Bharat Ka Future Badalne Wala Hai", "10X Faster Coding & Career Growth").
4. Maintain exact sentence meaning and energy.
5. Return ONLY the converted Roman Hinglish text without any explanation, markdown quotes, or prefix.

Input text:
"{text}"
"""
    # Try gemini-3.5-flash-lite, fallback to gemini-3.5-flash
    for m in ["gemini-3.5-flash-lite", "gemini-3.5-flash"]:
        try:
            resp = client.models.generate_content(
                model=m,
                contents=prompt
            )
            out = resp.text.strip().strip('"').strip("'")
            if out and not has_devanagari(out):
                return out
        except Exception as e:
            continue
            
    return convert_devanagari_to_hinglish_offline(text)

def convert_devanagari_to_hinglish_offline(text: str) -> str:
    """
    Robust fallback to convert any Devanagari text to Roman Hinglish offline
    without requiring external API calls.
    """
    if not text or not has_devanagari(text):
        return text

    tokens = text.split(" ")
    out_tokens = []
    for token in tokens:
        if has_devanagari(token):
            out_tokens.append(transliterate_word_fallback(token))
        else:
            out_tokens.append(token)
            
    res = " ".join(out_tokens)
    # Final pass: remove any lingering Devanagari marks
    res = DEVANAGARI_REGEX.sub("", res).strip()
    return re.sub(r'\s+', ' ', res)

def normalize_text_to_hinglish(text: str, client: Any = None) -> str:
    """
    Master function: checks text and normalizes to Roman Hinglish.
    Guarantees that the returned text contains 0 Devanagari characters.
    """
    if not text:
        return ""
    if not has_devanagari(text):
        return text.strip()
    
    # Try Gemini first for context-aware natural translation
    converted = convert_devanagari_to_hinglish_gemini(text, client=client)
    
    # Final verification
    if has_devanagari(converted):
        converted = convert_devanagari_to_hinglish_offline(converted)
        
    return converted.strip()

def enforce_storyboard_hinglish(storyboard: Dict[str, Any], client: Any = None) -> Dict[str, Any]:
    """
    Inspects and normalizes an entire storyboard structure to ensure 100%
    Roman Hinglish compliance across all scenes, typography, captions, and speech texts.
    """
    if not storyboard:
        return storyboard

    # Normalize title and hook
    if "title" in storyboard:
        storyboard["title"] = normalize_text_to_hinglish(storyboard["title"], client)
    if "hook" in storyboard:
        storyboard["hook"] = normalize_text_to_hinglish(storyboard["hook"], client)
    if "cta" in storyboard:
        storyboard["cta"] = normalize_text_to_hinglish(storyboard["cta"], client)
    if "narration_text" in storyboard:
        storyboard["narration_text"] = normalize_text_to_hinglish(storyboard["narration_text"], client)

    # Normalize SEO
    if "seo" in storyboard and isinstance(storyboard["seo"], dict):
        for k in ["youtube_title", "description", "tags"]:
            if k in storyboard["seo"] and isinstance(storyboard["seo"][k], str):
                storyboard["seo"][k] = normalize_text_to_hinglish(storyboard["seo"][k], client)

    # Normalize scenes
    scenes = storyboard.get("scenes", [])
    for sc in scenes:
        for text_key in ["narration", "script_point", "speech_text"]:
            if text_key in sc and isinstance(sc[text_key], str):
                sc[text_key] = normalize_text_to_hinglish(sc[text_key], client)

        # Normalize typography block
        typo = sc.get("typography", {})
        if typo and isinstance(typo, dict):
            for typo_key in ["primary", "secondary", "category"]:
                if typo_key in typo and isinstance(typo[typo_key], str):
                    typo[typo_key] = normalize_text_to_hinglish(typo[typo_key], client)

    return storyboard

def validate_final_text_is_hinglish(storyboard: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Pre-render Quality Check:
    Returns (True, []) if 100% of on-screen and spoken text is Roman Hinglish.
    Returns (False, [violations]) if any Devanagari characters are detected.
    """
    violations = []
    
    # Check top-level
    for k in ["title", "hook", "cta", "narration_text"]:
        v = storyboard.get(k, "")
        if isinstance(v, str) and has_devanagari(v):
            violations.append(f"Field '{k}' contains Devanagari: '{v[:40]}...'")

    # Check scenes
    for i, sc in enumerate(storyboard.get("scenes", [])):
        sc_num = sc.get("scene_number", i + 1)
        for tk in ["narration", "script_point", "speech_text"]:
            v = sc.get(tk, "")
            if isinstance(v, str) and has_devanagari(v):
                violations.append(f"Scene {sc_num} field '{tk}' contains Devanagari: '{v[:40]}...'")

        typo = sc.get("typography", {})
        if typo and isinstance(typo, dict):
            for yk in ["primary", "secondary", "category"]:
                v = typo.get(yk, "")
                if isinstance(v, str) and has_devanagari(v):
                    violations.append(f"Scene {sc_num} typography '{yk}' contains Devanagari: '{v}'")

    return (len(violations) == 0, violations)

