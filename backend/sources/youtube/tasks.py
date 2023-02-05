import yt_dlp
from fastapi.concurrency import run_in_threadpool
from loguru import logger

from config import YT_DLP_REFERER, OUTPUT_PATH, YT_OUTPUT_TEMPLATE
from database import Session
from models import Job, JobProgress, JobStatus
from sio import sio
from tasks import DownloadTask


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


yt_dlp.utils.std_headers.update({
    "Referer": YT_DLP_REFERER,
})

ytdlp = yt_dlp.YoutubeDL


class YoutubeDownloadTask(DownloadTask):
    def __init__(self, session: Session, job: Job):
        super().__init__(session, job)

        self.opts = DEFAULT_YLD_OPTS
        self.opts["progress_hooks"].append(self.progress_hook)
        self.opts["postprocessor_hooks"].append(self.progress_hook)

    async def run(self):
        await self.start()

        try:
            await run_in_threadpool(lambda: self._download(self.job.item))
        except Exception as e:
            logger.exception(f"Error occured while downloading {self.job.item}")
            await self.end(status=JobStatus.FAILED, result="Could not download")
        
        await self.end(status=JobStatus.DOWNLOADED)

    def progress_hook(self, progress):
        status = progress["status"]
        info = progress["info_dict"]
        # video_id = info.get("id", info.get("video_id"))
        postprocessor = progress.get("postprocessor")

        # if not video_id:
        #     logger.error("Video ID could not be determined")
        #     return

        progress = JobProgress(
            message=f"{postprocessor}: {status}",
            total_bytes=progress.get("total_bytes"),
            downloaded_bytes=progress.get("downloaded_bytes"),
        )

        self.loop.create_task(self.emit_update(progress))
        # self.loop.create_task(sio.emit("progress_update", {
        #     "video_id": video_id,
        #     "progress": {
        #         "processor": postprocessor or "downloader",
        #         "status": status,
        #         "total_bytes": total_bytes,
        #         "downloaded_bytes": downloaded_bytes,
        #         "percent": percent,
        #     }
        # }))

    def _download(self, item):
        with ytdlp(self.opts) as ydl:
            ydl.extract_info(item.item_url)
