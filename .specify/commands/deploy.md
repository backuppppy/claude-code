# /deploy — Deploy to Production

## Usage
```
/deploy [environment]
```

## Purpose
Safely deploys FXP Bot to production.

## Environments
```
/deploy staging         # Test environment (optional)
/deploy production      # Production (GitHub Actions)
/deploy rollback        # Revert to previous version
```

## Checklist (Pre-Deployment)
- [ ] All tests pass (`/test`)
- [ ] Code reviewed and approved
- [ ] SPEC.md updated with changes
- [ ] CLAUDE.md reflects current state
- [ ] No hardcoded secrets
- [ ] Environment variables set in GitHub Secrets
- [ ] Rollback plan documented

## Deployment Process

### Automatic (GitHub Actions)
1. Merge PR to `main`
2. `.github/workflows/deploy-fxp-bot.yml` triggers
3. Validates secrets
4. Prepares deployment package
5. Creates artifact
6. Sends Telegram notification
7. Creates GitHub deployment record

### Manual
```bash
# SSH to production server
ssh deploy@fxp.example.com

# Navigate to bot directory
cd /app/fxp_bot

# Pull latest
git pull origin main

# Restart bot
systemctl restart fxp-bot

# Check logs
journalctl -u fxp-bot -f
```

## Post-Deployment Verification
1. Check bot logs: `tail -f bot.log`
2. Verify Telegram notifications arriving
3. Monitor resource usage: `top`, `free`
4. Check error rates (if metrics enabled)

## Rollback
```bash
# If deployment fails
git revert <bad-commit-sha>
git push origin main

# Or manually restart with previous version
systemctl restart fxp-bot
```

## After Deployment
- [ ] Monitor logs for errors
- [ ] Check Telegram notifications
- [ ] Verify no duplicate posts
- [ ] Monitor resource usage (CPU, memory)
- [ ] Update CHANGELOG.md with version note

---

**Important:** Deploy during low-traffic hours if possible.

**Related:** `/test`, `/plan`, `/specify`
