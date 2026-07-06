# 🕵️ OSINT Tools Catalog

קטלוג מלא של כל כלי, שירות ומקור ה-OSINT שנאספו לפרויקט זה.
מסומן ב-✅ מה שמותקן מקומית בסביבת ה-recon, וב-🔑 מה שדורש מפתח API.

> **מטרה:** מקור-אמת יחיד למקורות מודיעין גלוי (OSINT) לשימוש ע"י `recon.py` ולחקירה ידנית.
> שימוש חוקי בלבד — מחקר אבטחה מורשה, bug bounty, CTF, והגנה.

---

## 1. פלטפורמות, פריימוורקים ואוספים (Meta)

| שם | קישור | תיאור |
|---|---|---|
| OSINT Framework | https://osintframework.com · https://github.com/lockfale/OSINT-Framework | עץ קישורים ענק לכלי OSINT לפי קטגוריה |
| awesome-osint | https://github.com/jivoi/awesome-osint | הרשימה המרכזית של כלי OSINT בקוד פתוח |
| sinwindie/OSINT | https://github.com/sinwindie/OSINT | מתודולוגיה + כלים לפי סוג ישות (username/email/domain/…) |
| cipher387 collection | https://github.com/cipher387/osint_stuff_tool_collection | אוסף ענק של כלים ובוטים |
| PenTest-Wiki | https://github.com/nixawk/pentest-wiki | ויקי pentest/recon |
| IntelTechniques Tools | https://inteltechniques.com/tools/index.html | הכלים של Michael Bazzell |
| Bellingcat toolkit | https://www.bellingcat.com/resources/2022/08/12/these-are-the-tools-open-source-researchers-say-they-need/ | ארגז הכלים של Bellingcat |
| start.me — OSINT general | https://start.me/p/wMPmoA/osint-general | לוח קישורים |
| start.me — Ultimate OSINT | https://start.me/p/DPYPMz/the-ultimate-osint-collection | לוח קישורים מקיף |
| D4rk_Intel Toolkit | https://www.notion.so/D4rk_Intel-OSINT-Investigative-Toolkit-2c64a75bcfd6804c9d72fce730814e84 | ערכת חקירה ב-Notion |
| The OSINT Rack | https://www.mariosantella.com/the-osint-rack/ | אוסף כלים |
| Juan Mathews OSINT | https://osint.juanmathewsrebellosantos.com/ | פורטל OSINT |
| MDPI paper (JCP 4/3/27) | https://www.mdpi.com/2624-800X/4/3/27 | מאמר אקדמי על OSINT |
| OSINT Network events | https://osintnetwork.com/osint-events.html | אירועי קהילה |
| HuggingFace osint-llm | https://huggingface.co/spaces/tomvaillant/osint-llm | דמו LLM ל-OSINT |
| Trace Labs OSINT VM | https://github.com/tracelabs/tlosint-vm | מכונה וירטואלית מוכנה ל-OSINT |
| TheBigBrother | https://github.com/chadi0x/TheBigBrother | פריימוורק recon כולל |
| FoxyRecon | https://github.com/vincenzocaputo/FoxyRecon | תוסף דפדפן ל-recon |
| WorldMonitor | https://worldmonitor.app · https://github.com/koala73/worldmonitor | ניטור אירועים עולמי בזמן אמת |
| OSINT-BIBLE | https://github.com/frangelbarrera/OSINT-BIBLE | מתודולוגיה + "תנ"ך" טכניקות OSINT (משוכפל מקומית ב-`references/OSINT-BIBLE`) |
| OSINT-Books | https://github.com/ubikron/OSINT-Books | אוסף ספרי/מדריכי OSINT להעמקה |

---

## 2. Domain / DNS / Infrastructure (מותקן ברובו)

| שם | קישור | תיאור |
|---|---|---|
| ✅ theHarvester | https://github.com/laramies/theHarvester | אימיילים/סאבדומיינים/hosts ממקורות מרובים |
| ✅ Amass | https://github.com/owasp-amass/amass | מיפוי משטח תקיפה + אנומרציית סאבדומיינים |
| ✅ Subfinder | https://github.com/projectdiscovery/subfinder | אנומרציית סאבדומיינים פסיבית |
| ✅ recon-ng | https://github.com/lanmaster53/recon-ng | פריימוורק recon מודולרי |
| ✅ Photon | https://github.com/s0md3v/Photon | קרולר מהיר לחילוץ URLs/נתונים/קבצים |
| ✅ dnstwist | https://github.com/elceef/dnstwist | typosquatting / דומיינים דומים (phishing) |
| ✅ Spiderfoot | https://github.com/smicallef/spiderfoot | אוטומציית OSINT מלאה עם GUI |
| crt.sh | https://crt.sh | חיפוש certificate transparency (סאבדומיינים) |
| dnsdumpster | https://dnsdumpster.com | מיפוי DNS |
| CertStream | https://certstream.calidog.io | סטרים תעודות SSL בזמן אמת |
| PassiveTotal | https://passivetotal.org | 🔑 Passive DNS |
| BGPView | https://bgpview.io | מידע BGP/ASN/IP ranges |
| SpyOnWeb | https://spyonweb.com | קישור אתרים לפי Analytics/Adsense |
| IVRE | https://ivre.rocks | פריימוורק recon רשתי עצמאי |

---

## 3. Attack Surface / Host & Service Search (רובם 🔑 עם שכבה חינמית)

| שם | קישור | תיאור |
|---|---|---|
| Shodan | https://shodan.io | 🔑 שרתים, פורטים, חולשות. **InternetDB חינמי ללא מפתח** |
| Censys | https://censys.io | 🔑 חיפוש hosts/certs |
| BinaryEdge | https://binaryedge.io · https://app.binaryedge.io | 🔑 משטח תקיפה / threat intel |
| Onyphe | https://onyphe.io | 🔑 חיפוש שרתים |
| ZoomEye | https://zoomeye.org | 🔑 חיפוש מכשירים |
| FOFA | https://fofa.info | 🔑 חיפוש נכסי אינטרנט |
| Netlas | https://app.netlas.io | 🔑 משטח תקיפה |
| FullHunt | https://fullhunt.io | 🔑 ניהול משטח תקיפה |
| LeakIX | https://leakix.net | 🔑 שירותים חשופים / דליפות |
| GreyNoise | https://viz.greynoise.io | 🔑 סיווג רעש/סורקים (Community API חינמי) |
| Onyphe / Pulsedive | https://pulsedive.com | 🔑 threat intelligence |
| SOCRadar | https://socradar.io | threat intelligence |
| ThreatMiner | https://threatminer.org | threat intel data mining |
| ThreatCrowd | https://threatcrowd.org | גרף threat intel |

---

## 4. Email / Breach / Identity

| שם | קישור | תיאור |
|---|---|---|
| ✅ holehe | https://github.com/megadose/holehe | בדיקת קיום חשבון לפי אימייל (100+ אתרים) |
| ✅ socialscan | https://github.com/iojw/socialscan | זמינות username/email בפלטפורמות |
| Hunter.io | https://hunter.io | 🔑 מציאת אימיילים לפי דומיין |
| Have I Been Pwned | https://haveibeenpwned.com | 🔑 דליפות מידע |
| IntelX | https://intelx.io | 🔑 חיפוש בדליפות/דארקנט/paste |
| osgint | https://github.com/hippiiee/osgint | חשיפת מידע מחשבון GitHub (אימייל/שם) |
| checkleaked (WhatsApp) | https://whatsapp.checkleaked.cc | בדיקת דליפות סביב מספר |

---

## 5. Username / People / Social

| שם | קישור | תיאור |
|---|---|---|
| ✅ Sherlock | https://github.com/sherlock-project/sherlock | חיפוש username ב-400+ אתרים |
| ✅ Maigret | https://github.com/soxoj/maigret | כמו Sherlock + דוחות עשירים ואיסוף מידע |
| Snoop | https://github.com/snooppr/snoop | חיפוש username (רוסי, DB גדול) |
| WebSift | https://github.com/s-r-e-e-r-a-j/WebSift | חילוץ אימיילים/סושיאל מאתר |
| picdetective | https://picdetective.com | חיפוש תמונה/פנים הפוך |

### Instagram-specific
| שם | קישור | תיאור |
|---|---|---|
| ✅ Instaloader | https://github.com/instaloader/instaloader | הורדת פרופילים/פוסטים/מטא-דאטה מאינסטגרם |
| InstaLooter | https://github.com/althonos/InstaLooter | הורדת מדיה ללא API |
| instapy-cli | https://github.com/instapy-dev/instapy-cli | CLI לאינסטגרם |
| instagram-scraper | https://github.com/rarcega/instagram-scraper | סקרייפר Scrapy |
| InstagramOSINT | https://github.com/megadose/instagramosint | OSINT ממוקד אינסטגרם |

---

## 6. Telegram / Messaging OSINT

| שם | קישור | תיאור |
|---|---|---|
| Telepathy-Community | https://github.com/proseltd/Telepathy-Community | ניתוח צ'אטים/קבוצות טלגרם |
| Telegram-OSINT (0xSojalSec) | https://github.com/0xSojalSec/Telegram-OSINT | אוסף כלי טלגרם |
| Telegram-OSINT CTI | https://github.com/kienmarkdo/Telegram-OSINT-for-Cyber-Threat-Intelligence-Analysis | טלגרם ל-CTI |
| Hawker | https://github.com/RetrO-M/Hawker | OSINT לטלגרם |
| SaveAny-Bot | https://github.com/krau/SaveAny-Bot | שמירת מדיה מטלגרם |

---

## 7. Code / Files / Documents Search (מוקד הפרויקט 📄)

| שם | קישור | תיאור |
|---|---|---|
| Google Dorks | https://google.com | `filetype:` `site:` `intitle:` `inurl:` — מנוע מציאת קבצים מס' 1 |
| grep.app | https://grep.app | חיפוש קוד ב-GitHub הציבורי |
| searchcode | https://searchcode.com | חיפוש קוד רב-מקורי |
| publicwww | https://publicwww.com | חיפוש בקוד מקור של אתרים |
| Wayback Machine | https://archive.org · web.archive.org CDX API | קבצים/גרסאות היסטוריות של אתרים |
| grayhatwarfare (buckets) | https://grayhatwarfare.com | 🔑 קבצים חשופים ב-S3/buckets |

---

## 8. Malware / Vulnerabilities / Threat DB

| שם | קישור | תיאור |
|---|---|---|
| Vulners | https://vulners.com | 🔑 מסד חולשות |
| CVE MITRE | https://cve.mitre.org | מסד CVE רשמי |
| VulDB | https://vuldb.com | מסד חולשות |
| Hybrid Analysis | https://hybrid-analysis.com | 🔑 sandbox לניתוח נוזקות |
| MalShare | https://malshare.com | 🔑 מאגר נוזקות |
| urlscan.io | https://urlscan.io | סריקה/צילום של URLs |

---

## 9. Geo / Wireless / Misc

| שם | קישור | תיאור |
|---|---|---|
| WiGLE | https://wigle.net | 🔑 מיפוי רשתות Wi-Fi גלובלי |
| youtube-comments.io | https://youtube-comments.io | חיפוש/ייצוא תגובות יוטיוב |
| quiteaplaylist | https://quiteaplaylist.com | חיפוש פלייליסטים |
| osint.industries | https://app.osint.industries | 🔑 חיפוש חשבונות לפי אימייל/טלפון |
| intelligenceonchain | https://osint.intelligenceonchain.com | OSINT קריפטו/בלוקצ'יין |

---

## 10. Dark Web

| שם | קישור | תיאור |
|---|---|---|
| darkdump | https://github.com/josh0xA/darkdump | חיפוש בדארקנט (Ahmia) |
| Onion Search Engine | https://onionsearchengine.com | מנוע חיפוש .onion |

---

## Free-tier / No-key endpoints שמנוצלים אוטומטית ב-recon.py
מקורות שנבחרו גם מתוך **[public-apis](https://github.com/public-apis/public-apis)** (קטגוריות Security / Open Data):
- **crt.sh** — `https://crt.sh/?q=%25.DOMAIN&output=json` (סאבדומיינים)
- **Shodan InternetDB** — `https://internetdb.shodan.io/IP` (פורטים/חולשות, ללא מפתח)
- **RDAP** — `https://rdap.org/domain/DOMAIN` · `/ip/IP` (רישום/registrar/netblock, ללא מפתח)
- **Wayback** — CDX + availability API (`archive.org/wayback/available`)
- **HackerTarget** — `https://api.hackertarget.com/hostsearch/?q=DOMAIN`
- **GreyNoise Community** — `https://api.greynoise.io/v3/community/IP`
- **Gravatar** — `https://www.gravatar.com/HASH.json` (פרופיל לפי אימייל)
- **GitHub API** — `https://api.github.com/users/USER` (פרופיל ציבורי)
- **ip-api** — `http://ip-api.com/json/IP` (geo/ASN)
- **DuckDuckGo** — דרך `ddgs` (כל הדורקים)

## מקורות מבוססי-מפתח (🔑, אופציונלי ב-`config.yaml`)
Shodan (host מלא) · Hunter.io (אימיילים) · VirusTotal (מוניטין domain/IP) · HIBP (דליפות) ·
EmailRep (מוניטין אימייל) · abuse.ch URLhaus (URLs זדוניים) · GreyNoise · IntelX · Censys.
> כל אלה **מושבתים בשקט** ללא מפתח — הכלי עובד מלא רק עם המקורות החינמיים.
> הערה: EmailRep ו-abuse.ch/URLhaus הפכו לאחרונה לדרוש מפתח (בעבר היו חינמיים ללא auth).
