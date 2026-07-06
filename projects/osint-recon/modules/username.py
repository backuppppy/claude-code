"""Username recon: account discovery across hundreds of sites."""
from __future__ import annotations
import json, tempfile, os, re
from pathlib import Path
from .utils import run_cmd, have, ddg, info, warn
from . import apis


def _sherlock(username):
    if not have("sherlock"):
        return []
    out_dir = tempfile.mkdtemp()
    ok, out = run_cmd(["sherlock", "--no-color", "--print-found",
                       "--timeout", "12", "--folderoutput", out_dir, username],
                      timeout=300)
    found = []
    # parse "[+] Site: url"
    for line in out.splitlines():
        m = re.search(r"\[\+\]\s+([^:]+):\s+(https?://\S+)", line)
        if m:
            found.append(f"{m.group(1).strip()}: {m.group(2).strip()}")
    return found


def _maigret(username):
    if not have("maigret"):
        return []
    jf = os.path.join(tempfile.gettempdir(), f"maigret_{username}.json")
    run_cmd(["maigret", username, "--json", "simple", "--no-color",
             "--timeout", "12", "-J", "simple", "--folderoutput",
             tempfile.gettempdir()], timeout=300)
    # maigret writes report_<user>_simple.json
    cand = list(Path(tempfile.gettempdir()).glob(f"report_{username}_simple.json"))
    found = []
    if cand:
        try:
            d = json.loads(cand[0].read_text())
            for site, meta in d.items():
                st = (meta or {}).get("status", {})
                if isinstance(st, dict) and st.get("status") == "Claimed":
                    url = (meta.get("url_user") or "")
                    found.append(f"{site}: {url}")
        except Exception:
            pass
    return found


def _socialscan(username):
    if not have("socialscan"):
        return []
    ok, out = run_cmd(["socialscan", username, "--json",
                       os.path.join(tempfile.gettempdir(), "ss.json")],
                      timeout=120)
    res = []
    jf = Path(tempfile.gettempdir()) / "ss.json"
    if jf.exists():
        try:
            for r in json.loads(jf.read_text()):
                if r.get("available") is False:  # taken == exists
                    res.append(f"{r.get('platform')}: taken")
        except Exception:
            pass
    return res


def run(target, ttype, report):
    info("=== USERNAME RECON ===")

    s = _sherlock(target)
    report.add("👤 Accounts (Sherlock)", s)

    m = _maigret(target)
    report.add("🔎 Accounts (Maigret)", m)

    ss = _socialscan(target)
    report.add("📱 Platform availability (socialscan)", ss)

    report.add("🐙 GitHub profile", apis.github_user(target))

    dorks = []
    for q in (f'"{target}" (site:twitter.com OR site:x.com OR site:instagram.com OR site:facebook.com OR site:linkedin.com)',
              f'"{target}" (site:github.com OR site:gitlab.com OR site:reddit.com OR site:telegram.me OR site:t.me)'):
        for r in ddg(q, max_results=10):
            dorks.append(f"[{r.get('title','')[:60]}]({r.get('href')})")
    report.add("🔗 Social mentions (dorks)", dorks)
