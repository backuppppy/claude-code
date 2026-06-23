---
name: פרויקט Suno API
description: המשתמש רוצה להתחבר ל-Suno (יצירת מוזיקה AI) דרך API לא רשמי מ-GitHub
type: project
originSessionId: ef4c4877-f8e4-4585-84cd-3d1d545a4617
---
המשתמש רוצה להשתמש ב-Suno לצורך יצירת מוזיקה דרך API, ולשלב אותו בקוד Python.

**מה שנחקר:**
- ל-Suno אין API רשמי ציבורי (נכון למאי 2026)
- הפתרון הטוב ביותר: [gcui-art/suno-api](https://github.com/gcui-art/suno-api) — קוד פתוח, חינמי
- עובד עם Cookie מחשבון Suno (לא מפתח API רשמי)
- תומך ב-Docker ו-Node.js
- המודל הכי עדכני של Suno: V5.5 (מרץ 2026)

**הגדרה:**
1. קבל Cookie מ-suno.com/create דרך DevTools → Network
2. הרץ עם Docker:
   `docker run -d -e SUNO_COOKIE="..." -p 3000:3000 gcuiart/suno-api`
3. קרא ל-API מ-Python:
   `POST http://localhost:3000/api/generate` עם `{"prompt": "...", "wait_audio": true}`

**Endpoints עיקריים:**
- `/api/generate` — יצירת מוזיקה
- `/api/custom_generate` — מצב מותאם אישית (מילים + סגנון)
- `/api/generate_lyrics` — יצירת מילים בלבד
- `/api/get` — קבלת מידע על שיר
- `/api/get_limit` — בדיקת מכסה

**Why:** המשתמש רוצה ליצור מוזיקה ב-AI ולשלב בפרויקטים.

**How to apply:** אם חוזרים לנושא, השלב הבא הוא להחליט אם להשתמש ב-Docker או Node.js, ולאחר מכן לכתוב סקריפט Python מלא.
