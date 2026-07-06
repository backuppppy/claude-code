#!/usr/bin/env python3
"""
osint-recon — one entrypoint, deep OSINT.

Give it anything: a domain, username, email, phone, IP, or a person's name.
It auto-detects the target type, runs every relevant module, and ALWAYS runs a
heavy file/document hunt. Output: a Markdown + JSON report under ./output/.

Usage:
    python recon.py <target> [--type auto|domain|username|email|phone|ip|person]
                             [-o OUTDIR] [--no-files] [--quiet]

Examples:
    python recon.py example.com
    python recon.py johnsmith
    python recon.py john@example.com
    python recon.py "+972501234567"
    python recon.py 8.8.8.8
    python recon.py "John Smith"
    python recon.py --type file "annual report 2023" --ext pdf   # filename hunt

Authorized OSINT / security research only.
"""
from __future__ import annotations
import sys, re, argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from modules.utils import Report, head, info, good, warn, err, now_stamp
from modules import (domain, username, email as email_mod, phone, ip, person,
                     filesearch, filenamesearch)

BANNER = r"""
   ____  _____ _____ _   _ _____   ____  _____ ____ ___  _   _
  / __ \/ ___//  _// | / //_  _/  / __ \/ ___// __// __ \/ | / /
 / /_/ /\__ \ / / /  |/ /  / /   / /_/ /\__ \/ /_ / / / /  |/ /
 \____//____/___//_/|_/  /_/    \_,_//____/\__//_/ /_/|_/|_/
        deep open-source intelligence  ·  authorized use only
"""

DISPATCH = {
    "domain":   domain.run,
    "username": username.run,
    "email":    email_mod.run,
    "phone":    phone.run,
    "ip":       ip.run,
    "person":   person.run,
}


def detect_type(t: str) -> str:
    t = t.strip()
    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", t):
        return "email"
    if re.fullmatch(r"(\d{1,3}\.){3}\d{1,3}", t):
        return "ip"
    if ":" in t and re.fullmatch(r"[0-9A-Fa-f:]+", t):
        return "ip"
    if re.fullmatch(r"([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}", t):
        return "domain"
    if re.fullmatch(r"\+?[\d][\d\s\-().]{6,}\d", t):
        return "phone"
    if " " in t:
        return "person"
    return "username"


def main():
    ap = argparse.ArgumentParser(description="Deep OSINT recon tool")
    ap.add_argument("target", help="domain / username / email / phone / ip / name")
    ap.add_argument("--type", default="auto",
                    choices=["auto", "domain", "username", "email", "phone",
                             "ip", "person", "file"])
    ap.add_argument("--ext", default="pdf",
                    help="file extension for --type file (default: pdf)")
    ap.add_argument("-o", "--outdir", default=None, help="output directory")
    ap.add_argument("--no-files", action="store_true",
                    help="skip the heavy file/document hunt")
    args = ap.parse_args()

    ttype = detect_type(args.target) if args.type == "auto" else args.type

    print(BANNER)
    head(f"TARGET: {args.target}   |   TYPE: {ttype}")

    outdir = Path(args.outdir) if args.outdir else \
        HERE / "output" / f"{re.sub(r'[^A-Za-z0-9._-]', '_', args.target)}_{now_stamp()}"
    report = Report(args.target, ttype, outdir)

    if ttype == "file":
        # dedicated multi-layer filename hunt
        try:
            filenamesearch.run(args.target, args.ext, report)
        except Exception as e:
            err(f"filename hunt crashed: {e}")
    else:
        # 1) type-specific module
        try:
            DISPATCH[ttype](args.target, ttype, report)
        except Exception as e:
            err(f"module '{ttype}' crashed: {e}")

        # 2) heavy file/document hunt (the priority) — runs for every type
        if not args.no_files:
            try:
                filesearch.run(args.target, ttype, report)
            except Exception as e:
                err(f"file hunt crashed: {e}")

    md, js = report.save()
    total = sum(len(l) for _, l in report.sections)
    head(f"DONE — {total} findings")
    good(f"Markdown report: {md}")
    good(f"JSON report:     {js}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] interrupted")
        sys.exit(1)
