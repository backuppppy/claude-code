"""
FXP Telegram Bot — monitors all FXP forums and sends new threads to Telegram.

DAILY FLOW (2026-08-16 FINAL):
1. **Startup** — sends report of TODAY's threads (00:00 to now)
2. **Real-time** — notifies ONLY for threads opened TODAY (not old threads)
3. **Midnight (00:00)** — sends report of YESTERDAY's threads only

Key Rules:
- TODAY = threads discovered from 00:00 to 23:59:59
- Midnight report = threads from previous day (00:00 to 23:59:59)
- Real-time notifications = only for TODAY's threads (older threads are skipped)

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
    Generate report for threads discovered ONLY on target_date (YYYY-MM-DD).
    Shows only threads from that specific day, grouped by forum.

    Examples:
    - get_daily_report(registry, "2026-08-16") → threads discovered on Aug 16 only
    - get_daily_report(registry, "2026-08-15") → threads discovered on Aug 15 only
    """
    # Parse target date
    try:
        target = datetime.strptime(target_date, "%Y-%m-%d").date()
    except ValueError:
        return ""

    # Collect threads by forum + title for ONLY the target date
    forums_threads: dict[str, list[tuple[str, str]]] = {}  # forum -> [(title, url)]

    for thread_id, data in registry.items():
        discovered_at = data.get("discovered_at", "")
        if not discovered_at:
            continue
        try:
            discovery_time = datetime.fromisoformat(discovered_at.replace("Z", "+00:00"))
            discovery_date = discovery_time.date()

            # Include ONLY if discovered on target date (exact match)
            if discovery_date == target:
                forum = data.get("forum", "Unknown")
                title = data.get("title", "Unknown")
                url = data.get("url", "")

                if forum not in forums_threads:
                    forums_threads[forum] = []
                forums_threads[forum].append((title, url))
        except Exception:
            continue

    if not forums_threads:
        return ""

    # Build report (sorted by forum count)
    date_str = target_date
    lines = [f"📊 דוח אשכולות — {date_str}\n"]

    total = sum(len(threads) for threads in forums_threads.values())
    sorted_forums = sorted(forums_threads.items(), key=lambda x: len(x[1]), reverse=True)

    # Show all forums with thread counts
    for forum, threads in sorted_forums:
        lines.append(f"📂 <b>{forum}</b>: {len(threads)} אשכולות")

    lines.append("")
    lines.append(f"סה״כ: {total} אשכולות ב-{len(forums_threads)} פורומים")

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
    """Format a single post/thread for Telegram display."""
    lines = []
    forum = post.get("forum", "Unknown")
    title = post.get("title", "Unknown")
    url = post.get("url", "")

    lines.append(f"📂 <b>{forum}</b>")
    lines.append(f"📌 {title}")
    if url:
        lines.append(f"🔗 {url}")
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
                                "url": p.get("url", ""),
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
                today = datetime.now().date()

                for post in reversed(new_posts):
                    # Add to registry first
                    if post["id"] not in registry:
                        registry[post["id"]] = {
                            "forum": post.get("forum", "Unknown"),
                            "title": post.get("title", ""),
                            "url": post.get("url", ""),
                            "discovered_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                        }

                    # Only send notifications for TODAY's threads
                    discovered_at = registry[post["id"]].get("discovered_at", "")
                    try:
                        discovery_time = datetime.fromisoformat(discovered_at.replace("Z", "+00:00"))
                        discovery_date = discovery_time.date()

                        if discovery_date == today:
                            msg = format_post(post)
                            send_telegram(token, chat_id, msg)
                            log.info(f"Sent: {post['title'][:60]}")
                            time.sleep(1)
                        else:
                            log.info(f"Skipped (not today): {post['title'][:60]}")
                    except Exception as e:
                        log.error(f"Date check error: {e}")

                    seen.add(post["id"])

                if new_posts:
                    save_seen(seen)
                    save_registry(registry)

            # Check for midnight (00:00) and send daily report for YESTERDAY
            now = datetime.now()
            today_date = now.date()

            if last_midnight_report_date != today_date and now.hour == 0:
                # At midnight: send report for YESTERDAY's threads only
                yesterday = today_date - timedelta(days=1)
                midnight_report = get_daily_report(registry, yesterday.isoformat())
                if midnight_report:
                    send_telegram(token, chat_id, midnight_report)
                    log.info(f"Midnight report sent for {yesterday.isoformat()}")
                last_midnight_report_date = today_date

        except Exception as e:
            log.error(f"Loop error: {e}")

        time.sleep(check_interval)


if __name__ == "__main__":
    run()
