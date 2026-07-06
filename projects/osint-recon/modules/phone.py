"""Phone recon: format variants, mentions, account checks."""
from __future__ import annotations
import re
from .utils import ddg, info


def _variants(num):
    digits = re.sub(r"\D", "", num)
    v = {num, digits, "+" + digits}
    if len(digits) >= 9:
        v.add(f"{digits[:3]}-{digits[3:6]}-{digits[6:]}")
        v.add(f"({digits[:3]}) {digits[3:6]}-{digits[6:]}")
        v.add(f"{digits[:3]} {digits[3:]}")
    # local IL form (drop 972, add leading 0)
    if digits.startswith("972"):
        v.add("0" + digits[3:])
    return sorted(v)


def run(target, ttype, report):
    info("=== PHONE RECON ===")
    variants = _variants(target)
    report.add("🔢 Number formats searched", variants)

    dorks = []
    for vv in variants[:6]:
        for q in (f'"{vv}"',
                  f'"{vv}" (site:facebook.com OR site:linkedin.com OR site:whocalledme.com OR site:truecaller.com)'):
            for r in ddg(q, max_results=6):
                dorks.append(f"[{r.get('title','')[:60]}]({r.get('href')})")
    # dedup
    report.add("🔎 Phone mentions (dorks)", sorted(set(dorks)))

    d = re.sub(r"\D", "", target)
    report.add("🧰 Manual lookups",
               [f"https://www.truecaller.com/search/il/{d}",
                f"https://app.osint.industries (phone: {target})",
                f"https://whatsapp.checkleaked.cc (WhatsApp: {target})"])
