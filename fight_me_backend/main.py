#!/usr/bin/env python

import uvicorn
import socketio


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_socketio import SocketManager

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)

socket_manager = SocketManager(app=app)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
