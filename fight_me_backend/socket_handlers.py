import random
import time
import asyncio
import uuid
from threading import Thread
from collections import deque

from .main import app, socket_manager as sm

users = {}
messages = {}
unfilled_rooms = deque()


@app.get("/health")
async def health_check():
    return {"status": "ok"}


def broadcast_message():
    message = "Hello, clients!"
    sm.emit("broadcast_message", message, broadcast=True)


@app.sio.on("connect")
def test_connect(sid, data):
    print(f"⚡: {sid} user just connected!")
    users[sid] = {"room": None}
    print(users)


@app.sio.on("disconnect")
async def test_disconnect(sid):
    print(f"🔥: {sid} user disconnected")
    app.sio.leave_room(sid, users[sid]["room"])
    users.pop(sid)
    await app.sio.disconnect(sid)
    print(users)


@app.sio.event
async def message(sid, data):
    print(f"SID: {sid}")
    print(data)

    data["timestamp"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time()))

    print(f"Message: {data['text']} from {data['name']} at {data['timestamp']}")

    if data.get("room") in messages:
        messages[data["room"]].append(data)
    else:
        messages[data["room"]] = [data]

    print(messages)

    await app.sio.emit("messageResponse", data)


@app.sio.event
async def getMessages(sid, data):
    print(f"SID {sid} catching up on messages for room {data['room']}")

    print(f"Message history: {messages.get(data['room'])}")
    await app.sio.emit("getMessagesResponse", messages.get(data["room"]))


def getRoomToJoin():
    if len(unfilled_rooms):
        return unfilled_rooms.popleft()
    else:
        room = uuid.uuid4().hex
        unfilled_rooms.append(room)
        return room


@app.sio.event
async def getRoom(sid):
    room = getRoomToJoin()
    print(f"Adding SID {sid} to room {room}")
    app.sio.enter_room(sid, room)
    users[sid]["room"] = room

    topic = "Lorem Ipsum"
    side = bool(random.getrandbits(1))

    await app.sio.emit("getRoomResponse", {"room": room, "topic": topic, "side": side})


@app.sio.event
async def leaveRoom(sid, data):
    print(f"Removing SID {sid} from room {data['room']}")
    app.sio.leave_room(sid, data["room"])

    num_in_room = sum(1 for _, user_data in users.items() if user_data.get("room") is data["room"])
    print(f"Num left in room: {num_in_room}")
    if num_in_room > 0:
        unfilled_rooms.append(data["room"])

    users[sid]["room"] = None
    await app.sio.emit("leaveRoomResponse", {"room": data["room"]}, to=sid)


async def connected_users():
    users_in_rooms = sum(1 for _, user_data in users.items() if user_data.get("room") is not None)
    await app.sio.emit("connectedUsers", {"users": len(users), "usersInRooms": users_in_rooms})


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
