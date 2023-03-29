#!/usr/bin/env python
import uvicorn

import socketio
import json

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = socketio.ASGIApp(sio)


users = []


@sio.on("connect")
def test_connect(sid, data):
    print(f"⚡: {sid} user just connected!")
    users.append(sid)
    print(users)


@sio.on("disconnect")
async def test_disconnect(sid):
    print(f"🔥: {sid} user disconnected")
    users.remove(sid)   
    await sio.disconnect(sid)
    print(users)


@sio.event
async def message(sid, data):
    print(f"SID: {sid}")
    print(data)
    print(f"Message: {data['text']} from {data['name']}")
    await sio.emit("messageResponse", data)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
