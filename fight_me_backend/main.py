#!/usr/bin/env python
import uvicorn
import socketio
import asyncio

from threading import Thread

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = socketio.ASGIApp(sio)


users = {}
room = "test_room"
messages = {}

def broadcast_message():
    message = "Hello, clients!"
    socketio.emit('broadcast_message', message, broadcast=True)


@sio.on("connect")
def test_connect(sid, data):
    print(f"⚡: {sid} user just connected!")
    users[sid] = { "room": None }
    print(users)


@sio.on("disconnect")
async def test_disconnect(sid):
    print(f"🔥: {sid} user disconnected")
    sio.leave_room(sid, room)
    users.pop(sid)
    await sio.disconnect(sid)
    print(users)


@sio.event
async def message(sid, data):
    print(f"SID: {sid}")
    print(data)
    print(f"Message: {data['text']} from {data['name']}")

    if room in messages:
        messages[room].append(data)
    else:
        messages[room] = [data]

    print(messages)

    await sio.emit("messageResponse", data)

@sio.event
async def getMessages(sid, data):
    print(f"SID {sid} catching up on messages for room {data['room']}")

    print(f"Message history: {messages.get(data['room'])}")
    await sio.emit("getMessagesResponse", messages.get(data['room']))

@sio.event
async def getRoom(sid):
    print(f"Adding SID {sid} to room {room}")
    sio.enter_room(sid, room)
    users[sid]["room"] = room

    await sio.emit("getRoomResponse", { "room": room })
    

@sio.event
async def leaveRoom(sid, data):
    print(f"Removing SID {sid} from room {data['room']}")
    sio.leave_room(sid, room)
    users[sid]["room"] = None
    await sio.emit("leaveRoomResponse", { "room": data['room'] })


async def connected_users():
    users_in_rooms = sum(1 for _, user_data in users.items() if user_data.get('room') is not None)
    await sio.emit("connectedUsers", users_in_rooms)

async def connected_users_timer(interval_seconds):
    while True:
        await connected_users()
        await asyncio.sleep(interval_seconds)

def start_connected_users_timer():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.create_task(connected_users_timer(2))
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
    finally:
        loop.close()


thread = Thread(target=start_connected_users_timer, daemon=True)
thread.start()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
