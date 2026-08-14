# Deployment Guide - Stips Monitor Bot

## Option 1: Railway (Recommended) ⭐

Railway is free and simple. Your bot runs 24/7 in the cloud.

### Steps:

1. **Go to:** https://railway.app
2. **Sign up** with GitHub
3. **Create new project** → "Deploy from GitHub repo"
4. **Select:** `backuppppy/claude-code`
5. **Select directory:** `projects/stips-monitor`
6. **Add environment variables:**
   - `BOT_TOKEN` = Your bot token
   - `POLLING_INTERVAL` = 300
   - `LOG_LEVEL` = INFO

7. **Deploy!** ✅

Your bot will restart automatically if it crashes.

**Monitoring:** Railway dashboard shows logs and status in real-time.

---

## Option 2: Replit (Free & Easy)

### Steps:

1. **Go to:** https://replit.com
2. **Sign up** with GitHub
3. **Import from GitHub:** `backuppppy/claude-code`
4. **Select folder:** `projects/stips-monitor`
5. **Create `.env` file:**
   ```
   BOT_TOKEN=your_token_here
   POLLING_INTERVAL=300
   LOG_LEVEL=INFO
   ```
6. **Click Run**

---

## Option 3: Docker (Local or VPS)

### Local Testing:

```bash
cp .env.example .env
# Edit .env with your BOT_TOKEN

docker-compose up
```

### Deploy to VPS (Ubuntu):

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone and run
git clone https://github.com/backuppppy/claude-code.git
cd claude-code/projects/stips-monitor

cp .env.example .env
# Edit .env with your BOT_TOKEN

docker-compose up -d
```

Check logs:
```bash
docker-compose logs -f
```

Stop:
```bash
docker-compose down
```

---

## Option 4: GitHub Actions (Scheduled Cloud Run)

### Note:
GitHub Actions has limited runtime (6 hours per run). Better for one-time jobs.

Create `.github/workflows/stips-monitor.yml`:

```yaml
name: Stips Monitor

on:
  schedule:
    - cron: '0 * * * *'  # Run every hour
  workflow_dispatch:  # Manual trigger

jobs:
  bot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd projects/stips-monitor
          pip install -r requirements.txt
      
      - name: Run bot
        env:
          BOT_TOKEN: ${{ secrets.BOT_TOKEN }}
          POLLING_INTERVAL: 300
        run: |
          cd projects/stips-monitor
          python main.py
```

Set GitHub Secret: `BOT_TOKEN` in Settings → Secrets

---

## Comparison

| Platform | Cost | Uptime | Setup | Monitoring |
|----------|------|--------|-------|------------|
| **Railway** | Free tier | 24/7 ⭐ | 5 min | ✅ Dashboard |
| **Replit** | Free | 24/7 ✅ | 3 min | ✅ Console |
| **Docker VPS** | $5-10/mo | 24/7 ✅ | 15 min | SSH logs |
| **GitHub Actions** | Free | Limited | 10 min | Limited |

---

## Troubleshooting

### Bot not sending messages
- Check bot token is correct
- Verify `POLLING_INTERVAL` is set
- Check logs for errors

### Database errors
- For Railway/Replit: Database resets on redeploy
- For Docker: Use persistent volumes

### High logs
- Set `LOG_LEVEL=WARNING` to reduce verbosity

---

## Keep it Running

All cloud options restart automatically on failure. Your bot is resilient! 🤖

For production, we recommend **Railway** for reliability and **Replit** for simplicity.
