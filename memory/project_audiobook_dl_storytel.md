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

**טיפים לדיבוג:** ה-API `https://www.storytel.com/api/login.action` עובד ומחזיר JSON עם `loginStatusEnum` (PREMIUM / INVALID_CREDENTIALS). אפשר לבדוק התחברות ידנית מתוך ה-venv (`/root/.local/share/pipx/venvs/audiobook-dl/bin/python`) שיש בו pycryptodome. הסיסמה מוצפנת AES-CBC עם מפתחות קבועים בקוד.

קשור ל-[[feedback_save_everything]].
