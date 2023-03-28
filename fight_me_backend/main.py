#!/usr/bin/env python
import uvicorn

import socketio

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = socketio.ASGIApp(sio)

background_task_started = False


async def background_task():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        await sio.sleep(1)
        count += 1
        await sio.emit("ping", {"data": count})


@sio.on("connect")
async def test_connect(sid, environ):
    print("Client connected")

    global background_task_started
    if not background_task_started:
        sio.start_background_task(background_task)
        background_task_started = True


@sio.on("disconnect")
def test_disconnect(sid):
    print("Client disconnected")


# @sio.on("my_event")
# async def test_message(sid, message):
#     await sio.emit("my_response", {"data": message["data"]}, room=sid)


# @sio.on("my_broadcast_event")
# async def test_broadcast_message(sid, message):
#     await sio.emit("my_response", {"data": message["data"]})


# @sio.on("join")
# async def join(sid, message):
#     sio.enter_room(sid, message["room"])
#     await sio.emit("my_response", {"data": "Entered room: " + message["room"]}, room=sid)


# @sio.on("leave")
# async def leave(sid, message):
#     sio.leave_room(sid, message["room"])
#     await sio.emit("my_response", {"data": "Left room: " + message["room"]}, room=sid)


# @sio.on("close room")
# async def close(sid, message):
#     await sio.emit("my_response", {"data": "Room " + message["room"] + " is closing."}, room=message["room"])
#     await sio.close_room(message["room"])


# @sio.on("my_room_event")
# async def send_room_message(sid, message):
#     await sio.emit("my_response", {"data": message["data"]}, room=message["room"])


# @sio.on("disconnect request")
# async def disconnect_request(sid):
#     await sio.disconnect(sid)


# @sio.on("connect")
# async def test_connect(sid, environ):
#     global background_task_started
#     if not background_task_started:
#         sio.start_background_task(background_task)
#         background_task_started = True
#     await sio.emit("my_response", {"data": "Connected", "count": 0}, room=sid)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
