# /deploy — Deployment and Release

## Purpose
Deploy code changes to production and ensure smooth operation.

## Pre-deployment Checklist

- [ ] All tests passing locally
- [ ] Code reviewed and approved
- [ ] CHANGELOG.md updated
- [ ] Version number bumped (if applicable)
- [ ] No secrets committed to git
- [ ] `.env` file in `.gitignore`
- [ ] Commits pushed to GitHub

## Deployment Steps

### 1. Verify GitHub Actions Status
```bash
# Check that test workflow passed
gh run list --workflow test-fxp-bot.yml --limit 1
```

### 2. Create Release (if applicable)
```bash
# Tag the release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### 3. Deploy to Production
The bot runs continuously on your machine. To deploy an update:

```bash
# Stop current bot
pkill -f "python3 bot.py"

# Pull latest code
git pull origin main

# Verify .env still exists with credentials
cat .env

# Start updated bot
nohup python3 bot.py > bot.log 2>&1 &
```

### 4. Verify Deployment
```bash
# Check bot is running
ps aux | grep "python3 bot.py"

# Check recent logs for errors
tail -20 bot.log

# Verify it's sending to Telegram
# (check chat for recent messages)
```

## GitHub Actions Workflows

### Test Workflow (.github/workflows/test-fxp-bot.yml)
Runs automatically on every push:
- Linting (flake8, black, isort)
- Syntax validation
- Security checks (no hardcoded tokens)
- Specification validation

### Deploy Workflow (.github/workflows/deploy-fxp-bot.yml)
Optional manual trigger:
- Validates secrets present
- Creates artifacts
- Sends Telegram notification on success

## Rollback Procedure

If something goes wrong:

```bash
# Stop current version
pkill -f "python3 bot.py"

# Revert to previous commit
git revert <commit-hash>

# Or checkout previous tag
git checkout v0.9.0

# Restart bot
nohup python3 bot.py > bot.log 2>&1 &
```

## Post-deployment Validation

### Within First Hour
- [ ] Bot is online and responding
- [ ] New threads are being detected
- [ ] Telegram messages are sending
- [ ] No errors in bot.log

### Within First 24 Hours
- [ ] Midnight report sent correctly
- [ ] Thread registry file growing normally
- [ ] No memory leaks or crashes
- [ ] Performance acceptable

## Troubleshooting

### Bot not starting
```bash
# Check for syntax errors
python3 -m py_compile bot.py fxp_monitor.py

# Check .env file exists
ls -la .env

# Run in foreground to see errors
python3 bot.py
```

### Missing Telegram messages
```bash
# Check if rate-limited (429 errors)
grep "Rate limited" bot.log

# Verify token and chat ID
grep "TELEGRAM" .env

# Check Telegram API status
```

### Performance issues
```bash
# Monitor memory usage
ps aux | grep python3

# Check for zombie threads
ps aux | grep fxp_monitor

# Review .log file for exceptions
tail -100 bot.log | grep ERROR
```

## Success Criteria
- ✓ Code deployed without errors
- ✓ Bot operational and stable
- ✓ All features working as expected
- ✓ No regressions observed
- ✓ Monitoring active (logs checked regularly)

## Documentation Updates
- [ ] README.md reflects latest version
- [ ] CHANGELOG.md has entry for this release
- [ ] CLAUDE.md updated if architecture changed
- [ ] Known issues documented
