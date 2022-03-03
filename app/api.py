from typing import List

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import JSONResponse
from loguru import logger
from sqlmodel import Session
from sqlalchemy import null

from config import (
    CRON_SCHEDULE,
    DATA_PATH,
    DB_FILE_PATH,
    LOG_FILE_PATH,
    OUTPUT_PATH,
    YT_OUTPUT_TEMPLATE,
    YT_PLAYLIST_ID,
    YT_PLAYLIST_MAX_COUNT,
)
from models import (
    DatabaseItem,
    DatabaseItemOut,
    Item,
    ItemOut,
)
from database import get_session
from youtube import get_playlist, DownloadTask


router = APIRouter(prefix="/api")


async def get_playlist_items(
    session: Session = Depends(get_session),
) -> List[Item]:
    items = []

    for playlist_item in get_playlist():
        item = Item(**playlist_item.dict())

        database_item = await session.first_or_none(
            DatabaseItem,
            DatabaseItem.video_id == playlist_item.video_id,
        )

        item.job = database_item if database_item else None

        items.append(item)

    return items


async def get_job(
    video_id: str,
    session: Session = Depends(get_session),
) -> DatabaseItem:
    job = await session.first_or_none(
        DatabaseItem, DatabaseItem.video_id == video_id
    )

    if job:
        return job

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No job found for video {video_id}",
    )


@router.get(
    "/state",
    response_class=JSONResponse,
)
async def state(
    session: Session = Depends(get_session),
):
    total_job_count = await session.count(DatabaseItem)
    ongoing_job_count = await session.count(
        DatabaseItem,
        DatabaseItem.started_at != null(),
        DatabaseItem.downloaded_at == null(),
        DatabaseItem.failed_at == null(),
    )
    completed_job_count = await session.count(
        DatabaseItem,
        DatabaseItem.downloaded_at != null(),
    )
    failed_job_count = await session.count(
        DatabaseItem,
        DatabaseItem.failed_at != null(),
    )

    return JSONResponse({
        "config": {
            "playlist_id": YT_PLAYLIST_ID,
            "max_video_count": YT_PLAYLIST_MAX_COUNT,
            "cron_schedule": CRON_SCHEDULE,
            "data_path": DATA_PATH,
            "db_file_path": DB_FILE_PATH,
            "log_file_path": LOG_FILE_PATH,
            "output_template": YT_OUTPUT_TEMPLATE,
            "output_path": OUTPUT_PATH,
        },
        "jobs": {
            "total_count": total_job_count,
            "ongoing_count": ongoing_job_count,
            "completed_count": completed_job_count,
            "failed_count": failed_job_count,
        }
    })


@router.get(
    "/videos",
    response_model=List[ItemOut],
    response_model_by_alias=False,
)
async def playlist(
    items = Depends(get_playlist_items)
):
    return items


@router.get(
    "/videos/process",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=List[ItemOut],
    response_model_by_alias=False,
)
async def process(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    items = Depends(get_playlist_items),
):
    items = [item for item in items if not item.job or not item.job.started_at]
    jobs = []

    if len(items) == 0:
        logger.info("No items to process")
        return []

    logger.debug(f"Preparing to process {len(items)} items(s)")

    for item in items:
        if item.job:
            jobs.append(item.job)
            continue

        database_item = DatabaseItem(
            video_id=item.video_id
        )
        session.add(database_item)
        jobs.append(database_item)

    await session.commit()

    for job in jobs:
        await session.refresh(job)

        for item in items:
            if item.video_id == job.video_id:
                item.job = job

    logger.info(f"Created {len(jobs)} jobs(s)")

    await session.close()

    for item in items:
        task = DownloadTask(item)
        background_tasks.add_task(task.run)

    return items


@router.get(
    "/videos/{video_id}/job",
    response_model=DatabaseItemOut,
    response_model_by_alias=False,
)
async def job(
    job: DatabaseItem = Depends(get_job),
):
    return job


@router.get(
    "/videos/{video_id}/job/clear",
    status_code=status.HTTP_202_ACCEPTED,
)
async def clear_job(
    session: Session = Depends(get_session),
    job: DatabaseItem = Depends(get_job),
):
    logger.info(f"Deleting job #{job.id} (video {job.video_id})")
    await session.delete(job)
    await session.commit()
    return {"detail": f"Deleted download job (#{job.id})"}
