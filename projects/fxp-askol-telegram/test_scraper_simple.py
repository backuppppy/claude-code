#!/usr/bin/env python3
"""
Simple scraper unit tests - no external dependencies needed
"""

import re
import sys


def extract_question_id(link):
    """Extract question ID from link"""
    try:
        # Pattern 1: showthread.php?t=12345678
        if '?t=' in link:
            question_id = link.split('?t=')[-1].split('&')[0]
            if question_id.isdigit():
                return question_id

        # Pattern 2: /thread/12345678/
        if '/thread/' in link:
            parts = link.split('/thread/')[-1].split('/')
            if parts[0].isdigit():
                return parts[0]

        # Pattern 3: showthread.php?p=12345678
        if '?p=' in link:
            question_id = link.split('?p=')[-1].split('&')[0]
            if question_id.isdigit():
                return question_id

        # Pattern 4: Try to extract any sequence of digits from URL
        matches = re.findall(r't=(\d+)', link)
        if matches:
            return matches[0]

        return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def test_extract_question_id_showthread_pattern():
    """Test extracting ID from showthread.php?t=123"""
    link = "https://www.fxp.co.il/showthread.php?t=12345678&p=1"
    result = extract_question_id(link)
    assert result == "12345678", f"Expected '12345678', got '{result}'"
    print("✓ test_extract_question_id_showthread_pattern")


def test_extract_question_id_thread_pattern():
    """Test extracting ID from /thread/123/ pattern"""
    link = "https://www.fxp.co.il/thread/98765432/"
    result = extract_question_id(link)
    assert result == "98765432", f"Expected '98765432', got '{result}'"
    print("✓ test_extract_question_id_thread_pattern")


def test_extract_question_id_post_pattern():
    """Test extracting ID from ?p= pattern"""
    link = "https://www.fxp.co.il/showthread.php?p=55555555&p=1"
    result = extract_question_id(link)
    assert result == "55555555", f"Expected '55555555', got '{result}'"
    print("✓ test_extract_question_id_post_pattern")


def test_extract_question_id_invalid():
    """Test that invalid links return None"""
    link = "https://www.fxp.co.il/invalid-page"
    result = extract_question_id(link)
    assert result is None, f"Expected None, got '{result}'"
    print("✓ test_extract_question_id_invalid")


def test_extract_question_id_empty_link():
    """Test handling empty link"""
    result = extract_question_id("")
    assert result is None, f"Expected None, got '{result}'"
    print("✓ test_extract_question_id_empty_link")


def run_tests():
    """Run all tests"""
    print("🧪 Running Scraper Tests...\n")

    tests = [
        test_extract_question_id_showthread_pattern,
        test_extract_question_id_thread_pattern,
        test_extract_question_id_post_pattern,
        test_extract_question_id_invalid,
        test_extract_question_id_empty_link,
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

    print(f"\n📊 Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
