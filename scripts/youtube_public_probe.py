#!/usr/bin/env python3
"""
Probe *publicly accessible* metadata for YouTube videos (no auth, no downloads).

This is useful for comparing what leaks for:
- public videos
- unlisted videos
- members-only videos

It does not attempt to bypass access controls.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable
from urllib.parse import quote_plus, urlparse

import requests


YOUTUBE_WATCH = "https://www.youtube.com/watch?v={video_id}"
YOUTUBE_SHORT = "https://youtu.be/{video_id}"
YOUTUBE_OEMBED = "https://www.youtube.com/oembed?url={url}&format=json"
YTIMG = "https://i.ytimg.com/vi/{video_id}/{name}.jpg"


META_RE = re.compile(
    r'<meta\s+(?P<attr>(?:name|property|itemprop))="(?P<key>[^"]+)"\s+content="(?P<val>[^"]*)"\s*/?>',
    re.IGNORECASE,
)
PLAYABILITY_RE = re.compile(r'"playabilityStatus"\s*:\s*(\{.*?\})\s*,\s*"miniplayer"', re.DOTALL)
JSON_KV_RE = re.compile(
    r'"(?P<k>videoId|channelId|ownerChannelName|author|lengthSeconds|isCrawlable|isLiveContent|category|publishDate|uploadDate)"\s*:\s*(?P<v>"[^"]*"|true|false|null|\d+)',
    re.IGNORECASE,
)


@dataclass
class ProbeResult:
    input: str
    video_id: str | None
    fetched_at_utc: str

    # oEmbed
    oembed_ok: bool = False
    oembed_title: str | None = None
    oembed_author_name: str | None = None
    oembed_author_url: str | None = None
    oembed_thumbnail_url: str | None = None

    # HTML meta tags
    meta_title: str | None = None
    meta_description: str | None = None
    meta_keywords: str | None = None
    meta_og_url: str | None = None
    meta_og_image: str | None = None
    meta_item_duration: str | None = None
    meta_item_date_published: str | None = None
    meta_item_upload_date: str | None = None
    meta_item_genre: str | None = None

    # playability
    playability_status: str | None = None
    playability_reason: str | None = None
    playability_offer_id: str | None = None

    # extracted JSON fields from HTML
    channel_id: str | None = None
    owner_channel_name: str | None = None
    author: str | None = None
    length_seconds: int | None = None
    category: str | None = None
    is_crawlable: bool | None = None
    is_live_content: bool | None = None
    publish_date: str | None = None
    upload_date: str | None = None

    # thumbnails HEAD checks
    thumbnails: dict[str, dict[str, Any]] = field(default_factory=dict)

    # errors
    error: str | None = None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def extract_video_id(s: str) -> str | None:
    s = s.strip()
    # raw ID
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s

    try:
        u = urlparse(s)
    except Exception:
        return None

    host = (u.netloc or "").lower()
    path = u.path or ""
    if host in {"youtu.be"}:
        vid = path.strip("/").split("/")[0]
        return vid if re.fullmatch(r"[A-Za-z0-9_-]{11}", vid or "") else None

    if host.endswith("youtube.com"):
        # /watch?v=...
        if path == "/watch":
            m = re.search(r"(?:^|[?&])v=([A-Za-z0-9_-]{11})(?:&|$)", u.query or "")
            return m.group(1) if m else None
        # /shorts/<id>
        m = re.match(r"^/shorts/([A-Za-z0-9_-]{11})", path)
        if m:
            return m.group(1)
        # /embed/<id>
        m = re.match(r"^/embed/([A-Za-z0-9_-]{11})", path)
        if m:
            return m.group(1)

    return None


def http_session(user_agent: str, timeout_s: float) -> requests.Session:
    sess = requests.Session()
    sess.headers.update({"User-Agent": user_agent, "Accept-Language": "en-US,en;q=0.9"})
    sess.request = _wrap_timeout(sess.request, timeout_s)
    return sess


def _wrap_timeout(fn, timeout_s: float):
    def _wrapped(method, url, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = timeout_s
        return fn(method, url, **kwargs)

    return _wrapped


def fetch_text(sess: requests.Session, url: str) -> str:
    r = sess.get(url)
    r.raise_for_status()
    return r.text


def fetch_json(sess: requests.Session, url: str) -> Any:
    r = sess.get(url)
    r.raise_for_status()
    return r.json()


def head_info(sess: requests.Session, url: str) -> dict[str, Any]:
    try:
        r = sess.head(url, allow_redirects=True)
        return {
            "ok": r.ok,
            "status_code": r.status_code,
            "content_type": r.headers.get("content-type"),
            "content_length": int(r.headers.get("content-length")) if r.headers.get("content-length") else None,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def parse_meta(html: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in META_RE.finditer(html):
        key = f'{m.group("attr").lower()}:{m.group("key").strip()}'
        out[key] = m.group("val")
    return out


def parse_playability(html: str) -> dict[str, Any] | None:
    m = PLAYABILITY_RE.search(html)
    if not m:
        return None
    blob = m.group(1)
    try:
        return json.loads(blob)
    except Exception:
        # Sometimes YouTube embeds JS-ish JSON with escapes; don't crash the whole probe.
        return None


def parse_json_fields(html: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for m in JSON_KV_RE.finditer(html):
        k = m.group("k")
        raw = m.group("v")
        if raw.startswith('"') and raw.endswith('"'):
            out[k] = raw[1:-1]
        elif raw in {"true", "false"}:
            out[k] = raw == "true"
        elif raw == "null":
            out[k] = None
        else:
            try:
                out[k] = int(raw)
            except Exception:
                out[k] = raw
    return out


def probe_one(
    sess: requests.Session,
    input_str: str,
    video_id: str,
    thumbnails: Iterable[str],
    sleep_s: float,
) -> ProbeResult:
    res = ProbeResult(input=input_str, video_id=video_id, fetched_at_utc=utc_now_iso())

    # oEmbed metadata (public)
    try:
        oembed_url = YOUTUBE_OEMBED.format(url=quote_plus(YOUTUBE_SHORT.format(video_id=video_id)))
        o = fetch_json(sess, oembed_url)
        res.oembed_ok = True
        res.oembed_title = o.get("title")
        res.oembed_author_name = o.get("author_name")
        res.oembed_author_url = o.get("author_url")
        res.oembed_thumbnail_url = o.get("thumbnail_url")
    except Exception as e:
        res.oembed_ok = False
        res.error = f"oembed: {e}"

    # Watch page HTML
    html = ""
    try:
        html = fetch_text(sess, YOUTUBE_WATCH.format(video_id=video_id))
        meta = parse_meta(html)
        res.meta_title = meta.get("name:title")
        res.meta_description = meta.get("name:description")
        res.meta_keywords = meta.get("name:keywords")
        res.meta_og_url = meta.get("property:og:url")
        res.meta_og_image = meta.get("property:og:image")
        res.meta_item_duration = meta.get("itemprop:duration")
        res.meta_item_date_published = meta.get("itemprop:datePublished")
        res.meta_item_upload_date = meta.get("itemprop:uploadDate")
        res.meta_item_genre = meta.get("itemprop:genre")

        play = parse_playability(html) or {}
        res.playability_status = play.get("status")
        res.playability_reason = play.get("reason")
        offer_id = (
            play.get("errorScreen", {})
            .get("playerLegacyDesktopYpcOfferRenderer", {})
            .get("offerId")
        )
        res.playability_offer_id = offer_id

        fields = parse_json_fields(html)
        res.channel_id = fields.get("channelId")
        res.owner_channel_name = fields.get("ownerChannelName")
        res.author = fields.get("author")
        res.length_seconds = fields.get("lengthSeconds")
        res.category = fields.get("category")
        res.is_crawlable = fields.get("isCrawlable")
        res.is_live_content = fields.get("isLiveContent")
        res.publish_date = fields.get("publishDate")
        res.upload_date = fields.get("uploadDate")
    except Exception as e:
        res.error = (res.error + "; " if res.error else "") + f"watch: {e}"

    # Thumbnail accessibility (public files)
    for name in thumbnails:
        url = YTIMG.format(video_id=video_id, name=name)
        res.thumbnails[name] = {"url": url, **head_info(sess, url)}
        if sleep_s:
            time.sleep(sleep_s)

    return res


def write_csv(path: str, rows: list[ProbeResult]) -> None:
    # Flatten thumbnail statuses; keep it compact.
    fieldnames = [
        "input",
        "video_id",
        "fetched_at_utc",
        "oembed_ok",
        "oembed_title",
        "oembed_author_name",
        "oembed_author_url",
        "oembed_thumbnail_url",
        "meta_title",
        "meta_description",
        "meta_keywords",
        "meta_og_url",
        "meta_og_image",
        "meta_item_duration",
        "meta_item_date_published",
        "meta_item_upload_date",
        "meta_item_genre",
        "playability_status",
        "playability_reason",
        "playability_offer_id",
        "channel_id",
        "owner_channel_name",
        "author",
        "length_seconds",
        "category",
        "is_crawlable",
        "is_live_content",
        "publish_date",
        "upload_date",
        "thumbnail_maxresdefault_ok",
        "thumbnail_sddefault_ok",
        "thumbnail_hqdefault_ok",
        "thumbnail_mqdefault_ok",
        "thumbnail_default_ok",
        "error",
    ]

    def thumb_ok(r: ProbeResult, key: str) -> Any:
        return (r.thumbnails.get(key) or {}).get("ok")

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            d = asdict(r)
            row = {k: d.get(k) for k in fieldnames}
            row["thumbnail_maxresdefault_ok"] = thumb_ok(r, "maxresdefault")
            row["thumbnail_sddefault_ok"] = thumb_ok(r, "sddefault")
            row["thumbnail_hqdefault_ok"] = thumb_ok(r, "hqdefault")
            row["thumbnail_mqdefault_ok"] = thumb_ok(r, "mqdefault")
            row["thumbnail_default_ok"] = thumb_ok(r, "default")
            w.writerow(row)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Probe public YouTube metadata (no auth).")
    ap.add_argument("inputs", nargs="+", help="Video IDs or URLs")
    ap.add_argument("--json", dest="json_path", help="Write JSON array to this file (optional)")
    ap.add_argument("--csv", dest="csv_path", help="Write CSV to this file (optional)")
    ap.add_argument(
        "--thumbnails",
        default="maxresdefault,sddefault,hqdefault,mqdefault,default",
        help="Comma-separated thumbnail names to HEAD-check",
    )
    ap.add_argument("--sleep", type=float, default=0.0, help="Sleep seconds between HEAD requests")
    ap.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout seconds")
    ap.add_argument(
        "--user-agent",
        default="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
    )
    args = ap.parse_args(argv)

    sess = http_session(args.user_agent, args.timeout)
    thumbs = [t.strip() for t in args.thumbnails.split(",") if t.strip()]

    results: list[ProbeResult] = []
    for inp in args.inputs:
        vid = extract_video_id(inp)
        if not vid:
            results.append(
                ProbeResult(
                    input=inp,
                    video_id=None,
                    fetched_at_utc=utc_now_iso(),
                    error="Could not extract video_id (expected 11-char ID or YouTube URL)",
                )
            )
            continue
        results.append(probe_one(sess, inp, vid, thumbs, args.sleep))

    payload = [asdict(r) for r in results]

    if args.json_path:
        with open(args.json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")
    else:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")

    if args.csv_path:
        write_csv(args.csv_path, results)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

