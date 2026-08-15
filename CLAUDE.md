# FXP Bot — Claude Code Context

## Project Overview

**FXP Telegram Bot** monitors all forums on FXP.co.il and sends new threads to a Telegram chat in real-time.

- **Language:** Python 3.9+
- **Dependencies:** `requests`, `beautifulsoup4`
- **Type:** Standalone CLI bot with persistent monitoring

## Architecture

```
fxp_bot/
├── bot.py              # Main bot loop — monitors, dedups, sends to Telegram
├── fxp_monitor.py      # Web scraper — discovers forums dynamically, fetches threads
├── config.py           # Configuration (tokens, intervals)
├── setup.py            # Interactive setup wizard (token, chat_id)
├── seen_posts.json     # State file (last 10k post IDs)
└── .env                # Runtime config (not in repo)
```

## Key Files

### bot.py
- Loads state from `seen_posts.json`
- Fetches all posts from `fxp_monitor.get_new_posts()`
- Sends new posts to Telegram via bot API
- Handles rate limiting (429 retry-after)
- Flood guard: >50 new posts = silent record (config expand protection)

**Important:** Post dedup happens by post `id` (thread ID from FXP), not title.

### fxp_monitor.py
- Discovers forums dynamically from FXP forum index
- Caches forums for 6 hours
- Parallel scraping (15 concurrent threads)
- Parses thread ID and title from FXP HTML

**Important:** Uses Hebrew user-agent headers; some IP throttling expected after many requests.

### config.py
- Pulls from `.env` file
- `TELEGRAM_TOKEN` (from @BotFather)
- `TELEGRAM_CHAT_ID` (auto-detect via setup.py, or manual)
- `CHECK_INTERVAL_SECONDS` (default 60)

## Running the Bot

```bash
# First-time setup (interactive)
python3 setup.py

# Then start bot
python3 bot.py

# Or in background
nohup python3 bot.py > bot.log 2>&1 &
```

## Development Notes

- **Logging:** stdout + `bot.log` (appended)
- **State:** `seen_posts.json` is source of truth for dedup
- **Crashes:** Bot resumes from last state (idempotent)
- **No database:** JSON file state only

## Common Issues

1. **Rate limit 429:** Handled by bot with exponential backoff
2. **Slow forums:** Timeout 15s per forum, skips if unreachable
3. **Duplicate posts:** Only happens if state file is deleted
4. **Token invalid:** Check `.env` file and `@BotFather` in Telegram

## Testing

Run locally:
```bash
export TELEGRAM_TOKEN=<test-token>
export TELEGRAM_CHAT_ID=<your-chat-id>
python3 bot.py
```

## Integration with GitHub

- `.github/workflows/test.yml` — validates code
- `.github/workflows/deploy.yml` — (optional) restarts bot on push
- Secrets: `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID` (GitHub Actions)

---

**Last updated:** 2026-08-15
