"""
Automatic Topic Discovery & Relevance Scoring Engine.
Discovers high-potential YouTube Shorts topics across the 6 Channel Categories:
1. AI Technology
2. Interesting Facts
3. Education
4. Science
5. Future Technology
6. Technology Explainers

Scores topics based on audience demand, educational value, production feasibility,
and ensures strict deduplication via SQLite persistence.
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Ensure root dir on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.trends import get_google_trends, get_hackernews_trends
from src.database import add_topic_to_queue, list_topic_queue, get_db_connection

# Category keyword dictionaries for relevance scoring
CATEGORY_KEYWORDS = {
    "AI Technology": [
        "ai", "artificial intelligence", "chatgpt", "gemini", "deepseek", "robot",
        "neural network", "machine learning", "agent", "llm", "automation", "algorithm"
    ],
    "Interesting Facts": [
        "fact", "mystery", "shocking", "hidden", "secret", "brain", "human body",
        "earth", "ocean", "animal", "history", "unbelievable", "record", "psychology"
    ],
    "Education": [
        "how to", "study", "learn", "student", "guide", "memory", "exam", "college",
        "focus", "trick", "productivity", "concept", "explained", "formula"
    ],
    "Science": [
        "space", "quantum", "gravity", "black hole", "nasa", "isro", "physics",
        "biology", "chemistry", "dna", "telescope", "mars", "moon", "energy", "sun"
    ],
    "Future Technology": [
        "future", "2030", "2050", "flying car", "nanotech", "cyborg", "metaverse",
        "neuralink", "spacex", "fusion", "supercomputer", "teleportation"
    ],
    "Technology Explainers": [
        "how it works", "processor", "internet", "gpu", "smartphone", "battery",
        "wifi", "5g", "6g", "cloud", "semiconductor", "chip", "coding", "software"
    ]
}

# Curated high-relevance seed topics for robust fallback and rotation
CURATED_CATEGORY_SEEDS = [
    # AI Technology
    {"topic": "Bharat Mein AI Ka Future: 2026 Ka Sabse Bada Revolution", "category": "AI Technology", "relevance": 95},
    {"topic": "Kya AI Hamari Daily Jobs Ko Replace Kar Dega?", "category": "AI Technology", "relevance": 92},
    {"topic": "Agentic AI Kya Hai Aur Ye ChatGPT Se Alag Kaise Hai?", "category": "AI Technology", "relevance": 90},
    {"topic": "Top 3 Free AI Tools Jo Har Student Ke Paas Hone Chahiye", "category": "AI Technology", "relevance": 94},
    # Interesting Facts
    {"topic": "Human Brain Ke 5 Shocking Facts Jo Aapko Hairan Kar Denge", "category": "Interesting Facts", "relevance": 88},
    {"topic": "Space Mein Sound Travel Kyun Nahi Karta?", "category": "Interesting Facts", "relevance": 89},
    {"topic": "Duniya Ki Sabse Quiet Jagah Jahan Aap Apna Dil Sun Sakte Hain", "category": "Interesting Facts", "relevance": 87},
    # Science
    {"topic": "Quantum Computing Kaise Traditional Supercomputers Ko Peeche Chhod Dega", "category": "Science", "relevance": 91},
    {"topic": "Black Hole Ke Event Horizon Ke Andar Kya Hota Hai?", "category": "Science", "relevance": 93},
    {"topic": "James Webb Telescope Ne Universe Ki Shuruat Ke Raaz Kaise Khole", "category": "Science", "relevance": 90},
    # Future Technology
    {"topic": "Neuralink Brain Chip: Kya Insan Aur AI Ek Ho Jayenge?", "category": "Future Technology", "relevance": 92},
    {"topic": "Nuclear Fusion: Unlimited Clean Energy Ka Sapna Sach Hone Wala Hai", "category": "Future Technology", "relevance": 91},
    {"topic": "Flying Cars Aur Drone Taxis: Hamara Future Transportation", "category": "Future Technology", "relevance": 86},
    # Technology Explainers
    {"topic": "Smartphone Processors Kaise Kaam Karte Hain: 3nm Chip Ka Jadu", "category": "Technology Explainers", "relevance": 88},
    {"topic": "Internet Cables Samundar Ke Andar Kaise Bichhai Jati Hain?", "category": "Technology Explainers", "relevance": 93},
    {"topic": "5G vs 6G: Agle 5 Salon Mein Speed Kitni Badh Jayegi?", "category": "Technology Explainers", "relevance": 87}
]

def calculate_relevance_score(topic: str) -> tuple[str, int]:
    """
    Calculates category and relevance score (0-100) based on category keyword matching,
    length, clarity, and Shorts virality indicators.
    """
    text_lower = topic.lower()
    best_category = "AI Technology"
    max_matches = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        matches = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', text_lower))
        if matches > max_matches:
            max_matches = matches
            best_category = category

    base_score = 70
    base_score += min(max_matches * 8, 24)

    # Word count penalty/bonus for Shorts suitability (ideal 5 to 14 words)
    words = len(topic.split())
    if 5 <= words <= 14:
        base_score += 6
    elif words > 20:
        base_score -= 10

    # Viral query signals
    if any(q in text_lower for q in ["how", "why", "kya", "kaise", "future", "secret", "fact", "top"]):
        base_score += 5

    return best_category, min(max(base_score, 50), 99)

def discover_and_populate_topics(limit_per_run: int = 10) -> List[Dict[str, Any]]:
    """
    Fetches real-time trends from Google Trends & Hacker News, scores them,
    and populates the SQLite `topic_queue` table with deduplication.
    """
    newly_added = []

    # 1. Google Trends (India & Global)
    g_trends = get_google_trends(geo="IN", limit=8)
    if not g_trends:
        g_trends = get_google_trends(geo="US", limit=8)

    for item in g_trends:
        title = item.get("title", "")
        if not title:
            continue
        # Filter out non-ASCII/non-Latin titles to enforce Roman readability
        if not re.match(r'^[\x00-\x7F\s\w\d\.\,\-\:\?\!]+$', title):
            continue
        category, score = calculate_relevance_score(title)
        added = add_topic_to_queue(
            topic=title,
            category=category,
            source=item.get("source", "Google Trends"),
            relevance=score,
            reason=f"Trending spike ({item.get('traffic', '10K+')})"
        )
        if added:
            newly_added.append({"topic": title, "category": category, "score": score, "source": "Google Trends"})

    # 2. Hacker News
    hn_trends = get_hackernews_trends(limit=6)
    for item in hn_trends:
        title = item.get("title", "")
        if not title:
            continue
        category, score = calculate_relevance_score(title)
        added = add_topic_to_queue(
            topic=title,
            category=category,
            source="Hacker News",
            relevance=score,
            reason=f"Hacker News front page ({item.get('traffic', '')})"
        )
        if added:
            newly_added.append({"topic": title, "category": category, "score": score, "source": "Hacker News"})

    # 3. If new topics were fewer than limit, seed with curated evergreen topics
    if len(newly_added) < limit_per_run:
        for seed in CURATED_CATEGORY_SEEDS:
            added = add_topic_to_queue(
                topic=seed["topic"],
                category=seed["category"],
                source="Curated Evergreen Radar",
                relevance=seed["relevance"],
                reason="High-CTR educational Shorts blueprint"
            )
            if added:
                newly_added.append({
                    "topic": seed["topic"],
                    "category": seed["category"],
                    "score": seed["relevance"],
                    "source": "Curated Evergreen"
                })
            if len(newly_added) >= limit_per_run:
                break

    return newly_added

if __name__ == "__main__":
    print("Testing Topic Discovery...")
    discovered = discover_and_populate_topics()
    print(f"Discovered and queued {len(discovered)} new topics!")
    for t in discovered[:5]:
        print(f" - [{t['category']}] {t['topic']} (Score: {t['score']})")
