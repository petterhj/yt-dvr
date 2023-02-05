import json
from asyncio import get_running_loop
from datetime import datetime

from loguru import logger

from database import Session, engine
from models import (
    Job,
    JobOutWithItem,
    JobProgress,
    JobStatus,
)
from sio import sio


class DownloadTask:
    def __init__(self, session: Session, job: Job):
        self.session = session
        self.job = job
        self.loop = get_running_loop()

    async def start(self):
        logger.info(f"Starting job #{self.job.id}: {self.job.item}")
        logger.debug(f"Title: {self.job.item.title}")
    
        self.job.started_at = datetime.now()

        self.session.add(self.job)
        await self.session.commit()
        await self.session.refresh(self.job)
        
        await self.emit_update()

    async def end(self, status: JobStatus, result=None):
        if status == JobStatus.DOWNLOADED:
            logger.success(f"Done downloading #{self.job.id}: {self.job.item}")
            self.job.downloaded_at = datetime.now()
            # await send_notification(f"New YouTube video downloaded: {self.item.title}")

        elif status == JobStatus.FAILED:
            logger.error(f"Failed downloading #{self.job.id}: {self.job.item}")
            self.job.failed_at = datetime.now()
            # await send_notification(f"YouTube video download failed: {self.item.title}")
        
        self.job.result = result

        # async with Session(engine) as session:
        self.session.add(self.job)
        await self.session.commit()
        await self.session.refresh(self.job)

        await self.emit_update()
        logger.info(f"Ended job #{self.job.id}")

    async def emit_update(self, progress: JobProgress = None):
        update = {
            "job": json.loads(
                JobOutWithItem(**self.job.dict()).json()
            ),
            "progress": progress.dict() if progress else None,
        }
        print(update)
        await sio.emit("progress_update", update)
    
    async def run(self):
        await self.start()

        logger.error((
            f"Nothing to do for job #{self.job.id}. The `run` method should"
            " implement the actual download task and call both `start` and `end`."
        ))

        await self.end(status=JobStatus.FAILED, result="Not implemented")
