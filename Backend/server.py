import os
import signal
import time
import queue
import aiofiles
import asyncio
import threading

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import socketio
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from parser.Auth import authParser
from parser.Nginx import nginxParser
from parser.Apache import apacheParser

from starter import starter, paths

#===============================================================================================================================================================================================
# PARSER OBJECTS

apacheObj = apacheParser()
nginxObj = nginxParser()
authObj = authParser()

# ===============================================================================================================================================================================
# MONITOR CODE:

refresh = False
active_tasks = []
active_generators = {}
connection_status = False

class Handler(FileSystemEventHandler):
    def __init__(self, newFileQueue, parserObj):
        self.newFileQueue = newFileQueue
        self.parserObj = parserObj
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        self.newFileQueue.put((self.parserObj, event.src_path))
        
        

async def generator(filePath):
    async with aiofiles.open(filePath) as f:
        while True:
            line = await f.readline()
            line = line.strip()
            yield line


async def polling_analyzing(gen_obj, parserObj):
    while True:
        line = await anext(gen_obj)
        if line == "":
            await asyncio.sleep(0.5)
        else:
            parserObj.analyze(line)


# async def readPrevContents(active_gen, filePath):
#     gen_obj, parserObj = active_gen[filePath]

#     loop = asyncio.get_running_loop()
#     while True:
#         line = await anext(gen_obj)
#         if not line:
#             break
        
#         await loop.run_in_executor(None, parserObj.analyze, line)


async def newFile(filePath, parserObj):
    print(f"New File Detected: {os.path.basename(filePath)}")
    print("Starting its Monitoring...\n")

    new_genObj = generator(filePath)
    task = asyncio.create_task(polling_analyzing(new_genObj, parserObj))

    active_generators[filePath] = (new_genObj, parserObj)
    active_tasks.append(task)


async def flush():
    print("Starting the Flush....")

    # flush_tasks = [flush(gen_obj, parserObj) for _, (gen_obj, parserObj) in active_generators.items()]
    # await asyncio.gather(*flush_tasks)

    if paths.get("Apache"):
        print("Sending Data to Apache Room...")
        data = apacheObj.data_collection()
        await sio.emit("Apache Logs Update" , data ,room= "apache")
    if paths.get("Nginx"):
        print("Sending Data to Nginx Room...")
        data = nginxObj.data_collection()
        await sio.emit("Nginx Logs Update" , data ,room= "nginx")
    if paths.get("Auth"):
        print("Sending Data to Auth Room...")
        data = authObj.data_collection()
        await sio.emit("Auth Logs Update" , data ,room= "auth")

    print("Flush completed....")



# async def flush(gen_obj, parserObj):
#     loop = asyncio.get_running_loop()

#     while True:
#         line = await anext(gen_obj)

#         if not line:
#             break
        
#         await loop.run_in_executor(None, parserObj.analyze, line)



async def start_monitoring(shutdown_event):
    global refresh

    apache_path = paths.get("Apache")
    nginx_path = paths.get("Nginx")
    auth_path = paths.get("Auth")

    observer = Observer()
    newFileQueue = queue.Queue()

    if apache_path:
        for fileName in os.listdir(apache_path):
            if os.path.splitext(fileName)[1] != '.log':
                continue
            
            filePath = os.path.join(apache_path, fileName)

            await newFile(filePath, apacheObj)

        apache_handler = Handler(newFileQueue, apacheObj)
        observer.schedule(apache_handler, path=apache_path, recursive=False)

    if nginx_path:
        for fileName in os.listdir(nginx_path):
            if os.path.splitext(fileName)[1] != '.log':
                continue
            
            filePath = os.path.join(nginx_path, fileName)

            await newFile(filePath, nginxObj)

        nginx_handler = Handler(newFileQueue, nginxObj)
        observer.schedule(nginx_handler, path=nginx_path, recursive=False)

    if auth_path:
        for fileName in os.listdir(auth_path):
            if os.path.splitext(fileName)[1] != '.log':
                continue
            
            filePath = os.path.join(auth_path, fileName)

            await newFile(filePath, authObj)

        auth_handler = Handler(newFileQueue, authObj)
        observer.schedule(auth_handler, path=auth_path, recursive=False)

    observer.start()

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, monitoring_loop, observer, newFileQueue, loop, shutdown_event)



def monitoring_loop(observer, newFileQueue, loop, shutdown_event):
    global refresh
    firstFlush = True
    try:
        last_flush = time.time()
        while True:
            try:
                parserObj, filePath = newFileQueue.get(timeout=1)
                asyncio.run_coroutine_threadsafe(newFile(filePath, parserObj), loop)
            except queue.Empty:
                pass
            
            if shutdown_event.is_set():
                break

            if (time.time() - last_flush >= 60 or refresh or firstFlush) and connection_status:
                last_flush = time.time()
                asyncio.run_coroutine_threadsafe(flush(), loop)

                refresh = False
                firstFlush = False
                
    finally:
        observer.stop()
        observer.join()

#======================================================================================================================================================================================
# SERVER

@asynccontextmanager
async def lifespan(app: FastAPI):
    msg = starter()
    if msg == "EXIT":
        os.kill(os.getpid(), signal.SIGTERM)
    
    shutdown_event = threading.Event()
    task = asyncio.create_task(start_monitoring(shutdown_event))

    try:
        yield
    finally:
        shutdown_event.set()
        task.cancel()



sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=["http://localhost:5173"])
fastapi_app = FastAPI(title="LogSentinalServer", lifespan=lifespan)

app = socketio.ASGIApp(sio, fastapi_app)


@sio.event
async def connect(sid, *args):
    print("Client Connected...\n")

    active_rooms = []

    if paths['Apache']:
        await sio.enter_room(sid, 'apache')
        active_rooms.append("Apache")
    if paths['Nginx']:
        await sio.enter_room(sid, 'nginx')
        active_rooms.append("Nginx")
    if paths['Auth']:
        await sio.enter_room(sid, 'auth')
        active_rooms.append("Auth")

    await sio.emit("Active Rooms", active_rooms)

    print("Starting Monitoring")

    global connection_status
    connection_status = True

@sio.event
async def disconnect(sid):
    global connection_status
    connection_status = False


@sio.event
async def Refresh(sid):
    print("Refresh Signal Recieved, Flusing the data...")
    
    global refresh
    refresh = True


@sio.event
def EXIT():
    os.kill(os.getpid(), signal.SIGTERM)

@fastapi_app.post("/refresh")
def refreshClicked():
    global refresh
    refresh = True

if __name__ == "__main__":
    uvicorn.run(app, port=8000)