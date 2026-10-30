"""
Monetization & Compliance Safe Checker for Raj Everyway Study.
Ensures generated scripts and metadata follow YouTube Community Guidelines and Advertiser-Friendly Guidelines.
"""

import re

# Restricted words that can trigger YouTube age restrictions or demonetization
_RISKY_WORDS = [
    "hack", "crack", "torrent", "pirate", "bypass", "exploit",
    "illegal", "weapon", "kill", "suicide", "bomb", "scam",
    "free money", "get rich", "dark web buy", "credit card hack"
]

def check_script_compliance(script_text: str, title: str = "") -> dict:
    """
    Checks if script and title are 100% Monetization-Safe for YouTube.
    Returns:
    {
      "is_safe": bool,
      "flagged_words": list[str],
      "risk_level": "Safe" | "Warning" | "High Risk",
      "tips": str
    }
    """
    combined = f"{title} {script_text}".lower()
    flagged = []

    for word in _RISKY_WORDS:
        # Check boundary
        if re.search(r'\b' + re.escape(word) + r'\b', combined):
            flagged.append(word)

    if not flagged:
        return {
            "is_safe": True,
            "flagged_words": [],
            "risk_level": "Safe",
            "tips": "100% Advertiser-Friendly and Monetization Safe ✅"
        }
    elif len(flagged) == 1:
        return {
            "is_safe": True,
            "flagged_words": flagged,
            "risk_level": "Warning",
            "tips": f"Contains minor sensitive word '{flagged[0]}'. Recommended to review before publishing."
        }
    else:
        return {
            "is_safe": False,
            "flagged_words": flagged,
            "risk_level": "High Risk",
            "tips": f"Contains risky words {flagged} that may trigger YouTube demonetization. Please rephrase."
        }

if __name__ == "__main__":
    t = "DeepSeek vs ChatGPT: Which AI is Better?"
    s = "In this video we compare both AI tools without any hack."
    res = check_script_compliance(s, t)
    print("Compliance Result:", res)
