---
name: פרויקט סריקת אתר conectedmmb
description: סריקה וניתוח של האתר conectedmmb.lovable.app — קהילת הורים, דף אימות
type: project
originSessionId: af944097-53c1-4698-9406-4cc76293bb4a
---
## האתר
- URL: https://conectedmmb.lovable.app/aut
- שם: **הורים מחוברים | קהילת ההורים של לוקחים אחריות**
- דף `/aut` = דף Authentication (כניסה/הרשמה)

## טכנולוגיה
- בנוי על **Lovable** (פלטפורמת React SPA)
- כנראה משתמש ב-**Supabase** לאימות (נפוץ מאוד ב-Lovable)
- כל הרינדור בצד הלקוח — WebFetch רואה רק HTML בסיסי ריק

## מה נעשה
- סריקת הדף דרך WebFetch — קיבלנו רק כותרת, כי JS לא מרונדר
- הסברנו 4 שיטות להוריד ולנתח את ה-JS bundle:
  1. Sources tab ב-DevTools + כפתור `{}` לעיצוב
  2. Network tab → סנן JS → Save as
  3. curl/wget + npx prettier לעיצוב
  4. grep לחיפוש מילות מפתח (register, signup, supabase)

## Why:
המשתמש רוצה לראות את לוגיקת ההרשמה של האתר.

## How to apply:
אם המשתמש חוזר לנושא — להציע Supabase dashboard או לחפש `supabase.auth.signUp` בקוד.
