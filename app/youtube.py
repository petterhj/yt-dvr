from datetime import datetime
from typing import List

import yt_dlp
from loguru import logger
from pyyoutube import Api

from config import (
    OUTPUT_PATH,
    YT_API_KEY,
    YT_DLP_REFERER,
    YT_OUTPUT_TEMPLATE,
    YT_PLAYLIST_ID,
    YT_PLAYLIST_MAX_COUNT,
    YT_SUBTITLE_LANGS,
)
from models import Item, PlaylistItem


api = Api(api_key=YT_API_KEY)

yt_dlp.utils.std_headers.update({
    "Referer": YT_DLP_REFERER,
})

ydl_opts = {
    "paths": {
        "home": OUTPUT_PATH,
    },
    "outtmpl": {"default": YT_OUTPUT_TEMPLATE},
    "writesubtitles": True,
    "writethumbnail": True,
    # "subtitleslangs": YT_SUBTITLE_LANGS,
    "postprocessors": [
        {
            "key": "FFmpegVideoRemuxer",
            "preferedformat": "mkv",
        },
        {"key": "FFmpegEmbedSubtitle"},
        {"key": "EmbedThumbnail"},
        {
            # Embed metadata (yt_dlp.postprocessor.FFmpegMetadataPP)
            "key": "FFmpegMetadata",
            "add_chapters": True,
            "add_metadata": True,
        },
    ],
    "simulate": False,
    "call_home": False,
    'progress_hooks': [],
}


def get_playlist() -> List[PlaylistItem]:
    playlist = api.get_playlist_items(
        playlist_id=YT_PLAYLIST_ID,
        count=YT_PLAYLIST_MAX_COUNT,
    )

    return [
        PlaylistItem(
            **video.snippet.to_dict()
        ) for video in playlist.items
    ]


def progress_hook(progress):
    if progress["status"] == "downloading":
        return

    logger.debug("Progress: {} - {}/{} bytes".format(
        progress["status"],
        progress["downloaded_bytes"],
        progress.get("total_bytes", "?"),
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
            logger.exception(f"Error occured while downloading {item.video_id}")
        else:
            item.job.downloaded_at = datetime.now()
            logger.success(f"Done downloading {item.video_id}")

        session.add(item.job)
        session.commit()
