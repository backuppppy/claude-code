#!/usr/bin/env python3
"""Generate synthetic email addresses for testing or demo data.

This script only generates syntactically valid email addresses.
It does not create real mailboxes.
"""

from __future__ import annotations

import argparse
import json
import random
import re
from dataclasses import dataclass
from typing import Iterable, List


DEFAULT_DOMAINS = [
    "example.com",
    "example.org",
    "example.net",
    "mailinator.com",
]

FIRST_NAMES = [
    "alex",
    "anya",
    "ben",
    "dana",
    "eli",
    "iris",
    "lev",
    "maya",
    "noam",
    "tamar",
]

LAST_NAMES = [
    "cohen",
    "levi",
    "mizrahi",
    "peretz",
    "rosen",
    "shapiro",
    "tal",
    "weiss",
    "yaron",
    "ziv",
]

ADJECTIVES = [
    "bright",
    "calm",
    "clever",
    "fuzzy",
    "lucky",
    "mellow",
    "quiet",
    "swift",
    "tidy",
    "witty",
]

NOUNS = [
    "anchor",
    "beacon",
    "cinder",
    "drift",
    "ember",
    "harbor",
    "meteor",
    "pulse",
    "signal",
    "spark",
]

EMAIL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9._+-]{0,62}[a-z0-9])?@[a-z0-9.-]+\.[a-z]{2,}$")


@dataclass(frozen=True)
class GeneratedEmail:
    address: str
    pattern: str


def normalize_domain(domain: str) -> str:
    domain = domain.strip().lower()
    if not domain:
        raise ValueError("domain cannot be empty")
    if "@" in domain:
        raise ValueError(f"domain should not include '@': {domain}")
    return domain


def make_local_part(rng: random.Random) -> tuple[str, str]:
    pattern = rng.choice(
        [
            "first.last",
            "firstlast",
            "adj.noun",
            "noun.number",
            "first.number",
        ]
    )

    first = rng.choice(FIRST_NAMES)
    last = rng.choice(LAST_NAMES)
    adj = rng.choice(ADJECTIVES)
    noun = rng.choice(NOUNS)
    digits = f"{rng.randint(10, 9999)}"

    if pattern == "first.last":
        local = f"{first}.{last}"
    elif pattern == "firstlast":
        local = f"{first}{last}"
    elif pattern == "adj.noun":
        local = f"{adj}.{noun}"
    elif pattern == "noun.number":
        local = f"{noun}{digits}"
    else:
        local = f"{first}{digits}"

    if rng.random() < 0.35:
        local = f"{local}{rng.randint(1, 99)}"

    local = local.lower()
    local = re.sub(r"[^a-z0-9._+-]", "", local)
    local = local.strip(".")
    return local, pattern


def generate_emails(count: int, domains: List[str], rng: random.Random) -> List[GeneratedEmail]:
    results: List[GeneratedEmail] = []
    seen: set[str] = set()

    while len(results) < count:
        local, pattern = make_local_part(rng)
        domain = rng.choice(domains)
        address = f"{local}@{domain}"
        if address in seen:
            continue
        if not EMAIL_RE.match(address):
            continue
        seen.add(address)
        results.append(GeneratedEmail(address=address, pattern=pattern))

    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic email addresses.")
    parser.add_argument("-n", "--count", type=int, default=10, help="Number of addresses to generate.")
    parser.add_argument(
        "-d",
        "--domain",
        action="append",
        dest="domains",
        help="Domain to use. Can be passed multiple times. Defaults to a small safe list.",
    )
    parser.add_argument("--seed", type=int, default=None, help="Seed for reproducible output.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of plain text.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.count < 1:
        raise SystemExit("--count must be at least 1")

    domains = [normalize_domain(d) for d in (args.domains or DEFAULT_DOMAINS)]
    rng = random.Random(args.seed)
    emails = generate_emails(args.count, domains, rng)

    if args.json:
        print(
            json.dumps(
                [{"email": item.address, "pattern": item.pattern} for item in emails],
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for item in emails:
            print(item.address)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
