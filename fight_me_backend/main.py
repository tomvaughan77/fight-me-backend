#!/usr/bin/env python
import uvicorn

import socketio

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = socketio.ASGIApp(sio)


users = []


@sio.on("connect")
def test_connect(sid):
    print(f"⚡: {sid} user just connected!")
    print(users)


@sio.on("disconnect")
def test_disconnect(sid):
    print(f"🔥: {sid} user disconnected")
    users.remove({"socketID": sid})
    sio.emit("newUserResponse", users)
    sio.disconnect()


@sio.on("newUser")
def new_user(data):
    users.push(data)
    sio.emit("newUserResponse", users)


@sio.event
def message(data):
    sio.emit("messageResponse", data)


@sio.event
def typing(sid, data):
    sio.emit("typingResponse", data, skip_sid=sid)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
