---
name: feedback-qa-before-push
description: לבצע QA ובדיקת קוד לפני כל push לגיטהאב — לא לדחוף ישירות
metadata:
  type: feedback
---

לפני כל push לגיטהאב: לבצע QA — לסקור את השינויים, לחפש באגים, לוודא שלא נשבר כלום.

**Why:** בעבר נדחפו שינויים עם באגים (ReferenceError, keystore שגוי) שגרמו לבניות פגומות.

**How to apply:**
1. לסיים לכתוב את הקוד
2. לעבור על הdiff — לחפש טעויות לוגיות, edge cases, פגיעה בפיצרים קיימים
3. לשאול את המשתמש לפני push
