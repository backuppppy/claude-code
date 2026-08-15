import logging
import time
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, MAX_RETRIES, RETRY_DELAY

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, bot_token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f'https://api.telegram.org/bot{bot_token}'
        self.max_retries = MAX_RETRIES
        self.retry_delay = RETRY_DELAY
        self._bot_info = None

    def get_bot_info(self):
        """קבל מידע על הבוט"""
        try:
            url = f'{self.api_url}/getMe'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            result = response.json()
            if result.get('ok'):
                self._bot_info = result.get('result', {})
                logger.info(f"בוט מחובר: @{self._bot_info.get('username')}")
                return self._bot_info
            return None
        except Exception as e:
            logger.error(f"שגיאה בקבלת מידע בוט: {e}")
            return None

    def send_question_notification(self, question):
        """שלח הודעת שאלה חדשה"""
        message = self._format_question_message(question)
        return self.send_message(message)

    def _format_question_message(self, question):
        """עצב הודעה על שאלה"""
        title = question.get('title', 'לא ידוע')
        link = question.get('link', '')
        question_id = question.get('id', '')

        message = f"""🆕 *שאלה חדשה ב\\-FXP*

📝 *{self._escape_markdown(title)}*

🔗 [לקריאת השאלה]({link})

#️⃣ `{question_id}`"""

        return message

    def _escape_markdown(self, text):
        """Escape markdown special characters"""
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text

    def send_message(self, message, parse_mode='MarkdownV2', retry=0):
        """שלח הודעה לטלגרם עם retry logic"""
        try:
            url = f'{self.api_url}/sendMessage'
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': False
            }

            logger.debug(f"שליחת הודעה (attempt {retry + 1}/{self.max_retries})")
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get('ok'):
                logger.info("הודעה נשלחה בהצלחה")
                return True
            else:
                error_desc = result.get('description', 'לא ידוע')
                logger.error(f"שגיאת Telegram: {error_desc}")

                if retry < self.max_retries - 1 and 'Too Many Requests' in error_desc:
                    logger.warning(f"Rate limit, הנסיה שוב בעוד {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                    return self.send_message(message, parse_mode, retry + 1)

                return False

        except requests.exceptions.Timeout:
            if retry < self.max_retries - 1:
                logger.warning(f"Timeout, הנסיה שוב...")
                time.sleep(self.retry_delay)
                return self.send_message(message, parse_mode, retry + 1)
            logger.error(f"Timeout אחרי {self.max_retries} ניסיונות")
            return False

        except requests.RequestException as e:
            logger.error(f"שגיאה בשליחה לטלגרם: {e}")
            return False

    def send_status(self, questions_found, new_questions, notifications_sent, duration_ms):
        """שלח דוח סטטוס"""
        message = f"""📊 *דוח סטטוס ניטור FXP*

🔍 שאלות נמצאו: `{questions_found}`
✨ שאלות חדשות: `{new_questions}`
📬 הודעות נשלחו: `{notifications_sent}`
⏱️ משך זמן: `{duration_ms}ms`"""

        return self.send_message(message)

    def send_error(self, error_message):
        """שלח התרעה על שגיאה"""
        message = f"""❌ *שגיאה בניטור FXP*

```
{error_message}
```"""

        return self.send_message(message)

    def send_summary(self, stats_dict):
        """שלח סיכום מפורט"""
        message = f"""📈 *סיכום יומי FXP Bot*

📊 סטטיסטיקות:
• סה״כ שאלות: `{stats_dict.get('total_questions', 0)}`
• שאלות חדשות: `{stats_dict.get('new_questions', 0)}`
• הודעות שנשלחו: `{stats_dict.get('notifications_sent', 0)}`
• שגיאות: `{stats_dict.get('errors', 0)}`

⏱️ ממוצע משך הרצה: `{stats_dict.get('avg_duration_ms', 0)}ms`"""

        return self.send_message(message)
