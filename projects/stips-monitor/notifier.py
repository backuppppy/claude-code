from config import logger

class Notifier:
    def format_post(self, post):
        title = post.get('title', 'Untitled')
        url = post.get('url', '')
        published_date = post.get('published_date', 'N/A')

        message = f"""📢 <b>New Post on Stips</b>

<b>{title}</b>

🔗 <a href="{url}">Read More</a>
📅 {published_date}"""

        return message

    async def send_notification(self, app, user_id, post):
        try:
            message = self.format_post(post)
            await app.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
            logger.info(f"Notification sent to {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send notification to {user_id}: {e}")
            return False

    async def notify_users(self, app, db, posts):
        if not posts:
            logger.info("No posts to notify")
            return

        subscribed_users = db.get_subscribed_users()
        logger.info(f"Notifying {len(subscribed_users)} users about {len(posts)} posts")

        sent_count = 0
        failed_count = 0

        for post in posts:
            for user_id in subscribed_users:
                if await self.send_notification(app, user_id, post):
                    sent_count += 1
                else:
                    failed_count += 1

            db.mark_post_sent(post['id'])

        logger.info(f"Notification batch complete: {sent_count} sent, {failed_count} failed")
