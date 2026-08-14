# Telegram Stips Monitor - Task Breakdown

## Phase 1: Core Setup & Database

### Task 1.1: Project Structure & Dependencies
- [ ] Create `src/` directory structure
- [ ] Create `requirements.txt` with all dependencies
- [ ] Create `.env.example` with required variables
- [ ] Create `.gitignore` (exclude .env, __pycache__, .db files)
- [ ] Create `README.md` with setup instructions

**Dependencies to install:**
- python-telegram-bot==21.4
- requests==2.31.0
- beautifulsoup4==4.12.0
- APScheduler==3.10.4
- python-dotenv==1.0.0

### Task 1.2: Configuration Module (`config.py`)
- [ ] Load environment variables from .env
- [ ] Define BOT_TOKEN (required)
- [ ] Define POLLING_INTERVAL (default: 300 seconds)
- [ ] Define DATABASE_PATH (default: stips_monitor.db)
- [ ] Add validation to ensure BOT_TOKEN is set
- [ ] Add logging configuration

### Task 1.3: Database Schema & Module (`database.py`)
- [ ] Create SQLite database initialization function
- [ ] Create `users` table:
  - telegram_id (PRIMARY KEY)
  - subscribed (BOOLEAN)
  - created_at (TIMESTAMP)
  - updated_at (TIMESTAMP)
- [ ] Create `posts` table:
  - id (PRIMARY KEY)
  - title (TEXT)
  - url (TEXT, UNIQUE)
  - published_date (DATETIME)
  - created_at (TIMESTAMP)
- [ ] Write CRUD functions:
  - add_user(telegram_id)
  - subscribe_user(telegram_id)
  - unsubscribe_user(telegram_id)
  - get_subscribed_users()
  - is_subscribed(telegram_id)
  - add_post(title, url, published_date)
  - get_unsent_posts()
  - mark_post_sent(post_id)
  - post_exists(url)

### Task 1.4: Unit Tests for Database
- [ ] Test user add/subscribe/unsubscribe operations
- [ ] Test post CRUD operations
- [ ] Test duplicate post detection
- [ ] Test subscribed users query
- [ ] Create test database fixture

---

## Phase 2: Web Monitoring

### Task 2.1: Web Scraper Module (`monitor.py`)
- [ ] Create function to fetch stips.co.il homepage
- [ ] Parse HTML with BeautifulSoup
- [ ] Extract post elements (title, link, date)
- [ ] Handle network errors gracefully
- [ ] Return list of posts as dictionaries
- [ ] Add retry logic for failed requests

### Task 2.2: HTML Analysis
- [ ] Inspect stips.co.il HTML structure
- [ ] Identify CSS selectors for:
  - Post containers
  - Post titles
  - Post links
  - Post dates
- [ ] Document selectors in comments

### Task 2.3: Post Detection Logic
- [ ] Compare scraped posts with database
- [ ] Filter to new posts only
- [ ] Handle date parsing from HTML
- [ ] Log detected vs. new posts

### Task 2.4: Unit Tests for Scraper
- [ ] Mock HTTP requests
- [ ] Test HTML parsing with sample data
- [ ] Test error handling for network failures
- [ ] Test date parsing accuracy
- [ ] Test duplicate detection

### Task 2.5: Scheduler Integration
- [ ] Initialize APScheduler
- [ ] Add job to run scraper every POLLING_INTERVAL
- [ ] Handle job failures
- [ ] Log scheduler activity
- [ ] Add start/stop methods

---

## Phase 3: Telegram Bot & Notifications

### Task 3.1: Bot Handler Module (`notifier.py`)
- [ ] Create format_post(post_dict) function
  - Format as: "📢 Title\n🔗 [link]\n📅 Date"
- [ ] Create send_notification(user_id, post) function
  - Send formatted message via Telegram API
  - Handle send failures
  - Log results
- [ ] Create batch_notify_users(posts) function
  - Send new posts to all subscribed users
  - Track sent posts in database
  - Log metrics (sent/failed count)

### Task 3.2: Bot Commands Module (`main.py`)
- [ ] Create Telegram Application instance
- [ ] Implement `/start` command handler
  - Welcome message
  - Suggest `/subscribe`
- [ ] Implement `/subscribe` command
  - Add user to database
  - Confirm subscription
- [ ] Implement `/unsubscribe` command
  - Mark user unsubscribed
  - Confirm action
- [ ] Implement `/status` command
  - Show subscription status
  - Show last update time
- [ ] Implement `/help` command
  - List all commands
  - Explain functionality

### Task 3.3: Error Handling & Logging
- [ ] Add try-catch around all Telegram API calls
- [ ] Log command executions with user ID
- [ ] Handle timeout errors
- [ ] Handle API rate limiting (backoff strategy)
- [ ] Send error notifications to admin (optional)

### Task 3.4: Integration Tests
- [ ] Test end-to-end flow:
  1. User sends /start
  2. User sends /subscribe
  3. New post is detected
  4. Notification is sent to user
- [ ] Test command handlers
- [ ] Test notification formatting
- [ ] Test database updates during notifications

---

## Phase 4: Deployment & Polish

### Task 4.1: Application Entry Point
- [ ] Create main.py that:
  - Loads config
  - Initializes database
  - Creates bot application
  - Registers all handlers
  - Starts scheduler
  - Runs bot with polling

### Task 4.2: Error Recovery
- [ ] Add signal handlers for graceful shutdown
- [ ] Implement resume logic after crash
- [ ] Add health check function
- [ ] Log startup/shutdown events

### Task 4.3: Documentation
- [ ] Write comprehensive README.md
  - Setup instructions
  - Configuration guide
  - Command reference
  - Troubleshooting section
- [ ] Add inline code comments
- [ ] Create DEVELOPMENT.md for contributors

### Task 4.4: .env Configuration
- [ ] Create .env.example with:
  - BOT_TOKEN=your_token_here
  - POLLING_INTERVAL=300
  - DATABASE_PATH=stips_monitor.db
  - LOG_LEVEL=INFO

### Task 4.5: Testing & QA
- [ ] Run all unit tests
- [ ] Manual testing with test bot account
- [ ] Test all commands (/start, /subscribe, etc.)
- [ ] Test notification delivery
- [ ] Stress test with multiple users
- [ ] Verify no duplicate notifications

### Task 4.6: Deployment Setup
- [ ] Create systemd service file (optional)
- [ ] Create Docker setup (optional)
- [ ] Document deployment process
- [ ] Test production-like environment

---

## Prioritization

**Must Have (MVP):**
- Tasks 1.1, 1.2, 1.3
- Tasks 2.1, 2.2, 2.3, 2.5
- Tasks 3.1, 3.2
- Tasks 4.1, 4.3

**Should Have:**
- Tasks 1.4, 2.4, 3.4
- Task 3.3 (basic error handling)

**Nice to Have:**
- Tasks 4.2, 4.5, 4.6
- Advanced monitoring/metrics

---

## Estimation

| Phase | Effort | Status |
|-------|--------|--------|
| Phase 1 | 4-6 hours | Not Started |
| Phase 2 | 3-5 hours | Not Started |
| Phase 3 | 5-7 hours | Not Started |
| Phase 4 | 2-3 hours | Not Started |
| **Total** | **14-21 hours** | **Not Started** |

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Website structure changes | Medium | High | Store CSS selectors as config, add monitoring alerts |
| Telegram API rate limits | Low | Medium | Implement exponential backoff retry |
| Database corruption | Low | High | Regular backups, transaction safety |
| Memory leaks in long-running bot | Medium | Medium | Monitor process memory, implement periodic restarts |
| Network interruptions | Medium | Medium | Retry logic, graceful degradation |
