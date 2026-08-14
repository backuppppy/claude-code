import sqlite3
from datetime import datetime
from contextlib import contextmanager
from config import DATABASE_PATH, logger

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    subscribed BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    published_date DATETIME,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sent BOOLEAN DEFAULT 0
                )
            ''')

            logger.info("Database initialized")

    def add_user(self, telegram_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO users (telegram_id, subscribed) VALUES (?, 1)',
                (telegram_id,)
            )
            logger.info(f"User {telegram_id} added")

    def subscribe_user(self, telegram_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET subscribed = 1, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = ?',
                (telegram_id,)
            )

    def unsubscribe_user(self, telegram_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET subscribed = 0, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = ?',
                (telegram_id,)
            )

    def is_subscribed(self, telegram_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT subscribed FROM users WHERE telegram_id = ?', (telegram_id,))
            row = cursor.fetchone()
            return row and row['subscribed'] == 1 if row else False

    def get_subscribed_users(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT telegram_id FROM users WHERE subscribed = 1')
            return [row['telegram_id'] for row in cursor.fetchall()]

    def add_post(self, title, url, published_date):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    'INSERT INTO posts (title, url, published_date) VALUES (?, ?, ?)',
                    (title, url, published_date)
                )
                logger.info(f"Post added: {title}")
                return True
            except sqlite3.IntegrityError:
                logger.debug(f"Post already exists: {url}")
                return False

    def post_exists(self, url):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM posts WHERE url = ?', (url,))
            return cursor.fetchone() is not None

    def get_unsent_posts(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, title, url, published_date FROM posts WHERE sent = 0 ORDER BY published_date DESC')
            return cursor.fetchall()

    def mark_post_sent(self, post_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE posts SET sent = 1 WHERE id = ?', (post_id,))
