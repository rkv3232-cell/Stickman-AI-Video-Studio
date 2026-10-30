"""
YouTube Performance Analytics Engine.
Fetches performance metrics (views, likes, comments, duration) for published videos
using the official YouTube Data API and caches metrics into SQLite history.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

# Ensure root dir on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.youtube_uploader import youtube_uploader
from src.database import get_db_connection

def fetch_video_analytics(video_ids: List[str]) -> List[Dict[str, Any]]:
    """Fetches real-time statistics for a list of YouTube video IDs."""
    if not video_ids:
        return []

    service = youtube_uploader.get_service()
    if not service:
        return []

    try:
        request = service.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids[:50])
        )
        response = request.execute()
        items = response.get("items", [])
        results = []

        conn = get_db_connection()
        cursor = conn.cursor()

        for item in items:
            vid = item.get("id")
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})
            title = snippet.get("title", "")
            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            comments = int(stats.get("commentCount", 0))

            results.append({
                "video_id": vid,
                "title": title,
                "views": views,
                "likes": likes,
                "comments": comments,
                "url": f"https://youtu.be/{vid}"
            })

            # Save in analytics_history table
            cursor.execute("""
            INSERT INTO analytics_history (youtube_video_id, title, views, likes, comments, recorded_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, (vid, title, views, likes, comments))

        conn.commit()
        return results
    except Exception as e:
        print(f"[YouTube Analytics] Fetch error: {e}")
        return []

def get_channel_analytics_summary() -> Dict[str, Any]:
    """Returns overview statistics of published videos."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get total uploads tracked
    cursor.execute("SELECT COUNT(DISTINCT youtube_video_id) FROM publishing_queue WHERE status = 'uploaded'")
    total_uploaded = cursor.fetchone()[0]

    # Get latest metrics
    cursor.execute("""
    SELECT COALESCE(SUM(views), 0), COALESCE(SUM(likes), 0), COALESCE(SUM(comments), 0)
    FROM (
        SELECT views, likes, comments
        FROM analytics_history
        GROUP BY youtube_video_id
        HAVING id = MAX(id)
    )
    """)
    row = cursor.fetchone()
    total_views = row[0] if row else 0
    total_likes = row[1] if row else 0
    total_comments = row[2] if row else 0

    return {
        "total_uploaded_videos": total_uploaded,
        "total_views": total_views,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "average_engagement_rate": f"{(total_likes / max(total_views, 1) * 100):.2f}%"
    }

if __name__ == "__main__":
    print("Analytics Summary:", get_channel_analytics_summary())

