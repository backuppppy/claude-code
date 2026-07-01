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

**🔎 חיפוש ספרים בסטוריטל (נוסף 2026-06-26):** audiobook-dl עצמו לא תומך בחיפוש (דורש URL). אבל ל-Storytel יש **API חיפוש ציבורי שלא דורש התחברות**:
`GET https://www.storytel.com/api/search.action?request_locale=he&q=<query>` → JSON עם `books[]`. לכל ספר: `book.name`, `book.authors[].name`, `book.consumableId` (ה-id להורדה), `abook.narrators[].name`, וקיום `abook`/`ebook` לפי פורמט. סקריפט מוכן: `scripts/storytel_search.py` בריפו [[project-claude-code-backup]] — `python3 storytel_search.py "<שם>" [--limit N] [--locale he]`. ה-`id` מהפלט מוזן ל-`storytel_direct_download.py`.

**הורדות שבוצעו:**
- "אדם רגיש מאוד" → הועבר ל-`/storage/emulated/0/Download/אדם רגיש מאוד.mp3` (306MB, 11h6m, 29 פרקים, עטיפה מוטמעת). הושלם 2026-06-22.
- "כראמל (10) הסוף" → `/storage/emulated/0/Download/Karamel_10_HaSof.mp3` (131MB, ~4h47m, פרקים+עטיפה מוטמעים). הושלם 2026-06-22.
- "מחלק העיתונים" (1328946, וינס וואטר, מקריא זיו זוהר מאיר) → `/storage/emulated/0/Download/מחלק העיתונים.mp3` (158MB, ~5h30m, מטא-דאטה מוטמע). הושלם 2026-06-26.

**⚠️ תקלה ופתרון — תווים אסורים בשם:** כשהכותרת מכילה תו אסור ב-FAT/אנדרואיד (למשל `?` — הכותרת הגיעה כ-"כראמל (10) הסוף?"), `-o "{title}"` נכשל עם `PermissionError: Operation not permitted`. הפתרון: לקבוע שם פלט מפורש ונקי, למשל `-o "Karamel_10_HaSof"`.

**⚠️ באג ב-audiobook-dl — מוריד רק עטיפה, יוצא בלי שגיאה (2026-06-23):**
בספר "הרומן שלי עם בן גוריון ועם פנינה" (1263712), audiobook-dl 0.7.3 הוריד רק `cover.jpg` ויצא עם **exit 0** בלי להוריד אודיו ובלי שגיאה (הלוג נעצר ב-"Downloading ... from storytel"). זו **לא** בעיית קליטה — אבחנּו שזרם ה-MP3 עצמו זמין לחלוטין (status 200, `audio/mpeg`, 166MB, מתחיל ב-`ID3`). הבאג ב-`get_files` של ה-extractor שלא מושך את הזרם בפועל.

**הפתרון — הורדה ישירה מ-API של Storytel (עוקף את הכלי):**
1. התחברות: `GET https://www.storytel.com/api/login.action?m=1&uid=<user>&pwd=<AES_hex>` → מחזיר `accountInfo.jwt` + `accountInfo.singleSignToken`. הצפנת הסיסמה: AES-CBC, key=`VQZBJ6TD8M9WBUWT`, iv=`joiwef08u23j341a`, PKCS7, hex.
2. מדף: `GET https://www.storytel.com/api/getBookShelf.action?token=<singleSignToken>` (עם header `authorization: Bearer <jwt>`). ~~הספר חייב להיות במדף~~ → **כבר לא נכון, ראה סעיף "עקיפת המדף" למטה** (2026-07-01).
3. מציאת הספר: לולאה על `books[]`, התאמה `book["book"]["consumableId"] == <id מה-URL>` (החלק האחרון אחרי `-`). משם לוקחים `book["book"]["AId"]` (program id).
4. אודיו: `GET https://www.storytel.com/mp3streamRangeReq?startposition=0&programId=<AId>&token=<singleSignToken>` → MP3 מלא (stream, iter_content).
5. מטא-דאטה: מחבר=`book["authors"][].name`, מקריא=`abook["narrators"][].name`. עטיפה: `https://www.storytel.com/images/<abook.isbn>/640x640/cover.jpg`.
6. תיוג: `ffmpeg -i raw.mp3 -i cover.jpg -map 0:a -map 1 -c copy -id3v2_version 3 -metadata title=.. -metadata artist=<author> -metadata composer=<narrator> out.mp3`.

הסקריפט המלא שמור בגיטהאב: `scripts/storytel_direct_download.py` בריפו [[project-claude-code-backup]] (קורא קרדנציאלס מהקונפיג, ללא סודות בקוד). "הרומן שלי עם בן גוריון ועם פנינה" הורד כך (167MB, ~6h3m) והועבר ל-`/storage/emulated/0/Download/`.

**טיפים לדיבוג:** ה-API `https://www.storytel.com/api/login.action` עובד ומחזיר JSON עם `loginStatusEnum` (PREMIUM / INVALID_CREDENTIALS). אפשר לבדוק התחברות ידנית מתוך ה-venv (`/root/.local/share/pipx/venvs/audiobook-dl/bin/python`) שיש בו pycryptodome. הסיסמה מוצפנת AES-CBC עם מפתחות קבועים בקוד.

**✅ עקיפת המדף — הורדה בלי להוסיף למדף (2026-07-01):** ה-extractor המקורי של audiobook-dl (`.../audiobookdl/sources/storytel.py`) *דרש* שהספר יהיה במדף: `download()` מושך את כל המדף ומחפש בו, ואם הספר לא שם → `MissingBookAccess`. זו הייתה כל הסיבה למאבק ב"הוספה למדף". **התגלה endpoint שנותן את אותה רשומה בדיוק בלי המדף:**
`GET https://www.storytel.com/api/getBookInfoForContent.action?bookId=<book.id>&token=<sst>` → מחזיר `slb` שהוא **מבנה זהה לרשומת מדף** (`book`, `abook`, `owns`, `restriction`...) כולל `book.AId`, `book.consumableId`, `abook.isbn`, מחברים/מקריאים. עובד גם על ספרים שאינם במדף (`owns=0`).
- שים לב: ה-endpoint ממופתח ב-**book.id** (למשל 10517918), *לא* ב-consumableId (13457186). המרה מ-consumableId ל-book.id: `GET https://api.storytel.net/book-details/consumables/<cid>` → שדה `bookId`. (playback-metadata של הצ'אפטרים ממופתח דווקא ב-consumableId.)
- endpoint לצ'אפטרים (ללא מדף): `GET https://api.storytel.net/playback-metadata/consumable/<consumableId>` → `formats[abook].chapters`.
- **הפאץ' יושם** ב-storytel.py: `download()` קורא ל-`get_book_info(book_id)` חדש במקום `download_bookshelf`+`find_book_info`. נוספו `get_book_info` / `_get_slb` / `_consumable_to_bookid` (מנסה קודם כ-bookId, ואם אין → ממיר מ-consumableId). מטפל גם ב-URL שמסתיים ב-book.id וגם ב-consumableId. גיבוי מקורי: `storytel.py.orig` באותה תיקייה. נבדק end-to-end דרך המחלקות האמיתיות (stream 206 audio/mpeg, 46 פרקים, מטא-דאטה מלא) גם על ספר שלא במדף.
- **נדחף לגיטהאב (2026-07-01):** הפאץ' שמור בריפו הגיבוי [[project-claude-code-backup]] תחת `scripts/audiobook-dl-patch/` — הקובץ המתוקן המלא `storytel.py`, diff אחיד `storytel-shelf-bypass.patch`, ו-`README.md` עם הסבר והוראות התקנה. commit `5265f67`.
- **בדיקת שטח — הורדת ספר שלא במדף (2026-07-01):** נבחר "התפכחות" מאת דן מרגלית (consumableId `1373088`, לא במדף, `owns=0`). audiobook-dl המתוקן זיהה ואימת אותו בלי מדף (`1373088`→bookId `2615107`→AId `2615109`), אבל **נתקל בבאג `get_files`** (exit 0 בלי אודיו). לכן ההורדה בפועל בוצעה דרך המסלול הישיר (endpoint עוקף + `mp3streamRangeReq` + ffmpeg). **מסקנה 1:** עקיפת המדף מזהה/מאמתת ספרים מחוץ למדף, אבל להורדת הקובץ לספרים שנתקלים בבאג צריך את המסלול הישיר. **מסקנה 2 חשובה:** גם עם `owns=0` הזרם `mp3streamRangeReq` מחזיר את **הספר המלא** (לא רק דגימה) — כאן 333,443,259 bytes / 11h34m / 24 פרקים.
- **⚠️ באג טרנקציה בהורדה (2026-07-01):** הגרסה הראשונה של ההורדה הישירה (לולאת `iter_content` חד-פעמית בלי אימות גודל) נתנה **קובץ חתוך של 1h46m (~49MB) במקום 11.5h** — החיבור נקטע והסקריפט תייג את החלקי כאילו הושלם. **הפתרון:** הורדה עם **Range מתחדש** (`Range: bytes=<have>-`) בלולאה עד ש-`os.path.getsize == content-length`, ורק אז ffmpeg. תמיד לאמת גודל מול ה-`content-range`/`content-length` לפני התיוג. הקובץ המלא (11h34m, 318MB, גודל מאומת) הועתק ל-`/storage/emulated/0/Download/התפכחות - דן מרגלית.mp3`. הסקריפט העמיד: `scratchpad/robust_dl.py`.
- **`storytel_direct_download.py` עודכן לעבוד בלי מדף (2026-07-01, commit `df21ccd`):** במקום לסרוק `getBookShelf`, קורא ל-`getBookInfoForContent.action` (עם fallback המרת consumableId→bookId דרך `book-details/consumables/<cid>`). כך גם ההורדה הישירה עובדת על ספרים שאינם במדף. שאר הצינור לא השתנה (מבנה `slb` תואם לרשומת מדף). ה-README של הפאץ' עודכן עם סעיף בדיקת השטח והסייג (commit `4c69ad8`).

קשור ל-[[feedback_save_everything]], [[project-claude-code-backup]].
