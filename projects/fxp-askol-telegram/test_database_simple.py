#!/usr/bin/env python3
"""
טסטים בסיסיים ללא תלויות חיצוניות
"""

import os
import tempfile
import sqlite3
from datetime import datetime


def create_test_db():
    """יצור בסיס נתונים זמני לטסט"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    return path


def test_table_creation():
    """בדוק יצירת טבלאות"""
    db_path = create_test_db()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # יצור טבלאות
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

        # בדוק שהטבלאות קיימות
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        assert 'processed_questions' in tables
        assert 'monitoring_log' in tables

        conn.close()
        print("✓ test_table_creation")

    finally:
        os.unlink(db_path)


def test_insert_question():
    """בדוק הוספת שאלה"""
    db_path = create_test_db()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # יצור טבלה
        cursor.execute('''
            CREATE TABLE processed_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fxp_question_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                link TEXT NOT NULL,
                category TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_to_telegram BOOLEAN DEFAULT FALSE
            )
        ''')

        # הוסף שאלה
        cursor.execute('''
            INSERT INTO processed_questions
            (fxp_question_id, title, link, category, sent_to_telegram)
            VALUES (?, ?, ?, ?, ?)
        ''', ("123", "איך מתקנים מחשב", "https://fxp.co.il/t/123", "טכנולוגיה", True))

        conn.commit()

        # בדוק
        cursor.execute("SELECT COUNT(*) FROM processed_questions")
        count = cursor.fetchone()[0]
        assert count == 1

        cursor.execute("SELECT title FROM processed_questions WHERE fxp_question_id = ?", ("123",))
        title = cursor.fetchone()[0]
        assert title == "איך מתקנים מחשב"

        conn.close()
        print("✓ test_insert_question")

    finally:
        os.unlink(db_path)


def test_duplicate_prevention():
    """בדוק שאל דופליקט לא יכנסו"""
    db_path = create_test_db()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # יצור טבלה
        cursor.execute('''
            CREATE TABLE processed_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fxp_question_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                link TEXT NOT NULL
            )
        ''')

        # הוסף שתי שאלות עם אותו ID
        cursor.execute('''
            INSERT INTO processed_questions
            (fxp_question_id, title, link)
            VALUES (?, ?, ?)
        ''', ("123", "שאלה 1", "link1"))

        conn.commit()

        # נסה להוסיף דופליקט
        try:
            cursor.execute('''
                INSERT INTO processed_questions
                (fxp_question_id, title, link)
                VALUES (?, ?, ?)
            ''', ("123", "שאלה 2", "link2"))
            conn.commit()
            assert False, "יש לבדוק שדופליקט זורק שגיאה"
        except sqlite3.IntegrityError:
            pass  # זה מה שצפוי

        conn.close()
        print("✓ test_duplicate_prevention")

    finally:
        os.unlink(db_path)


def test_log_insertion():
    """בדוק הוספת יומן"""
    db_path = create_test_db()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # יצור טבלה
        cursor.execute('''
            CREATE TABLE monitoring_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                questions_found INTEGER DEFAULT 0,
                new_questions INTEGER DEFAULT 0,
                notifications_sent INTEGER DEFAULT 0,
                duration_ms INTEGER DEFAULT 0
            )
        ''')

        # הוסף יומן
        cursor.execute('''
            INSERT INTO monitoring_log
            (questions_found, new_questions, notifications_sent, duration_ms)
            VALUES (?, ?, ?, ?)
        ''', (10, 3, 3, 1250))

        conn.commit()

        # בדוק
        cursor.execute("SELECT COUNT(*) FROM monitoring_log")
        count = cursor.fetchone()[0]
        assert count == 1

        cursor.execute("SELECT new_questions FROM monitoring_log")
        new_q = cursor.fetchone()[0]
        assert new_q == 3

        conn.close()
        print("✓ test_log_insertion")

    finally:
        os.unlink(db_path)


def test_indexes_creation():
    """בדוק יצירת indexes"""
    db_path = create_test_db()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # יצור טבלה ו-indexes
        cursor.execute('''
            CREATE TABLE processed_questions (
                id INTEGER PRIMARY KEY,
                fxp_question_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                link TEXT NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('CREATE INDEX idx_fxp_id ON processed_questions(fxp_question_id)')
        cursor.execute('CREATE INDEX idx_processed_at ON processed_questions(processed_at)')

        # בדוק שהindexes קיימים
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]

        assert 'idx_fxp_id' in indexes
        assert 'idx_processed_at' in indexes

        conn.close()
        print("✓ test_indexes_creation")

    finally:
        os.unlink(db_path)


def run_tests():
    """הרץ את כל הטסטים"""
    print("🧪 טסטים של Database...\n")

    tests = [
        test_table_creation,
        test_insert_question,
        test_duplicate_prevention,
        test_log_insertion,
        test_indexes_creation,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1

    print(f"\n📊 תוצאות: {passed} הצליחו, {failed} נכשלו")
    return failed == 0


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
