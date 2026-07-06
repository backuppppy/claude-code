# claude-code — גיבוי סביבת העבודה והפרויקטים

גיבוי מלא של כל מה שעבדנו עליו בסביבת **Claude Code** (Ubuntu בתוך Termux על אנדרואיד).
המטרה: אם נחזור לכאן בעוד חודש או שנה — נדע **בדיוק** מה עשינו, איפה כל דבר, ואיך לשחזר ולהמשיך.

> 📌 **התיעוד המלא והעדכני ביותר נמצא בתיקיית [`memory/`](memory/)** — כל פרויקט עם קובץ זיכרון משלו (היסטוריה, תקלות, פתרונות). ה-README הזה הוא מפת-על.

> 🔐 **סודות וטוקנים לא נשמרים בקוד הזה** — הם מאוחסנים ב-**GitHub Secrets** של הריפו. ראו [סעיף הסודות](#-סודות-וטוקנים-github-secrets) לרשימה ולשחזור.

---

## מבנה הריפו

```
claude-code/
├── README.md                  ← הקובץ הזה (מפת-על)
├── memory/                    ← קבצי הזיכרון המלאים (המקור האמיתי לכל פרט)
├── projects/                  ← קוד המקור של כל הפרויקטים
│   ├── tg-backup-apk/         ← אפליקציית גיבוי טלגרם (APK) — הפרויקט המרכזי
│   ├── tg_apk/                ← גרסה/ניסוי מוקדם של אותו פרויקט
│   ├── wa-counter/            ← ספירת קבוצות וואטסאפ
│   ├── web/                   ← סריקת אתר "הורים מחוברים" (conectedmmb)
│   ├── fxp_bot/               ← בוט טלגרם לניטור FXP
│   ├── font_maker/            ← יצירת פונט
│   └── G0DM0D3-changes/       ← רק ה-diff שלנו ל-fork של elder-plinius/G0DM0D3
├── scripts/                   ← סקריפטים עצמאיים
│   ├── book/                  ← בניית הספר מקובץ הכתיבה הענק (EPUB/PDF)
│   ├── godmod3_proxy.py       ← proxy ל-OpenRouter
│   ├── email_generator.py, fb_to_md.py, youtube_public_probe.py ...
│   └── build_runner*.sh       ← סקריפטי בנייה
├── config-templates/          ← תבניות קונפיג עם placeholders (הערכים האמיתיים ב-Secrets)
└── .github/workflows/
    └── restore-secrets.yml    ← הרצה ידנית שמשחזרת את הסודות לקבצים (artifact)
```

---

## הפרויקטים — סקירה

### 1. TG Backup APK — `projects/tg-backup-apk/` (הפרויקט המרכזי)
אפליקציית אנדרואיד (APK) לגיבוי טלגרם. מחסנית: **Kivy + Flask + Telethon**.
- גרסה **v1.3** + אינטגרציית **Sentry** לניטור שגיאות.
- גשר Sentry→Telegram דרך **GitHub Actions** (polling, **ללא טוקנים בקוד**).
- ריפו ייעודי קיים: `backuppppy/tg-backup-apk` (public). כאן שמור עותק המקור.
- Sentry: ארגון `bubababa`, פרויקט `python-5n` (python-flask). ה-DSN ציבורי-בעצם-טבעו ולכן נשאר ב-`server.py`.
- 📖 פרטים מלאים: [`memory/project_tg_backup_apk.md`](memory/project_tg_backup_apk.md)
- 💡 חלופה מוכנה ל-self-host (Go): [SaveAny-Bot](https://github.com/krau/SaveAny-Bot) — בוט טלגרם לגיבוי כל קובץ ליעדי אחסון שונים. (ראו [#1](https://github.com/backuppppy/claude-code/issues/1))

### 2. WhatsApp Groups Counter — `projects/wa-counter/`
ניסיון לספור קבוצות וואטסאפ דרך סקריפט. **לא הושלם** — נחסם על שלב ה-QR.
נתון שעלה: 110 שיחות פעילות + 280 בארכיון.
- 📖 [`memory/project_whatsapp_groups.md`](memory/project_whatsapp_groups.md)

### 3. אתר "הורים מחוברים" (conectedmmb) — `projects/web/`
סריקת אתר בנוי Lovable/React/Supabase. סרקנו את דף `/aut` והסברנו איך להוריד את ה-JS bundle.
- 📖 [`memory/project_conectedmmb.md`](memory/project_conectedmmb.md)

### 4. FXP Bot — `projects/fxp_bot/`
בוט טלגרם לניטור FXP. קונפיג ב-`.env` (טוקן ב-Secrets, ראו `config-templates/fxp_bot.env.example`).

### 5. G0DM0D3 — `projects/G0DM0D3-changes/`
fork של `elder-plinius/G0DM0D3`. שמרנו **רק את ה-diff שלנו** (שינויים ב-`api/routes/research.ts` ו-`api/server.ts`) ולא את כל הקוד של upstream.
שחזור: `git clone https://github.com/elder-plinius/G0DM0D3 && cd G0DM0D3 && git apply ../our-changes.diff`

### 6. font_maker — `projects/font_maker/`
כלי ליצירת פונט.

---

## סקריפטים עצמאיים — `scripts/`

### הפיכת קובץ כתיבה ענק לספר — `scripts/book/`
הפכנו קובץ כתיבה של שנים (`all_posts.txt`, ~6MB, לא בריפו) לספר מאורגן לפי נושאים.
- `build_epub.py`, `build_sefer.py` → ייצור EPUB (`sefer_bezalel.epub`).
- `book_to_pdf.py`, `md_to_pdf_pango.py`, `pdf_to_markdown.py` → המרות PDF/Markdown.
- 📖 [`memory/project_book_from_file.md`](memory/project_book_from_file.md)

### תרגום *Dopamine Nation* לעברית (הושלם ✅)
התוצר: `Dopamine_Nation_Hebrew.epub` (5.3MB) ב-`/storage/emulated/0/Download/`.
- 📖 [`memory/project_dopamine_epub.md`](memory/project_dopamine_epub.md)

### `godmod3_proxy.py`
Proxy ל-OpenRouter. מפתח ב-`~/.config/godmod3.env` (ראו `config-templates/godmod3.env.example`; הערך ב-Secrets).

### אחרים
`email_generator.py`, `fb_to_md.py` (פייסבוק→Markdown), `youtube_public_probe.py`, `build_runner.sh`, `build_runner2.sh`.

---

## כלים מותקנים בסביבה (לא קוד שלנו, רק לתיעוד)

- **audiobook-dl** (0.7.3) + ffmpeg — הורדת ספרי שמע מ-**Storytel**. קונפיג: `config-templates/audiobook-dl.toml.example`. חשבון PREMIUM, מייל `9917099@gmail.com`. 📖 [`memory/project_audiobook_dl_storytel.md`](memory/project_audiobook_dl_storytel.md)
  - ⚠️ **באג ידוע:** audiobook-dl 0.7.3 לפעמים מוריד רק את העטיפה ויוצא exit 0 בלי האודיו (לא בעיית קליטה — הזרם זמין). **פתרון:** `scripts/storytel_direct_download.py` — מוריד ישירות מ-API של Storytel (login → bookshelf → `mp3streamRangeReq`) ומטמיע עטיפה+מטא-דאטה. דרישה: הספר חייב להיות ב-Bookshelf. שימוש: `python3 scripts/storytel_direct_download.py "<URL>" [שם_פלט]`.
- **Suno API** — `gcui-art/suno-api` (Cookie-based). 📖 [`memory/project_suno_api.md`](memory/project_suno_api.md)
- **25 Skills** מותקנים מ-skills.sh (בסיס + חבילת סייבר/סריקה/תכנות). 📖 [`memory/project_skills_sh_install.md`](memory/project_skills_sh_install.md)
- **subfinder** — קונפיג ספקים ב-`config-templates/subfinder-provider-config.yaml` (ריק, ללא מפתחות).
- `zeroclaw` (binary ~29MB) — לא נכלל בגיבוי בשל גודלו.

---

## 🔐 סודות וטוקנים (GitHub Secrets)

הערכים הרגישים אוחסנו כ-**Repository Secrets** של הריפו (מוצפנים). מיפוי:

| Secret | מקור מקורי | שימוש |
|--------|------------|-------|
| `GH_TOKEN` | `~/.gh_token` | טוקן GitHub (PAT) |
| `OPENROUTER_API_KEY` | `~/.config/godmod3.env` | godmod3 / OpenRouter |
| `FXP_TELEGRAM_TOKEN` | `fxp_bot/.env` | בוט טלגרם FXP |
| `FXP_TELEGRAM_CHAT_ID` | `fxp_bot/.env` | chat id של הבוט |
| `STORYTEL_USERNAME` | `~/.config/audiobook-dl/audiobook-dl.toml` | התחברות סטוריטל |
| `STORYTEL_PASSWORD` | אותו קובץ | סיסמת סטוריטל |
| `CLAUDE_JSON_B64` | `~/.claude.json` (base64) | קונפיג Claude Code המלא |
| `GITCONFIG_B64` | `~/.gitconfig` (base64) | הגדרות git |

### שחזור הסודות בעוד שנה
ב-GitHub Secrets לא ניתן **לקרוא** ערך חזרה ישירות (write-only). לכן יש workflow ייעודי:

1. בריפו ב-GitHub → טאב **Actions** → **Restore secrets to files** → **Run workflow**.
2. בסיום, הורידו את ה-**artifact** `restored-secrets` — הוא מכיל את כל הקבצים הרגישים משוחזרים.
3. פזרו אותם למקומותיהם:
   ```bash
   cp restored/.gh_token ~/.gh_token
   cp restored/godmod3.env ~/.config/godmod3.env
   cp restored/audiobook-dl.toml ~/.config/audiobook-dl/audiobook-dl.toml
   cp restored/fxp.env fxp_bot/.env
   base64 -d restored/claude.json.b64 > ~/.claude.json
   base64 -d restored/gitconfig.b64 > ~/.gitconfig
   ```

---

## שחזור מלא של הסביבה — צ'ק-ליסט

1. `git clone https://github.com/backuppppy/claude-code`
2. הריצו את workflow השחזור (לעיל) והחזירו את הסודות.
3. התקנות סביבה: `pip install`/`npm install` בכל פרויקט לפי הצורך; `audiobook-dl`, `ffmpeg`, `subfinder` לפי הזיכרון.
4. קראו את `memory/` להקשר המלא של כל משימה.

---

*נוצר אוטומטית כגיבוי סביבת Claude Code · עודכן לאחרונה: 2026-06-23*
