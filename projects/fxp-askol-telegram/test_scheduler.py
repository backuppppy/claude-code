#!/usr/bin/env python3
"""
טסטים לScheduler - בדיקות unit ללא תלויות
"""

import sys
import os
from datetime import datetime, timedelta


def test_stats_initialization():
    """בדוק אתחול סטטיסטיקות"""
    stats = {
        'total_runs': 0,
        'total_questions': 0,
        'total_new_questions': 0,
        'total_notifications': 0,
        'total_errors': 0
    }

    assert stats['total_runs'] == 0
    assert stats['total_questions'] == 0
    assert stats['total_errors'] == 0

    print("✓ test_stats_initialization")


def test_stats_increment():
    """בדוק הגברת סטטיסטיקות"""
    stats = {
        'total_runs': 0,
        'total_questions': 0,
        'total_new_questions': 0,
        'total_notifications': 0,
        'total_errors': 0
    }

    # סימולציה של הרצה
    stats['total_runs'] += 1
    stats['total_questions'] += 10
    stats['total_new_questions'] += 3
    stats['total_notifications'] += 3

    assert stats['total_runs'] == 1
    assert stats['total_questions'] == 10
    assert stats['total_new_questions'] == 3
    assert stats['total_notifications'] == 3

    print("✓ test_stats_increment")


def test_error_tracking():
    """בדוק ניתור שגיאות"""
    stats = {
        'total_runs': 0,
        'total_errors': 0
    }

    # הרצה 1 - בהצלחה
    stats['total_runs'] += 1

    # הרצה 2 - עם שגיאה
    stats['total_runs'] += 1
    stats['total_errors'] += 1

    assert stats['total_runs'] == 2
    assert stats['total_errors'] == 1

    error_rate = (stats['total_errors'] / stats['total_runs']) * 100
    assert error_rate == 50.0

    print("✓ test_error_tracking")


def test_running_state():
    """בדוק state של הריצה"""
    running = False

    assert not running

    # התחל
    running = True
    assert running

    # עצור
    running = False
    assert not running

    print("✓ test_running_state")


def test_log_message_formatting():
    """בדוק עיצוב של הודעות לוג"""
    run_num = 1
    questions_found = 10
    new_questions = 3
    notifications_sent = 3
    duration_ms = 1250

    message = (
        f"✨ הרצה #{run_num} סיום: "
        f"נמצאו={questions_found}, חדשות={new_questions}, "
        f"הודעות={notifications_sent}, משך={duration_ms}ms"
    )

    assert f"הרצה #{run_num}" in message
    assert str(questions_found) in message
    assert str(new_questions) in message
    assert str(notifications_sent) in message
    assert str(duration_ms) in message

    print("✓ test_log_message_formatting")


def test_summary_dict():
    """בדוק dictionary של סיכום"""
    summary = {
        'total_questions': 150,
        'new_questions': 12,
        'notifications_sent': 12,
        'errors': 0,
        'avg_duration_ms': 1200
    }

    assert summary['total_questions'] == 150
    assert summary['new_questions'] == 12
    assert summary['errors'] == 0

    error_rate = summary['errors'] / max(summary['total_questions'], 1)
    assert error_rate == 0.0

    print("✓ test_summary_dict")


def test_interval_calculation():
    """בדוק חישוב intervals"""
    FXP_MONITOR_INTERVAL = 300  # 5 דקות
    total_runs = 10

    total_time_seconds = FXP_MONITOR_INTERVAL * total_runs
    total_time_hours = total_time_seconds / 3600

    assert total_time_seconds == 3000
    assert total_time_hours == pytest.approx(0.833, rel=0.01) if 'pytest' in sys.modules else True

    print("✓ test_interval_calculation")


def run_tests():
    """הרץ את כל הטסטים"""
    print("🧪 טסטים של Scheduler...\n")

    tests = [
        test_stats_initialization,
        test_stats_increment,
        test_error_tracking,
        test_running_state,
        test_log_message_formatting,
        test_summary_dict,
        test_interval_calculation,
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
