# FXP Bot — Project Specification

## 1. Purpose & Goals

Monitor **all forums** on FXP.co.il and notify a Telegram chat of new threads in real-time.

### Success Criteria
- ✅ Discovers and scrapes all forums automatically
- ✅ Sends new posts to Telegram within 2 minutes of posting
- ✅ Never sends duplicate notifications
- ✅ Survives network hiccups and restarts gracefully
- ✅ Respects FXP rate limits (no blocking/IP ban)

---

## 2. Scope

### In Scope
- Monitor FXP forum index and all sub-forums
- Scrape thread titles and URLs
- Send formatted messages to Telegram
- Maintain dedup state across restarts

### Out of Scope
- Full thread content (title + URL only)
- User authentication for Telegram (chat-level only)
- Web UI (CLI + Telegram only)
- Thread archival or search

---

## 3. Requirements

### Functional

| Requirement | Description |
|---|---|
| **Forum Discovery** | Auto-discover all forums from FXP index, refresh every 6 hours |
| **New Post Detection** | Fetch new posts every 60 seconds (configurable) |
| **Deduplication** | Never send the same post twice (state-based) |
| **Telegram Delivery** | Send within 2 min, format with forum name + title + URL |
| **Rate Limiting** | Handle Telegram 429 with exponential backoff |
| **Graceful Failure** | Log errors, continue on transient failures, restore state on restart |

### Non-Functional

| Requirement | Metric |
|---|---|
| **Availability** | 99% uptime (acceptable: 14 min downtime/week) |
| **Latency** | New post → Telegram delivery < 2 min |
| **Memory** | < 100 MB (JSON state only, no DB) |
| **CPU** | < 5% average (idle between checks) |

---

## 4. Configuration

### Environment Variables

```env
TELEGRAM_TOKEN=<bot-token>          # From @BotFather
TELEGRAM_CHAT_ID=<numeric-id>       # Destination chat
CHECK_INTERVAL=120                  # Seconds between scans (default: 60)
```

### State File

- **Location:** `seen_posts.json`
- **Format:** JSON array of post IDs
- **Size limit:** Last 10,000 posts (prevents unbounded growth)
- **Persistence:** Synced to disk after each batch

---

## 5. API & Interfaces

### Telegram API

```
POST https://api.telegram.org/bot{TOKEN}/sendMessage
{
  "chat_id": "...",
  "text": "📂 Forum\n📌 <b>Title</b>\nhttp://...",
  "parse_mode": "HTML"
}
```

**Retry Strategy:**
- 429 (Rate Limit): Sleep `retry_after` seconds, retry once
- 5xx (Server Error): Log and skip, try next cycle
- Network error: Log and skip, try next cycle

### FXP HTML API (Scrape)

- Forum Index: `https://www.fxp.co.il/forum.php`
- Forum Feed: `https://www.fxp.co.il/forumdisplay.php?f={fid}`
- Thread URL: `https://www.fxp.co.il/showthread.php?t={tid}`

**Parsing:**
- Extract forum ID (`f=123`) and name from index
- Extract thread ID (`t=456`) and title from forum page
- Timeout: 15 seconds per forum

---

## 6. Implementation Plan

### Phase 1: Core Monitoring (DONE ✅)
- [x] Dynamic forum discovery
- [x] Parallel scraping (ThreadPoolExecutor)
- [x] State management (seen_posts.json)
- [x] Telegram integration with retry

### Phase 2: Robustness (DONE ✅)
- [x] Error handling (transient failures)
- [x] Rate limit backoff (429)
- [x] Flood guard (>50 posts = silent record)
- [x] Logging to bot.log

### Phase 3: Deployment & CI/CD (IN PROGRESS)
- [ ] GitHub Actions: test + lint
- [ ] GitHub Actions: deploy to server
- [ ] Systemd service file (for production)
- [ ] Docker image (optional)

### Phase 4: Observability (FUTURE)
- [ ] Prometheus metrics (posts/min, errors)
- [ ] Health check endpoint (optional)
- [ ] Alert on 1+ hour downtime

---

## 7. Testing Strategy

### Unit Tests
- `test_fxp_monitor.py` — forum discovery, parsing
- `test_bot.py` — dedup logic, Telegram formatting

### Integration Tests
- Real FXP scrape (slow, runs nightly)
- Real Telegram send (to test chat)

### Manual Tests
```bash
export CHECK_INTERVAL=30  # Fast testing
python3 bot.py
# Should fetch forums, find ~2000 posts, record in state
```

---

## 8. Risks & Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| FXP IP ban | Bot offline | Use rotating delays, UA headers, 1 forum at a time |
| Telegram rate limit | Missing posts | Exponential backoff + batch sends |
| State file corruption | Duplicate floods | Atomic writes, backup on startup |
| Memory leak | Crash after days | Limit seen_posts to 10k entries |

---

## 9. Success Metrics

After deployment, track:
- Posts sent per day (target: ~50-200)
- Telegram send success rate (target: >99%)
- Bot uptime (target: >99%)
- Avg latency post → notification (target: < 2 min)

---

**Version:** 1.0  
**Status:** In Progress (Phase 3)  
**Last Updated:** 2026-08-15
