#!/usr/bin/env python3
import zipfile, json, datetime, sys

ZIP_PATH = "/storage/emulated/0/Download/facebook-bzllhkwtb-10_05_2026-PSiUSNuC.zip"
JSON_PATH = "your_facebook_activity/posts/your_posts__check_ins__photos_and_videos_1.json"
OUT_PATH  = "/storage/emulated/0/Download/facebook_posts.md"

def fix(s):
    if not s:
        return ""
    try:
        return s.encode("latin1").decode("utf-8")
    except Exception:
        return s

def ts(unix):
    return datetime.datetime.fromtimestamp(unix).strftime("%d/%m/%Y %H:%M")

with zipfile.ZipFile(ZIP_PATH) as z:
    raw = z.read(JSON_PATH)

posts = json.loads(raw.decode("utf-8"))

lines = []
lines.append('<div dir="rtl" lang="he">\n')
lines.append("# פוסטים שלי בפייסבוק\n")
lines.append(f"סה\"כ: {len(posts)} פוסטים\n")
lines.append("---\n")

for i, post in enumerate(posts, 1):
    date_str = ts(post.get("timestamp", 0))
    lines.append(f"\n## פוסט {i} — {date_str}\n")

    # Post text
    post_text = ""
    for d in post.get("data", []):
        if d.get("post"):
            post_text = fix(d["post"])
            break

    if post_text:
        # Preserve line breaks
        for ln in post_text.split("\n"):
            lines.append(ln + "  \n")
        lines.append("\n")

    # Attachments
    for att in post.get("attachments", []):
        for d in att.get("data", []):
            # Media
            if "media" in d:
                m = d["media"]
                uri = m.get("uri", "")
                caption = fix(m.get("description", ""))
                title_m = fix(m.get("title", ""))
                if caption:
                    lines.append(f"> **תיאור תמונה/וידאו:** {caption}\n")
                elif title_m:
                    lines.append(f"> **כותרת מדיה:** {title_m}\n")
                if uri:
                    lines.append(f"> *קובץ:* `{uri}`\n")

            # External link
            if "external_context" in d:
                url = d["external_context"].get("url", "")
                name = fix(d["external_context"].get("name", ""))
                source = fix(d["external_context"].get("source", ""))
                label = name or source or url
                if url:
                    lines.append(f"> **קישור:** [{label}]({url})\n")
                elif label:
                    lines.append(f"> **קישור:** {label}\n")

            # Place / check-in
            if "place" in d:
                p = d["place"]
                pname = fix(p.get("name", ""))
                addr = ""
                coord = p.get("coordinate", {})
                if pname:
                    lines.append(f"> **מיקום:** {pname}")
                    if addr:
                        lines.append(f" — {addr}")
                    lines.append("\n")

            # Text inside attachment
            if "text" in d:
                lines.append(f"> {fix(d['text'])}\n")

    lines.append("\n---\n")

lines.append("\n</div>\n")

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write("".join(lines))

print(f"Done! {len(posts)} posts written to {OUT_PATH}")
