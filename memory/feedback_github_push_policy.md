---
name: feedback-github-push-policy
description: לא לבצע push לגיטהאב בלי אישור מפורש מהמשתמש — צריך לשאול לפני כל push
metadata:
  type: feedback
---

לא לבצע `git push` לגיטהאב Actions ללא אישור מפורש מהמשתמש.

**Why:** כל push מפעיל בנייה ב-GitHub Actions. המשתמש רוצה לשלוט מתי מופעלת בנייה.

**How to apply:**
1. לסיים שינויי קוד וQA מקומי
2. לשאול: "האם לדחוף לגיטהאב ולהתחיל בנייה?"
3. לחכות לאישור לפני push
