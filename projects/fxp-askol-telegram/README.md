# FXP Askol Telegram Bot 🤖

Automatically monitor the FXP website for new questions ("askol") and send instant notifications to a Telegram bot with direct links.

## ✨ Features

✅ Monitor FXP website every N minutes  
✅ Detect new questions automatically  
✅ Send formatted Telegram notifications  
✅ Include clickable links to questions  
✅ No duplicate notifications  
✅ Comprehensive error handling  
✅ SQLite persistence  
✅ Detailed logging  

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- Telegram Bot (get from [@BotFather](https://t.me/botfather))
- Terminal/SSH access

### 2. Installation

```bash
# Clone/navigate to project
cd projects/fxp-askol-telegram

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required variables:**
```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_chat_id
```

Get your chat ID:
1. Send a message to your bot in Telegram
2. Visit: `https://api.telegram.org/botYOUR_TOKEN/getUpdates`
3. Find your chat ID in the response

### 4. Run

```bash
# Run the monitor
python main.py

# Or with dry-run mode (test without sending)
ENABLE_DRY_RUN=True python main.py
```

## 📂 Project Structure

```
fxp-askol-telegram/
├── main.py              ← Entry point & scheduler
├── scraper.py           ← FXP website scraper
├── telegram_bot.py      ← Telegram API wrapper
├── database.py          ← SQLite database manager
├── config.py            ← Configuration management
├── requirements.txt     ← Python dependencies
├── .env.example         ← Environment template
├── .env                 ← Actual config (not committed)
├── fxp_askol.db        ← SQLite database (auto-created)
├── logs/               ← Log files
└── tests/              ← Unit tests
```

## ⚙️ Configuration Options

### Environment Variables

```bash
# Telegram
TELEGRAM_BOT_TOKEN=          # Telegram bot token (required)
TELEGRAM_CHAT_ID=            # Chat to send notifications to (required)

# FXP Monitoring
FXP_BASE_URL=https://www.fxp.co.il
FXP_MONITOR_INTERVAL=300     # Check every 300 seconds (5 minutes)
FXP_SCRAPER_TIMEOUT=30       # Timeout for HTTP requests

# Logging
LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR

# Database
DATABASE_PATH=./fxp_askol.db

# Feature Flags
ENABLE_NOTIFICATIONS=True    # Send Telegram messages
ENABLE_DRY_RUN=False        # Test without sending
```

## 📊 Database Schema

### processed_questions
```sql
CREATE TABLE processed_questions (
    id INTEGER PRIMARY KEY,
    fxp_question_id TEXT UNIQUE,
    title TEXT,
    link TEXT,
    category TEXT,
    created_at TIMESTAMP,
    processed_at TIMESTAMP,
    sent_to_telegram BOOLEAN
);
```

### monitoring_log
```sql
CREATE TABLE monitoring_log (
    id INTEGER PRIMARY KEY,
    run_at TIMESTAMP,
    questions_found INTEGER,
    new_questions INTEGER,
    notifications_sent INTEGER,
    errors TEXT,
    duration_ms INTEGER
);
```

## 🧪 Testing

### Dry Run Mode
```bash
ENABLE_DRY_RUN=True python main.py
# Will log what would be sent without actually sending
```

### Manual Testing
```bash
# Test scraper
python -c "from scraper import FXPScraper; print(FXPScraper().get_latest_questions())"

# Test Telegram bot
python -c "from telegram_bot import TelegramBot; TelegramBot().send_message('Test')"
```

## 📝 Logs

Logs are written to both console and file:

```bash
# View logs
tail -f logs/fxp_monitor.log

# Search for errors
grep ERROR logs/fxp_monitor.log
```

Log format:
```
2026-08-15 10:30:45,123 - root - INFO - Starting monitoring run...
2026-08-15 10:30:52,456 - root - INFO - Parsed 3 questions from FXP
2026-08-15 10:30:54,789 - root - INFO - Sent notification for: השאלה החדשה
```

## 🔐 Security

**Secrets:**
- ✅ Never commit `.env` file (it's in `.gitignore`)
- ✅ Use strong bot token from Telegram
- ✅ Keep chat ID private
- ✅ Use environment variables in production

**Best Practices:**
- Store credentials in GitHub Secrets for CI/CD
- Use separate bots for testing and production
- Rotate tokens periodically
- Monitor logs for suspicious activity

## 🚨 Troubleshooting

### "TELEGRAM_BOT_TOKEN not found"
**Solution:** Ensure `.env` file exists with `TELEGRAM_BOT_TOKEN` set

### "Connection timeout when fetching FXP"
**Solution:** Check internet connection, try increasing `FXP_SCRAPER_TIMEOUT`

### "No questions found"
**Solution:** FXP website structure may have changed - check HTML selectors in scraper.py

### "Duplicate notifications"
**Solution:** Database might be corrupted - delete `fxp_askol.db` and restart

## 📅 Development Roadmap

- [ ] Phase 1: Core scraping
- [ ] Phase 2: Database & persistence
- [ ] Phase 3: Telegram integration
- [ ] Phase 4: Scheduling & automation
- [ ] Phase 5: Testing & deployment

## 🤝 Contributing

To improve or extend this project:

1. Read `/specs/001-fxp-askol-telegram-bot/spec.md`
2. Check current implementation
3. Make changes following Python best practices
4. Add tests for new features
5. Update README documentation

## 📞 Support

For issues or improvements, check:
- GitHub Issues: https://github.com/backuppppy/claude-code/issues
- Project memory: `memory/project_fxp_bot.md`

---

**Created:** 2026-08-15  
**Status:** ✨ In Development  
**Spec:** [001-fxp-askol-telegram-bot](../../specs/001-fxp-askol-telegram-bot/spec.md)
