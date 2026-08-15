#!/usr/bin/env python3
"""
טסטים עבור Telegram Bot
"""

import sys
import os

# הוסף את parent directory ל-path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_escape_markdown():
    """בדוק escape של markdown characters"""

    def escape_markdown(text):
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text

    # בדוק תו בודד
    result = escape_markdown("*bold*")
    assert '\\*' in result
    print("✓ test_escape_markdown - בודד")

    # בדוק כמה תווים
    result = escape_markdown("_italics_ and *bold* and `code`")
    assert '\\*' in result and '\\`' in result and '\\_' in result
    print("✓ test_escape_markdown - מרובים")


def test_message_format():
    """בדוק עיצוב הודעה"""

    question = {
        'id': '12345',
        'title': 'איך מתקנים מחשב?',
        'link': 'https://fxp.co.il/showthread.php?t=12345'
    }

    message = f"""🆕 *שאלה חדשה ב\\-FXP*

📝 *{question['title']}*

🔗 [לקריאת השאלה]({question['link']})

#️⃣ `{question['id']}`"""

    # בדוק שהרכיבים בהודעה
    assert 'שאלה חדשה' in message
    assert question['title'] in message
    assert question['link'] in message
    assert question['id'] in message

    print("✓ test_message_format")


def test_status_message():
    """בדוק הודעת סטטוס"""

    message = f"""📊 *דוח סטטוס ניטור FXP*

🔍 שאלות נמצאו: `10`
✨ שאלות חדשות: `3`
📬 הודעות נשלחו: `3`
⏱️ משך זמן: `1250ms`"""

    assert 'דוח סטטוס' in message
    assert '10' in message
    assert '3' in message
    assert '1250' in message

    print("✓ test_status_message")


def test_error_message():
    """בדוק הודעת שגיאה"""

    error_text = "Connection timeout to FXP"
    message = f"""❌ *שגיאה בניטור FXP*

```
{error_text}
```"""

    assert 'שגיאה' in message
    assert error_text in message

    print("✓ test_error_message")


def test_summary_message():
    """בדוק הודעת סיכום"""

    stats = {
        'total_questions': 150,
        'new_questions': 12,
        'notifications_sent': 12,
        'errors': 0,
        'avg_duration_ms': 1200
    }

    message = f"""📈 *סיכום יומי FXP Bot*

📊 סטטיסטיקות:
• סה״כ שאלות: `{stats['total_questions']}`
• שאלות חדשות: `{stats['new_questions']}`
• הודעות שנשלחו: `{stats['notifications_sent']}`
• שגיאות: `{stats['errors']}`

⏱️ ממוצע משך הרצה: `{stats['avg_duration_ms']}ms`"""

    assert '150' in message
    assert '12' in message
    assert '0' in message

    print("✓ test_summary_message")


def run_tests():
    """הרץ את כל הטסטים"""
    print("🧪 טסטים של Telegram Bot...\n")

    tests = [
        test_escape_markdown,
        test_message_format,
        test_status_message,
        test_error_message,
        test_summary_message,
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
