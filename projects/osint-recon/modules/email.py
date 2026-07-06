"""Email recon: account existence, breaches, mentions."""
from __future__ import annotations
import json, tempfile, os
from pathlib import Path
from .utils import run_cmd, have, ddg, http_json, info, warn


def _holehe(email):
    if not have("holehe"):
        return []
    ok, out = run_cmd(["holehe", "--only-used", "--no-color", email], timeout=180)
    found = []
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("[+]"):
            found.append(line[3:].strip())
    return found


def _socialscan(email):
    if not have("socialscan"):
        return []
    jf = Path(tempfile.gettempdir()) / "ss_email.json"
    run_cmd(["socialscan", email, "--json", str(jf)], timeout=120)
    res = []
    if jf.exists():
        try:
            for r in json.loads(jf.read_text()):
                if r.get("available") is False:
                    res.append(f"{r.get('platform')}: registered")
        except Exception:
            pass
    return res


def run(target, ttype, report):
    info("=== EMAIL RECON ===")

    report.add("✅ Accounts using this email (holehe)", _holehe(target))
    report.add("📱 Platform registration (socialscan)", _socialscan(target))

    user = target.split("@")[0]
    dorks = []
    for q in (f'"{target}"',
              f'"{target}" (site:pastebin.com OR site:github.com OR site:trello.com)',
              f'"{user}" filetype:pdf OR "{user}" filetype:xlsx'):
        for r in ddg(q, max_results=10):
            dorks.append(f"[{r.get('title','')[:60]}]({r.get('href')})")
    report.add("🔎 Email mentions (dorks)", dorks)

    report.add("⚠️ Breach check (manual)",
               [f"https://haveibeenpwned.com/account/{target}",
                f"https://intelx.io/?s={target}"])
