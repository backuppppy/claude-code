"""Person / full-name recon: social, professional, docs, images."""
from __future__ import annotations
from .utils import ddg, info


def run(target, ttype, report):
    info("=== PERSON RECON ===")
    q = f'"{target}"'

    social = []
    for query in (f'{q} (site:linkedin.com OR site:facebook.com OR site:instagram.com OR site:twitter.com OR site:x.com)',
                  f'{q} (site:tiktok.com OR site:youtube.com OR site:reddit.com OR site:medium.com)'):
        for r in ddg(query, max_results=10):
            social.append(f"[{r.get('title','')[:60]}]({r.get('href')})")
    report.add("👥 Social / professional profiles", social)

    prof = []
    for query in (f'{q} (site:github.com OR site:gitlab.com OR site:stackoverflow.com)',
                  f'{q} (email OR "@gmail.com" OR "@outlook.com" OR contact)'):
        for r in ddg(query, max_results=8):
            prof.append(f"[{r.get('title','')[:60]}]({r.get('href')})")
    report.add("💼 Professional / contact", prof)

    news = []
    for r in ddg(f'{q} (news OR interview OR profile OR biography)', max_results=8):
        news.append(f"[{r.get('title','')[:60]}]({r.get('href')})")
    report.add("📰 News & mentions", news)

    report.add("🖼️ Manual image / face lookups",
               ["https://picdetective.com",
                f"https://www.google.com/search?q={target.replace(' ','+')}&tbm=isch",
                "https://pimeyes.com"])
