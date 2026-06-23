import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# FXP RSS feeds to monitor (can add more)
FXP_RSS_FEEDS = [
    "https://www.fxp.co.il/external.php?type=RSS2",
    "https://www.fxp.co.il/external.php?type=RSS2&forumids=2",  # general forum
]

# Fallback: scrape the new posts page
FXP_NEWPOSTS_URL = "https://www.fxp.co.il/search.php?do=getnew"

CHECK_INTERVAL_SECONDS = 60  # check every minute

STATE_FILE = "/root/fxp_bot/seen_posts.json"
