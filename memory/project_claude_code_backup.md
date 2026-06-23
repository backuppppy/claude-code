---
name: project-claude-code-backup
description: גיבוי כל סביבת העבודה והפרויקטים לריפו backuppppy/claude-code
metadata: 
  node_type: memory
  type: project
  originSessionId: 4f7deafa-32f9-4228-b7f4-92a94b53be66
---

גיבינו את כל סביבת Claude Code לריפו הפרטי **`backuppppy/claude-code`** (היה ריק, אוכלס 2026-06-23).

**מבנה:** `README.md` (מפת-על), `memory/` (העתק קבצי הזיכרון), `projects/` (tg-backup-apk, tg_apk, wa-counter, web, fxp_bot, font_maker, G0DM0D3-changes=רק diff), `scripts/` (book/, godmod3_proxy.py, ועוד), `config-templates/` (placeholders), `.github/workflows/restore-secrets.yml`.

**מקור הגיבוי:** `/root/claude-code-backup/` (git repo מקומי, remote=origin).

**סודות → GitHub Secrets** (לא בקוד): `GH_TOKEN`, `OPENROUTER_API_KEY`, `FXP_TELEGRAM_TOKEN`, `FXP_TELEGRAM_CHAT_ID`, `STORYTEL_USERNAME`, `STORYTEL_PASSWORD`, `CLAUDE_JSON_B64`, `GITCONFIG_B64`.

**שחזור סודות:** Actions→"Restore secrets to files"→Run→הורדת artifact `restored-secrets` (secrets הם write-only, אי אפשר לקרוא ישירות).

**הוסר בסניטציה לפני push:** `fxp_bot/.env` (טוקן), `wa-counter/auth/creds.json` (מפתחות וואטסאפ), `web/dist/` (2MB קוד צד-שלישי). הוחלפו בתבניות/הערות.

קשור ל-[[feedback_save_everything]], [[feedback_github_push_policy]].
