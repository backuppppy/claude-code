import requests
from bs4 import BeautifulSoup
from datetime import datetime
from config import logger
import time

class WebMonitor:
    def __init__(self):
        self.url = "https://www.stips.co.il"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_page(self, retries=3):
        for attempt in range(retries):
            try:
                response = self.session.get(self.url, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Fetch attempt {attempt + 1}/{retries} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        return None

    def parse_posts(self, html):
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        posts = []

        try:
            post_elements = soup.find_all('article', class_='post-item')
            if not post_elements:
                post_elements = soup.find_all('div', class_='post')

            for element in post_elements:
                try:
                    title_elem = element.find('h2') or element.find('h3') or element.find('a')
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)

                    link_elem = element.find('a', href=True)
                    url = link_elem['href'] if link_elem else None

                    if url and not url.startswith('http'):
                        url = self.url + url

                    date_elem = element.find('time') or element.find('span', class_='date')
                    published_date = date_elem.get_text(strip=True) if date_elem else datetime.now().isoformat()

                    if title and url:
                        posts.append({
                            'title': title,
                            'url': url,
                            'published_date': published_date
                        })
                except Exception as e:
                    logger.debug(f"Error parsing post element: {e}")
                    continue

            logger.info(f"Parsed {len(posts)} posts from page")
            return posts

        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return []

    def get_new_posts(self, db):
        html = self.fetch_page()
        if not html:
            logger.error("Failed to fetch page")
            return []

        posts = self.parse_posts(html)
        new_posts = []

        for post in posts:
            if not db.post_exists(post['url']):
                if db.add_post(post['title'], post['url'], post['published_date']):
                    new_posts.append(post)

        if new_posts:
            logger.info(f"Found {len(new_posts)} new posts")

        return new_posts
