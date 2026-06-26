#!/usr/bin/env python3
"""חיפוש ספרים בסטוריטל לפי שם / מחבר.

שימוש:
    python3 storytel_search.py "harry potter"
    python3 storytel_search.py "אדם רגיש"  --locale he  --limit 15

ה-API הציבורי של החיפוש לא דורש התחברות. הפלט מציג שם, מחבר, מקריא,
פורמט (אודיו/איבוק) ו-consumableId שמשמש להורדה דרך storytel_direct_download.py.
"""
import argparse
import json
import urllib.parse
import urllib.request

SEARCH_URL = "https://www.storytel.com/api/search.action"


def search(query: str, locale: str = "he") -> list:
    params = urllib.parse.urlencode({"request_locale": locale, "q": query})
    req = urllib.request.Request(
        f"{SEARCH_URL}?{params}",
        headers={"User-Agent": "Mozilla/5.0 (Android)"},
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r).get("books", [])


def main() -> None:
    ap = argparse.ArgumentParser(description="חיפוש ספרים בסטוריטל")
    ap.add_argument("query", help="מילות חיפוש (שם ספר / מחבר)")
    ap.add_argument("--locale", default="he", help="קוד שפה לתוצאות (ברירת מחדל he)")
    ap.add_argument("--limit", type=int, default=10, help="מספר תוצאות להצגה")
    args = ap.parse_args()

    books = search(args.query, args.locale)
    print(f"נמצאו {len(books)} תוצאות עבור: {args.query}\n")
    for b in books[: args.limit]:
        book = b.get("book", {})
        title = book.get("name", "?")
        authors = ", ".join(a.get("name", "") for a in book.get("authors", []))
        ab = b.get("abook") or {}
        ebook = b.get("ebook") or {}
        narr = ", ".join(n.get("name", "") for n in ab.get("narrators", []))
        fmts = []
        if ab:
            fmts.append("אודיו")
        if ebook:
            fmts.append("איבוק")
        cid = book.get("consumableId") or book.get("id")
        print(f"• {title}")
        print(f"    מחבר: {authors}  |  מקריא: {narr or '—'}  |  {'+'.join(fmts) or '—'}")
        print(f"    id: {cid}")
        print()


if __name__ == "__main__":
    main()
