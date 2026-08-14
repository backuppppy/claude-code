# Telegram Stips Monitor 🤖

Automatically send new posts from [stips.co.il](https://www.stips.co.il) to Telegram users in real-time.

## Features

✅ Monitors stips.co.il for new posts every 5 minutes  
✅ Sends instant notifications to subscribed Telegram users  
✅ No duplicate messages - tracks all seen posts  
✅ Simple commands: `/subscribe`, `/unsubscribe`, `/status`  
✅ Lightweight and reliable - uses SQLite for persistence  
✅ Error handling and graceful degradation  

## Prerequisites

- Python 3.11 or higher
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))

## Installation

### 1. Clone the project (if not already done)
```bash
cd my-project
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your BOT_TOKEN
nano .env
```

Get your BOT_TOKEN:
1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Follow the prompts to create a new bot
4. Copy the token and paste it in `.env`

### 5. Run the bot
```bash
python main.py
```

## Usage

Once the bot is running, users can:

- **`/start`** - Show welcome message
- **`/subscribe`** - Enable notifications
- **`/unsubscribe`** - Disable notifications
- **`/status`** - Check subscription status
- **`/help`** - Show all commands

## Configuration

Edit `.env` to customize:

| Variable | Default | Description |
|----------|---------|-------------|
| BOT_TOKEN | (required) | Your Telegram bot token |
| POLLING_INTERVAL | 300 | Check frequency in seconds |
| DATABASE_PATH | stips_monitor.db | SQLite database file path |
| LOG_LEVEL | INFO | Logging level (DEBUG/INFO/WARNING/ERROR) |

## How It Works

```
┌─────────────────────────────────────────┐
│   Telegram Users                        │
└─────────────┬───────────────────────────┘
              │
              │ /subscribe, /start, etc.
              │
┌─────────────▼───────────────────────────┐
│   Telegram Bot (main.py)                │
│                                         │
│  ├─ Command Handler                     │
│  └─ Scheduler (APScheduler)             │
│     └─ Monitor Job (every 5 min)        │
└─────────────┬───────────────────────────┘
              │
              ├─────────────────────────────────┐
              │                                 │
    ┌─────────▼──────┐        ┌───────────────▼──┐
    │ Web Monitor    │        │   Database       │
    │ (scraper)      │        │   (SQLite)       │
    └─────────┬──────┘        └───────────────┬──┘
              │                               │
              │ New posts                     │ Users, Posts
              │                               │
    ┌─────────▼──────────────────────────────▼──┐
    │   stips.co.il                             │
    └────────────────────────────────────────────┘
```

## Troubleshooting

### Bot doesn't start
- Check that `BOT_TOKEN` is set in `.env`
- Verify the token is correct (from @BotFather)
- Check internet connection

### Not receiving notifications
- Use `/subscribe` in Telegram
- Check bot is running: `python main.py`
- Monitor logs for errors
- Check `LOG_LEVEL=DEBUG` for detailed output

### Database errors
- Delete `stips_monitor.db` to start fresh
- Check file permissions on the database directory

## Logging

The bot logs to console. Set `LOG_LEVEL=DEBUG` in `.env` for detailed debugging.

Key log entries:
- `Bot started` - Bot is running
- `Parsed X posts` - Web monitor found posts
- `Notification sent to` - Message delivered
- Errors are logged with context for troubleshooting

## Development

### Project Structure
```
my-project/
├── main.py          # Bot application & handlers
├── monitor.py       # Web scraper
├── database.py      # SQLite operations
├── notifier.py      # Message formatting & sending
├── config.py        # Configuration & logging
├── requirements.txt # Dependencies
├── .env.example     # Config template
├── README.md        # This file
└── specs/          # Spec documents
```

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Check logs with `LOG_LEVEL=DEBUG`
- Review the spec documents in `specs/`
- Open an issue on GitHub

---

**Happy monitoring! 📢**
