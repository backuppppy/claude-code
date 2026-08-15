# FXP Askol Telegram Bot - Deployment Guide

## ✅ Pre-Deployment Checklist

### קונפיגורציה
- [ ] טוקן Telegram Bot מ-@BotFather
- [ ] Chat ID שאליו לשלוח הודעות
- [ ] סביבה Linux/Unix (מומלץ Termux)
- [ ] Python 3.11+

### בדיקות
- [ ] כל unit tests עוברים
- [ ] E2E tests עוברים
- [ ] יומן פעולות נבדק

### בטיחות
- [ ] גיטינור ל-.env file
- [ ] API token בטוח
- [ ] אנטי-דופליקט עבודה

---

## 🚀 Deployment Steps

### 1. הכנה

```bash
# היכנס למנוי שלך
cd fxp-askol-telegram

# יצור virtual environment
python3 -m venv venv
source venv/bin/activate

# התקן dependencies
pip install -r requirements.txt
```

### 2. הגדרה

```bash
# יצור .env file
cp .env.example .env

# ערוך עם פרטיים שלך
nano .env
```

**שדות חובה:**
```env
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
FXP_MONITOR_INTERVAL=300
ENABLE_NOTIFICATIONS=True
```

### 3. בדיקות

```bash
# הרץ unit tests
python test_scraper_simple.py
python test_database_simple.py
python test_telegram_bot.py
python test_scheduler.py

# הרץ E2E tests
python test_integration.py
```

### 4. Run ראשונית

```bash
# הרץ עם YOLO mode לראות תוצאות מיידיות
ENABLE_DRY_RUN=True python main.py

# הרץ עם הודעות אמיתיות
python main.py
```

---

## 🔧 Production Setup

### Option 1: Termux (Android)

```bash
# התקן במנוי Termux
cd ~/.zeroclaw/projects/fxp-askol-telegram

# חברת daemonize עם termux-services
pkg install termux-services

# יצור service file
mkdir -p ~/.local/etc/sv/fxp-bot
cd ~/.local/etc/sv/fxp-bot

# יצור run script
cat > run << 'EOF'
#!/bin/bash
exec 2>&1
cd ~/projects/fxp-askol-telegram
exec python main.py
EOF

chmod +x run

# הפעל
sv-enable fxp-bot
```

### Option 2: Linux Server (systemd)

```bash
# יצור service file
sudo nano /etc/systemd/system/fxp-bot.service
```

תוכן:
```ini
[Unit]
Description=FXP Askol Telegram Bot
After=network.target

[Service]
Type=simple
User=username
WorkingDirectory=/home/username/fxp-askol-telegram
Environment="PATH=/home/username/fxp-askol-telegram/venv/bin"
ExecStart=/home/username/fxp-askol-telegram/venv/bin/python main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

הפעל:
```bash
sudo systemctl enable fxp-bot
sudo systemctl start fxp-bot
sudo systemctl status fxp-bot
```

### Option 3: Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
```

Build וRun:
```bash
docker build -t fxp-bot .
docker run -d --env-file .env fxp-bot
```

---

## 📊 Monitoring

### לוג files

```bash
# הצג לוגים אחרונים
tail -f logs/fxp_monitor.log

# חיפוש לשגיאות
grep ERROR logs/fxp_monitor.log

# חיפוש הודעות שנשלחו
grep "הודעה נשלחה" logs/fxp_monitor.log
```

### Database

```bash
# בדוק סטטיסטיקות
sqlite3 fxp_askol.db "SELECT COUNT(*) FROM processed_questions;"

# ראה הרצות אחרונות
sqlite3 fxp_askol.db "SELECT * FROM monitoring_log LIMIT 10;"

# נקה נתונים ישנים (30 ימים)
python -c "from database import Database; db = Database(); db.cleanup_old_data(30); db.close()"
```

---

## 🚨 Troubleshooting

### בוט לא מחובר
```bash
# בדוק טוקן
curl "https://api.telegram.org/bot<TOKEN>/getMe"
```

### אין שאלות נמצאות
- בדוק את FXP בדפדפן - אולי בעיית FXP
- בדוק את HTML selectors - אולי השתנה
- חפש בלוגים: `grep "No questions" logs/fxp_monitor.log`

### Telegram rate limits
- המתן כמה דקות
- בדוק `logs/fxp_monitor.log` ל-"Too Many Requests"
- הקטן את `FXP_MONITOR_INTERVAL`

### Memory leak
- בדוק `top` או `htop`
- גדל את זיכרון המכשיר
- אם זה קשוח, restart את הbot כל 12 שעות

---

## 🔐 Security

### סודות
- לא שומרים טוקן בקוד
- `.env` ב-`.gitignore`
- בדוק permissions ל-`fxp_askol.db`

### Logging
- סודות לא מתורגמים בלוגים
- רק titles ו-links של שאלות
- לא שומרים chat IDs בבר

---

## 📈 Scaling

### Multiple bots
```bash
# בוט נפרד לכל קטגוריה
python main.py --category=tech
python main.py --category=health
```

### Database optimization
```sql
-- בדוק indexes
PRAGMA index_list(processed_questions);

-- ניקוי מחזוריים
DELETE FROM processed_questions 
WHERE processed_at < datetime('now', '-30 days');
```

---

## ✅ Post-Deployment

### בדיקות יומיות
- [ ] בוט פעיל ו-responding
- [ ] הודעות מתקבלות
- [ ] אין שגיאות בלוגים
- [ ] Database גדל בהתאמה

### בדיקות שבועיות
- [ ] Cleanup old data
- [ ] בדוק דיסק
- [ ] בדוק memory usage
- [ ] Review statistics

---

## 📞 Support

### לוגים
```bash
# מקור לוגים
cat logs/fxp_monitor.log

# צפה בזמן אמת
tail -f logs/fxp_monitor.log
```

### בדיקה ידנית
```bash
# בדוק בוט
python -c "from telegram_bot import TelegramBot; TelegramBot().get_bot_info()"

# בדוק scraper
python -c "from scraper import FXPScraper; print(len(FXPScraper().get_latest_questions()))"

# בדוק database
python -c "from database import Database; db = Database(); print(db.get_processed_questions_count())"
```

---

**Deployment Guide - Completed ✅**

תאריך: 2026-08-15
