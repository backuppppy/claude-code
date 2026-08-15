# Contributing to FXP Bot

תודה על ההעניין לתרום! 🙏

## Development Workflow

We follow **Spec-Driven Development (SDD)** — requirements come first, then implementation.

### 1. Start with Specification

**Any change starts in SPEC.md:**

```bash
# Edit SPEC.md and add your requirement
# - What it does
# - Why we need it
# - Success criteria
# - Risk assessment
```

### 2. Plan Implementation

```bash
/plan "Your requirement from SPEC.md"
```

This creates a step-by-step plan with:
- Critical path (what to do first)
- Dependencies
- File changes needed
- Testing approach

### 3. Implement

```bash
/implement "Your requirement"
```

This generates:
- Code changes
- Unit tests
- Updated documentation

### 4. Test Locally

```bash
cd projects/fxp_bot
export TELEGRAM_TOKEN=xoxb-test
export TELEGRAM_CHAT_ID=12345
python3 -m pytest tests/ -v
```

Or run the bot manually:
```bash
python3 bot.py
```

### 5. Create Pull Request

```bash
git checkout -b feature/your-feature
git add projects/fxp_bot/ SPEC.md CLAUDE.md
git commit -m "feat: add your feature

- What you changed
- Why you changed it
- How to test it"
git push origin feature/your-feature
```

### 6. Automated Checks

GitHub Actions runs automatically:
- ✅ `test-fxp-bot.yml` — lint, tests, security
- ✅ `deploy-fxp-bot.yml` — (only on `main` branch)

All checks must pass before merge.

### 7. Code Review

A maintainer will review:
- [ ] Code quality (style, design)
- [ ] Test coverage
- [ ] Documentation updated
- [ ] SPEC.md and CLAUDE.md aligned

### 8. Merge & Deploy

Once approved:
1. Maintainer merges PR to `main`
2. GitHub Actions deploys automatically
3. Telegram bot receives update notification

---

## Development Guidelines

### Code Style

We use `black` for formatting and `flake8` for linting:

```bash
# Auto-format code
black projects/fxp_bot/

# Check for issues
flake8 projects/fxp_bot/
```

### Python Version

- **Minimum:** Python 3.9
- **Tested:** Python 3.11

### Dependencies

Keep them minimal. Current stack:
- `requests` — HTTP calls
- `beautifulsoup4` — HTML parsing
- `pytest` — Testing
- `black`, `flake8`, `isort` — Development tools

**Before adding a dependency:**
- Is it necessary?
- Is it maintained?
- Does it add security risk?
- Are there lighter alternatives?

### Commits

Use **Conventional Commits** format:

```
feat: add new feature
fix: fix bug in X
docs: update README
test: add tests for Y
refactor: simplify Z
chore: update dependencies
```

Example:
```
feat: add forum filtering by category

- Adds category parameter to monitor
- Updates SPEC.md with requirements
- Adds tests for edge cases
```

### Testing

**All code changes need tests:**

```python
# tests/test_fxp_monitor.py
def test_forum_discovery():
    forums = get_forums()
    assert len(forums) > 0
    assert all('id' in f and 'name' in f for f in forums)
```

Run tests before committing:
```bash
python3 -m pytest tests/ -v --cov=projects/fxp_bot
```

### Documentation

Update docs when changing code:

- **Code behavior changes** → Update CLAUDE.md
- **Requirements change** → Update SPEC.md
- **Usage changes** → Update README.md
- **New features** → Update all three

### No Hardcoded Secrets

Never commit:
- `TELEGRAM_TOKEN`
- `TELEGRAM_CHAT_ID`
- API keys
- Passwords

Use environment variables or GitHub Secrets. The CI checks for this automatically.

---

## Reporting Issues

Found a bug? Create an issue on GitHub:

1. **Title:** Be specific ("Bot crashes on missing .env" not "Bot broken")
2. **Reproduction:** Steps to reproduce
3. **Expected:** What should happen
4. **Actual:** What actually happened
5. **Environment:** Python version, OS, etc.

Example:
```
Title: Bot crashes if TELEGRAM_TOKEN is empty

Reproduction:
1. Remove TELEGRAM_TOKEN from .env
2. Run `python3 bot.py`

Expected: Error message asking for token

Actual: Traceback (TypeError: cannot use empty string)

Environment: Python 3.11, Ubuntu 22.04
```

---

## Questions?

- Check [`CLAUDE.md`](CLAUDE.md) — architecture and technical details
- Check [`SPEC.md`](SPEC.md) — what we're building and why
- Open an issue — we'll help!

---

## Code of Conduct

Be respectful. No discrimination, harassment, or bad faith.

---

**Happy coding!** 🚀
