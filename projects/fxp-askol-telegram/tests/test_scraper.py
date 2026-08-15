import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper import FXPScraper


class TestFXPScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = FXPScraper()

    def test_extract_question_id_showthread_pattern(self):
        """Test extracting ID from showthread.php?t=123"""
        link = "https://www.fxp.co.il/showthread.php?t=12345678&p=1"
        question_id = self.scraper._extract_question_id(link)
        self.assertEqual(question_id, "12345678")

    def test_extract_question_id_thread_pattern(self):
        """Test extracting ID from /thread/123/ pattern"""
        link = "https://www.fxp.co.il/thread/98765432/"
        question_id = self.scraper._extract_question_id(link)
        self.assertEqual(question_id, "98765432")

    def test_extract_question_id_post_pattern(self):
        """Test extracting ID from ?p= pattern"""
        link = "https://www.fxp.co.il/showthread.php?p=55555555&p=1"
        question_id = self.scraper._extract_question_id(link)
        self.assertEqual(question_id, "55555555")

    def test_extract_question_id_invalid(self):
        """Test that invalid links return None"""
        link = "https://www.fxp.co.il/invalid-page"
        question_id = self.scraper._extract_question_id(link)
        self.assertIsNone(question_id)

    def test_extract_question_id_empty_link(self):
        """Test handling empty link"""
        question_id = self.scraper._extract_question_id("")
        self.assertIsNone(question_id)

    def test_parse_questions_empty_html(self):
        """Test parsing empty HTML"""
        questions = self.scraper.parse_questions("")
        self.assertEqual(questions, [])

    def test_parse_questions_none_html(self):
        """Test parsing None HTML"""
        questions = self.scraper.parse_questions(None)
        self.assertEqual(questions, [])

    def test_parse_questions_no_duplicates(self):
        """Test that duplicate IDs are not returned"""
        html = """
        <a href="https://www.fxp.co.il/showthread.php?t=123">Question 1</a>
        <a href="https://www.fxp.co.il/showthread.php?t=123">Question 1 Duplicate</a>
        <a href="https://www.fxp.co.il/showthread.php?t=456">Question 2</a>
        """
        questions = self.scraper.parse_questions(html)
        self.assertEqual(len(questions), 2)
        ids = [q['id'] for q in questions]
        self.assertEqual(len(ids), len(set(ids)))

    def test_parse_questions_title_validation(self):
        """Test that very short titles are filtered"""
        html = """
        <a href="https://www.fxp.co.il/showthread.php?t=123">Hi</a>
        <a href="https://www.fxp.co.il/showthread.php?t=456">This is a valid question title</a>
        """
        questions = self.scraper.parse_questions(html)
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]['title'], "This is a valid question title")

    def test_question_structure(self):
        """Test that returned questions have correct structure"""
        html = """
        <a href="https://www.fxp.co.il/showthread.php?t=123">How to fix computer?</a>
        """
        questions = self.scraper.parse_questions(html)
        self.assertEqual(len(questions), 1)

        question = questions[0]
        self.assertIn('id', question)
        self.assertIn('title', question)
        self.assertIn('link', question)
        self.assertEqual(question['id'], "123")
        self.assertEqual(question['title'], "How to fix computer?")


if __name__ == '__main__':
    unittest.main()
