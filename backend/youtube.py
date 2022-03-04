import json
from datetime import datetime
from typing import List

import yt_dlp
from loguru import logger
import asyncio

from fastapi.concurrency import run_in_threadpool
from pyyoutube import Api

from config import (
    OUTPUT_PATH,
    YT_API_KEY,
    YT_DLP_REFERER,
    YT_OUTPUT_TEMPLATE,
    YT_PLAYLIST_ID,
    YT_PLAYLIST_MAX_COUNT,
    # YT_SUBTITLE_LANGS,
)
from models import (
    Item,
    PlaylistItem,
    DatabaseItemOut,
)
from database import Session, engine
from sio import sio

DEFAULT_YLD_OPTS = {
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
        {
            # Embed metadata (yt_dlp.postprocessor.FFmpegMetadataPP)
            "key": "FFmpegMetadata",
            "add_chapters": True,
            "add_metadata": True,
        },
        {"key": "FFmpegEmbedSubtitle"},
        {
            "key": "FFmpegThumbnailsConvertor",
            "format": "png",
            "when": "before_dl",
        },
        {
            "key": "EmbedThumbnail",
            "already_have_thumbnail": True, # Keep thumbnail after embedding
        },
    ],
    "simulate": False,
    "call_home": False,
    "progress_hooks": [],
    "postprocessor_hooks": [],
}


api = Api(api_key=YT_API_KEY)

yt_dlp.utils.std_headers.update({
    "Referer": YT_DLP_REFERER,
})


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


class DownloadTask:
    def __init__(self, item: Item):
        self.opts = DEFAULT_YLD_OPTS
        self.item = item
        self.loop = asyncio.get_running_loop()

        self.opts["progress_hooks"].append(self.progress_hook)
        self.opts["postprocessor_hooks"].append(self.progress_hook)

    def progress_hook(self, progress):
        status = progress["status"]
        info = progress["info_dict"]
        video_id = info.get("id", info.get("video_id"))
        postprocessor = progress.get("postprocessor")

        if not video_id:
            logger.error("Video ID could not be determined")
            return

        total_bytes = progress.get("total_bytes")
        downloaded_bytes = progress.get("downloaded_bytes")
        percent = None

        if total_bytes and downloaded_bytes:
            percent = round((int(downloaded_bytes) / int(total_bytes)) * 100)

        self.loop.create_task(sio.emit("progress_update", {
            "video_id": video_id,
            "progress": {
                "processor": postprocessor or "downloader",
                "status": status,
                "total_bytes": total_bytes,
                "downloaded_bytes": downloaded_bytes,
                "percent": percent,
            }
        }))

        # if progress["status"] == "downloading":
        #     return

        # logger.debug("Progress: {} - {}/{} bytes".format(
        #     progress["status"],
        #     progress["downloaded_bytes"],
        #     progress.get("total_bytes", "?"),
        # ))

    async def run(self):
        logger.info(f"Starting job (#{self.item.job.id}): {self.item.video_id}")
        logger.debug(f"Title: {self.item.title}")

        self.item.job.started_at = datetime.now()
        async with Session(engine) as session:
            session.add(self.item.job)
            await session.commit()
            await session.refresh(self.item.job)

        await sio.emit("progress_update", {
            "video_id": self.item.video_id,
            "job": json.loads(
                DatabaseItemOut(**self.item.job.dict()).json()
            ),
        })

        try:
            await run_in_threadpool(lambda: self._download(self.item))
        except Exception:
            self.item.job.failed_at = datetime.now()
            logger.exception(f"Error occured while downloading {self.item.video_id}")
        else:
            self.item.job.downloaded_at = datetime.now()
            logger.success(f"Done downloading {self.item.video_id}")

        async with Session(engine) as session:
            session.add(self.item.job)
            await session.commit()
            await session.refresh(self.item.job)

        await sio.emit("progress_update", {
            "video_id": self.item.video_id,
            "job": json.loads(
                DatabaseItemOut(**self.item.job.dict()).json()
            ),
        })

        logger.info(f"Job ended for {self.item.video_id}")

    def _download(self, item: Item):
        with yt_dlp.YoutubeDL(self.opts) as ydl:
            ydl.extract_info(item.video_url)
