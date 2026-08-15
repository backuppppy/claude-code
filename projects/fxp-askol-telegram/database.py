import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.conn = None
        self.init_db()

    def init_db(self):
        """Initialize database and create tables"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()

        # Table for processed questions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_questions (
                id INTEGER PRIMARY KEY,
                fxp_question_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                link TEXT NOT NULL,
                category TEXT,
                created_at TIMESTAMP,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_to_telegram BOOLEAN DEFAULT FALSE
            )
        ''')

        # Table for monitoring logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_log (
                id INTEGER PRIMARY KEY,
                run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                questions_found INTEGER,
                new_questions INTEGER,
                notifications_sent INTEGER,
                errors TEXT,
                duration_ms INTEGER
            )
        ''')

        # Table for telegram users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telegram_users (
                user_id INTEGER PRIMARY KEY,
                chat_id INTEGER UNIQUE NOT NULL,
                enabled BOOLEAN DEFAULT TRUE,
                subscribed_categories TEXT,
                last_notification TIMESTAMP
            )
        ''')

        self.conn.commit()
        logger.info(f"Database initialized: {self.db_path}")

    def add_processed_question(self, fxp_id, title, link, category=None):
        """Add a processed question"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO processed_questions
                (fxp_question_id, title, link, category, sent_to_telegram)
                VALUES (?, ?, ?, ?, ?)
            ''', (fxp_id, title, link, category, True))
            self.conn.commit()
            logger.debug(f"Added question: {fxp_id}")
            return True
        except sqlite3.IntegrityError:
            logger.debug(f"Question already exists: {fxp_id}")
            return False

    def is_question_processed(self, fxp_id):
        """Check if question was already processed"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM processed_questions WHERE fxp_question_id = ?', (fxp_id,))
        return cursor.fetchone() is not None

    def log_monitoring_run(self, questions_found, new_questions, notifications_sent, duration_ms, errors=None):
        """Log a monitoring run"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO monitoring_log
            (questions_found, new_questions, notifications_sent, duration_ms, errors)
            VALUES (?, ?, ?, ?, ?)
        ''', (questions_found, new_questions, notifications_sent, duration_ms, errors))
        self.conn.commit()

    def get_recent_logs(self, limit=10):
        """Get recent monitoring logs"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM monitoring_log
            ORDER BY run_at DESC
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
