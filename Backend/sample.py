import os
import signal
import time
import queue
import aiofiles
import asyncio

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

# ===============================================================================================================================================================================================

class Handler(FileSystemEventHandler):
    def __init__(self,active_gen, file_queue):
        self.active_gen = active_gen
        self.file_queue = file_queue
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        self.file_queue.put(event.src_path)
        
        
def generator(filePath):
    with open(filePath) as f:
        while True:
            line = f.readline().strip()
            yield line



def readPrevContents(active_gen, fileName):
    gen_obj, parserObj = active_gen[fileName]

    while True:
        line = next(gen_obj, "EOF")
        if line == "EOF":
            break
        
        parserObj.analyze(line)



def modify_inFile(filePath, active_gen):
    fileName = os.path.basename(filePath)

    if os.path.splitext(filePath)[1] != ".log":
        return

    if fileName not in active_gen.keys():
        return
    
    gen_obj, parserObj = active_gen[fileName]

    while True:
        line = next(gen_obj, "EOF")
        if line == "EOF":
            break

        print(f"Change Detected in the file = {fileName}")
        print(f"{line}\n")
        parserObj().analyze(line)



def newFile(filePath, active_gen):
    fileName = os.path.basename(filePath)

    if os.path.splitext(fileName)[1] != ".log":
        return
    elif not os.access(filePath, os.R_OK):
        print("You dont' have permissions to read this file. Ignoring the file.")
        return

    fileType = int(input(f"New log File Detected: {fileName}, Please Enter its type = [1] Auth, [2] Apache, [3] Nginx : "))
    match fileType:
        case 1:
            new_genObj = generator(filePath)
            active_gen[fileName] = (new_genObj, authObj)
        case 2:
            new_genObj = generator(filePath)
            active_gen[fileName] = (new_genObj, apacheObj)
        case 3:
            new_genObj = generator(filePath)
            active_gen[fileName] = (new_genObj, nginxObj)

    readPrevContents(active_gen, fileName)



def main():
    inputPath = input("Enter the path of the folder to be monitored : ")

    if os.path.isfile(inputPath):
        print(f"{os.path.basename(inputPath)} is a File. Please Enter the path to a folder")
        print("Bye Bye")
        return
    elif not os.access(inputPath, os.R_OK):
        print("You don't have the valid permission to read this Folder.")
        print("Bye Bye")
        return

    active_generators = {}

    for fileName in os.listdir(inputPath):
        if os.path.splitext(fileName)[1] != ".log":
            continue
            
        filePath = os.path.join(inputPath, fileName)

        newFile(filePath, active_generators)

    observer = Observer()
    file_queue = queue.Queue()
    handler = Handler(active_generators, file_queue)

    observer.schedule(handler, path=inputPath, recursive=False)

    observer.start()

    try:
        while True:
            try:
                filePath = file_queue.get(timeout=1)
                newFile(filePath, active_generators)
            except queue.Empty:
                continue
    except KeyboardInterrupt:
        observer.stop()

    observer.join()