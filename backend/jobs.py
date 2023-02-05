from datetime import datetime

from fastapi import (
    BackgroundTasks,
    Depends,
    HTTPException,
    status,
)
from loguru import logger
# from sqlalchemy import null
from sqlmodel import Session

from database import get_session
from items import get_item
from models import Item, Job, JobStatus
from sources import SOURCES


def status_filter(status: JobStatus = None):
    if not status:
        return ()
    if status == JobStatus.NEW:
        return (
            Job.created_at != None,
            Job.queued_at == None,
            Job.started_at == None,
            Job.downloaded_at == None,
            Job.failed_at == None,
        )
    elif status == JobStatus.QUEUED:
        return (
            Job.created_at != None,
            Job.queued_at != None,
            Job.started_at == None,
            Job.downloaded_at == None,
            Job.failed_at == None,
        )
    elif status == JobStatus.STARTED:
        return (
            Job.created_at != None,
            Job.queued_at != None,
            Job.started_at != None,
            Job.downloaded_at == None,
            Job.failed_at == None,
        )
    elif status == JobStatus.DOWNLOADED:
        return (
            Job.created_at != None,
            Job.queued_at != None,
            Job.started_at != None,
            Job.downloaded_at != None,
            Job.failed_at == None,
        )
    elif status == JobStatus.FAILED:
        return (
            Job.created_at != None,
            Job.queued_at != None,
            Job.started_at != None,
            Job.downloaded_at == None,
            Job.failed_at != None,
        )
    

def get_jobs(
    filter_status: JobStatus = None,
):
    async def _get_jobs(
        status: JobStatus = None,
        session: Session = Depends(get_session),
    ) -> list[Job]:
        jobs = await session.query(
            Job,
            *status_filter(filter_status or status),
        )

        return jobs
    return _get_jobs


# async def get_item_jobs(
#     item: Item = Depends(get_item),
#     # session: Session = Depends(get_session),
# ) -> list[Job]:
#     # job = await session.first_or_none(
#     #     Job,
#     #     Job.source == source,
#     #     Job.video_id == video_id,
#     # )

#     # if not job:
#     #     raise HTTPException(
#     #         status_code=status.HTTP_404_NOT_FOUND,
#     #         detail=f"No job found for video {video_id}",
#     #     )
    
#     return item.jobs


async def add_job(
    item: Item = Depends(get_item),
    session: Session = Depends(get_session),
):
    for job in item.jobs:
        if job.status != JobStatus.DOWNLOADED and job.status != JobStatus.FAILED:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unprocessed job found for {item} (#{job.id})",
            )

    job = Job()
    job.item_id = item.id
    session.add(job)
    await session.commit()
    await session.refresh(job)

    return job


async def get_started_jobs(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    queued_jobs: list[Job] = Depends(get_jobs(JobStatus.NEW)),
):
    if len(queued_jobs) == 0:
        logger.info(f"No new items to process")
        return []

    logger.info(f"Found {len(queued_jobs)} new item(s)")

    for job in queued_jobs:
        logger.info(f"Enqueuing {job.item}")
        job.queued_at = datetime.now()
        session.add(job)
        await session.commit()
        await session.refresh(job)

        source = SOURCES[job.item.source]
        task = source.get_download_task(session, job)
        background_tasks.add_task(task.run)

    return queued_jobs


# async def get_started_job(
#     background_tasks: BackgroundTasks,
#     session: Session = Depends(get_session),
#     queued_jobs: list[Job] = Depends(get_jobs(JobStatus.NEW)),
# ):
#     if len(queued_jobs) == 0:
#         logger.info(f"No new items to process")
#         return []

#     logger.info(f"Found {len(queued_jobs)} new item(s)")

#     for job in queued_jobs:
#         logger.info(f"Enqueuing {job.item}")
#         job.queued_at = datetime.now()
#         session.add(job)
#         await session.commit()
#         await session.refresh(job)

#         source = SOURCES[job.item.source]
#         task = source.get_download_task(session, job)
#         background_tasks.add_task(task.run)

#     return queued_jobs
