# Telegram Stips Monitor - Implementation Plan

## Architecture Overview

```
┌─────────────────────────────────────────┐
│   Main Bot Application (Python)         │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │ Telegram     │  │ Web Monitor  │   │
│  │ Handler      │  │ (Scraper)    │   │
│  └──────────────┘  └──────────────┘   │
│         │                   │           │
│         └───────────────────┘           │
│                   │                     │
│         ┌─────────▼─────────┐          │
│         │   SQLite DB       │          │
│         │ (Users + Posts)   │          │
│         └───────────────────┘          │
│                                         │
└─────────────────────────────────────────┘
```

## Technology Stack

- **Language**: Python 3.11+
- **Telegram**: `python-telegram-bot` (v21+)
- **Web Scraping**: `requests` + `BeautifulSoup4`
- **Database**: SQLite (local, no setup needed)
- **Scheduling**: `APScheduler` for periodic monitoring
- **Configuration**: `python-dotenv` for environment variables
- **Logging**: Built-in Python `logging` module

## Component Breakdown

### 1. Bot Application (`main.py`)
- Initialize Telegram bot with token
- Register command handlers (/start, /subscribe, /unsubscribe, /status)
- Start the scheduler for web monitoring
- Handle incoming messages

### 2. Web Monitor (`monitor.py`)
- Function to scrape stips.co.il homepage
- Parse HTML to extract post titles, links, dates
- Compare with database to find new posts
- Queue new posts for notification

### 3. Database Layer (`database.py`)
- SQLite schema for:
  - `users` table (telegram_id, subscribed, created_at)
  - `posts` table (title, url, date, sent_at)
- CRUD operations for users and posts
- Query for unsent posts and active users

### 4. Notification Service (`notifier.py`)
- Format posts into Telegram messages
- Send to all subscribed users
- Handle send failures and retries
- Log all activity

### 5. Configuration (`config.py`)
- Load environment variables
- Define constants (polling interval, etc.)
- Validate required settings

## Implementation Phases

### Phase 1: Core Setup (MVP)
1. Create project structure
2. Set up dependencies (requirements.txt)
3. Create SQLite database schema
4. Implement basic Telegram bot handlers
5. Add `/start`, `/subscribe` commands
6. Write basic logging

### Phase 2: Web Monitoring
1. Implement web scraper for stips.co.il
2. Extract post titles, links, dates
3. Store new posts in database
4. Set up APScheduler for polling

### Phase 3: Notifications
1. Build notification formatter
2. Send messages to subscribed users
3. Track sent posts
4. Implement error retry logic

### Phase 4: Polish & Deployment
1. Add `/status` and `/help` commands
2. Improve logging and error handling
3. Create `.env.example` file
4. Add shutdown handlers
5. Test with real Telegram bot

## File Structure

```
my-project/
├── main.py              # Entry point
├── monitor.py           # Web scraper
├── database.py          # SQLite operations
├── notifier.py          # Message formatting
├── config.py            # Configuration
├── requirements.txt     # Dependencies
├── .env.example         # Config template
├── .gitignore           # Git ignore rules
├── README.md            # Documentation
└── specs/              # Spec documents
    ├── constitution.md
    ├── specification.md
    └── plan.md
```

## Dependencies

```
python-telegram-bot==21.4
requests==2.31.0
beautifulsoup4==4.12.0
APScheduler==3.10.4
python-dotenv==1.0.0
```

## Key Design Decisions

1. **SQLite over Cloud DB**: Local database eliminates dependency on external services
2. **Polling over Webhooks**: Website doesn't offer webhooks, polling is simpler to implement
3. **APScheduler**: Lightweight, no external service needed
4. **BeautifulSoup**: Easy HTML parsing without JavaScript rendering
5. **Single-process**: Simpler deployment, fine for 100+ users

## Deployment Strategy

- Run as systemd service or Docker container
- Store .env file securely (NOT in git)
- Log to file + console
- Restart on failure via supervisor or systemd

## Success Metrics

- Bot responds to commands within 2 seconds
- New posts detected within 2 minutes
- 0 duplicate notifications
- 99%+ message delivery success rate
- Clear, actionable logs for debugging
