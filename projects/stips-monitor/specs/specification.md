# Telegram Stips Monitor - Specification

## Overview

A Telegram bot that monitors the website stips.co.il for new posts and automatically sends them to subscribed users in real-time.

## User Stories

### User: Regular Site Visitor
- **As a** regular visitor to stips.co.il
- **I want to** receive Telegram notifications when new posts are published
- **So that** I don't miss any important updates and can check them immediately on mobile

### User: Bot Operator
- **As a** bot operator/admin
- **I want to** start/stop the monitoring service easily
- **So that** I can manage the bot's operations without coding

### User: Telegram Subscriber
- **As a** Telegram user
- **I want to** easily subscribe/unsubscribe from notifications
- **So that** I have full control over what I receive

## Features

### Core Features
1. **Web Monitoring**
   - Continuously monitor stips.co.il for new posts
   - Detect posts within 1-2 minutes of publishing
   - Track already-seen posts to avoid duplicates

2. **Telegram Bot Interface**
   - `/start` - Welcome message and subscribe option
   - `/subscribe` - Enable notifications
   - `/unsubscribe` - Disable notifications
   - `/status` - Show current subscription status

3. **Post Notifications**
   - Send formatted message with:
     - Post title
     - Post link
     - Short description (if available)
     - Publication date
   - One message per post per user

4. **Error Handling**
   - Handle network failures gracefully
   - Retry failed sends
   - Log all errors for debugging

## Non-Functional Requirements

- **Performance**: Start monitoring within 30 seconds of bot launch
- **Reliability**: 99% uptime target
- **Scalability**: Support 100+ concurrent users
- **Security**: Store bot token securely via environment variable
- **Logging**: Detailed logs for troubleshooting

## User Interface

### Telegram Messages

**Welcome Message:**
```
Welcome! I monitor stips.co.il for new posts.
Use /subscribe to get notifications
Use /help for more commands
```

**Post Notification:**
```
📢 New Post on Stips

Title: [Post Title]
🔗 [Link to post]
📅 [Date Published]
```

**Status Message:**
```
Status: ✅ Subscribed
Last update: [time]
```

## Success Criteria

- ✅ Bot starts and connects to Telegram API
- ✅ Can detect new posts on stips.co.il
- ✅ Sends notifications to subscribed users within 2 minutes
- ✅ Users can subscribe/unsubscribe via commands
- ✅ No duplicate notifications sent
- ✅ Graceful error handling for network issues
- ✅ Detailed logging for debugging
