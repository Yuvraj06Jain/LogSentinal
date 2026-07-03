import os
import signal
import time
import queue
import aiofiles
import asyncio
import threading
from datetime import datetime

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import socketio
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from parser.Auth import authParser
from parser.Nginx import nginxParser
from parser.Apache import apacheParser

from starter import starter
import database_operations as dbos

import mmdb_operations as mmdbos
from blacklist_check import obj as blck
from bot_check import obj as botchk

#=====================================================================================================================================================================================
# PARSER OBJECTS

apacheObj = apacheParser()
nginxObj = nginxParser()
authObj = authParser()

# ===============================================================================================================================================================================
# STARTER OBJECT:

st = starter() # Obj for the starter Class.

#FUNCTION TO DETECT THE PARSER OBJ FOR A LOG TYPE
def detectParserObj(logType:str):
    return {"Apache" : apacheParser, "Nginx" : nginxParser, "Auth" : authParser}[logType]()

# KEEPING A TRACK OF ACTIVE TASKS
active_tasks = {}       # (FILE PATH, TASK, STOP EVENT, PARSER OBJ)

# KEEPING A TRACK OF THE COUNTERS FOR THE FILES BEING MONITORED.
shippedLines = {}       # { FILEPATH : COUNTER }

# Summary Report Folder:
reportFolder = os.path.join(os.path.dirname(__file__), "..", "..", "SummaryReports")
# Database Folder:
dbFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), "Databases"))

# PORT at which the server is running:
PORT = int(os.environ.get("PORT", 8000))

# GeoData Update Timer:
async def geoDataTimer():
    print("[LogSentinal] Downloading the Geolocation Database...\n")
    mmdbos.download_unzip()
    
    while True:
        await asyncio.sleep(60 * 60 * 24)                 # TO RUN AFTER EVERY 24 HOURS
        print("[LogSentinal] Downloading the Geolocation Database...\n")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, mmdbos.download_unzip)

# Blacklist Cache Timer:
async def blacklistCacheTimer():
    print("[LogSentinal] Creating the cache for Blacklisted IPs...\n")
    blck.create_cache()
    while True:
        await asyncio.sleep(60 * 60 * 7)                  # TO RUN AFTER EVERY 7 HOURS
        print("[LogSentinal] Creating the cache for Blacklisted IPs...\n")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, blck.create_cache)

# BotList IPs Cache Timer: 
async def botListCacheTimer():
    print("[LogSentinal] Creating the cache for Botlist IPs...\n")
    botchk.create_cache()
    while True:
        await asyncio.sleep(60 * 60 * 3)                  # TO RUN AFTER EVERY 3 HOURS
        print("[LogSentinal] Creating the cache for BotList IPs...\n")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, botchk.create_cache)


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



async def polling_analyzing_realTime(filePath, gen_obj, parserObj, startIndex, stop_event):
    
    while True:
        line = await anext(gen_obj)

        if startIndex!=1:
            startIndex-=1
            shippedLines[filePath] += 1
            continue

        if line == "":           # EOF reached
            if stop_event.is_set():
                break

            await asyncio.sleep(0.5)
            continue

        parserObj.analyze(line)
        shippedLines[filePath] += 1
        


async def newFile(filePath, parserObj):
    print(f"New File Detected in Folder {os.path.dirname(filePath)}: {os.path.basename(filePath)}. Starting its Monitoring...")
    dir_name = os.path.dirname(filePath)

    # Fetching the task of the older file in the folder:
    oldFilePath , oldFileTask, stop_event, parserObj = active_tasks[dir_name]

    stop_event.set()
    await oldFileTask

    print(f"Deleted the old File ({os.path.basename(oldFilePath)}) task")

    # Starting the monitoring for the new File
    shippedLines[filePath] = 0

    new_genObj = generator(filePath)
    stop_event = asyncio.Event()

    task = asyncio.create_task(polling_analyzing_realTime(filePath, new_genObj, parserObj, 1, stop_event))

    dir_name = os.path.dirname(filePath)
    active_tasks[dir_name] = (filePath, task, stop_event , parserObj)



async def flush():
    print("Starting the Flush....")

    FinalData = {}

    for folder, (filePath, _, _, parserObj) in active_tasks.items():
        data = {}
        try:
            data, events, requests = parserObj.data_collection()
            await dbos.writing_data(st.detectFileType(filePath), events, requests, (os.path.basename(filePath), shippedLines[filePath]))
            print(f"Database Write for {os.path.basename(folder)} folder Successful.\n")
            parserObj.data_clear()
        except Exception as e:
            print(f"Encountered an Error for the folder {os.path.basename(folder)}...\n{e}\n")

        fileType = st.detectFileType(filePath)
        FinalData[fileType] = data if data else {}

    await sio.emit(f"Real Time Logs Update", FinalData)
    print(f"Real Time logs Updated successfully...\n")

    print("Flush completed....\n")



async def monitoring(shutdown_event):
    print("\n================================================================\n")
    print(f"[LogSentinal] Open your browser at 'http://localhost:{PORT}'\n")
    print("[LogSentinal] Waiting for a connection...\n")


    observer = Observer()
    newFileQueue = queue.Queue()

    files: dict[str, tuple] = {fileType: st.newestFiles[fileType] for fileType in ['Apache', 'Nginx', 'Auth'] if st.newestFiles.get(fileType)}

    print()

    for fileType, (file, startIndex) in files.items():
        print(f"Starting Monitoring for file :  {os.path.basename(file)} from Line No. : {startIndex}")

        shippedLines[file] = 0
        
        new_genObj = generator(file)
        parserObj = detectParserObj(fileType)
        stop_event = asyncio.Event()

        task = asyncio.create_task(polling_analyzing_realTime(file, new_genObj, parserObj, startIndex, stop_event))

        dir_name = os.path.dirname(file)
        active_tasks[dir_name] = (file, task, stop_event, parserObj)

        handler = Handler(newFileQueue, parserObj)
        observer.schedule(handler, path=dir_name, recursive=False)
    
    print()

    observer.start()

    loop = asyncio.get_running_loop()
    await asyncio.gather(*[reviewingOldFiles(logType) for logType in ['Apache', 'Nginx', 'Auth']], loop.run_in_executor(None, monitoring_loop, observer, newFileQueue, loop, shutdown_event))



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
            
            timeInterval = 5 if firstFlush else 60
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
    if not logType in st.unreadOldFiles.keys():
        return
    
    tasks = [asyncio.create_task(processOldFile(logType,filePath, startIndex )) for filePath,startIndex in st.unreadOldFiles[logType] ]
    oldFileTasks[logType] = tasks

    try:
        await asyncio.gather(*tasks, return_exceptions=True)
    finally:
        oldFileTasks[logType] = []
    

async def processOldFile(logType, filePath, startIndex):
    parserObj = detectParserObj(logType)
    genObj = generator(filePath)

    #Process the Old File
    line_count = await polling_analyzing_oldFiles(genObj, parserObj, startIndex)
    #Write to DB
    _, events, requests = parserObj.data_collection()
    await dbos.writing_data(logType, events, requests, (os.path.basename(filePath), line_count))

    st.unreadOldFiles[logType].remove((filePath, startIndex))


async def polling_analyzing_oldFiles(genObj, parserObj, startIndex):
        count = 0
        while True:
            line = await anext(genObj)
            if startIndex!=1:
                startIndex-=1
                continue

            if line == "":          # EOF reached
                break

            parserObj.analyze(line)
            count+=1
        return count

#======================================================================================================================================================================================
# SERVER

# FastApi events
@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(reportFolder, exist_ok=True)
    os.makedirs(dbFolder, exist_ok=True)

    try:
        x = st.begin()
    except:
        x = "EXIT"

    if x == "EXIT":
        os.kill(os.getpid(), signal.SIGTERM)

    dbos.deleteData()
    

    shutdown_event = threading.Event()

    print("\n================================================================\n")

    # Starting the Timers for updating the databases and then starting monitoring...
    geoData_task = asyncio.create_task(geoDataTimer())
    blacklistCache_task = asyncio.create_task(blacklistCacheTimer())
    botList_task = asyncio.create_task(botListCacheTimer())
    monitoring_task = asyncio.create_task(monitoring(shutdown_event))

    try:
        yield
    finally:
        shutdown_event.set()

        for task in (geoData_task, blacklistCache_task, botList_task, monitoring_task):
            task.cancel()

        await asyncio.gather(geoData_task, blacklistCache_task, botList_task, monitoring_task, return_exceptions=True)


sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=["*"])
fastapi_app = FastAPI(title="LogSentinalServer", lifespan=lifespan)

app = socketio.ASGIApp(sio, fastapi_app)

# Socketio Events
@sio.event
async def connect(sid, *args):
    print("[LogSentinal] Client Connected...\n")
    active_rooms = []
    
    for val in st.logType.values():
        active_rooms.append(val)

    print("[LogSentinal]  Sending Rooms Data...\n")
    await sio.emit("Sending Rooms Data...", active_rooms,to=sid)

    print("[LogSentinal] Starting Monitoring")

    global connection_status
    connection_status = True
    global firstFlush
    firstFlush = True


@sio.event
async def disconnect(sid):
    global connection_status
    connection_status = False

@sio.event
async def historical(sid, logType, from_ts, to_ts):

    print(f"[LogSentinal] Fetching Historical Data From : {from_ts} to To : {to_ts}\n")

    if logType not in ['Apache', 'Nginx', 'Auth']:
        print("[LogSentinal] Historical Data Fetching Failed...\n")
        return {"Status" : "Failed" , "Message" : "Invalid Log Type", "Data" : {}}

    if oldFileTasks.get(logType):
        print("[LogSentinal] Historical Data Fetching Failed...\n")
        return {"Status" : "Failed", "Message" : "Reviewing Old Files. Please Wait...", "Data" : {}}
    
    if db_tasks.get(logType):
        print("[LogSentinal] Historical Data Fetching Failed...\n")
        return {"Status" : "Failed", "Message" : "Previous Fetch has not been completed. Please Wait...", "Data" : {}}
    
    msg = await dbos.getData(logType, from_ts, to_ts)

    print("[LogSentinal] Historical Data Fetched Successfully...\n")
    await sio.emit(f"Updating Historical data of {logType} logs", msg['Data'], to=sid)
    return {"Status" : msg["Status"], "Message" : msg["Message"]}
    

@sio.event
async def Refresh(sid):
    print("[LogSentinal] Refresh Signal Recieved, Flusing the data...\n")
    
    global refresh
    refresh = True
    return {"Status" : "OK", "Message" : "Refreshed..."}


@sio.event
async def generateSummary(sid, from_ts:str, to_ts:str, selected:dict):
    print("[LogSentinal] Sumamry Message Recieved")
    markdown_str = dbos.summary(from_ts, to_ts, selected)

    fileName = f"Summary dated on {datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.md"
    filePath = os.path.join(reportFolder, fileName)

    try:
        async with aiofiles.open(filePath, "w") as f:
            await f.write(markdown_str)
        return {"Status" : "Success", "Message" : "Summary Report created and stored successfully in the folder SummaryReport. Please Check..."}
    except Exception as e:
        print(f"[LogSentinal] Summary Failure : {e}")
        return {"Status" : "Failed", "Message" : "Failed to create the summary report. Please Try Again..."}

@sio.event
def EXIT(sid):
    os.kill(os.getpid(), signal.SIGTERM)


# FastAPI Events
fastapi_app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

@fastapi_app.get("/")
async def serve_frontend():
    return FileResponse("dist/index.html")
