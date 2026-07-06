"""
External API enrichers — free (no key) + optional key-based.
Sources curated from github.com/public-apis/public-apis (Security / Open Data).
Every function is best-effort and returns a list[str]; missing keys -> [].
"""
from __future__ import annotations
import hashlib
from .utils import http_json, api_key

# ---------------- FREE / no-key ----------------

def rdap_domain(domain):
    """Structured registration data (registrar, dates, NS, status). rdap.org, no key."""
    d = http_json(f"https://rdap.org/domain/{domain}", timeout=20)
    if not d:
        return []
    out = []
    for ev in d.get("events", []) or []:
        out.append(f"{ev.get('eventAction')}: {ev.get('eventDate')}")
    for ent in d.get("entities", []) or []:
        roles = ",".join(ent.get("roles", []) or [])
        h = ent.get("handle", "")
        if roles:
            out.append(f"entity[{roles}]: {h}")
    ns = [n.get("ldhName") for n in d.get("nameservers", []) or [] if n.get("ldhName")]
    if ns:
        out.append("nameservers: " + ", ".join(ns))
    if d.get("status"):
        out.append("status: " + ", ".join(d["status"]))
    return out


def rdap_ip(ip):
    d = http_json(f"https://rdap.org/ip/{ip}", timeout=20)
    if not d:
        return []
    out = []
    for k in ("name", "handle", "type", "country", "startAddress", "endAddress"):
        if d.get(k):
            out.append(f"{k}: {d[k]}")
    for ent in d.get("entities", []) or []:
        roles = ",".join(ent.get("roles", []) or [])
        if roles:
            out.append(f"entity[{roles}]: {ent.get('handle','')}")
    return out


def gravatar(email):
    """Reveals a public Gravatar profile (avatar, name, linked accounts). No key."""
    h = hashlib.md5(email.strip().lower().encode()).hexdigest()
    d = http_json(f"https://www.gravatar.com/{h}.json", timeout=15,
                  headers={"User-Agent": "osint-recon"})
    out = []
    for e in (d or {}).get("entry", []) or []:
        if e.get("displayName"):
            out.append(f"name: {e['displayName']}")
        if e.get("aboutMe"):
            out.append(f"about: {e['aboutMe']}")
        for a in e.get("accounts", []) or []:
            out.append(f"account: {a.get('shortname','')} → {a.get('url','')}")
        for u in e.get("urls", []) or []:
            out.append(f"url: {u.get('value','')}")
        out.append(f"avatar: https://www.gravatar.com/avatar/{h}")
    return out


def github_user(username):
    """Public GitHub profile: name, company, blog, email, repos. No key (60/hr)."""
    d = http_json(f"https://api.github.com/users/{username}", timeout=15,
                  headers={"User-Agent": "osint-recon"})
    if not d or d.get("message") == "Not Found":
        return []
    out = []
    for k in ("name", "company", "blog", "location", "email", "bio",
              "twitter_username", "public_repos", "followers", "created_at"):
        if d.get(k):
            out.append(f"{k}: {d[k]}")
    out.append(f"profile: {d.get('html_url','')}")
    return out


def emailrep(email):
    """Email reputation / exposure summary. emailrep.io now needs a free key."""
    key = api_key("emailrep")
    if not key:
        return []
    d = http_json(f"https://emailrep.io/{email}", timeout=20,
                  headers={"User-Agent": "osint-recon", "Key": key})
    if not d or "reputation" not in d:
        return []
    det = d.get("details", {}) or {}
    out = [f"reputation: {d.get('reputation')}",
           f"suspicious: {d.get('suspicious')}"]
    for k in ("blacklisted", "malicious_activity", "credentials_leaked",
              "data_breach", "profiles", "last_seen"):
        if k in det:
            out.append(f"{k}: {det[k]}")
    return out


def urlhaus_host(host):
    """abuse.ch URLhaus — malware URLs served by this host. Needs free Auth-Key."""
    key = api_key("abusech")
    if not key:
        return []
    import requests
    try:
        r = requests.post("https://urlhaus-api.abuse.ch/v1/host/",
                          data={"host": host}, timeout=20,
                          headers={"User-Agent": "osint-recon", "Auth-Key": key})
        d = r.json()
    except Exception:
        return []
    if not d or d.get("query_status") != "ok":
        return []
    out = [f"urlhaus: {d.get('url_count')} known malicious URLs"]
    for u in (d.get("urls") or [])[:8]:
        out.append(f"{u.get('threat','')}: {u.get('url','')} [{u.get('url_status','')}]")
    return out


# ---------------- optional / key-based ----------------

def shodan_host(ip):
    key = api_key("shodan")
    if not key:
        return []
    d = http_json(f"https://api.shodan.io/shodan/host/{ip}", timeout=25,
                  params={"key": key})
    if not d:
        return []
    out = []
    if d.get("ports"):
        out.append("ports: " + ", ".join(map(str, d["ports"])))
    for f in ("org", "isp", "os", "asn", "country_name"):
        if d.get(f):
            out.append(f"{f}: {d[f]}")
    for v in (d.get("vulns") or []):
        out.append(f"VULN: {v}")
    for item in (d.get("data") or [])[:8]:
        out.append(f"{item.get('port')}/{item.get('transport','tcp')}: "
                   f"{(item.get('product') or item.get('_shodan',{}).get('module',''))}")
    return out


def hunter_domain(domain):
    key = api_key("hunter")
    if not key:
        return []
    d = http_json("https://api.hunter.io/v2/domain-search", timeout=25,
                  params={"domain": domain, "api_key": key, "limit": "50"})
    data = (d or {}).get("data", {})
    out = []
    for e in data.get("emails", []) or []:
        pos = e.get("position") or ""
        out.append(f"{e.get('value')}" + (f" ({pos})" if pos else ""))
    return out


def virustotal(kind, target):
    """kind: 'domains' | 'ip_addresses'."""
    key = api_key("virustotal")
    if not key:
        return []
    d = http_json(f"https://www.virustotal.com/api/v3/{kind}/{target}",
                  timeout=25, headers={"x-apikey": key})
    attr = (d or {}).get("data", {}).get("attributes", {})
    if not attr:
        return []
    stats = attr.get("last_analysis_stats", {}) or {}
    out = [f"detections: {stats.get('malicious',0)} malicious / "
           f"{stats.get('suspicious',0)} suspicious"]
    if attr.get("reputation") is not None:
        out.append(f"reputation: {attr['reputation']}")
    for c in (attr.get("categories") or {}).values():
        out.append(f"category: {c}")
    return out


def hibp(email):
    key = api_key("hibp")
    if not key:
        return []
    d = http_json(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                  timeout=25, params={"truncateResponse": "false"},
                  headers={"hibp-api-key": key, "User-Agent": "osint-recon"})
    if not d:
        return []
    return [f"{b.get('Name')} ({b.get('BreachDate')}): "
            f"{', '.join(b.get('DataClasses', [])[:5])}" for b in d]
