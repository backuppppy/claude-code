"""
Dedicated multi-layer FILENAME hunt (ported & extended from the user's
filesearch.sh). Give it a filename + extension; it finds the actual file
across search engines, open directories, cloud shares and the Wayback Machine.

    ./osint --type file "annual report 2023" --ext pdf
"""
from __future__ import annotations
import re, urllib.parse
from .utils import ddg, http_text, http_json, info, good

# document / file-sharing / ebook hosts to sweep with site: dorks
FILE_SITES = [
    "scribd.com", "slideshare.net", "vdoc.pub", "pdfcoffee.com", "dokumen.pub",
    "fliphtml5.com", "yumpu.com", "calameo.com", "issuu.com", "academia.edu",
    "anyflip.com", "docero.com", "pdfdrive.com", "oceanofpdf.com", "z-lib.io",
    "annas-archive.org", "libgen.is", "4shared.com", "mediafire.com", "mega.nz",
    "dropbox.com", "drive.google.com", "docs.google.com", "box.com",
    "wetransfer.com", "anonfiles.com", "t.me", "archive.org", "readanybook.com",
]


def _agg_links(name):
    """Direct SEARCH links on major ebook / document aggregators (always useful)."""
    q = urllib.parse.quote(name)
    return [
        f"[Anna's Archive](https://annas-archive.org/search?q={q})",
        f"[Library Genesis](https://libgen.is/search.php?req={q})",
        f"[Open Library](https://openlibrary.org/search?q={q})",
        f"[Google Books](https://www.google.com/search?tbm=bks&q={q})",
        f"[Z-Library](https://z-lib.io/s/{q})",
        f"[PDF Drive](https://www.pdfdrive.com/search?q={q})",
        f"[Scribd search](https://www.scribd.com/search?query={q})",
        f"[Internet Archive](https://archive.org/search?query={q})",
        f"[WorldCat](https://search.worldcat.org/search?q={q})",
    ]


def _or_sites(sites):
    return "(" + " OR ".join(f"site:{s}" for s in sites) + ")"


def _dork(query, cap=15):
    out = []
    for r in ddg(query, max_results=cap):
        href = r.get("href")
        if href:
            title = (r.get("title") or "").strip()
            out.append(f"[{title[:70]}]({href})" if title else href)
    return out


def _url_of(hit):
    return hit.split("](")[-1].rstrip(")")


def _wayback_snapshot(url):
    """Fast, reliable: nearest archived copy of a specific URL (availability API)."""
    j = http_json("http://archive.org/wayback/available",
                  params={"url": url}, timeout=15)
    snap = (((j or {}).get("archived_snapshots") or {}).get("closest") or {})
    return snap.get("url") if snap.get("available") else None


def run(name, ext, report):
    ext = (ext or "pdf").lstrip(".").lower()
    info(f"=== FILENAME HUNT: \"{name}\" .{ext} ===")

    under = name.replace(" ", "_")
    hyphen = name.replace(" ", "-")

    all_hits, seen = [], set()

    def collect(label, queries, per=15):
        info(f">>> {label}")
        hits = []
        for q in queries:
            for h in _dork(q, cap=per):
                # dedup by URL inside the markdown link
                key = h.split("](")[-1].rstrip(")")
                if key not in seen:
                    seen.add(key)
                    hits.append(h)
        report.add(f"📄 {label}", hits)
        all_hits.extend(hits)

    # layer 1 — direct
    collect("Direct filetype match", [f'"{name}" filetype:{ext}'])

    # layer 2 — name variations
    varq = []
    if under != name:
        varq.append(f'"{under}" filetype:{ext}')
    if hyphen != name:
        varq.append(f'"{hyphen}" filetype:{ext}')
    if varq:
        collect("Name variations (_ / -)", varq)

    # layer 3 — open directories
    collect("Open directories", [f'intitle:"index of" "{name}"'])

    # layer 4 — broad exact filename (forums, repos, cloud shares)
    collect("Exact filename (broad)", [
        f'"{name}.{ext}"',
        f'"{name}" ({ext} OR download OR télécharger OR "free pdf" OR ebook)',
    ])

    # layer 4b — sweep document / file-sharing / ebook hosts (split to avoid long query)
    half = len(FILE_SITES) // 2
    collect("Document & file-sharing sites", [
        f'"{name}" {_or_sites(FILE_SITES[:half])}',
        f'"{name}" {_or_sites(FILE_SITES[half:])}',
    ])

    # layer 4c — ebook aggregators direct search links (deterministic)
    info(">>> Ebook / document aggregators")
    aggs = _agg_links(name)
    report.add("📚 Ebook / document aggregators (search)", aggs)
    all_hits.extend(aggs)

    # layer 5 — Wayback archived copy of the actual file URLs found above
    info(">>> Wayback Machine (archived copies of found files)")
    wb, seen_wb = [], set()
    file_urls = [u for u in (_url_of(h) for h in all_hits)
                 if u.lower().split("?")[0].endswith("." + ext)]
    for u in file_urls[:12]:
        snap = _wayback_snapshot(u)
        if snap and snap not in seen_wb:
            seen_wb.add(snap)
            wb.append(snap)
    report.add("🕰️ Wayback archived copies", wb)
    all_hits.extend(wb)

    good(f"filename hunt: {len(all_hits)} total link(s)")
