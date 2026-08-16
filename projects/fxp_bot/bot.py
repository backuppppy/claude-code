"""
FXP Telegram Bot — monitors all FXP forums and sends new threads to Telegram.

Usage:
  TELEGRAM_TOKEN=xxx TELEGRAM_CHAT_ID=yyy python3 bot.py
  Or set in .env file and run: python3 bot.py
"""

import json
import os
import sys
import time
import logging
from datetime import datetime, timedelta, timezone

import requests
from requests.adapters import HTTPAdapter

from fxp_monitor import get_new_posts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
# Suppress connection pool warnings
logging.getLogger("urllib3").setLevel(logging.ERROR)

log = logging.getLogger(__name__)

STATE_FILE = os.path.join(os.path.dirname(__file__), "seen_posts.json")
REGISTRY_FILE = os.path.join(os.path.dirname(__file__), "thread_registry.json")

# Max new posts to send per cycle — if more, record silently (config change)
FLOOD_THRESHOLD = 50


def load_env():
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()


def load_seen() -> set:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen(seen: set):
    ids = list(seen)[-10000:]
    with open(STATE_FILE, "w") as f:
        json.dump(ids, f)


def load_registry() -> dict:
    """Load thread registry with timestamps."""
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE) as f:
                return json.load(f)
        except Exception as e:
            log.error(f"Error loading registry: {e}")
    return {}


def save_registry(registry: dict):
    """Save thread registry (keep last 5000 entries)."""
    # Trim to avoid unbounded growth
    if len(registry) > 5000:
        # Keep the 5000 most recent (by timestamp)
        sorted_entries = sorted(
            registry.items(),
            key=lambda x: x[1].get("discovered_at", ""),
            reverse=True
        )
        registry = dict(sorted_entries[:5000])

    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f)


def get_daily_report(registry: dict, target_date: str) -> str:
    """
    Generate a report for threads discovered ON target_date (YYYY-MM-DD).
    Only shows threads from that specific day, groups by forum.
    Used for: Daily reports (after midnight, until next midnight)
    """
    # Parse target date
    try:
        target = datetime.strptime(target_date, "%Y-%m-%d").date()
    except ValueError:
        return ""

    # Count threads by forum for the target date only
    forum_counts: dict[str, int] = {}
    for thread_id, data in registry.items():
        discovered_at = data.get("discovered_at", "")
        if not discovered_at:
            continue
        try:
            # Parse ISO format: "2026-08-16T14:30:45Z"
            discovery_date = datetime.fromisoformat(discovered_at.replace("Z", "+00:00")).date()
            if discovery_date == target:
                forum = data.get("forum", "Unknown")
                forum_counts[forum] = forum_counts.get(forum, 0) + 1
        except Exception:
            continue

    if not forum_counts:
        return ""

    # Build report
    date_str = target_date
    lines = [f"📊 דוח אשכולות — {date_str}\n"]

    total = sum(forum_counts.values())
    sorted_forums = sorted(forum_counts.items(), key=lambda x: x[1], reverse=True)

    # Show forums sorted by thread count (most active first)
    for i, (forum, count) in enumerate(sorted_forums, 1):
        lines.append(f"{i:2d}. {forum}: {count}")

    lines.append("")
    lines.append(f"סה״כ: {total} אשכולות ב-{len(forum_counts)} פורומים")

    return "\n".join(lines)


def get_cumulative_report(registry: dict, up_to_date: str) -> str:
    """
    Generate cumulative report for threads discovered UP TO AND INCLUDING up_to_date.
    Shows all threads from beginning through that date.
    Used for: Midnight reports (at 00:00)
    """
    # Parse target date
    try:
        target = datetime.strptime(up_to_date, "%Y-%m-%d").date()
    except ValueError:
        return ""

    # Count threads by forum UP TO AND INCLUDING target date
    forum_counts: dict[str, int] = {}
    for thread_id, data in registry.items():
        discovered_at = data.get("discovered_at", "")
        if not discovered_at:
            continue
        try:
            # Parse ISO format: "2026-08-16T14:30:45Z"
            discovery_date = datetime.fromisoformat(discovered_at.replace("Z", "+00:00")).date()
            if discovery_date <= target:  # Include all dates up to target
                forum = data.get("forum", "Unknown")
                forum_counts[forum] = forum_counts.get(forum, 0) + 1
        except Exception:
            continue

    if not forum_counts:
        return ""

    # Build report with forum links
    date_str = up_to_date
    lines = [f"📊 דוח קומולטיבי עד — {date_str}\n"]

    total = sum(forum_counts.values())
    sorted_forums = sorted(forum_counts.items(), key=lambda x: x[1], reverse=True)

    # Show forums sorted by thread count (most active first)
    for i, (forum, count) in enumerate(sorted_forums, 1):
        lines.append(f"{i:2d}. {forum}: {count}")

    lines.append("")
    lines.append(f"סה״כ: {total} אשכולות ב-{len(forum_counts)} פורומים (עד {date_str})")

    return "\n".join(lines)


def format_startup_summary(registry: dict) -> str:
    """Generate startup summary for TODAY's threads only (from 00:00 until now)."""
    today = datetime.now().date()
    report = get_daily_report(registry, today.isoformat())
    return report if report else "📊 אין אשכולות חדשים היום"


_tg_session = requests.Session()
_tg_session.mount("https://", HTTPAdapter(pool_connections=2, pool_maxsize=5))


def send_telegram(token: str, chat_id: str, text: str):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        resp = _tg_session.post(url, json=payload, timeout=15)
        if resp.status_code == 429:
            retry_after = resp.json().get("parameters", {}).get("retry_after", 5)
            log.warning(f"Rate limited — sleeping {retry_after}s")
            time.sleep(retry_after)
            _tg_session.post(url, json=payload, timeout=15)
        else:
            resp.raise_for_status()
    except requests.RequestException as e:
        log.error(f"Telegram send error: {e}")


def format_post(post: dict) -> str:
    lines = []
    if post.get("forum"):
        lines.append(f"📂 {post['forum']}")
    lines.append(f"📌 <b>{post['title']}</b>")
    lines.append(post["url"])
    return "\n".join(lines)


def run():
    load_env()

    token = os.environ.get("TELEGRAM_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    check_interval = int(os.environ.get("CHECK_INTERVAL", "120"))

    if not token or not chat_id:
        log.error("Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID in .env")
        sys.exit(1)

    log.info(f"Bot started — monitoring all FXP forums, interval: {check_interval}s → chat {chat_id}")

    seen = load_seen()
    registry = load_registry()
    first_run = len(seen) == 0
    last_midnight_report_date = None

    # Send startup report with today's threads
    if first_run:
        startup_msg = "🤖 הבוט הופעל\n\nציטור את כל האשכולות שיתגלו היום..."
        send_telegram(token, chat_id, startup_msg)
        log.info("Startup notification sent")
    else:
        startup_report = format_startup_summary(registry)
        send_telegram(token, chat_id, startup_report)
        log.info("Startup daily report sent")

    while True:
        try:
            posts = get_new_posts()
            log.info(f"Fetched {len(posts)} posts from FXP")

            new_posts = [p for p in posts if p["id"] and p["id"] not in seen]

            if first_run or len(new_posts) > FLOOD_THRESHOLD:
                # Record all existing posts silently (first run or config expansion)
                for p in posts:
                    if p["id"]:
                        seen.add(p["id"])
                        # Add to registry if not already there
                        if p["id"] not in registry:
                            registry[p["id"]] = {
                                "forum": p.get("forum", "Unknown"),
                                "title": p.get("title", ""),
                                "discovered_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                            }
                save_seen(seen)
                save_registry(registry)
                if first_run:
                    log.info(f"First run: recorded {len(seen)} posts, will notify on new ones.")
                    first_run = False
                else:
                    log.info(f"Flood guard: {len(new_posts)} new posts recorded silently.")
            else:
                for post in reversed(new_posts):
                    msg = format_post(post)
                    send_telegram(token, chat_id, msg)
                    seen.add(post["id"])

                    # Add to registry
                    if post["id"] not in registry:
                        registry[post["id"]] = {
                            "forum": post.get("forum", "Unknown"),
                            "title": post.get("title", ""),
                            "discovered_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                        }

                    log.info(f"Sent: {post['title'][:60]}")
                    time.sleep(1)

                if new_posts:
                    save_seen(seen)
                    save_registry(registry)

            # Check for midnight (00:00) and send cumulative report
            now = datetime.now()
            today_date = now.date()

            if last_midnight_report_date != today_date and now.hour == 0:
                # At midnight: send cumulative report (all threads up to yesterday)
                yesterday = today_date - timedelta(days=1)
                midnight_report = get_cumulative_report(registry, yesterday.isoformat())
                if midnight_report:
                    send_telegram(token, chat_id, midnight_report)
                    log.info(f"Midnight cumulative report sent for {yesterday.isoformat()}")
                last_midnight_report_date = today_date

        except Exception as e:
            log.error(f"Loop error: {e}")

        time.sleep(check_interval)


if __name__ == "__main__":
    run()
