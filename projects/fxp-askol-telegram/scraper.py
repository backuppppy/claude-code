import logging
import time
import re
import requests
from bs4 import BeautifulSoup
from config import FXP_BASE_URL, FXP_QUESTIONS_URL, HEADERS, FXP_SCRAPER_TIMEOUT, MAX_RETRIES, RETRY_DELAY

logger = logging.getLogger(__name__)

class FXPScraper:
    def __init__(self):
        self.base_url = FXP_BASE_URL
        self.questions_url = FXP_QUESTIONS_URL
        self.headers = HEADERS
        self.timeout = FXP_SCRAPER_TIMEOUT
        self.max_retries = MAX_RETRIES
        self.retry_delay = RETRY_DELAY

    def fetch_page(self, url=None, retry=0):
        """Fetch FXP forum page with retry logic"""
        url = url or self.questions_url

        try:
            logger.debug(f"Fetching: {url} (attempt {retry + 1}/{self.max_retries})")
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.debug(f"Successfully fetched {len(response.text)} bytes")
            return response.text

        except requests.exceptions.Timeout:
            if retry < self.max_retries - 1:
                logger.warning(f"Timeout, retrying in {self.retry_delay}s...")
                time.sleep(self.retry_delay)
                return self.fetch_page(url, retry + 1)
            logger.error(f"Timeout after {self.max_retries} attempts")
            return None

        except requests.exceptions.ConnectionError as e:
            if retry < self.max_retries - 1:
                logger.warning(f"Connection error, retrying in {self.retry_delay}s...")
                time.sleep(self.retry_delay)
                return self.fetch_page(url, retry + 1)
            logger.error(f"Connection error after {self.max_retries} attempts: {e}")
            return None

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                logger.warning("Rate limited (429), waiting before retry...")
                time.sleep(self.retry_delay * 2)
                return self.fetch_page(url, retry + 1)
            logger.error(f"HTTP error {response.status_code}: {e}")
            return None

        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            return None

    def parse_questions(self, html):
        """Parse questions from HTML with multiple selector strategies"""
        if not html:
            logger.warning("Empty HTML received")
            return []

        questions = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            logger.debug(f"Parsing HTML ({len(html)} bytes)")

            # Strategy 1: Look for FXP thread rows (most common)
            question_elements = soup.find_all('tr', {'class': lambda x: x and 'alt' in x})

            if not question_elements:
                # Strategy 2: Look for thread links in divs
                question_elements = soup.find_all('a', {
                    'href': lambda x: x and 'showthread' in x
                })

            if not question_elements:
                # Strategy 3: Look for any elements with thread pattern
                all_links = soup.find_all('a', href=True)
                question_elements = [
                    link for link in all_links
                    if 'showthread.php?t=' in link.get('href', '')
                ]

            logger.info(f"Found {len(question_elements)} potential question elements")

            seen_ids = set()

            for element in question_elements:
                try:
                    # Extract link
                    if element.name == 'tr':
                        link_elem = element.find('a', href=lambda x: x and 'showthread' in x)
                        if not link_elem:
                            continue
                        link = link_elem.get('href', '')
                        title = link_elem.get_text(strip=True)
                    else:
                        link = element.get('href', '')
                        title = element.get_text(strip=True)

                    if not title or not link:
                        continue

                    # Ensure absolute URL
                    if link.startswith('/'):
                        link = f"{self.base_url}{link}"
                    elif not link.startswith('http'):
                        link = f"{self.base_url}/{link}"

                    # Extract question ID from link
                    question_id = self._extract_question_id(link)

                    if not question_id or question_id in seen_ids:
                        continue

                    seen_ids.add(question_id)

                    # Clean title
                    title = title.strip()
                    if len(title) < 5 or len(title) > 500:
                        continue

                    questions.append({
                        'id': question_id,
                        'title': title,
                        'link': link
                    })

                except Exception as e:
                    logger.debug(f"Error parsing element: {e}")
                    continue

            logger.info(f"Successfully parsed {len(questions)} questions from FXP")
            return questions

        except Exception as e:
            logger.error(f"Critical error parsing HTML: {e}")
            return []

    def _extract_question_id(self, link):
        """Extract question ID from link with multiple patterns"""
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

            logger.debug(f"Could not extract ID from: {link}")
            return None

        except Exception as e:
            logger.debug(f"Error extracting question ID: {e}")
            return None

    def get_latest_questions(self):
        """Get latest questions from FXP homepage"""
        html = self.fetch_page()
        return self.parse_questions(html)

    def get_questions_from_category(self, category_id):
        """Get questions from specific FXP category"""
        category_url = f"{self.base_url}/forumdisplay.php?f={category_id}"
        html = self.fetch_page(category_url)
        return self.parse_questions(html)

    def get_questions_from_search(self, query):
        """Search FXP for questions"""
        search_url = f"{self.base_url}/search.php?query={query}"
        html = self.fetch_page(search_url)
        return self.parse_questions(html)
