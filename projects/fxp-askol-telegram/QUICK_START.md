# FXP Askol Telegram Bot - Quick Start Guide

## ⚡ התחלה מהירה (5 דקות)

### 1️⃣ קבל Telegram Bot Token

```bash
# עבור לטלגרם
# חפש @BotFather
# כתוב /newbot
# בחר שם לבוט שלך
# קבל את ה-TOKEN

# לדוגמה:
# TOKEN = 8867679619:AAEHgXKMBhp_zBtB3eBRE8NS-NiNqk2YLUg
```

### 2️⃣ קבל Chat ID

```bash
# שלח הודעה לבוט שלך בטלגרם
# בדוק את ה-chat ID כאן:
curl "https://api.telegram.org/bot<TOKEN>/getUpdates" | grep -o '"chat":{"id":[0-9]*'

# או שלח הודעה וראה את התוקן בהודעה הראשונה
```

### 3️⃣ התקן וערוך .env

```bash
# היכנס לתיקייה
cd projects/fxp-askol-telegram

# ערוך .env
nano .env
# או
cat > .env << EOF
TELEGRAM_BOT_TOKEN=<TOKEN_שלך>
TELEGRAM_CHAT_ID=<CHAT_ID_שלך>
FXP_MONITOR_INTERVAL=300
ENABLE_NOTIFICATIONS=True
ENABLE_DRY_RUN=False
LOG_LEVEL=INFO
EOF
```

### 4️⃣ הרץ את הבוט

```bash
# הרץ עם test mode (ללא הודעות אמיתיות)
ENABLE_DRY_RUN=True python main.py

# או הרץ עם הודעות אמיתיות
python main.py
```

---

## 📍 איפה להריץ

### Option 1: Termux (Android) - המומלץ לך

```bash
# בטרמוקס שלך
cd ~/.zeroclaw
git clone https://github.com/backuppppy/claude-code
cd claude-code/projects/fxp-askol-telegram

# הגדר .env
nano .env

# הרץ
python main.py
```

**כדי להפוך לdaemon (רץ בהרקע):**

```bash
# התקן termux-services
pkg install termux-services

# יצור directory
mkdir -p ~/.local/etc/sv/fxp-bot
cd ~/.local/etc/sv/fxp-bot

# יצור run script
cat > run << 'EOF'
#!/bin/bash
exec 2>&1
cd ~/.zeroclaw/claude-code/projects/fxp-askol-telegram
source ~/.zshrc 2>/dev/null || source ~/.bashrc 2>/dev/null
exec python main.py
EOF

chmod +x run

# הפעל
sv-enable fxp-bot
sv status fxp-bot
```

### Option 2: Ubuntu/Linux Server

```bash
# התקן Python
sudo apt update
sudo apt install python3.11 python3.11-venv git

# קלון ריפו
git clone https://github.com/backuppppy/claude-code
cd claude-code/projects/fxp-askol-telegram

# יצור venv
python3.11 -m venv venv
source venv/bin/activate

# התקן dependencies
pip install -r requirements.txt

# הגדר
nano .env

# הרץ כ-background service
# (ראו DEPLOYMENT.md)
```

### Option 3: Docker

```bash
# בנה image
docker build -t fxp-bot .

# הרץ container
docker run -d \
  --name fxp-bot \
  --env-file .env \
  --restart unless-stopped \
  fxp-bot

# בדוק logs
docker logs -f fxp-bot
```

---

## 🧪 בדוק שהכל עובד

### 1️⃣ בדוק את הטסטים

```bash
# כל הטסטים
python test_scraper_simple.py
python test_database_simple.py
python test_telegram_bot.py
python test_scheduler.py
python test_integration.py

# אם הכל עבר - ✅ Good to go!
```

### 2️⃣ בדוק בוט Telegram

```bash
# יצור Python script זמני
python3 << 'EOF'
from telegram_bot import TelegramBot
import os
os.environ['TELEGRAM_BOT_TOKEN'] = 'your_token'
os.environ['TELEGRAM_CHAT_ID'] = 'your_chat_id'

bot = TelegramBot()
info = bot.get_bot_info()
if info:
    print(f"✅ בוט מחובר: @{info.get('username')}")
else:
    print("❌ בעיה בחיבור לבוט")
EOF
```

### 3️⃣ בדוק scraper

```bash
python3 << 'EOF'
from scraper import FXPScraper
scraper = FXPScraper()
questions = scraper.get_latest_questions()
print(f"✅ נמצאו {len(questions)} שאלות")
for q in questions[:3]:
    print(f"  - {q['title']}")
EOF
```

### 4️⃣ בדוק database

```bash
python3 << 'EOF'
from database import Database
db = Database()
count = db.get_processed_questions_count()
print(f"✅ בסיס נתונים: {count} שאלות מעובדות")
db.close()
EOF
```

---

## 📊 Monitor את ה-Logs

```bash
# ראה לוגים בזמן אמת
tail -f logs/fxp_monitor.log

# חפש הודעות שנשלחו
grep "הודעה נשלחה" logs/fxp_monitor.log

# חפש שגיאות
grep ERROR logs/fxp_monitor.log

# בדוק סטטיסטיקות
grep "סיום:" logs/fxp_monitor.log | tail -10
```

---

## 🛑 עצור את הבוט

### Termux
```bash
# בחזרה ל-foreground
sv-disable fxp-bot
# או
kill $(pgrep -f "python main.py")
```

### Linux
```bash
sudo systemctl stop fxp-bot
# או
pkill -f "python main.py"
```

### Docker
```bash
docker stop fxp-bot
docker rm fxp-bot
```

---

## 🔧 עדכן את הקוד

```bash
cd claude-code
git pull origin main
cd projects/fxp-askol-telegram

# אם התקנת dependencies חדשות
pip install -r requirements.txt

# הרץ מחדש
python main.py
```

---

## 💡 Tips

### Dry Run Mode - בדוק בלי להשלוח הודעות
```bash
ENABLE_DRY_RUN=True python main.py
```

### Change Monitor Interval
```bash
FXP_MONITOR_INTERVAL=600 python main.py  # כל 10 דקות
FXP_MONITOR_INTERVAL=60 python main.py   # כל דקה
```

### Different Log Level
```bash
LOG_LEVEL=DEBUG python main.py
LOG_LEVEL=ERROR python main.py
```

---

## ✅ Checklist לפני הריצה

- [ ] יש לך Telegram Bot Token
- [ ] יש לך Chat ID
- [ ] .env file עם הפרטים שלך
- [ ] כל הטסטים עוברים (28/28)
- [ ] יש לך Python 3.11+
- [ ] התקנת requirements.txt

---

## 📞 Troubleshooting

### "ModuleNotFoundError: No module named 'requests'"
```bash
pip install -r requirements.txt
```

### "Telegram error: 401 Unauthorized"
```bash
# בדוק את TELEGRAM_BOT_TOKEN ב-.env
curl "https://api.telegram.org/bot<TOKEN>/getMe"
```

### "No questions found"
```bash
# בדוק את FXP בדפדפן
# או שנה את FXP_QUESTIONS_URL ב-config.py
```

### "Too many requests (rate limit)"
```bash
# הגבל את FXP_MONITOR_INTERVAL
FXP_MONITOR_INTERVAL=600 python main.py
```

---

**בואו להריץ את הבוט שלך!** 🚀

```bash
python main.py
```

Good luck! 🎉
