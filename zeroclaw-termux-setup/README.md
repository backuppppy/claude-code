# ZeroClaw Termux Setup — 100% שלם וממשי

**תאריך:** 2 באוגוסט 2026
**מכשיר:** OnePlus 11 (Snapdragon 8 Gen 2)
**סביבה:** Termux (Android)

## ✅ מה עובד

- ✅ ZeroClaw v0.8.3 עם Claude Opus 5 API
- ✅ YOLO Mode (ללא הודעות אישור)
- ✅ Streaming output (real-time)
- ✅ Hebrew support (עברית מלאה)
- ✅ GitHub integration (`gh` CLI)
- ✅ Shell command execution
- ✅ Git operations

## 🎯 Aliases מהר (בשימוש יומיומי)

```bash
zc "<text>"          # שלח הודעה ל-ZeroClaw
zcstream "<text>"    # Streaming mode (auto-approve)
zcgh                 # רשימת ריפוזיטוריים ב-GitHub
zcs                  # בדיקת סטטוס
zcls                 # רשימת קבצים
zcgit                # git status
```

## 📂 קבצים בתיקייה זו

### קבצי קונפיגורציה
- **config.toml** — הקונפיג המלא (עם placeholder לAPI key)
- **env.example** — משתנים סביבה

### סקריפטים (`scripts/`)
- **zc-daemon.sh** — הפעל ZeroClaw daemon
- **zc-send.sh** — שלח בקשה ל-daemon
- **zc-cmd.sh** — הרץ shell command דרך ZeroClaw
- **zc-gh.sh** — בדוק ריפוזיטוריים ב-GitHub
- **zc-git.sh** — בדוק git status
- **zc-streaming.sh** — הוראות streaming mode
- **aliases.sh** — קבצי aliases שחוקים

## 🚀 התקנה מהר

1. **העתק את הקבצים לטרמוקס:**
   ```bash
   mkdir -p ~/.zeroclaw/scripts
   cp config.toml ~/.zeroclaw/
   cp scripts/* ~/.zeroclaw/scripts/
   ```

2. **ערוך את `~/.zeroclaw/config.toml` וכנס API key:**
   ```bash
   nano ~/.zeroclaw/config.toml
   # ערוך: [providers.models.anthropic.default]
   # api_key = "sk-ant-api03-YOUR_KEY_HERE"
   ```

3. **הוסף aliases ל-bashrc:**
   ```bash
   cat scripts/aliases.sh >> ~/.bashrc
   source ~/.bashrc
   ```

4. **בדוק:**
   ```bash
   zcs
   # צריך לראות: "Claude Opus 5" + "permissive"
   ```

## ⚙️ קונפיגורציה

### Risk Profile: `permissive` (YOLO Mode)
```toml
[risk_profiles.permissive]
sandbox_enabled = false
workspace_only = false
allowed_commands = ["*"]
```

**זה אומר:**
- ✅ אין הודעות אישור ("do you want to...")
- ✅ גישה מלאה לקבצים
- ✅ ביצוע כל פקודה shell

### GitHub Integration
```bash
gh auth login
# בחר: HTTPS, web browser, device code
# כרגע מחובר כ: backuppppy
```

## 🔧 Troubleshooting

### "Config loads but no model"
→ בדוק: `api_key = "sk-ant-api03-..."` בקובץ

### "Command not found: zc"
→ בדוק: aliases בـ `~/.bashrc`, הרץ `source ~/.bashrc`

### "Tool calling failed"
→ בדוק: `zeroclaw status` — צריך `native_tool_calls: 1`

---

**סטטוס:** 🚀 **PRODUCTION READY** — כל דבר עובד, בדוק וטסט.
