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

                # Clean up: FXP HTML sometimes has forum names mixed with other text
                # Take only the first meaningful part before separators
                # Split on common separators and take first non-empty part
                for sep in ["–", "—", " - ", "  ", "|", ":", "•"]:
                    if sep in name:
                        name = name.split(sep)[0].strip()
                        break

                # Take only first Hebrew/Latin word or phrase (up to ~25 chars)
                if len(name) > 30:
                    # If still too long, try to find word boundary
                    name = re.split(r"[\s]{2,}|[•|]", name)[0].strip()

                name = name[:28].strip()

                # If name contains mix of Hebrew and Latin AND too many chars, take just Hebrew part
                # This catches cases like "אתאיזםמכה לאטאיסטים: אדונ" → "אתאיזם"
                if len(name) > 20 and re.search(r"[א-ת].*[a-z0-9]|[a-z0-9].*[א-ת]", name, re.IGNORECASE):
                    # Has mixed scripts - take only first script run
                    m = re.match(r"^[֐-׿\s]+", name)  # Hebrew characters
                    if m:
                        name = m.group(0).strip()
                    else:
                        # Take everything up to first Hebrew char
                        m = re.search(r"[א-ת]", name)
                        if m:
                            name = name[:m.start()].strip()

                name = name.strip()

                # Final check: should have Hebrew or Latin letters
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

        # Extract title from the link text
        full_text = a.get_text(strip=True)
        if len(full_text) < 4:
            continue

        # Try to remove forum name from beginning if it appears there
        title = full_text
        if title.startswith(forum_name):
            title = title[len(forum_name):].strip()
            # Remove leading dashes, spaces, RTL marks, etc.
            title = re.sub(r"^[\s–\-–:•|‏]+", "", title).strip()

        # Fallback: if the title removal didn't work well, try to extract
        # by looking for common separators in Hebrew/English text
        if not title or len(title) < 3:
            # Try to split on Hebrew-English boundary or common separators
            parts = re.split(r"(?=[א-ת])|(?=[A-Z])|[\-–•:|]", full_text)
            # Take parts that aren't empty and aren't the forum name
            valid_parts = [p.strip() for p in parts if p.strip() and p.strip() != forum_name and len(p.strip()) > 3]
            if valid_parts:
                title = valid_parts[0]
            else:
                title = full_text[:50]  # Fallback: first 50 chars

        if len(title) < 4:
            continue

        full_url = href if href.startswith("http") else BASE_URL + "/" + href.lstrip("/")
        seen.add(tid)
        results.append({
            "id": tid,
            "title": title,
            "url": full_url,
            "forum": forum_name,  # Use the clean forum_name from discovery
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
