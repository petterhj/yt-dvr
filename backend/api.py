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
from sqlalchemy.exc import IntegrityError

from config import (
    ALLOWED_ORIGINS,
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
    Item,
    ItemIn,
    ItemOut,
    ItemOutWithJobs,
    Job,
    JobOut,
    JobOutWithItem,
    JobStatus,
)
from database import get_session
from exceptions import ItemNotFoundError
from items import get_items, get_item
from jobs import (
    add_job,
    get_jobs,
    get_started_jobs,
    # get_started_job,
    status_filter,
)
from sources import SOURCES


router = APIRouter(prefix="/api")

for source in SOURCES.values():
    router.include_router(source.router)


@router.get(
    "/state",
    response_class=JSONResponse,
)
async def state(
    session: Session = Depends(get_session),
):
    total_job_count = await session.count(Job)
    new_job_count = await session.count(Job, *status_filter(JobStatus.NEW))
    queued_job_count = await session.count(Job, *status_filter(JobStatus.QUEUED))
    started_job_count = await session.count(Job, *status_filter(JobStatus.STARTED))
    downloaded_job_count = await session.count(Job, *status_filter(JobStatus.DOWNLOADED))
    failed_job_count = await session.count(Job, *status_filter(JobStatus.FAILED))

    return JSONResponse({
        "config": {
            "cron_schedule": CRON_SCHEDULE,
            "data_path": DATA_PATH,
            "db_file_path": DB_FILE_PATH,
            "log_file_path": LOG_FILE_PATH,
            "output_template": YT_OUTPUT_TEMPLATE,
            "output_path": OUTPUT_PATH,
            "allowed_origins": ALLOWED_ORIGINS,
            "sources": {
                name: source.get_config() for name, source in SOURCES.items()
            },
        },
        "jobs": {
            "total_count": total_job_count,
            "new_count": new_job_count,
            "queued_count": queued_job_count,
            "started_count": started_job_count,
            "downloaded_count": downloaded_job_count,
            "failed_count": failed_job_count,
        }
    })


@router.get(
    "/items",
    response_model=list[ItemOutWithJobs],
    response_model_by_alias=False,
)
async def items(
    items: list[Item] = Depends(get_items),
):
    return items


@router.post(
    "/items",
    response_model=ItemOutWithJobs,
    response_model_by_alias=False,
)
async def add_item(
    item_in: ItemIn,
    session: Session = Depends(get_session),
):
    source = SOURCES.get(item_in.source)

    if not source:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown source {item_in.source}",
        )

    try:
        item = source.get_item(item_id=item_in.item_id)
    except ItemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find item {item_in.source}:{item_in.item_id}",
        )
    
    try:
        session.add(item)
        await session.commit()
        await session.refresh(item)
    except IntegrityError as error:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Could not add item {item_in.source}:{item_in.item_id} (already added)",
        )

    await add_job(item, session)

    return item


@router.get(
    "/items/{source}",
    response_model=list[ItemOut],
    response_model_by_alias=False,
)
async def items_by_source(
    items: list[Item] = Depends(get_items),
):
    return items


@router.get(
    "/items/{source}/{item_id}",
    response_model=ItemOutWithJobs,
    response_model_by_alias=False,
)
async def item(
    item: Item = Depends(get_item),
):
    return item


@router.delete(
    "/items/{source}/{item_id}",
    status_code=status.HTTP_202_ACCEPTED,
)
async def delete_item(
    session: Session = Depends(get_session),
    item: Item = Depends(get_item),
):
    logger.info(f"Deleting item #{item.id} (video {item.source}:{item.item_id})")
    await session.delete(item)
    await session.commit()
    return {"detail": f"Deleted item {item}"}


@router.get(
    "/items/{source}/{item_id}/retry",
    response_model=JobOut,
    response_model_by_alias=False,
)
async def item(
    job: Job = Depends(add_job),
):
    return job


@router.get(
    "/jobs",
    response_model=list[JobOutWithItem],
    response_model_by_alias=False,
)
async def jobs(
    jobs: list[Job] = Depends(get_jobs()),
):
    return jobs


@router.get(
    "/jobs/start",
    response_model=list[JobOutWithItem],
    response_model_by_alias=False,
)
async def jobs(
    jobs: list[Job] = Depends(get_started_jobs),
):
    return jobs
