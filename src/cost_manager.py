"""
Provider & Cost Management Engine.
Tracks API usage across text, image, video, and voice providers.
Enforces daily and monthly budget caps to protect against runaway costs.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Ensure root dir on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.database import get_db_connection, get_setting

# Estimated pricing per operation (USD)
PRICING_TABLE = {
    "gemini_text_1k_tokens": 0.00015,
    "gemini_image_gen": 0.03,
    "runway_video_clip": 0.25,
    "kling_video_clip": 0.20,
    "minimax_video_clip": 0.20,
    "sarvam_tts_1k_chars": 0.002,
    "edge_tts": 0.000  # 100% Free
}

class CostManager:
    def record_usage(self, provider: str, operation: str, units: float, cost_usd: float, job_id: str = "", details: str = ""):
        """Records an API cost entry in SQLite."""
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
        INSERT INTO provider_usage (provider, operation, units_used, cost_usd, job_id, details, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (provider, operation, units, cost_usd, job_id, details, now))
        conn.commit()

    def get_today_spent(self) -> float:
        """Calculates total USD spent today."""
        conn = get_db_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COALESCE(SUM(cost_usd), 0.0) FROM provider_usage WHERE created_at LIKE ?", (f"{today}%",))
        return float(cursor.fetchone()[0])

    def get_monthly_spent(self) -> float:
        """Calculates total USD spent this month."""
        conn = get_db_connection()
        cursor = conn.cursor()
        month = datetime.now().strftime("%Y-%m")
        cursor.execute("SELECT COALESCE(SUM(cost_usd), 0.0) FROM provider_usage WHERE created_at LIKE ?", (f"{month}%",))
        return float(cursor.fetchone()[0])

    def check_budget_allowance(self, anticipated_cost: float = 0.10) -> tuple[bool, str]:
        """Verifies if today's spending limit has been reached."""
        daily_limit_str = get_setting("daily_budget_usd", "5.00")
        try:
            daily_limit = float(daily_limit_str)
        except ValueError:
            daily_limit = 5.00

        spent_today = self.get_today_spent()
        if spent_today + anticipated_cost > daily_limit:
            return False, f"Daily budget reached (${spent_today:.2f} / ${daily_limit:.2f}). Pausing automated production."
        return True, "Within budget"

    def get_cost_report(self) -> Dict[str, Any]:
        """Provides itemized cost summary for the dashboard."""
        conn = get_db_connection()
        cursor = conn.cursor()

        spent_today = self.get_today_spent()
        spent_month = self.get_monthly_spent()
        daily_limit = float(get_setting("daily_budget_usd", "5.00"))

        cursor.execute("""
        SELECT provider, operation, COUNT(*), SUM(cost_usd)
        FROM provider_usage
        GROUP BY provider, operation
        ORDER BY SUM(cost_usd) DESC
        """)
        breakdown = [
            {"provider": r[0], "operation": r[1], "count": r[2], "total_cost": round(r[3], 4)}
            for r in cursor.fetchall()
        ]

        return {
            "spent_today_usd": round(spent_today, 4),
            "spent_month_usd": round(spent_month, 4),
            "daily_budget_limit_usd": daily_limit,
            "remaining_budget_today": max(round(daily_limit - spent_today, 4), 0.0),
            "breakdown": breakdown
        }

cost_mgr = CostManager()

if __name__ == "__main__":
    print("Cost Report:", cost_mgr.get_cost_report())

