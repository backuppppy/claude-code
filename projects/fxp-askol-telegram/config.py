import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATABASE_PATH = os.getenv('DATABASE_PATH', str(BASE_DIR / 'fxp_askol.db'))
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env")

# FXP Configuration
FXP_BASE_URL = 'https://www.fxp.co.il'
FXP_QUESTIONS_URL = f'{FXP_BASE_URL}/forum'
FXP_MONITOR_INTERVAL = int(os.getenv('FXP_MONITOR_INTERVAL', 300))  # 5 minutes
FXP_SCRAPER_TIMEOUT = int(os.getenv('FXP_SCRAPER_TIMEOUT', 30))

# Request headers to avoid blocking
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Logging Configuration
LOG_FILE = LOGS_DIR / 'fxp_monitor.log'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Database Configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Feature flags
ENABLE_NOTIFICATIONS = os.getenv('ENABLE_NOTIFICATIONS', 'True').lower() == 'true'
ENABLE_DRY_RUN = os.getenv('ENABLE_DRY_RUN', 'False').lower() == 'true'
