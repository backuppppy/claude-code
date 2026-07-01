#!/usr/bin/env python3
"""
storytel_direct_download.py — הורדת ספר שמע מ-Storytel ישירות דרך ה-API.

למה זה קיים:
  audiobook-dl 0.7.3 נתקל בבאג שבו (לפחות לחלק מהספרים) הוא מוריד רק את העטיפה
  ויוצא עם exit 0 *בלי* להוריד את האודיו ובלי שגיאה. אבחנּו שזרם ה-MP3 עצמו
  זמin לחלוטין (HTTP 200, audio/mpeg, קובץ מלא) — ה-extractor פשוט לא מושך אותו.
  הסקריפט הזה עוקף את הכלי ומדבר ישירות מול ה-API.

דרישות מוקדמות:
  - קרדנציאלס ב-~/.config/audiobook-dl/audiobook-dl.toml תחת [sources.storytel].
  - ffmpeg ו-pycryptodome (Crypto) ו-requests מותקנים.
  - הספר *אינו* חייב להיות במדף — נעשה שימוש ב-getBookInfoForContent.action
    שמחזיר את אותה רשומה גם לספרים שאינם במדף (owns=0).

שימוש:
  python3 storytel_direct_download.py "<URL של הספר>" [שם_פלט]

הצינור: login.action -> getBookInfoForContent.action (עוקף מדף) -> AId ->
        mp3streamRangeReq -> הורדה -> הטמעת עטיפה+מטא-דאטה עם ffmpeg.
"""
import sys, os, subprocess, tomllib
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

CONFIG = os.path.expanduser("~/.config/audiobook-dl/audiobook-dl.toml")
# מפתחות הצפנה קבועים של Storytel (פומביים, מתוך storytel-tui / audiobook-dl)
AES_KEY, AES_IV = b"VQZBJ6TD8M9WBUWT", b"joiwef08u23j341a"
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0"


def encrypt_password(p: str) -> str:
    return AES.new(AES_KEY, AES.MODE_CBC, AES_IV).encrypt(pad(p.encode(), 16)).hex()


def book_id_from_url(url: str) -> str:
    return url.rstrip("/").split("-")[-1]


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: storytel_direct_download.py <book_url> [output_name]")
    url = sys.argv[1]
    book_id = book_id_from_url(url)

    cfg = tomllib.load(open(CONFIG, "rb"))["sources"]["storytel"]
    s = requests.Session()
    s.headers.update({"User-Agent": UA})

    # 1) התחברות
    ud = s.get("https://www.storytel.com/api/login.action",
               params={"m": 1, "uid": cfg["username"],
                       "pwd": encrypt_password(cfg["password"])}).json()
    jwt = ud["accountInfo"]["jwt"]
    token = ud["accountInfo"]["singleSignToken"]
    s.headers.update({"authorization": f"Bearer {jwt}"})

    # 2) מציאת הספר בלי מדף — getBookInfoForContent.action מחזיר רשומה בצורת מדף
    #    (book/abook...) גם לספרים שאינם במדף. ה-id ב-URL יכול להיות bookId או
    #    consumableId; אם consumableId — ממירים ל-bookId דרך book-details.
    def get_slb(bid):
        r = s.get("https://www.storytel.com/api/getBookInfoForContent.action",
                  params={"bookId": bid, "token": token})
        if r.status_code != 200:
            return None
        slb = r.json().get("slb")
        if slb and (slb.get("book") or {}).get("AId") is not None:
            return slb
        return None

    book = get_slb(book_id)
    if book is None:
        r = s.get(f"https://api.storytel.net/book-details/consumables/{book_id}")
        legacy_id = r.json().get("bookId") if r.status_code == 200 else None
        if legacy_id is not None:
            book = get_slb(legacy_id)
    if book is None:
        sys.exit("לא נמצאה רשומת ספר עבור ה-id (בדוק את ה-URL / החשבון).")

    aid = book["book"]["AId"]
    title = book["book"]["name"]
    author = ", ".join(a["name"] for a in book["book"].get("authors", []))
    narrator = ", ".join(n["name"] for n in book.get("abook", {}).get("narrators", []))
    isbn = book.get("abook", {}).get("isbn")
    out_name = sys.argv[2] if len(sys.argv) > 2 else title
    print(f"📖 {title} | מחבר: {author} | מקריא: {narrator}")

    # 4) הורדת זרם האודיו — הורדה מתחדשת עם אימות גודל.
    #    ⚠️ הזרם עלול להיקטע באמצע. אסור לתייג קובץ חלקי (טעינו פעם ומסרנו 1h46m
    #    במקום 11.5h). לכן: קוראים את הגודל המלא מ-content-range, ומורידים עם
    #    Range מתחדש (bytes=<כמה שכבר יש>-) עד שגודל הקובץ תואם בדיוק.
    raw = f"/tmp/{book_id}_raw.mp3"
    stream = (f"https://www.storytel.com/mp3streamRangeReq?startposition=0"
              f"&programId={aid}&token={token}")
    if os.path.exists(raw):
        os.remove(raw)
    head = s.get(stream, headers={"Range": "bytes=0-0"}, stream=True)
    total = int(head.headers["content-range"].split("/")[-1])
    head.close()
    print(f"  גודל צפוי: {total >> 20} MB")
    stalls = 0
    while True:
        have = os.path.getsize(raw) if os.path.exists(raw) else 0
        if have >= total:
            break
        try:
            r = s.get(stream, headers={"Range": f"bytes={have}-"},
                      stream=True, timeout=60)
            if r.status_code not in (200, 206):
                r.close(); stalls += 1
            else:
                with open(raw, "ab" if have else "wb") as f:
                    for ch in r.iter_content(1 << 20):
                        if ch:
                            f.write(ch)
                r.close()
        except requests.RequestException as e:
            print(f"  שגיאת רשת, ממשיך מ-{have >> 20}MB: {e}")
        now = os.path.getsize(raw) if os.path.exists(raw) else 0
        print(f"  {now >> 20}/{total >> 20} MB")
        stalls = stalls + 1 if now == have else 0
        if stalls >= 10:
            sys.exit(f"ההורדה נתקעה ב-{now}/{total} bytes — נסה שוב.")
    final = os.path.getsize(raw)
    if final != total:
        sys.exit(f"אי-התאמת גודל: {final} != {total} — הקובץ חלקי, לא מתייג.")
    print(f"  הורדה הושלמה ואומתה: {final >> 20} MB")

    # 5) עטיפה
    cover = f"/tmp/{book_id}_cover.jpg"
    if isbn:
        with open(cover, "wb") as f:
            f.write(s.get(f"https://www.storytel.com/images/{isbn}/640x640/cover.jpg").content)

    # 6) תיוג + הטמעת עטיפה
    out = f"{out_name}.mp3"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", raw]
    if isbn and os.path.exists(cover):
        cmd += ["-i", cover, "-map", "0:a", "-map", "1"]
    else:
        cmd += ["-map", "0:a"]
    cmd += ["-c", "copy", "-id3v2_version", "3",
            "-metadata", f"title={title}",
            "-metadata", f"album={title}",
            "-metadata", f"artist={author}",
            "-metadata", f"composer={narrator}", out]
    subprocess.run(cmd, check=True)
    os.remove(raw)
    if os.path.exists(cover):
        os.remove(cover)
    print(f"✅ נוצר: {out}")


if __name__ == "__main__":
    main()
