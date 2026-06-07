import asyncio 
import socketio
import uvicorn
from fastapi import FastAPI


filePath = "./sample_log_files/apache_sample.log"

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=["http://localhost:5173"])
fastapi_app = FastAPI(title="LogSentinalServer")

app = socketio.ASGIApp(sio, fastapi_app)

