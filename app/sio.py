from socketio import (
    AsyncServer,
    ASGIApp,
)


sio = AsyncServer(async_mode="asgi", cors_allowed_origins=[])
socket_app = ASGIApp(sio)


@sio.on("connect")
async def connect(sid, environ):
    print("CONNECT---------------------------")
    print(sid)
    print(environ)
    print("----------------------------------")
