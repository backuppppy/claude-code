# /test — Testing and Validation

## Purpose
Verify that the implementation meets the specification and doesn't break existing functionality.

## Testing Strategy

### 1. Code Quality Tests
```bash
# Format check
black --check bot.py fxp_monitor.py

# Linting
flake8 bot.py fxp_monitor.py

# Import sorting
isort --check-only bot.py fxp_monitor.py
```

### 2. Unit Tests
- Test individual functions in isolation
- Mock external dependencies (Telegram API, FXP website)
- Use pytest framework

```bash
pytest tests/ -v
```

### 3. Integration Tests
- Test bot with actual forum data
- Verify Telegram message delivery
- Check state file persistence

### 4. Manual Testing
- Start bot locally with test token
- Monitor logs for errors
- Verify new features work as intended

## Test Checklist

### Daily Report Feature
- [ ] Bot sends startup report with today's threads
- [ ] Bot sends midnight report with yesterday's threads
- [ ] Thread registry file created and updated
- [ ] Threads grouped correctly by forum
- [ ] Timestamps stored in ISO format
- [ ] Registry trimmed to 5,000 entries
- [ ] Bot handles day boundary transitions
- [ ] No data loss on restart

### Regression Tests
- [ ] Bot still sends new thread alerts
- [ ] Deduplication still works (seen_posts.json)
- [ ] Rate limiting (429 retry) still works
- [ ] Flood guard (>50 posts) still works
- [ ] Bot recovers from network errors
- [ ] Telegram message formatting correct

## Running Tests Locally

```bash
# Set up environment
export TELEGRAM_TOKEN=<test-token>
export TELEGRAM_CHAT_ID=<your-chat-id>

# Run code quality checks
black --check *.py
flake8 *.py
isort --check-only *.py

# Test bot locally (will send real Telegram messages to test chat)
python3 bot.py &
# Monitor logs and Telegram output for 5 minutes
# Press Ctrl+C to stop
```

## Success Criteria
- ✓ All code quality checks pass
- ✓ No new security issues introduced
- ✓ All acceptance criteria from specification met
- ✓ No regressions in existing features
- ✓ Bot stable for 24+ hours of operation

## Output
- Test results summary
- Coverage report (if applicable)
- List of verified features
- Any known limitations or caveats
