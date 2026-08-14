import os
from dotenv import load_dotenv
import logging

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment. Please set it in .env file")

POLLING_INTERVAL = int(os.getenv('POLLING_INTERVAL', '300'))
DATABASE_PATH = os.getenv('DATABASE_PATH', 'stips_monitor.db')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
