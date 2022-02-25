import os
from datetime import datetime
from typing import List

import yt_dlp
from loguru import logger
from pyyoutube import Api

from models import Item, PlaylistItem


api = Api(api_key=os.environ["YT_API_KEY"])

yt_dlp.utils.std_headers.update({'Referer': 'https://www.google.com'})

ydl_opts = {
    "paths": {
        "home": os.environ["OUTPUT_PATH"],
    },
    "outtmpl": {"default": os.getenv(
        "YT_OUTPUT_TEMPLATE",
        "%(title)s [%(id)s].%(ext)s",
    )},
    "postprocessors": [
        {
            "key": "FFmpegVideoRemuxer",
            "preferedformat": "mkv",
        },
        {
            # Embed metadata (yt_dlp.postprocessor.FFmpegMetadataPP)
            "key": "FFmpegMetadata",
            "add_chapters": True,
            "add_metadata": True,
        },
    ],
    "call_home": False,
    'progress_hooks': [],
    # ffmpeg_location
}


def get_playlist() -> List[PlaylistItem]:
    playlist = api.get_playlist_items(
        playlist_id=os.environ["YT_PLAYLIST_ID"],
        count=int(os.getenv("YT_PLAYLIST_MAX_COUNT", 3)),
    )

    return [
        PlaylistItem(
            **video.snippet.to_dict()
        ) for video in playlist.items
    ]


def progress_hook(progress):
    logger.debug("Progress: {} - {}/{} bytes".format(
        progress["status"],
        progress["downloaded_bytes"],
        progress["total_bytes"],
    ))  


def download_videos(session, items: List[Item]):
    for i, item in enumerate(items, 1):
        logger.info("Starting job {}/{} (#{}): {}".format(
            i, len(items), item.job.id, item.video_id
        ))
        logger.debug(f"Title: {item.title}")

        item.job.started_at = datetime.now()
        session.add(item.job)
        session.commit()

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.add_progress_hook(progress_hook)
                ydl.extract_info(item.video_url)
        except Exception:
            item.job.failed_at = datetime.now()
            logger.error(f"Error occured while downloading {item.video_id}")
        else:
            item.job.downloaded_at = datetime.now()
            logger.success(f"Done downloading {item.video_id}")

        session.add(item.job)
        session.commit()
