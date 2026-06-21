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

from starter import starter
import database_operations as dbos

#=====================================================================================================================================================================================
# PARSER OBJECTS

apacheObj = apacheParser()
nginxObj = nginxParser()
authObj = authParser()

# ===============================================================================================================================================================================
# STARTER OBJECT:
st = starter() # Obj for the starter Class.

# Asyncio.Events for all the file Types for controlling the tasks related to these Log types
realTime: dict[str, asyncio.Event]  = {"Apache" : asyncio.Event(), "Nginx" : asyncio.Event(), "Auth" : asyncio.Event()}
for e in realTime.values():
    e.set()

#FUNCTION TO DETECT THE PARSER OBJ FOR A LOG TYPE
def detectParserObj(logType:str):
    return {"Apache" : apacheObj, "Nginx" : nginxObj, "Auth" : authObj}.get(logType)

# KEEPING A TRACK OF ACTIVE TASKS
active_tasks = {}       # (FILE PATH, TASK, GEN OBJ, PARSER OBJ)

# KEEPING A TRACK OF THE COUNTERS FOR THE FILES BEING MONITORED.
shippedLines = {}       # { FILEPATH : COUNTER }

# ===============================================================================================================================================================================
#REAL TIME MONITOR CODE:

refresh = False
firstFlush = True
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
            yield line


async def polling_analyzing_realTime(filePath, gen_obj, parserObj, startIndex, event:asyncio.Event):
    while True:
        await event.wait()

        line = await anext(gen_obj)

        if startIndex!=1:
            startIndex-=1
            shippedLines[filePath] += 1
            continue

        if line == "":              # EOF reached
            await asyncio.sleep(0.5)
            continue

        parserObj.analyze(line)
        shippedLines[filePath] += 1
        


async def drain_to_eof(oldGenObj, parserObj, oldFilePath):
    while True:
        line = await anext(oldGenObj)

        if not line:
            break

        parserObj.analyze(line)
        shippedLines[oldFilePath] += 1


async def newFile(filePath, parserObj):
    print(f"New File Detected in Folder {os.path.dirname(filePath)}: {os.path.basename(filePath)}. Starting its Monitoring...")
    dir_name = os.path.dirname(filePath)

    # Fetching the generator of the older file in the folder:
    oldFilePath , oldFileTask, oldGenObj, oldParserObj = active_tasks[dir_name]

    if oldFileTask:

        oldFileTask.cancel()
        try:
            await oldFileTask
        except asyncio.CancelledError:
            pass

        await drain_to_eof(oldGenObj, oldParserObj, oldFilePath)
    
    print(f"Deleted the old File ({os.path.basename(oldFilePath)}) task")
    # Starting the monitoring for the new File
    shippedLines[filePath] = 0

    new_genObj = generator(filePath)
    task = asyncio.create_task(polling_analyzing_realTime(filePath, new_genObj, parserObj, 1, realTime[st.detectFileType(filePath)]))

    dir_name = os.path.dirname(filePath)
    active_tasks[dir_name] = (filePath, task, new_genObj, parserObj)



async def flush():
    print("Starting the Flush....")

    for folder, (filePath, _, _, parserObj) in active_tasks.items():
        
        if not realTime[st.detectFileType(filePath)].is_set():
            return
        
        try:
            data, events, requests = parserObj.data_collection()
        except Exception as e:
            print(f"Encountered an Error during Data Collection for the folder {os.path.basename(folder)}...\n{e}")

        # try:
        #     await dbos.writing_data(st.detectFileType(filePath), events, requests, (os.path.basename(filePath), shippedLines[filePath]))
        #     print(f"Database Write for {os.path.basename(folder)} folder Successful.\n")
        #     parserObj.data_clear()
        # except:
        #     print(f"Database Write for {os.path.basename(folder)} folder Failed. Will Try Again...\n")


        print(data)
        fileType = st.detectFileType(filePath)
        await sio.emit(f"{fileType} Logs Update", data)
        print(f"{fileType} Logs Updated successfully...\n")

    print("Flush completed....")



async def monitoring(shutdown_event):
    # apacheFile = st.newestFiles.get("Apache")       # returns (NEWEST FILE PATH, STARTING POINT)
    # nginxFile = st.newestFiles.get("Nginx")
    # authFile = st.newestFiles.get("Auth")

    observer = Observer()
    newFileQueue = queue.Queue()

    files: dict[str, tuple] = {fileType: st.newestFiles[fileType] for fileType in ['Apache', 'Nginx', 'Auth'] if st.newestFiles[fileType]}

    print()

    for fileType, (file, startIndex) in files.items():
        print(f"Most Recent file in {os.path.dirname(file)} is {os.path.basename(file)}. Starting its monitoring....")

        shippedLines[file] = 0
        
        new_genObj = generator(file)
        parserObj = detectParserObj(fileType)
        task = asyncio.create_task(polling_analyzing_realTime(file, new_genObj, parserObj, startIndex, realTime[fileType]))

        dir_name = os.path.dirname(file)
        active_tasks[dir_name] = (file, task, new_genObj, parserObj)

        handler = Handler(newFileQueue, parserObj)
        observer.schedule(handler, path=dir_name, recursive=False)
    
    print()

    observer.start()

    loop = asyncio.get_running_loop()
    await asyncio.gather(*[reviewingOldFiles(logType) for logType in realTime.keys()], loop.run_in_executor(None, monitoring_loop, observer, newFileQueue, loop, shutdown_event))



def monitoring_loop(observer, newFileQueue, loop, shutdown_event):
    global refresh
    global firstFlush

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
            
            timeInterval = 5 if firstFlush else 30
            if (time.time() - last_flush >= timeInterval or refresh) and connection_status:
                last_flush = time.time()

                future = asyncio.run_coroutine_threadsafe(flush(), loop)
                future.add_done_callback(lambda f: f.exception() and print(f"Flush Failed. Error : {f.exception()!r}"))

                refresh = False
                firstFlush = False
                
    finally:
        observer.stop()
        observer.join()

#======================================================================================================================================================================================
#HISTORICAL DATA:

db_tasks: dict[str, asyncio.Task] = {}
oldFileTasks: dict[str,list] = {}

async def reviewingOldFiles(logType):
    tasks = [asyncio.create_task(processOldFile(logType,filePath, startIndex )) for filePath,startIndex in st.unreadOldFiles[logType]]


    oldFileTasks[logType] = tasks
    await asyncio.gather(*tasks)
    

async def processOldFile(logType, filePath, startIndex):
    parserObj = detectParserObj.get(logType)
    genObj = generator(filePath)

    #Process the Old File
    await polling_analyzing_oldFiles(genObj, parserObj, startIndex)
    #Write to DB
    _, events, requests, shippedLines = parserObj.data_collection()
    await dbos.writing_data(logType, events, requests, (filePath, shippedLines))

    st.unreadOldFiles[logType].remove((filePath, startIndex))


async def polling_analyzing_oldFiles(genObj, parserObj, startIndex):
        while True:
            line = await anext(genObj)
            if startIndex!=1:
                startIndex-=1
                continue

            if line == "":          # EOF reached
                break

            parserObj.analyze(line)

#======================================================================================================================================================================================
# SERVER

# FastApi events
@asynccontextmanager
async def lifespan(app: FastAPI):
    x = st.begin()

    if x == "EXIT":
        os.kill(os.getpid(), signal.SIGTERM)
    
    shutdown_event = threading.Event()
    task = asyncio.create_task(monitoring(shutdown_event))

    try:
        yield
    finally:
        shutdown_event.set()
        task.cancel()


sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=["http://localhost:5173"])
fastapi_app = FastAPI(title="LogSentinalServer", lifespan=lifespan)

app = socketio.ASGIApp(sio, fastapi_app)

# Socketio Events
@sio.event
async def connect(sid, *args):
    print("Client Connected...\n")
    active_rooms = []
    
    for val in st.logType.values():
        active_rooms.append(val)

    print("Sending Rooms Data...\n")
    await sio.emit("Sending Rooms Data...", active_rooms,to=sid)

    print("Starting Monitoring")

    global connection_status
    connection_status = True
    global firstFlush
    firstFlush = True


@sio.event
async def disconnect(sid):
    global connection_status
    connection_status = False

@sio.event
async def historical(sid, logType:str, from_ts, to_ts):
    if logType not in realTime.keys():
        return {"Status" : "Failed" , "Message" : "Invalid Log Type"}

    if oldFileTasks[logType]:
        return {"Status" : "Failed", "Message" : "Reviewing Old Files. Please Wait..."}
    
    if db_tasks.get(logType):
        return {"Status" : "Failed", "Message" : "Previous Fetch has not been completed. Please Wait..."}
    
    msg = await dbos.getData(logType, from_ts, to_ts)

    await sio.emit(f"Updating Historical data of {logType} logs", msg, to=sid)
    

@sio.event
async def pause_resume(logType:str):
    if logType not in realTime.keys():
        return {"Status" : "Failed", "Message" : "Invalid Log Type"}
    
    if realTime[logType].is_set():
        realTime[logType].clear()
        return {"Status" : "Success", "Message" : "Paused"}
    else:
        realTime[logType].is_set()
        return {"Status" : "Success", "Message" : "Resumed"}



@sio.event
async def Refresh(sid):
    print("Refresh Signal Recieved, Flusing the data...")
    
    global refresh
    refresh = True
    return {"Status" : "OK"}


@sio.event
def EXIT():
    os.kill(os.getpid(), signal.SIGTERM)


if __name__ == "__main__":
    uvicorn.run(app, port=8000)



# if apacheFile:
    #     print(f"Most Recent file in {os.path.dirname(apacheFile[0])} is {os.path.basename(apacheFile[0])}. Starting its monitoring....")
        
    #     new_genObj = generator(apacheFile[0])
    #     task = asyncio.create_task(polling_analyzing_realTime(new_genObj, apacheObj, apacheFile[1], realTime["Apache"]))

    #     dir_name = os.path.dirname(apacheFile[0])
    #     active_tasks[dir_name] = (apacheFile[0], task, new_genObj, apacheObj)

    
    #     apache_handler = Handler(newFileQueue, apacheObj)
    #     observer.schedule(apache_handler, path=os.path.dirname(apacheFile[0]), recursive=False)

    # if nginxFile:
    #     print(f"Most Recent file in {os.path.dirname(nginxFile[0])} is {os.path.basename(nginxFile[0])}. Starting its monitoring....")

    #     new_genObj = generator(nginxFile[0])
    #     task = asyncio.create_task(polling_analyzing_realTime(new_genObj, nginxObj, nginxFile[1], realTime["Nginx"]))

    #     dir_name = os.path.dirname(nginxFile[0])
    #     active_tasks[dir_name] = (nginxFile[0], task, new_genObj, nginxObj)

    #     nginx_handler = Handler(newFileQueue, nginxObj)
    #     observer.schedule(nginx_handler, path=os.path.dirname(nginxFile[0]), recursive=False)

    # if authFile:
    #     print(f"Most Recent file in {os.path.dirname(authFile[0])} is {os.path.basename(authFile[0])}. Starting its monitoring....")

    #     new_genObj = generator(authFile[0])
    #     task = asyncio.create_task(polling_analyzing_realTime(new_genObj, authObj, authFile[1], realTime["Auth"]))

    #     dir_name = os.path.dirname(authFile[0])
    #     active_tasks[dir_name] = (authFile[0], task, new_genObj, authObj)

    #     auth_handler = Handler(newFileQueue, authObj)
    #     observer.schedule(auth_handler, path=os.path.dirname(authFile[0]), recursive=False)