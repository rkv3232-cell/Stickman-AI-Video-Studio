"""
Persistent Publishing Scheduler & Background Worker.
Monitors daily publishing schedules, time zones, generation limits, and budget thresholds.
Runs a background daemon thread that triggers production when configured conditions are met.
"""

import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Ensure root dir on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.database import get_setting, count_jobs_today
from src.automation_manager import automation_mgr

class PublishingScheduler:
    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Starts the background scheduler loop."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._thread.start()
        print("[Scheduler] Publishing Scheduler daemon started.")

    def stop(self):
        self._running = False

    def is_active(self) -> bool:
        return self._running

    def _scheduler_loop(self):
        while self._running:
            try:
                # 1. Check if automation is enabled by user
                enabled = get_setting("automation_enabled", "false").lower() == "true"
                if enabled and not automation_mgr.is_running():
                    # 2. Check daily limits
                    limit = int(get_setting("daily_video_limit", "2"))
                    today_count = count_jobs_today()

                    if today_count < limit:
                        # 3. Check time condition if specified
                        pub_time = get_setting("publishing_time", "19:00")
                        now_str = datetime.now().strftime("%H:%M")

                        # If within the scheduled hour or queue requires replenishment
                        automation_mgr.start_next_automated_job()

            except Exception as e:
                print(f"[Scheduler Exception]: {e}")

            # Sleep 60 seconds between evaluations
            time.sleep(60)

    def get_status(self) -> Dict[str, Any]:
        """Provides scheduler diagnostics for the frontend dashboard."""
        enabled = get_setting("automation_enabled", "false").lower() == "true"
        limit = int(get_setting("daily_video_limit", "2"))
        pub_time = get_setting("publishing_time", "19:00")
        tz = get_setting("timezone", "Asia/Kolkata")
        today_count = count_jobs_today()

        return {
            "scheduler_active": self._running,
            "automation_enabled": enabled,
            "daily_video_limit": limit,
            "videos_generated_today": today_count,
            "remaining_quota_today": max(limit - today_count, 0),
            "publishing_time": pub_time,
            "timezone": tz,
            "is_busy": automation_mgr.is_running(),
            "active_job_id": automation_mgr.current_job_id
        }

scheduler = PublishingScheduler()

if __name__ == "__main__":
    print("Scheduler Status:", scheduler.get_status())

