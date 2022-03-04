from loguru import logger
from socketio import (
    AsyncServer,
    ASGIApp,
)


sio = AsyncServer(async_mode="asgi", cors_allowed_origins=[])
socket_app = ASGIApp(sio)


@sio.on("connect")
async def connect(sid, environ):
    logger.info(f"Socket client connected (sid={sid})")


@sio.on("disconnect")
async def disconnect(sid):
    logger.info(f"Socket client disconnected (sid={sid})")
