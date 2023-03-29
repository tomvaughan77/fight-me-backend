#!/usr/bin/env python
import uvicorn

import socketio

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = socketio.ASGIApp(sio)


users = []
room = "test_room"


@sio.on("connect")
def test_connect(sid, data):
    print(f"⚡: {sid} user just connected!")
    users.append(sid)
    print(users)


@sio.on("disconnect")
async def test_disconnect(sid):
    print(f"🔥: {sid} user disconnected")
    sio.leave_room(sid, room)
    users.remove(sid)   
    await sio.disconnect(sid)
    print(users)


@sio.event
async def message(sid, data):
    print(f"SID: {sid}")
    print(data)
    print(f"Message: {data['text']} from {data['name']}")
    await sio.emit("messageResponse", data)

@sio.event
async def getRoom(sid):
    print(f"Adding SID {sid} to room {room}")
    await sio.emit("getRoomResponse", { "room": room })
    sio.enter_room(sid, room)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
