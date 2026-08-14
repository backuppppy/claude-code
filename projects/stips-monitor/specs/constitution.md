# Telegram Stips Monitor Constitution

## Core Principles

### I. Reliability First
The bot must reliably deliver all posts from stips.co.il to Telegram users without missing updates. Graceful error handling and retry mechanisms are mandatory.

### II. Real-Time Monitoring
Updates should be detected and sent within minutes of posting. Polling frequency must balance responsiveness with resource efficiency.

### III. User-Centric Design
Simple commands, clear messages, and intuitive controls. Users should easily subscribe/unsubscribe from notifications.

### IV. Data Integrity
No duplicate messages sent. Posts must be accurately captured with full context (title, link, date).

### V. Minimal Dependencies
Use lightweight libraries. Favor built-in Python features over heavy frameworks where possible.

## Technical Constraints

- **Language**: Python 3.11+
- **Hosting**: Lightweight, can run on budget VPS or local machine
- **Database**: SQLite for tracking seen posts
- **Telegram**: Official python-telegram-bot library

## Quality Standards

- All core functions must have unit tests
- Logging must be structured and debug-friendly
- Configuration should be environment-based (.env)
- Code must handle network failures gracefully

## Governance

This constitution guides all implementation decisions. Deviations require documented justification.

**Version**: 1.0 | **Ratified**: 2026-08-14 | **Last Amended**: 2026-08-14
