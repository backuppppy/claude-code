---
name: feedback-permissions
description: המשתמש העניק הרשאות מקסימליות — bypassPermissions. לא לשאול אישור על כלים.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: dd68b699-23d1-4222-888d-caf6ed3e52e0
---

# הרשאות מקסימליות

המשתמש ביקש שלא אשאל אישור על פעולות. הגדרתי `bypassPermissions` ב-`~/.claude/settings.json`.

**Why:** המשתמש אמר "תן לי לאשר הכל פעם אחת ואז תהיה לך הרשאות". הוא מעדיף זרימת עבודה ללא הפרעות.

**How to apply:** לא לשאול אישור על Bash, Read, Write, Edit, WebFetch. אם יש פעולה הרסנית במיוחד (מחיקת קבצים לא הפיכה, push force למשהו חשוב) — לציין בטקסט לפני הביצוע, לא לעצור לשאלה.

## הגדרה נוכחית ב-~/.claude/settings.json
```json
{
  "permissions": {
    "defaultMode": "bypassPermissions",
    "allow": ["Bash(*)", "Read(*)", "Write(*)", "Edit(*)", "WebFetch(*)", "WebSearch(*)"]
  }
}
```
