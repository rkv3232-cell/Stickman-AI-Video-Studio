"""
YouTube SEO Toolkit for Raj Everyway Study.
Features:
1. Real YouTube Autocomplete Search Suggestions (keyless)
2. 100-Point SEO Findability Audit Score with Actionable Recommendations
"""

import json
import re
import requests

def get_youtube_suggestions(query: str, lang: str = "hi") -> list[str]:
    """Queries Google/YouTube search autocomplete to see what real viewers type."""
    if not query.strip():
        return []
    url = "https://suggestqueries.google.com/complete/search"
    params = {"client": "firefox", "ds": "yt", "q": query.strip(), "hl": lang}
    try:
        r = requests.get(url, params=params, timeout=6)
        if r.status_code == 200:
            data = json.loads(r.content.decode("utf-8", errors="replace"))
            return [s for s in data[1] if isinstance(s, str)][:15]
    except Exception as e:
        print(f"[SEO Tool] Suggestion error: {e}")
    return []

_CURIOSITY_WORDS = (
    "why", "how", "what", "secret", "never", "truth", "shocking",
    "hidden", "real", "danger", "top", "viral", "?", "!",
    "क्यों", "कैसे", "क्या", "सच", "रहस्य", "चौंकाने", "खतरनाक", "नंबर"
)

def audit_seo_score(
    title: str,
    description: str,
    tags: list[str] | str,
    topic_keyword: str = "",
    is_shorts: bool = True
) -> dict:
    """
    Computes a 100-point YouTube SEO Findability Score based on published best practices.
    Returns:
    {
      "total_score": int (0-100),
      "grade": str ("A+ Excellent", "B Good", etc.),
      "checks": [ {"name": str, "points": int, "passed": bool, "tip": str} ],
      "keyword_suggestions": list[str]
    }
    """
    title = (title or "").strip()
    description = (description or "").strip()
    if isinstance(tags, str):
        tag_list = [t.strip() for t in re.split(r"[,#\n]", tags) if t.strip()]
    else:
        tag_list = [t.strip() for t in tags if t.strip()]

    kw = topic_keyword.lower().strip()
    tl = title.lower()
    dl = description.lower()

    # Rule checks
    checks = []
    score = 0

    # 1. Title Length (Shorts: 30-70 chars) - 15 pts
    c1_passed = 25 <= len(title) <= 75
    checks.append({
        "name": "Title Length (25-75 chars)",
        "points": 15,
        "passed": c1_passed,
        "tip": f"Current: {len(title)} chars. Optimal for YouTube mobile search display."
    })
    if c1_passed: score += 15

    # 2. Curiosity / Question / Number Hook in Title - 15 pts
    c2_passed = any(w in tl for w in _CURIOSITY_WORDS) or any(c.isdigit() for c in title)
    checks.append({
        "name": "Magnetic Hook / Question / Numbers",
        "points": 15,
        "passed": c2_passed,
        "tip": "Contains curiosity trigger words (e.g. Why, How, Secret, 3, 5, ?)."
    })
    if c2_passed: score += 15

    # 3. Keyword in Title - 15 pts
    c3_passed = True if not kw else any(word in tl for word in kw.split() if len(word) > 2)
    checks.append({
        "name": "Target Keyword in Title",
        "points": 15,
        "passed": c3_passed,
        "tip": f"Core topic keyword found in YouTube title."
    })
    if c3_passed: score += 15

    # 4. #Shorts tag in Title or Description - 15 pts
    c4_passed = "#shorts" in tl or "#shorts" in dl or not is_shorts
    checks.append({
        "name": "#Shorts Identifier Tag",
        "points": 15,
        "passed": c4_passed,
        "tip": "Essential for YouTube Shorts algorithm indexing."
    })
    if c4_passed: score += 15

    # 5. Description Depth (>150 chars) - 15 pts
    c5_passed = len(description) >= 120
    checks.append({
        "name": "Rich Video Description (120+ chars)",
        "points": 15,
        "passed": c5_passed,
        "tip": f"Current: {len(description)} chars. Gives YouTube context for recommending video."
    })
    if c5_passed: score += 15

    # 6. Quality Hashtags (3-12 hashtags) - 15 pts
    hashtags = re.findall(r"#\w+", description + " " + title)
    c6_passed = 3 <= len(hashtags) <= 15
    checks.append({
        "name": "Optimal Hashtag Density (3-15 hashtags)",
        "points": 15,
        "passed": c6_passed,
        "tip": f"Found {len(hashtags)} hashtags. Too few reduces reach; over 15 gets ignored by YouTube."
    })
    if c6_passed: score += 15

    # 7. Tags Count (5-25 tags) - 10 pts
    c7_passed = 4 <= len(tag_list) <= 25
    checks.append({
        "name": "Targeted Video Tags (4-25 tags)",
        "points": 10,
        "passed": c7_passed,
        "tip": f"Found {len(tag_list)} tags. Helps match relevant search queries."
    })
    if c7_passed: score += 10

    # Grade calculation
    if score >= 90:
        grade = "A+ (Viral Ready)"
    elif score >= 75:
        grade = "A (Strong SEO)"
    elif score >= 60:
        grade = "B (Good)"
    else:
        grade = "C (Needs Optimization)"

    # Autocomplete Suggestions for the keyword
    suggestions = get_youtube_suggestions(topic_keyword or title[:30])

    return {
        "total_score": score,
        "grade": grade,
        "checks": checks,
        "hashtags": hashtags,
        "suggestions": suggestions
    }

if __name__ == "__main__":
    test_title = "DeepSeek vs ChatGPT: Which AI is Better? 🤖 #Shorts"
    test_desc = "Complete viral breakdown of DeepSeek vs ChatGPT in 2026!\n\nSubscribe to Raj Everyway Study.\n#shorts #ai #tech #deepseek"
    test_tags = ["deepseek", "chatgpt", "openai", "coding", "raj everyway study"]
    res = audit_seo_score(test_title, test_desc, test_tags, "DeepSeek AI")
    print(f"SEO Score: {res['total_score']}/100 ({res['grade']})")
    for chk in res['checks']:
        print(f" - [{ 'PASS' if chk['passed'] else 'FAIL' }] {chk['name']}")
