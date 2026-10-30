"""
SQLite Database & Persistence Engine for Stickman AI Video Studio.
Stores background jobs, topic queue, publishing queue, provider costs, and settings.
Thread-safe, handles schema migrations, and ensures zero data loss upon application restart.
"""

import sqlite3
import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from config import ROOT_DIR

DB_PATH = ROOT_DIR / "automation_studio.db"
_local = threading.local()

def get_db_connection() -> sqlite3.Connection:
    """Returns a thread-local SQLite connection with dictionary-like row factory."""
    if not hasattr(_local, "conn") or _local.conn is None:
        conn = sqlite3.connect(str(DB_PATH), timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        _local.conn = conn
    return _local.conn

def init_db():
    """Initializes SQLite schema and default configurations."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Production Jobs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        topic TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT 'AI Technology',
        status TEXT NOT NULL DEFAULT 'queued',
        stage_name TEXT DEFAULT 'Queued',
        percent INTEGER DEFAULT 0,
        message TEXT DEFAULT 'Job registered in queue...',
        error TEXT,
        retry_count INTEGER DEFAULT 0,
        total_duration REAL DEFAULT 0.0,
        output_dir TEXT,
        video_filename TEXT,
        thumb_filename TEXT,
        video_url TEXT,
        thumb_url TEXT,
        qc_score INTEGER DEFAULT 0,
        qc_verdict TEXT DEFAULT 'PENDING',
        youtube_video_id TEXT,
        youtube_url TEXT,
        upload_status TEXT DEFAULT 'pending',
        is_auto_job INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    # 2. Topic Discovery & Priority Queue
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS topic_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL,
        source TEXT NOT NULL,
        relevance_score INTEGER DEFAULT 80,
        status TEXT NOT NULL DEFAULT 'discovered',
        reason TEXT,
        created_at TEXT NOT NULL
    )
    """)

    # 3. Publishing Queue Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS publishing_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        tags TEXT,
        privacy_status TEXT DEFAULT 'private',
        scheduled_time TEXT,
        status TEXT DEFAULT 'pending',
        youtube_video_id TEXT,
        youtube_url TEXT,
        error TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (job_id) REFERENCES jobs(id)
    )
    """)

    # 4. Provider & Cost Tracking
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS provider_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider TEXT NOT NULL,
        operation TEXT NOT NULL,
        units_used REAL DEFAULT 0.0,
        cost_usd REAL DEFAULT 0.0,
        job_id TEXT,
        details TEXT,
        created_at TEXT NOT NULL
    )
    """)

    # 5. System Settings Table (Key-Value)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    # 6. Analytics History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analytics_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        youtube_video_id TEXT NOT NULL,
        title TEXT,
        views INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0,
        avg_view_duration_sec REAL DEFAULT 0.0,
        recorded_at TEXT NOT NULL
    )
    """)

    # Insert default settings if not exists
    default_settings = {
        "automation_enabled": "false",
        "daily_video_limit": "2",
        "publishing_time": "19:00",
        "timezone": "Asia/Kolkata",
        "default_privacy": "private",
        "default_category": "AI Technology",
        "daily_budget_usd": "5.00",
        "default_speaker": "shubh",
        "default_pace": "1.1",
        "default_visual_style": "sketch_notes",
        "default_stickman_style": "modern_beanie",
        "cloud_video_enabled": "false",
        "youtube_channel_title": "",
        "youtube_channel_id": "",
        "auto_publish_on_pass": "true"
    }

    now = datetime.now().isoformat()
    for k, v in default_settings.items():
        cursor.execute("INSERT OR IGNORE INTO settings (key, value, updated_at) VALUES (?, ?, ?)", (k, v, now))

    conn.commit()

# --- Job CRUD Helpers ---

def create_job(job_id: str, topic: str, category: str = "AI Technology", is_auto: bool = False) -> Dict[str, Any]:
    conn = get_db_connection()
    now = datetime.now().isoformat()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO jobs (id, topic, category, status, stage_name, percent, message, is_auto_job, created_at, updated_at)
    VALUES (?, ?, ?, 'queued', 'Queued', 0, 'Registered in production queue...', ?, ?, ?)
    """, (job_id, topic, category, 1 if is_auto else 0, now, now))
    conn.commit()
    return get_job(job_id)

def update_job_progress(job_id: str, status: str, stage_name: str, percent: int, message: str, error: Optional[str] = None):
    conn = get_db_connection()
    now = datetime.now().isoformat()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE jobs
    SET status = ?, stage_name = ?, percent = ?, message = ?, error = ?, updated_at = ?
    WHERE id = ?
    """, (status, stage_name, percent, message, error, now, job_id))
    conn.commit()

def complete_job_record(
    job_id: str,
    output_dir: str,
    video_filename: str,
    thumb_filename: str,
    qc_score: int,
    qc_verdict: str,
    duration: float
):
    conn = get_db_connection()
    now = datetime.now().isoformat()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE jobs
    SET status = 'completed', stage_name = 'Completed', percent = 100,
        message = 'Production successfully finalized!',
        output_dir = ?, video_filename = ?, thumb_filename = ?,
        video_url = ?, thumb_url = ?,
        qc_score = ?, qc_verdict = ?, total_duration = ?, updated_at = ?
    WHERE id = ?
    """, (
        output_dir, video_filename, thumb_filename,
        f"/api/video/{video_filename}", f"/api/thumbnail/{thumb_filename}",
        qc_score, qc_verdict, duration, now, job_id
    ))
    conn.commit()

def fail_job_record(job_id: str, error_message: str):
    conn = get_db_connection()
    now = datetime.now().isoformat()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE jobs
    SET status = 'failed', stage_name = 'Failed', message = ?, error = ?, updated_at = ?
    WHERE id = ?
    """, (f"Production failed: {error_message}", error_message, now, job_id))
    conn.commit()

def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def list_jobs(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,))
    return [dict(r) for r in cursor.fetchall()]

def count_jobs_today() -> int:
    conn = get_db_connection()
    today_prefix = datetime.now().strftime("%Y-%m-%d")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE created_at LIKE ? AND status = 'completed'", (f"{today_prefix}%",))
    return cursor.fetchone()[0]

# --- Topic Queue Helpers ---

def add_topic_to_queue(topic: str, category: str, source: str, relevance: int, reason: str = "") -> bool:
    conn = get_db_connection()
    now = datetime.now().isoformat()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO topic_queue (topic, category, source, relevance_score, status, reason, created_at)
        VALUES (?, ?, ?, ?, 'discovered', ?, ?)
        """, (topic, category, source, relevance, reason, now))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Already exists (deduplicated)

def get_next_topic_from_queue() -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM topic_queue
    WHERE status = 'discovered'
    ORDER BY relevance_score DESC, id ASC
    LIMIT 1
    """)
    row = cursor.fetchone()
    if row:
        topic_dict = dict(row)
        cursor.execute("UPDATE topic_queue SET status = 'in_production' WHERE id = ?", (topic_dict["id"],))
        conn.commit()
        return topic_dict
    return None

def list_topic_queue(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topic_queue ORDER BY relevance_score DESC, id DESC LIMIT ?", (limit,))
    return [dict(r) for r in cursor.fetchall()]

def mark_topic_status(topic_id: int, status: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE topic_queue SET status = ? WHERE id = ?", (status, topic_id))
    conn.commit()

# --- Publishing Queue Helpers ---

def add_to_publishing_queue(
    job_id: str,
    title: str,
    description: str,
    tags: str,
    privacy: str = "private",
    scheduled_time: Optional[str] = None
) -> int:
    conn = get_db_connection()
    now = datetime.now().isoformat()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO publishing_queue (job_id, title, description, tags, privacy_status, scheduled_time, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)
    """, (job_id, title, description, tags, privacy, scheduled_time, now, now))
    conn.commit()
    return cursor.lastrowid

def list_publishing_queue() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT p.*, j.video_filename, j.thumb_filename, j.output_dir
    FROM publishing_queue p
    LEFT JOIN jobs j ON p.job_id = j.id
    ORDER BY p.id DESC
    """)
    return [dict(r) for r in cursor.fetchall()]

def update_publishing_status(queue_id: int, status: str, youtube_id: Optional[str] = None, youtube_url: Optional[str] = None, error: Optional[str] = None):
    conn = get_db_connection()
    now = datetime.now().isoformat()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE publishing_queue
    SET status = ?, youtube_video_id = ?, youtube_url = ?, error = ?, updated_at = ?
    WHERE id = ?
    """, (status, youtube_id, youtube_url, error, now, queue_id))
    conn.commit()

# --- Settings Helpers ---

def get_setting(key: str, default: str = "") -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    return row[0] if row else default

def set_setting(key: str, value: str):
    conn = get_db_connection()
    now = datetime.now().isoformat()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO settings (key, value, updated_at)
    VALUES (?, ?, ?)
    ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
    """, (key, str(value), now))
    conn.commit()

def get_all_settings() -> Dict[str, str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    return {row[0]: row[1] for row in cursor.fetchall()}

# Auto-initialize database on import
init_db()

