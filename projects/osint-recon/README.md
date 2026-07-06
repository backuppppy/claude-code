# 🕵️ osint-recon

כלי OSINT חזק בפקודה אחת. נותנים לו **מטרה** — דומיין, שם משתמש, אימייל, טלפון, IP או שם אדם —
הוא **מזהה אוטומטית** את הסוג, מפעיל את כל המודולים הרלוונטיים, ו**תמיד** מריץ חיפוש קבצים/מסמכים
עמוק. התוצאה: דוח Markdown + JSON בתיקיית `output/`.

> ⚖️ לשימוש חוקי בלבד — מחקר אבטחה מורשה, bug bounty, CTF, והגנה.
> קטלוג כל המקורות: [`docs/OSINT_TOOLS_CATALOG.md`](docs/OSINT_TOOLS_CATALOG.md)

## הרצה
```bash
cd projects/osint-recon
./osint example.com                 # דומיין
./osint johnsmith                   # שם משתמש
./osint john@example.com            # אימייל
./osint "+972501234567"             # טלפון
./osint 8.8.8.8                     # IP
./osint "Israel Israeli"            # שם אדם
./osint --type file "annual report 2023" --ext pdf   # 🔎 חיפוש קובץ ייעודי (5 שכבות)
```
או ישירות: `.venv/bin/python recon.py <target>`

אפשרויות: `--type <סוג>` לכפות סוג (כולל `file`) · `--ext` סיומת לחיפוש קובץ · `-o DIR` לפלט · `--no-files` לדלג על חיפוש הקבצים.

### מצב חיפוש-קובץ (`--type file`)
5 שכבות (פורט מורחב מהסקריפט המקורי): (1) `filetype:` ישיר · (2) וריאציות שם (רווח/`_`/`-`) ·
(3) ספריות פתוחות `index of` · (4) שם מדויק רחב + שיתופי ענן (Drive/Dropbox/Mega/Scribd) ·
(5) עותקי Wayback מאומתים של הקבצים שנמצאו.

## מה זה מריץ לפי סוג
| סוג | מקורות |
|---|---|
| **domain** | crt.sh · subfinder · amass · hackertarget · theHarvester · DNS · dnstwist · דורקים |
| **username** | Sherlock · Maigret · socialscan · דורקים סושיאל |
| **email** | holehe · socialscan · דורקים · לינקים ל-HIBP/IntelX |
| **phone** | וריאציות פורמט · דורקים · Truecaller/OSINT.industries |
| **ip** | Shodan InternetDB (חינם) · GreyNoise · geo/ASN · reverse DNS · WHOIS |
| **person** | פרופילים סושיאל/מקצועי · חדשות · חיפוש תמונה |
| **כל סוג** | 📄 **חיפוש קבצים עמוק**: דורקי filetype, ספריות פתוחות, Wayback, grep.app |

## התקנה (כבר בוצעה בסביבה הזו)
Python venv עם `requests dnspython ddgs rich pyyaml`, וכלי CLI חיצוניים
(`theHarvester amass subfinder sherlock maigret holehe socialscan dnstwist`)
מותקנים דרך pipx/go. מפתחות API אופציונליים ב-`config.yaml` (ראה `config.example.yaml`).

## מבנה
```
recon.py               # entrypoint + זיהוי סוג
osint                  # launcher (venv)
modules/
  utils.py             # HTTP, subprocess, דורקים, דוח
  filesearch.py        # 📄 חיפוש קבצים/מסמכים עמוק (רץ לכל סוג)
  filenamesearch.py    # 🔎 מצב חיפוש-קובץ ייעודי (5 שכבות)
  domain.py username.py email.py phone.py ip.py person.py
docs/OSINT_TOOLS_CATALOG.md   # קטלוג כל הכלים
references/OSINT-BIBLE/       # מתודולוגיית OSINT (rev משוכפל)
```
