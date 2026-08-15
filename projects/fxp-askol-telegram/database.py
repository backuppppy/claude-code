import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from config import DATABASE_PATH

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.conn = None
        self.init_db()

    def init_db(self):
        """יצור טבלאות בסיס נתונים עם indexes"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        # טבלת שאלות מעובדות
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fxp_question_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                link TEXT NOT NULL,
                category TEXT,
                created_at TIMESTAMP,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_to_telegram BOOLEAN DEFAULT FALSE
            )
        ''')

        # indexes לביצועים טובים
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fxp_id ON processed_questions(fxp_question_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_processed_at ON processed_questions(processed_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON processed_questions(category)')

        # טבלת יומני ניטור
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                questions_found INTEGER DEFAULT 0,
                new_questions INTEGER DEFAULT 0,
                notifications_sent INTEGER DEFAULT 0,
                errors TEXT,
                duration_ms INTEGER DEFAULT 0,
                success BOOLEAN DEFAULT TRUE
            )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_run_at ON monitoring_log(run_at)')

        # טבלת משתמשים בטלגרם
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telegram_users (
                user_id INTEGER PRIMARY KEY,
                chat_id INTEGER UNIQUE NOT NULL,
                enabled BOOLEAN DEFAULT TRUE,
                subscribed_categories TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_notification TIMESTAMP
            )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_id ON telegram_users(chat_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_enabled ON telegram_users(enabled)')

        # טבלת סטטיסטיקות
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                total_questions INTEGER DEFAULT 0,
                new_questions INTEGER DEFAULT 0,
                notifications_sent INTEGER DEFAULT 0,
                errors_count INTEGER DEFAULT 0,
                avg_duration_ms INTEGER DEFAULT 0
            )
        ''')

        self.conn.commit()
        logger.info(f"בסיס נתונים אתחל: {self.db_path}")

    def add_processed_question(self, fxp_id, title, link, category=None, created_at=None):
        """הוסף שאלה מעובדת"""
        if not fxp_id or not title or not link:
            logger.warning("חסרים נתונים נדרשים")
            return False

        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO processed_questions
                (fxp_question_id, title, link, category, created_at, sent_to_telegram)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (fxp_id, title, link, category, created_at or datetime.now(), True))
            self.conn.commit()
            logger.debug(f"נוסף שאלה: {fxp_id}")
            return True
        except sqlite3.IntegrityError:
            logger.debug(f"שאלה כבר קיימת: {fxp_id}")
            return False
        except Exception as e:
            logger.error(f"שגיאה בהוספת שאלה: {e}")
            return False

    def is_question_processed(self, fxp_id):
        """בדוק אם שאלה כבר עובדה"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('SELECT 1 FROM processed_questions WHERE fxp_question_id = ?', (fxp_id,))
            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"שגיאה בבדיקה: {e}")
            return False

    def get_processed_questions_count(self):
        """קבל מספר שאלות מעובדות"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM processed_questions')
        return cursor.fetchone()[0]

    def get_recent_questions(self, limit=20):
        """קבל שאלות אחרונות"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM processed_questions
            ORDER BY processed_at DESC
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()

    def log_monitoring_run(self, questions_found, new_questions, notifications_sent, duration_ms, errors=None):
        """רשום הרצה של ניטור"""
        cursor = self.conn.cursor()
        try:
            success = errors is None or errors == ""
            cursor.execute('''
                INSERT INTO monitoring_log
                (questions_found, new_questions, notifications_sent, duration_ms, errors, success)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (questions_found, new_questions, notifications_sent, duration_ms, errors, success))
            self.conn.commit()
            logger.debug(f"רשום ניטור: {new_questions} חדשות")
            return True
        except Exception as e:
            logger.error(f"שגיאה ברישום: {e}")
            return False

    def get_recent_logs(self, limit=10):
        """קבל יומני ניטור אחרונים"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                SELECT * FROM monitoring_log
                ORDER BY run_at DESC
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"שגיאה בקבלת יומנים: {e}")
            return []

    def get_statistics(self, days=7):
        """קבל סטטיסטיקות למספר ימים"""
        cursor = self.conn.cursor()
        try:
            start_date = datetime.now() - timedelta(days=days)
            cursor.execute('''
                SELECT
                    COUNT(DISTINCT fxp_question_id) as total_questions,
                    COUNT(*) as processed_count,
                    AVG(julianday('now') - julianday(processed_at)) as avg_days_old
                FROM processed_questions
                WHERE processed_at > ?
            ''', (start_date,))
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"שגיאה בקבלת סטטיסטיקות: {e}")
            return None

    def cleanup_old_data(self, days=30):
        """נקה נתונים ישנים"""
        cursor = self.conn.cursor()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cursor.execute('''
                DELETE FROM processed_questions
                WHERE processed_at < ? AND sent_to_telegram = TRUE
            ''', (cutoff_date,))
            deleted = cursor.rowcount
            self.conn.commit()
            logger.info(f"נמחקו {deleted} שאלות ישנות")
            return deleted
        except Exception as e:
            logger.error(f"שגיאה בניקוי: {e}")
            return 0

    def get_status(self):
        """קבל סטטוס בסיס הנתונים"""
        try:
            total_questions = self.get_processed_questions_count()
            recent_logs = self.get_recent_logs(1)
            last_run = recent_logs[0] if recent_logs else None

            return {
                'total_questions': total_questions,
                'last_run': last_run['run_at'] if last_run else None,
                'database_path': self.db_path,
                'connected': self.conn is not None
            }
        except Exception as e:
            logger.error(f"שגיאה בקבלת סטטוס: {e}")
            return None

    def close(self):
        """סגור חיבור לבסיס הנתונים"""
        if self.conn:
            self.conn.close()
            logger.info("בסיס הנתונים סגור")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
