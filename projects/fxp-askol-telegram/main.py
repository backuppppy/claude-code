#!/usr/bin/env python3
"""
FXP Askol Telegram Bot - Main entry point

ניטור של אתר FXP לשאלות חדשות וקישור הודעות דרך Telegram.
"""

import logging
import time
import signal
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from config import (
    LOG_FILE, LOG_LEVEL, FXP_MONITOR_INTERVAL,
    ENABLE_NOTIFICATIONS, ENABLE_DRY_RUN
)
from database import Database
from scraper import FXPScraper
from telegram_bot import TelegramBot

# הגדר logging
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

        # סטטיסטיקות
        self.stats = {
            'total_runs': 0,
            'total_questions': 0,
            'total_new_questions': 0,
            'total_notifications': 0,
            'total_errors': 0
        }

        self.running = False

    def monitor_questions(self):
        """לולאת ניטור ראשית"""
        start_time = time.time()
        self.stats['total_runs'] += 1

        try:
            logger.info(f"🔍 הרצה #{self.stats['total_runs']} - התחלה...")

            # קבל שאלות אחרונות
            questions = self.scraper.get_latest_questions()
            if not questions:
                logger.warning("⚠️ לא נמצאו שאלות מ-FXP")
                return

            questions_found = len(questions)
            new_questions = 0
            notifications_sent = 0
            errors = None

            # עבור על כל שאלה
            for question in questions:
                question_id = question.get('id')
                title = question.get('title')
                link = question.get('link')

                # בדוק אם כבר עובדה
                if self.db.is_question_processed(question_id):
                    logger.debug(f"שאלה כבר עובדה: {question_id}")
                    continue

                # הוסף למסד הנתונים
                if self.db.add_processed_question(question_id, title, link):
                    new_questions += 1
                    self.stats['total_new_questions'] += 1

                    # שלח הודעת Telegram
                    if ENABLE_NOTIFICATIONS and not ENABLE_DRY_RUN:
                        if self.bot.send_question_notification(question):
                            notifications_sent += 1
                            self.stats['total_notifications'] += 1
                            logger.info(f"✅ הודעה נשלחה: {title[:50]}...")
                        else:
                            self.stats['total_errors'] += 1
                            logger.error(f"❌ שגיאה בשליחה: {title[:50]}...")
                    elif ENABLE_DRY_RUN:
                        logger.info(f"🔄 [DRY RUN] הודעה תישלח: {title[:50]}...")
                        notifications_sent += 1

            # רשום הרצה
            duration_ms = int((time.time() - start_time) * 1000)
            self.db.log_monitoring_run(
                questions_found=questions_found,
                new_questions=new_questions,
                notifications_sent=notifications_sent,
                duration_ms=duration_ms,
                errors=errors
            )

            self.stats['total_questions'] += questions_found

            logger.info(
                f"✨ הרצה #{self.stats['total_runs']} סיום: "
                f"נמצאו={questions_found}, חדשות={new_questions}, "
                f"הודעות={notifications_sent}, משך={duration_ms}ms"
            )

        except Exception as e:
            self.stats['total_errors'] += 1
            logger.error(f"❌ שגיאה בהרצה: {e}", exc_info=True)
            if ENABLE_NOTIFICATIONS:
                self.bot.send_error(str(e))

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

    def start(self):
        """הפעל את המוניטור"""
        logger.info("=" * 60)
        logger.info("🤖 FXP Askol Telegram Bot")
        logger.info(f"⏱️ זמן: {datetime.now()}")
        logger.info(f"📍 Interval: {FXP_MONITOR_INTERVAL} שניות")
        logger.info(f"🔔 הודעות: {'מופעל' if ENABLE_NOTIFICATIONS else 'כבוי'}")
        logger.info(f"🧪 Dry Run: {'כן' if ENABLE_DRY_RUN else 'לא'}")
        logger.info("=" * 60)

        self.running = True

        # קבל מידע בוט
        bot_info = self.bot.get_bot_info()
        if bot_info:
            logger.info(f"✅ בוט מחובר: @{bot_info.get('username')}")
        else:
            logger.error("❌ לא הצליח להתחבר לבוט")

        # הרץ הרצה ראשונית
        logger.info("🔄 הרצה ראשונה...")
        self.monitor_questions()

        # הוסף job לScheduler
        self.scheduler.add_job(
            self.monitor_questions,
            'interval',
            seconds=FXP_MONITOR_INTERVAL,
            id='fxp_monitor'
        )

        logger.info(f"⏳ Scheduler מפעיל... (הרצה כל {FXP_MONITOR_INTERVAL}s)")
        self.scheduler.start()

        # Handle SIGTERM/SIGINT
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    def _signal_handler(self, signum, frame):
        """handle signal"""
        logger.info(f"📛 Signal {signum} התקבל")
        self.shutdown()

    def shutdown(self):
        """כבה בצורה נכונה"""
        if not self.running:
            return

        logger.info("🛑 כיבוי...")
        self.running = False

        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("✓ Scheduler כבוי")

        # שלח סטטוס סיום
        if ENABLE_NOTIFICATIONS:
            self.bot.send_summary({
                'total_questions': self.stats['total_questions'],
                'new_questions': self.stats['total_new_questions'],
                'notifications_sent': self.stats['total_notifications'],
                'errors': self.stats['total_errors'],
                'avg_duration_ms': 0
            })

        self.db.close()
        logger.info("✓ מסד הנתונים סגור")

        logger.info("=" * 60)
        logger.info("📊 סטטיסטיקות סיום:")
        logger.info(f"  הרצות: {self.stats['total_runs']}")
        logger.info(f"  שאלות כוללות: {self.stats['total_questions']}")
        logger.info(f"  שאלות חדשות: {self.stats['total_new_questions']}")
        logger.info(f"  הודעות שנשלחו: {self.stats['total_notifications']}")
        logger.info(f"  שגיאות: {self.stats['total_errors']}")
        logger.info("=" * 60)


def main():
    """נקודת כניסה"""
    monitor = FXPMonitor()
    try:
        monitor.start()
    except Exception as e:
        logger.error(f"שגיאה קריטית: {e}", exc_info=True)
        monitor.shutdown()
        exit(1)


if __name__ == '__main__':
    main()
