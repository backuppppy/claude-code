"""Domain recon: subdomains, DNS, emails, typosquatting, tech."""
from __future__ import annotations
import json, tempfile, os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from .utils import (run_cmd, http_json, http_text, ddg, have,
                    info, warn, good)


def _crtsh(domain):
    data = http_json(f"https://crt.sh/?q=%25.{domain}&output=json", timeout=40)
    subs = set()
    if data:
        for row in data:
            for name in str(row.get("name_value", "")).splitlines():
                name = name.strip().lstrip("*.").lower()
                if name.endswith(domain):
                    subs.add(name)
    return sorted(subs)


def _hackertarget(domain):
    txt = http_text(f"https://api.hackertarget.com/hostsearch/?q={domain}")
    subs = set()
    if txt and "error" not in txt.lower() and "api count" not in txt.lower():
        for line in txt.splitlines():
            host = line.split(",")[0].strip().lower()
            if host.endswith(domain):
                subs.add(host)
    return sorted(subs)


def _subfinder(domain):
    if not have("subfinder"):
        return []
    ok, out = run_cmd(["subfinder", "-silent", "-d", domain], timeout=90)
    return sorted({l.strip().lower() for l in out.splitlines()
                   if l.strip().endswith(domain)}) if ok else []


def _amass(domain):
    if not have("amass"):
        return []
    ok, out = run_cmd(["amass", "enum", "-passive", "-nocolor",
                       "-timeout", "2", "-d", domain], timeout=150)
    subs = set()
    for l in out.splitlines():
        tok = l.strip().split()
        if tok and tok[0].endswith(domain):
            subs.add(tok[0].lower())
    return sorted(subs)


def _theharvester(domain):
    if not have("theHarvester"):
        return [], []
    prefix = os.path.join(tempfile.gettempdir(), f"th_{domain}")
    run_cmd(["theHarvester", "-d", domain, "-b",
             "duckduckgo,crtsh,otx,hackertarget,rapiddns,urlscan",
             "-f", prefix], timeout=150)
    emails, hosts = [], []
    jf = Path(prefix + ".json")
    if jf.exists():
        try:
            d = json.loads(jf.read_text())
            emails = sorted(set(d.get("emails", []) or []))
            hosts = sorted(set(d.get("hosts", []) or []))
        except Exception:
            pass
    return emails, hosts


def _dns(domain):
    try:
        import dns.resolver
    except Exception:
        return []
    out = []
    for rr in ("A", "AAAA", "MX", "NS", "TXT", "SOA"):
        try:
            ans = dns.resolver.resolve(domain, rr, lifetime=8)
            for a in ans:
                out.append(f"{rr}: {a.to_text()}")
        except Exception:
            continue
    return out


def _dnstwist(domain):
    if not have("dnstwist"):
        return []
    ok, out = run_cmd(["dnstwist", "--registered", "--format", "json", domain],
                      timeout=180)
    if not ok:
        return []
    try:
        rows = json.loads(out)
    except Exception:
        return []
    res = []
    for r in rows:
        dom = r.get("domain")
        if dom and dom != domain:
            dns_a = ",".join(r.get("dns_a", []) or [])
            res.append(f"{dom}" + (f" → {dns_a}" if dns_a else ""))
    return res


def run(target, ttype, report):
    info("=== DOMAIN RECON (parallel) ===")

    # Fire all independent, slow sources concurrently.
    jobs = {
        "crtsh":        (_crtsh, target),
        "hackertarget": (_hackertarget, target),
        "subfinder":    (_subfinder, target),
        "amass":        (_amass, target),
        "dns":          (_dns, target),
        "theharvester": (_theharvester, target),
        "dnstwist":     (_dnstwist, target),
    }
    results = {}
    with ThreadPoolExecutor(max_workers=len(jobs)) as ex:
        futs = {ex.submit(fn, arg): name for name, (fn, arg) in jobs.items()}
        for fut in futs:
            name = futs[fut]
            try:
                results[name] = fut.result(timeout=200)
            except Exception as e:
                warn(f"{name} failed: {e}")
                results[name] = None

    subs = set()
    for name in ("crtsh", "hackertarget", "subfinder", "amass"):
        subs.update(results.get(name) or [])
    report.add("🌐 Subdomains", sorted(subs))

    report.add("🧭 DNS records", results.get("dns") or [])

    emails, hosts = results.get("theharvester") or ([], [])
    report.add("📧 Emails (theHarvester)", emails)
    if hosts:
        report.add("🖧 Hosts (theHarvester)", sorted(set(hosts)))

    report.add("🎭 Typosquat / lookalike domains", results.get("dnstwist") or [])

    # quick login / sensitive dorks
    dorks = []
    for q in (f"site:{target} (inurl:login OR inurl:admin OR inurl:portal)",
              f"site:{target} intext:@{target}"):
        for r in ddg(q, max_results=8):
            dorks.append(f"[{r.get('title','')[:60]}]({r.get('href')})")
    report.add("🔑 Login / admin surfaces", dorks)
