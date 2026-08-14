import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import BOT_TOKEN, POLLING_INTERVAL, logger
from database import Database
from monitor import WebMonitor
from notifier import Notifier

db = Database()
monitor = WebMonitor()
notifier = Notifier()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db.add_user(user_id)

    message = """🤖 <b>Welcome to Stips Monitor!</b>

I automatically send you new posts from stips.co.il

Use /subscribe to get notifications
Use /unsubscribe to stop notifications
Use /status to check your subscription"""

    await update.message.reply_text(message, parse_mode='HTML')
    logger.info(f"User {user_id} started bot")

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db.add_user(user_id)
    db.subscribe_user(user_id)

    await update.message.reply_text(
        "✅ <b>Subscribed!</b>\n\nYou will now receive notifications about new posts.",
        parse_mode='HTML'
    )
    logger.info(f"User {user_id} subscribed")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db.unsubscribe_user(user_id)

    await update.message.reply_text(
        "❌ <b>Unsubscribed</b>\n\nYou won't receive notifications anymore.\n\nUse /subscribe to turn them back on.",
        parse_mode='HTML'
    )
    logger.info(f"User {user_id} unsubscribed")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_subscribed = db.is_subscribed(user_id)

    status_text = "✅ Subscribed" if is_subscribed else "❌ Not Subscribed"
    message = f"""<b>Your Status</b>

{status_text}

Use /subscribe or /unsubscribe to change your preferences."""

    await update.message.reply_text(message, parse_mode='HTML')
    logger.info(f"User {user_id} checked status")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """<b>Available Commands</b>

/start - Welcome message
/subscribe - Enable notifications
/unsubscribe - Disable notifications
/status - Check subscription status
/help - Show this message"""

    await update.message.reply_text(message, parse_mode='HTML')

async def monitor_job(context: ContextTypes.DEFAULT_TYPE):
    logger.info("Starting monitoring job")
    try:
        posts = monitor.get_new_posts(db)
        if posts:
            await notifier.notify_users(context.application, db, posts)
    except Exception as e:
        logger.error(f"Error in monitor job: {e}")

async def post_init(app: Application):
    app.job_queue.run_repeating(monitor_job, interval=POLLING_INTERVAL, first=10)
    logger.info(f"Bot started. Polling interval: {POLLING_INTERVAL}s")

def main():
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("help", help_command))

    app.post_init = post_init

    app.run_polling()

if __name__ == '__main__':
    main()
