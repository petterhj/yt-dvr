import os
from io import BytesIO
from typing import List

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    status,
)
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    JSONResponse,
    StreamingResponse,
)
from loguru import logger
from lz.reversal import reverse
from sqlalchemy import null
from sqlmodel import Session

load_dotenv()

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
from models import DatabaseItem, Item, ItemOut
from database import create_db_and_tables, get_session
from youtube import get_playlist, download_videos


logger.add(
    LOG_FILE_PATH,
    rotation="10 MB",
    retention="3 days",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.on_event("startup")
async def on_startup():
    logger.info("App startup")
    await create_db_and_tables()


@app.get(
    "/",
    response_class=JSONResponse,
)
async def index(
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


@app.get(
    "/videos",
    response_model=List[ItemOut],
    response_model_by_alias=False,
)
async def playlist(
    items = Depends(get_playlist_items)
):
    return items


@app.get(
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
    items = [item for item in items if not item.job]
    jobs = []

    if len(items) == 0:
        logger.info("No items to process")
        return []

    logger.debug(f"Preparing to process {len(items)} items(s)")

    for item in items:
        database_item = DatabaseItem(
            video_id=item.video_id
        )
        session.add(database_item)
        jobs.append(database_item)
        
    await session.commit()

    for job in jobs:
        session.refresh(job)
        for item in items:
            if item.video_id == job.video_id:
                item.job = job

    logger.info(f"Created {len(jobs)} jobs(s)")

    background_tasks.add_task(download_videos, session, items)
    
    return items


@app.get(
    "/log",
    response_class=StreamingResponse,
)
async def log():
    if not os.path.exists(LOG_FILE_PATH):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No log file found"
        )
    
    with open(LOG_FILE_PATH, 'rb') as fh:
        buf = BytesIO(fh.read())
        log_data = reverse(buf)

    return StreamingResponse(log_data, media_type="text/plain")
