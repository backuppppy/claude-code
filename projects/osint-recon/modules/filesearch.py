"""
Heavy FILE / DOCUMENT discovery — the core of osint-recon.
Runs for every target type. Hunts leaked/public files via search-engine dorks,
open directories, Wayback archive, and public code search.
"""
from __future__ import annotations
from .utils import ddg, http_json, http_text, good, info, warn

# document / data / secret-ish extensions worth hunting
DOC_EXTS   = ["pdf", "doc", "docx", "odt", "rtf", "txt", "ppt", "pptx"]
DATA_EXTS  = ["xls", "xlsx", "csv", "json", "xml", "sql", "db", "sqlite"]
JUICY_EXTS = ["env", "conf", "cfg", "ini", "yml", "yaml", "log", "bak",
              "old", "backup", "zip", "rar", "7z", "tar", "gz",
              "key", "pem", "git"]

FILE_HOSTS = ["scribd.com", "slideshare.net", "docs.google.com",
              "drive.google.com", "dropbox.com", "mega.nz", "mediafire.com",
              "pastebin.com", "issuu.com", "academia.edu", "researchgate.net",
              "anonfiles.com", "4shared.com", "wetransfer.com", "box.com"]


def _or(prefix, items):
    return "(" + " OR ".join(f"{prefix}:{i}" for i in items) + ")"


def _collect(queries, per=12, cap=60):
    seen, out = set(), []
    for q in queries:
        info(f"dork: {q}")
        for r in ddg(q, max_results=per):
            href = r.get("href")
            if href and href not in seen:
                seen.add(href)
                title = (r.get("title") or "").strip()
                out.append(f"[{title[:70]}]({href})" if title else href)
            if len(out) >= cap:
                return out
    return out


def _wayback_files(domain, cap=100):
    """List archived file URLs from the Wayback CDX API (server-side ext filter)."""
    all_exts = DOC_EXTS + DATA_EXTS + JUICY_EXTS
    filt = "|".join(all_exts)
    url = ("http://web.archive.org/cdx/search/cdx"
           f"?url={domain}&matchType=domain&output=json&fl=original"
           f"&collapse=urlkey&limit=4000"
           rf"&filter=original:.*\.({filt})(\?.*)?$")
    data = http_json(url, timeout=45)
    if not data or len(data) < 2:
        return []
    exts = tuple("." + e for e in all_exts)
    files, seen = [], set()
    for row in data[1:]:
        u = row[0] if isinstance(row, list) else row
        low = u.lower().split("?")[0]
        if low.endswith(exts) and u not in seen:
            seen.add(u)
            files.append(u)
        if len(files) >= cap:
            break
    return files


def _code_mentions(term, cap=25):
    """Find the target string in public code via reliable search-engine dorks."""
    out, seen = [], set()
    q = (f'"{term}" (site:github.com OR site:gitlab.com OR site:bitbucket.org '
         f'OR site:pastebin.com OR site:gist.github.com OR site:sourcegraph.com)')
    for r in ddg(q, max_results=cap):
        href = r.get("href")
        if href and href not in seen:
            seen.add(href)
            out.append(f"[{(r.get('title') or '')[:65]}]({href})")
    return out


def run(target, ttype, report):
    info("=== FILE / DOCUMENT HUNT (deep) ===")

    if ttype == "domain":
        queries = [
            f"site:{target} {_or('filetype', DOC_EXTS)}",
            f"site:{target} {_or('filetype', DATA_EXTS)}",
            f"site:{target} {_or('filetype', JUICY_EXTS)}",
            f'site:{target} intitle:"index of"',
            f"site:{target} (inurl:backup OR inurl:admin OR inurl:private OR inurl:secret)",
            f'"{target}" {_or("filetype", DOC_EXTS + DATA_EXTS)} -site:{target}',
        ]
    else:
        t = f'"{target}"'
        queries = [
            f"{t} {_or('filetype', DOC_EXTS)}",
            f"{t} {_or('filetype', DATA_EXTS)}",
            f"{t} {_or('site', FILE_HOSTS[:8])}",
            f"{t} {_or('site', FILE_HOSTS[8:])}",
            f'{t} (intext:password OR intext:confidential OR filetype:env OR filetype:sql)',
        ]

    files = _collect(queries)
    report.add("📄 Files & documents (dorks)", files)

    # Open directories are always worth a dedicated look
    od = _collect([
        f'intitle:"index of" "{target}"',
        f'intitle:"index of" (parent directory) "{target}"',
    ], per=10, cap=25)
    report.add("📂 Open directories", od)

    if ttype == "domain":
        wb = _wayback_files(target)
        report.add("🕰️ Archived files (Wayback)", wb)

    # public code search — great for emails / domains / usernames hardcoded in repos
    if ttype in ("domain", "email", "username"):
        gc = _code_mentions(target)
        report.add("💻 Public code mentions", gc)
