"""
FXP.co.il monitor — dynamically discovers all forums and scrapes them in parallel.
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://www.fxp.co.il"
FORUM_INDEX = BASE_URL + "/forum.php"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "he,en;q=0.9",
}

MAX_WORKERS = 15        # concurrent requests
FORUM_REFRESH_SECS = 6 * 3600  # re-discover forums every 6 hours

_session = requests.Session()
_session.headers.update(HEADERS)

_forum_cache: dict[str, str] = {}  # {forum_id: name}
_forum_cache_ts: float = 0


def _discover_forums() -> dict[str, str]:
    global _forum_cache, _forum_cache_ts
    now = time.time()
    if _forum_cache and (now - _forum_cache_ts) < FORUM_REFRESH_SECS:
        return _forum_cache

    try:
        resp = _session.get(FORUM_INDEX, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        forums: dict[str, str] = {}
        for a in soup.find_all("a", href=True):
            m = re.search(r"f=(\d+)", a["href"])
            if m:
                fid = m.group(1)
                name = a.get_text(strip=True).replace("הצג עוד", "").strip()
                # Limit to first 30 chars - most forum names are shorter
                name = name[:30].strip()
                if name and len(name) > 2 and fid not in forums:
                    forums[fid] = name
        if forums:
            _forum_cache = forums
            _forum_cache_ts = now
            print(f"[Monitor] Discovered {len(forums)} forums")
    except Exception as e:
        print(f"[Monitor] Forum discovery error: {e}")

    return _forum_cache


def _fetch_forum(fid: str, name: str) -> list[dict]:
    url = f"{BASE_URL}/forumdisplay.php?f={fid}"
    try:
        resp = _session.get(url, timeout=15)
        resp.raise_for_status()
        return _parse_threads(resp.text, name)
    except Exception as e:
        print(f"[Monitor] Error f={fid} ({name}): {e}")
        return []


def _parse_threads(html: str, forum_name: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    results = []
    seen: set[str] = set()

    for a in soup.find_all("a", href=True):
        href: str = a.get("href", "")
        m = re.search(r"t=(\d+)", href)
        if not m:
            continue
        tid = m.group(1)
        if tid in seen:
            continue
        title = a.get_text(strip=True)
        if len(title) < 4:
            continue

        full_url = href if href.startswith("http") else BASE_URL + "/" + href.lstrip("/")
        seen.add(tid)
        results.append({
            "id": tid,
            "title": title,
            "url": full_url,
            "forum": forum_name,
        })

    return results


def get_new_posts() -> list[dict]:
    forums = _discover_forums()
    all_posts: list[dict] = []
    seen_ids: set[str] = set()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(_fetch_forum, fid, name): (fid, name)
            for fid, name in forums.items()
        }
        for future in as_completed(futures):
            for post in future.result():
                if post["id"] not in seen_ids:
                    seen_ids.add(post["id"])
                    all_posts.append(post)

    return all_posts
