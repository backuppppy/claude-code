import logging
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, bot_token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f'https://api.telegram.org/bot{bot_token}'

    def send_question_notification(self, question):
        """Send question notification to Telegram"""
        message = self._format_question_message(question)
        return self.send_message(message)

    def _format_question_message(self, question):
        """Format question as Telegram message"""
        title = question.get('title', 'Unknown')
        link = question.get('link', '')

        # Format message with markdown
        message = f"""
🆕 *שאלה חדשה ב-FXP*

📝 *{title}*

🔗 [לקריאת השאלה]({link})
"""
        return message.strip()

    def send_message(self, message, parse_mode='Markdown'):
        """Send message to Telegram chat"""
        try:
            url = f'{self.api_url}/sendMessage'
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': False
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get('ok'):
                logger.info(f"Message sent successfully")
                return True
            else:
                logger.error(f"Telegram error: {result.get('description')}")
                return False

        except requests.RequestException as e:
            logger.error(f"Error sending message to Telegram: {e}")
            return False

    def send_status(self, questions_found, new_questions, notifications_sent, duration_ms):
        """Send status report to Telegram"""
        message = f"""
📊 *FXP Monitor Status Report*

🔍 Questions found: {questions_found}
✨ New questions: {new_questions}
📬 Notifications sent: {notifications_sent}
⏱️ Duration: {duration_ms}ms
"""
        return self.send_message(message.strip())

    def send_error(self, error_message):
        """Send error notification to Telegram"""
        message = f"""
❌ *FXP Monitor Error*

{error_message}
"""
        return self.send_message(message.strip())
