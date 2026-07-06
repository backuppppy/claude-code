"""IP recon: open ports, vulns, reverse DNS, geo, threat intel (free APIs)."""
from __future__ import annotations
import socket
from .utils import http_json, http_text, run_cmd, have, info
from . import apis


def _internetdb(ip):
    """Shodan InternetDB — free, no API key."""
    d = http_json(f"https://internetdb.shodan.io/{ip}")
    out = []
    if d:
        if d.get("ports"):
            out.append("Open ports: " + ", ".join(map(str, d["ports"])))
        if d.get("hostnames"):
            out.append("Hostnames: " + ", ".join(d["hostnames"]))
        if d.get("cpes"):
            out.append("CPEs: " + ", ".join(d["cpes"][:15]))
        for v in d.get("vulns", []) or []:
            out.append(f"VULN: {v}")
        for t in d.get("tags", []) or []:
            out.append(f"tag: {t}")
    return out


def _greynoise(ip):
    d = http_json(f"https://api.greynoise.io/v3/community/{ip}")
    if not d:
        return []
    return [f"{k}: {v}" for k, v in d.items()
            if k in ("classification", "name", "noise", "riot", "last_seen")]


def _geo(ip):
    d = http_json(f"http://ip-api.com/json/{ip}"
                  "?fields=country,regionName,city,isp,org,as,reverse")
    if not d or d.get("status") == "fail":
        return []
    return [f"{k}: {v}" for k, v in d.items() if v]


def _rdns(ip):
    try:
        return [f"PTR: {socket.gethostbyaddr(ip)[0]}"]
    except Exception:
        return []


def _whois(ip):
    if not have("whois"):
        return []
    ok, out = run_cmd(["whois", ip], timeout=30)
    keep = []
    for l in out.splitlines():
        if any(l.lower().startswith(k) for k in
               ("netname", "orgname", "descr", "country", "cidr", "inetnum")):
            keep.append(l.strip())
    return keep[:12]


def run(target, ttype, report):
    info("=== IP RECON ===")
    report.add("🛰️ Open ports & vulns (Shodan InternetDB)", _internetdb(target))
    report.add("🔦 Shodan full host (🔑)", apis.shodan_host(target))
    report.add("🌍 Geolocation / ASN", _geo(target))
    report.add("↩️ Reverse DNS", _rdns(target))
    report.add("🚦 GreyNoise (scanner classification)", _greynoise(target))
    report.add("📜 Netblock (RDAP)", apis.rdap_ip(target))
    report.add("🦠 Malware URLs (URLhaus 🔑)", apis.urlhaus_host(target))
    report.add("🛡️ Reputation (VirusTotal 🔑)", apis.virustotal("ip_addresses", target))
    report.add("📇 WHOIS / netblock", _whois(target))
