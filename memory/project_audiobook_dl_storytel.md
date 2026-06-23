---
name: project-audiobook-dl-storytel
description: שימוש ב-audiobook-dl להורדת ספרי שמע מסטוריטל
metadata: 
  node_type: memory
  type: project
  originSessionId: f0937fd7-3d3f-4d61-bf3d-0557733337bd
---

עובדים על הורדת ספרי שמע מ-**Storytel** באמצעות הכלי [audiobook-dl](https://github.com/jo1gi/audiobook-dl) (jo1gi, קוד פתוח, Python CLI).

- מותקן: גרסה **0.7.3** (זו הגרסה האחרונה ב-PyPI; ה-`1.7.1` שראינו בהתחלה היה גרסת pipx, לא הכלי), ב-`/root/.local/bin/audiobook-dl`. ffmpeg 7.1.1 מותקן.
- קונפיג ב-`~/.config/audiobook-dl/audiobook-dl.toml` עם `[sources.storytel]` — username/password, הרשאות 600.
- **המייל הנכון לסטוריטל: `9917099@gmail.com`** (שתי תשיעיות — זהה למייל הכללי בחשבון). בהתחלה נוסה `917099@gmail.com` בטעות והחזיר INVALID_CREDENTIALS. הסיסמה שמורה בקובץ הקונפיג בלבד. החשבון PREMIUM.
- שימוש: `cd ~/Downloads && audiobook-dl --combine --cover "<URL>"`. דורש URL של ספר ספציפי.
- אופציות שימושיות: `--combine` (קובץ mp3 אחד), `--cover`, `-o` (תבנית פלט), `-f` (פורמט), `--print-output` (בדיקה יבשה), `--debug`.

**הורדות שבוצעו:**
- "אדם רגיש מאוד" → הועבר ל-`/storage/emulated/0/Download/אדם רגיש מאוד.mp3` (306MB, 11h6m, 29 פרקים, עטיפה מוטמעת). הושלם 2026-06-22.
- "כראמל (10) הסוף" → `/storage/emulated/0/Download/Karamel_10_HaSof.mp3` (131MB, ~4h47m, פרקים+עטיפה מוטמעים). הושלם 2026-06-22.

**⚠️ תקלה ופתרון — תווים אסורים בשם:** כשהכותרת מכילה תו אסור ב-FAT/אנדרואיד (למשל `?` — הכותרת הגיעה כ-"כראמל (10) הסוף?"), `-o "{title}"` נכשל עם `PermissionError: Operation not permitted`. הפתרון: לקבוע שם פלט מפורש ונקי, למשל `-o "Karamel_10_HaSof"`.

**⚠️ באג ב-audiobook-dl — מוריד רק עטיפה, יוצא בלי שגיאה (2026-06-23):**
בספר "הרומן שלי עם בן גוריון ועם פנינה" (1263712), audiobook-dl 0.7.3 הוריד רק `cover.jpg` ויצא עם **exit 0** בלי להוריד אודיו ובלי שגיאה (הלוג נעצר ב-"Downloading ... from storytel"). זו **לא** בעיית קליטה — אבחנּו שזרם ה-MP3 עצמו זמין לחלוטין (status 200, `audio/mpeg`, 166MB, מתחיל ב-`ID3`). הבאג ב-`get_files` של ה-extractor שלא מושך את הזרם בפועל.

**הפתרון — הורדה ישירה מ-API של Storytel (עוקף את הכלי):**
1. התחברות: `GET https://www.storytel.com/api/login.action?m=1&uid=<user>&pwd=<AES_hex>` → מחזיר `accountInfo.jwt` + `accountInfo.singleSignToken`. הצפנת הסיסמה: AES-CBC, key=`VQZBJ6TD8M9WBUWT`, iv=`joiwef08u23j341a`, PKCS7, hex.
2. מדף: `GET https://www.storytel.com/api/getBookShelf.action?token=<singleSignToken>` (עם header `authorization: Bearer <jwt>`). **הספר חייב להיות במדף** אחרת `MissingBookAccess`.
3. מציאת הספר: לולאה על `books[]`, התאמה `book["book"]["consumableId"] == <id מה-URL>` (החלק האחרון אחרי `-`). משם לוקחים `book["book"]["AId"]` (program id).
4. אודיו: `GET https://www.storytel.com/mp3streamRangeReq?startposition=0&programId=<AId>&token=<singleSignToken>` → MP3 מלא (stream, iter_content).
5. מטא-דאטה: מחבר=`book["authors"][].name`, מקריא=`abook["narrators"][].name`. עטיפה: `https://www.storytel.com/images/<abook.isbn>/640x640/cover.jpg`.
6. תיוג: `ffmpeg -i raw.mp3 -i cover.jpg -map 0:a -map 1 -c copy -id3v2_version 3 -metadata title=.. -metadata artist=<author> -metadata composer=<narrator> out.mp3`.

הסקריפט המלא שמור בגיטהאב: `scripts/storytel_direct_download.py` בריפו [[project-claude-code-backup]] (קורא קרדנציאלס מהקונפיג, ללא סודות בקוד). "הרומן שלי עם בן גוריון ועם פנינה" הורד כך (167MB, ~6h3m) והועבר ל-`/storage/emulated/0/Download/`.

**טיפים לדיבוג:** ה-API `https://www.storytel.com/api/login.action` עובד ומחזיר JSON עם `loginStatusEnum` (PREMIUM / INVALID_CREDENTIALS). אפשר לבדוק התחברות ידנית מתוך ה-venv (`/root/.local/share/pipx/venvs/audiobook-dl/bin/python`) שיש בו pycryptodome. הסיסמה מוצפנת AES-CBC עם מפתחות קבועים בקוד.

קשור ל-[[feedback_save_everything]], [[project-claude-code-backup]].
