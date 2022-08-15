from gotify import AsyncGotify, GotifyConfigurationError
from loguru import logger

from config import (
    GOTIFY_BASE_URL,
    GOTIFY_APP_TOKEN,
)


gotify = AsyncGotify(
    base_url=GOTIFY_BASE_URL,
    app_token=GOTIFY_APP_TOKEN,
)


async def send_notification(message, title="YTDVR", priority=0):
    try:
        await gotify.create_message(
            title=title,
            message=message,
            priority=priority
        )
    except GotifyConfigurationError:
        logger.info("No notification created (Goatify not configured)")
    except Exception as e:
        logger.error(f"Notification error: {e}")
    else:
        logger.success(f"Notification sent")
