import logging
import requests
from bs4 import BeautifulSoup
from config import FXP_BASE_URL, FXP_QUESTIONS_URL, HEADERS, FXP_SCRAPER_TIMEOUT

logger = logging.getLogger(__name__)

class FXPScraper:
    def __init__(self):
        self.base_url = FXP_BASE_URL
        self.questions_url = FXP_QUESTIONS_URL
        self.headers = HEADERS
        self.timeout = FXP_SCRAPER_TIMEOUT

    def fetch_page(self):
        """Fetch FXP forum page"""
        try:
            response = requests.get(
                self.questions_url,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching FXP page: {e}")
            return None

    def parse_questions(self, html):
        """Parse questions from HTML"""
        if not html:
            return []

        questions = []
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Look for question elements (adjust selectors based on FXP structure)
            # This is a generic implementation - actual selectors may vary
            question_elements = soup.find_all('div', {'class': 'question-item'})

            if not question_elements:
                # Fallback: try alternative selectors
                question_elements = soup.find_all('a', {'class': 'thread-link'})

            for element in question_elements:
                try:
                    title = element.get_text(strip=True)
                    link = element.get('href', '')

                    if not title or not link:
                        continue

                    # Ensure absolute URL
                    if link.startswith('/'):
                        link = f"{self.base_url}{link}"
                    elif not link.startswith('http'):
                        link = f"{self.base_url}/{link}"

                    # Extract question ID from link
                    question_id = self._extract_question_id(link)

                    if question_id and title:
                        questions.append({
                            'id': question_id,
                            'title': title,
                            'link': link
                        })

                except Exception as e:
                    logger.debug(f"Error parsing question element: {e}")
                    continue

            logger.info(f"Parsed {len(questions)} questions from FXP")
            return questions

        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return []

    def _extract_question_id(self, link):
        """Extract question ID from link"""
        try:
            # Try to extract ID from URL pattern
            # Example: https://www.fxp.co.il/showthread.php?t=12345678
            if '?t=' in link:
                return link.split('?t=')[-1].split('&')[0]
            elif '/thread/' in link:
                return link.split('/thread/')[-1].split('/')[0]
            else:
                # Use full link as ID if no pattern matches
                return link.split('/')[-1]
        except Exception as e:
            logger.debug(f"Error extracting question ID: {e}")
            return None

    def get_latest_questions(self):
        """Get latest questions from FXP"""
        html = self.fetch_page()
        return self.parse_questions(html)
