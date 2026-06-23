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
    first_run = len(seen) == 0

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
                save_seen(seen)
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
                    log.info(f"Sent: {post['title'][:60]}")
                    time.sleep(1)

                if new_posts:
                    save_seen(seen)

        except Exception as e:
            log.error(f"Loop error: {e}")

        time.sleep(check_interval)


if __name__ == "__main__":
    run()
