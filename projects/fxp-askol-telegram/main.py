#!/usr/bin/env python3
"""
FXP Askol Telegram Bot - Main entry point

Monitors FXP website for new questions and sends Telegram notifications.
"""

import logging
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from config import (
    LOG_FILE, LOG_LEVEL, FXP_MONITOR_INTERVAL,
    ENABLE_NOTIFICATIONS, ENABLE_DRY_RUN
)
from database import Database
from scraper import FXPScraper
from telegram_bot import TelegramBot

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FXPMonitor:
    def __init__(self):
        self.scraper = FXPScraper()
        self.bot = TelegramBot()
        self.db = Database()
        self.scheduler = BackgroundScheduler()

    def monitor_questions(self):
        """Main monitoring loop"""
        start_time = time.time()
        try:
            logger.info("Starting monitoring run...")

            # Fetch latest questions
            questions = self.scraper.get_latest_questions()
            if not questions:
                logger.warning("No questions found from scraper")
                return

            questions_found = len(questions)
            new_questions = 0
            notifications_sent = 0

            # Process each question
            for question in questions:
                question_id = question.get('id')
                title = question.get('title')
                link = question.get('link')

                # Check if already processed
                if self.db.is_question_processed(question_id):
                    logger.debug(f"Question already processed: {question_id}")
                    continue

                # Add to database
                if self.db.add_processed_question(question_id, title, link):
                    new_questions += 1

                    # Send Telegram notification
                    if ENABLE_NOTIFICATIONS and not ENABLE_DRY_RUN:
                        if self.bot.send_question_notification(question):
                            notifications_sent += 1
                            logger.info(f"Sent notification for: {title}")
                        else:
                            logger.error(f"Failed to send notification for: {title}")
                    elif ENABLE_DRY_RUN:
                        logger.info(f"[DRY RUN] Would send: {title}")
                        notifications_sent += 1

            # Log monitoring run
            duration_ms = int((time.time() - start_time) * 1000)
            self.db.log_monitoring_run(
                questions_found=questions_found,
                new_questions=new_questions,
                notifications_sent=notifications_sent,
                duration_ms=duration_ms
            )

            logger.info(
                f"Monitoring complete: found={questions_found}, "
                f"new={new_questions}, sent={notifications_sent}, "
                f"duration={duration_ms}ms"
            )

        except Exception as e:
            logger.error(f"Error during monitoring: {e}", exc_exc_info=True)
            if ENABLE_NOTIFICATIONS:
                self.bot.send_error(str(e))

    def start(self):
        """Start monitoring scheduler"""
        logger.info(f"Starting FXP Monitor (interval: {FXP_MONITOR_INTERVAL}s)")

        # Add monitoring job
        self.scheduler.add_job(
            self.monitor_questions,
            'interval',
            seconds=FXP_MONITOR_INTERVAL,
            id='fxp_monitor'
        )

        # Start scheduler
        self.scheduler.start()

        try:
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt - shutting down...")
            self.shutdown()

    def shutdown(self):
        """Shutdown gracefully"""
        logger.info("Shutting down FXP Monitor...")
        if self.scheduler.running:
            self.scheduler.shutdown()
        self.db.close()
        logger.info("Monitor stopped")

def main():
    """Entry point"""
    logger.info("=" * 50)
    logger.info("FXP Askol Telegram Bot")
    logger.info(f"Time: {datetime.now()}")
    logger.info("=" * 50)

    monitor = FXPMonitor()

    # Run once immediately, then schedule
    logger.info("Running initial check...")
    monitor.monitor_questions()

    # Start scheduler for continuous monitoring
    monitor.start()

if __name__ == '__main__':
    main()
