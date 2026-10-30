"""
Live Trend Radar for Raj Everyway Study.
Fetches real-time trending search spikes and tech news without API keys:
1. Google Trends Daily RSS (India & Global)
2. Hacker News Front Page (Tech & AI)
3. Wikipedia Most Read Articles
"""

import sys
import xml.etree.ElementTree as ET
import requests
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

_HT = {"ht": "https://trends.google.com/trending/rss"}
_WIKI_SKIP = ("Main_Page", "Special:", "Wikipedia:", "Portal:", "File:", "Deaths_in_")

def get_google_trends(geo: str = "IN", limit: int = 10) -> list[dict]:
    """Fetches trending search queries from Google Trends daily RSS feed."""
    url = "https://trends.google.com/trending/rss"
    try:
        res = requests.get(url, params={"geo": geo}, timeout=8)
        if res.status_code != 200:
            return []
        root = ET.fromstring(res.content)
        out = []
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            if not title:
                continue
            news = item.find("ht:news_item", _HT)
            headline = (news.findtext("ht:news_item_title", namespaces=_HT) if news is not None else "")
            traffic = (item.findtext("ht:approx_traffic", namespaces=_HT) or "").strip()
            out.append({
                "title": title,
                "headline": headline or title,
                "traffic": traffic or "10K+",
                "source": f"Google Trends ({geo})",
                "category": "Trending Search"
            })
        return out[:limit]
    except Exception as e:
        print(f"[Trend Radar] Google Trends fetch error: {e}")
        return []

def get_hackernews_trends(limit: int = 8) -> list[dict]:
    """Fetches top tech & AI stories from Hacker News."""
    try:
        url = "https://hn.algolia.com/api/v1/search"
        res = requests.get(url, params={"tags": "front_page", "hitsPerPage": limit}, timeout=8)
        if res.status_code != 200:
            return []
        data = res.json()
        out = []
        for h in data.get("hits", []):
            title = h.get("title", "")
            if title:
                out.append({
                    "title": title,
                    "headline": f"{h.get('points', 0)} points by {h.get('author', 'user')}",
                    "traffic": f"{h.get('points', 0)} pts",
                    "source": "Hacker News",
                    "category": "Tech News"
                })
        return out[:limit]
    except Exception as e:
        print(f"[Trend Radar] Hacker News fetch error: {e}")
        return []

def get_all_trending_topics(geo: str = "IN") -> list[dict]:
    """Combines Google Trends and Hacker News into a single curated list."""
    trends = []
    g_trends = get_google_trends(geo=geo, limit=6)
    hn_trends = get_hackernews_trends(limit=4)
    
    # If India trends empty, fallback to US
    if not g_trends:
        g_trends = get_google_trends(geo="US", limit=6)

    trends.extend(g_trends)
    trends.extend(hn_trends)

    if not trends:
        # Fallback curated evergreen tech topics
        return [
            {"title": "DeepSeek AI vs ChatGPT", "traffic": "500K+", "source": "Curated", "category": "AI War"},
            {"title": "Top 3 AI Tools for Students", "traffic": "250K+", "source": "Curated", "category": "Study Tech"},
            {"title": "Will AI Replace Programmers?", "traffic": "100K+", "source": "Curated", "category": "Future Tech"},
            {"title": "What is Quantum Computing?", "traffic": "80K+", "source": "Curated", "category": "Science"},
        ]
    return trends

if __name__ == "__main__":
    print("Testing Trend Radar...")
    items = get_all_trending_topics()
    for i, it in enumerate(items, 1):
        print(f"{i}. [{it['category']}] {it['title']} ({it['traffic']})")
