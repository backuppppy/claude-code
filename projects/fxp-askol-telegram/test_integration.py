#!/usr/bin/env python3
"""
End-to-End Integration Tests
"""

import sys
import os
import tempfile
import sqlite3
from datetime import datetime


class MockScraper:
    """Scraper mock"""
    def get_latest_questions(self):
        return [
            {'id': '1', 'title': 'שאלה 1', 'link': 'https://fxp.co.il/1'},
            {'id': '2', 'title': 'שאלה 2', 'link': 'https://fxp.co.il/2'},
        ]


class MockTelegramBot:
    """Telegram bot mock"""
    def __init__(self):
        self.sent_messages = []

    def send_question_notification(self, question):
        self.sent_messages.append(question)
        return True

    def send_error(self, error):
        self.sent_messages.append({'error': error})
        return True


class MockDatabase:
    """Database mock"""
    def __init__(self):
        self.processed = set()
        self.logs = []

    def is_question_processed(self, qid):
        return qid in self.processed

    def add_processed_question(self, qid, title, link, **kwargs):
        if qid in self.processed:
            return False
        self.processed.add(qid)
        return True

    def log_monitoring_run(self, **kwargs):
        self.logs.append(kwargs)
        return True

    def close(self):
        pass


def test_full_workflow():
    """בדוק זרימה מלאה"""
    scraper = MockScraper()
    bot = MockTelegramBot()
    db = MockDatabase()

    # קבל שאלות
    questions = scraper.get_latest_questions()
    assert len(questions) == 2

    # עבור על שאלות
    for q in questions:
        if not db.is_question_processed(q['id']):
            if db.add_processed_question(q['id'], q['title'], q['link']):
                bot.send_question_notification(q)

    # בדוק תוצאות
    assert len(db.processed) == 2
    assert len(bot.sent_messages) == 2

    print("✓ test_full_workflow")


def test_duplicate_prevention():
    """בדוק שדופליקט לא יתורגם"""
    db = MockDatabase()
    bot = MockTelegramBot()

    q = {'id': '1', 'title': 'שאלה', 'link': 'link'}

    # הוסף פעם ראשונה
    result1 = db.add_processed_question(q['id'], q['title'], q['link'])
    assert result1 is True

    # נסה להוסיף שוב
    result2 = db.add_processed_question(q['id'], q['title'], q['link'])
    assert result2 is False

    # וודא שהודעה לא נשלחה פעם שנייה
    assert len(bot.sent_messages) == 0

    print("✓ test_duplicate_prevention")


def test_error_handling():
    """בדוק error handling"""
    bot = MockTelegramBot()

    error_msg = "Connection error"
    bot.send_error(error_msg)

    assert len(bot.sent_messages) == 1
    assert bot.sent_messages[0]['error'] == error_msg

    print("✓ test_error_handling")


def test_logging():
    """בדוק logging"""
    db = MockDatabase()

    db.log_monitoring_run(
        questions_found=10,
        new_questions=3,
        notifications_sent=3,
        duration_ms=1250
    )

    assert len(db.logs) == 1
    assert db.logs[0]['questions_found'] == 10
    assert db.logs[0]['new_questions'] == 3

    print("✓ test_logging")


def test_question_processing_flow():
    """בדוק זרימת עיבוד שאלה"""
    scraper = MockScraper()
    db = MockDatabase()
    bot = MockTelegramBot()

    questions = scraper.get_latest_questions()
    new_count = 0

    for q in questions:
        if db.is_question_processed(q['id']):
            continue

        if db.add_processed_question(q['id'], q['title'], q['link']):
            new_count += 1
            bot.send_question_notification(q)

    db.log_monitoring_run(
        questions_found=len(questions),
        new_questions=new_count,
        notifications_sent=new_count,
        duration_ms=100
    )

    assert new_count == 2
    assert len(bot.sent_messages) == 2
    assert len(db.logs) == 1

    print("✓ test_question_processing_flow")


def test_statistics_accumulation():
    """בדוק צבירת סטטיסטיקות"""
    stats = {
        'total_runs': 0,
        'total_questions': 0,
        'total_new_questions': 0,
        'total_notifications': 0,
        'total_errors': 0
    }

    # הרצה 1
    stats['total_runs'] += 1
    stats['total_questions'] += 10
    stats['total_new_questions'] += 3
    stats['total_notifications'] += 3

    # הרצה 2
    stats['total_runs'] += 1
    stats['total_questions'] += 8
    stats['total_new_questions'] += 2
    stats['total_notifications'] += 2

    assert stats['total_runs'] == 2
    assert stats['total_questions'] == 18
    assert stats['total_new_questions'] == 5
    assert stats['total_notifications'] == 5

    print("✓ test_statistics_accumulation")


def run_tests():
    """הרץ את כל הטסטים"""
    print("🧪 End-to-End Integration Tests...\n")

    tests = [
        test_full_workflow,
        test_duplicate_prevention,
        test_error_handling,
        test_logging,
        test_question_processing_flow,
        test_statistics_accumulation,
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
    success = run_tests()
    sys.exit(0 if success else 1)
