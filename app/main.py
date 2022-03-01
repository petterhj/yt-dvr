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
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from loguru import logger
from lz.reversal import reverse

from sqlmodel import Session

load_dotenv()

from models import DatabaseItem, Item, ItemOut
from database import create_db_and_tables, get_session
from youtube import get_playlist, download_videos


logger.add(
    os.path.join(os.environ["DATA_PATH"], "ytdvr.log"),
    rotation="10 MB",
    retention="3 days",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
)

app = FastAPI()


def get_playlist_items(
    session: Session = Depends(get_session),
) -> List[Item]:
    items = []

    for playlist_item in get_playlist():
        item = Item(**playlist_item.dict())

        database_item = session.first_or_none(
            DatabaseItem,
            DatabaseItem.video_id == playlist_item.video_id,
        )

        item.job = database_item if database_item else None
        
        items.append(item)

    return items


@app.on_event("startup")
def on_startup():
    logger.info("App startup")
    create_db_and_tables()


@app.get(
    "/",
    response_model=List[ItemOut],
    response_model_by_alias=False,
)
def playlist(
    items = Depends(get_playlist_items)
):
    return items


@app.get(
    "/process",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=List[ItemOut],
    response_model_by_alias=False,
)
def process(
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
        
    session.commit()

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
def log():
    log_file = os.path.join(os.environ["DATA_PATH"], "ytdvr.log")

    if not os.path.exists(log_file):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No log file found"
        )
    
    with open(log_file, 'rb') as fh:
        buf = BytesIO(fh.read())
        log_data = reverse(buf)

    return StreamingResponse(log_data, media_type="text/plain")
