# Feature: FXP Askol Telegram Bot Notifications

**Feature ID:** 001-fxp-askol-telegram-bot  
**Status:** In Design  
**Created:** 2026-08-15  
**Owner:** backuppppy  
**Priority:** High  

---

## 🎯 Overview

Automatically monitor the FXP website (fxp.co.il) for new questions ("askol") and instantly send notifications to a Telegram bot with direct links and details.

### Success Criteria
- ✅ Monitor FXP website every N minutes
- ✅ Detect new questions posted
- ✅ Extract question title, content, link
- ✅ Send formatted message to Telegram bot
- ✅ Include clickable link to question
- ✅ No duplicate notifications
- ✅ Graceful error handling

---

## 📋 Requirements

### Functional Requirements

#### FR-1: Website Monitoring
- Monitor `https://www.fxp.co.il` for new questions
- Polling interval: configurable (default 5 minutes)
- Store last-seen question ID to prevent duplicates
- Handle rate limiting gracefully

#### FR-2: Question Detection
- Extract question metadata:
  - Title (שם השאלה)
  - Content/Description
  - Direct link to question
  - Author (if available)
  - Category/Tags
  - Creation timestamp

#### FR-3: Telegram Integration
- Send formatted message to Telegram bot
- Include clickable link with preview
- Format: Title + preview + direct link
- Handle Telegram API errors
- Retry on failure

#### FR-4: Data Persistence
- Store processed question IDs (SQLite)
- Track monitoring history
- Log errors and notifications
- Enable/disable notifications per user

---

## 🚀 Implementation Phases

### Phase 1: Core Scraping (Week 1)
- [ ] Setup project structure
- [ ] Implement FXP scraper
- [ ] Extract question metadata
- [ ] Unit tests for scraper

### Phase 2: Database & Persistence (Week 1-2)
- [ ] Design SQLite schema
- [ ] Implement database wrapper
- [ ] Setup processed_questions table
- [ ] Add error logging

### Phase 3: Telegram Integration (Week 2)
- [ ] Create telegram_bot.py
- [ ] Implement message formatting
- [ ] Add user subscription system
- [ ] Handle bot commands

### Phase 4: Scheduling & Automation (Week 2-3)
- [ ] Setup APScheduler
- [ ] Implement monitoring loop
- [ ] Add error recovery
- [ ] Create metrics logging

### Phase 5: Testing & Deployment (Week 3-4)
- [ ] Write unit tests
- [ ] Integration testing
- [ ] Deployment configuration
- [ ] Documentation

---

## 📂 Project Structure

```
projects/fxp-askol-telegram/
├── README.md
├── requirements.txt
├── config.py
├── main.py
├── scraper.py
├── telegram_bot.py
├── database.py
├── scheduler.py
├── .env.example
└── tests/
```

---

## 🔐 Security

```bash
# Store in .env (not committed)
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id
FXP_SCRAPER_TIMEOUT=30
DATABASE_PATH=/path/to/fxp.db
```

---

## 📊 Key Metrics

- Questions per hour
- Notification delivery rate
- Scraper success rate
- Average response time
- Error frequency

---

## ✅ Acceptance Criteria

- [ ] Scraper successfully extracts 100+ questions
- [ ] Telegram messages delivered successfully
- [ ] No duplicate notifications in 24-hour test
- [ ] Error rate < 0.1%
- [ ] Response time < 5 seconds per notification
- [ ] Full test coverage (>80%)
- [ ] Documentation complete
- [ ] Deployment runbook ready

---

**Status:** Ready for Implementation ✅  
**Next Action:** Create project directory and start Phase 1  
**Assigned To:** backuppppy  
**Date:** 2026-08-15
