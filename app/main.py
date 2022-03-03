import os
from io import BytesIO

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from lz.reversal import reverse

load_dotenv()

from api import router as api
from config import (
    ALLOWED_ORIGINS,
    LOG_FILE_PATH,
    STATIC_FILES_PATH,
)
from database import create_db_and_tables
from sio import socket_app


logger.add(
    LOG_FILE_PATH,
    rotation="10 MB",
    retention="3 days",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api)


@app.on_event("startup")
async def on_startup():
    logger.info("App startup")
    await create_db_and_tables()


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


app.mount('/ws', socket_app)

if os.path.exists(STATIC_FILES_PATH):
    app.mount("/", StaticFiles(
        directory=STATIC_FILES_PATH,
        html=True,
    ), name="frontend")
