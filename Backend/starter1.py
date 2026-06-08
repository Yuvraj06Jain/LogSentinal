import os
import time
import queue
import asyncio
import aiofiles
import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from parser.Auth import authParser
from parser.Nginx import nginxParser
from parser.Apache import apacheParser

class Handler(FileSystemEventHandler):
    def __init__(self, active_gen, newFileQueue, parserObj):
        self.active_gen = active_gen
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
            await asyncio.sleep(0)


async def readPrevContents(active_gen, filePath):
    gen_obj, parserObj = active_gen[filePath]

    loop = asyncio.get_running_loop()
    while True:
        line = await anext(gen_obj)
        if not line:
            break
        
        data = await loop.run_in_executor(None, parserObj.analyze, line)

    

def newFile(filePath, active_gen, parserObj):
    new_genObj = generator(filePath)

    active_gen[filePath] = (new_genObj, parserObj)

    asyncio.create_task(readPrevContents(active_gen, filePath))

    if parserObj == apacheParser:
        print("Sending Package")
        # await sio.emit("Apache" , data)
    elif parserObj == nginxParser:
        print("Sending Package")
        # await sio.emit("Nginx" , data)
    else:
        print("Sending Package")
        # await sio.emit("Auth", data)

async def flush(gen_obj, parserObj):
    loop = asyncio.get_running_loop()

    while True:
        line = await anext(gen_obj)

        if not line:
            break
        
        data = await loop.run_in_executor(None, parserObj.analyze, line)

    if parserObj == apacheParser:
        print("Sending Package")
        # await sio.emit("Apache" , data)
    elif parserObj == nginxParser:
        print("Sending Package")
        # await sio.emit("Nginx" , data)
    else:
        print("Sending Package")
        # await sio.emit("Auth", data)


    

async def main():
    print("Hello, User")

    apache_path = input("Path for the Apache Log File [Just Hit Enter if you don't want to] : ")
    nginx_path = input("Path for the Nginx Log File [Just Hit Enter if you don't want to] : ")
    auth_path = input("Path for the Auth Log File [Just Hit Enter if you don't want to] : ")

    if not apache_path and not nginx_path and not auth_path:
        print("Didn't recieve any path.")
        print("Bye Bye")
        return
    
    active_generators = {}
    observer = Observer()
    newFileQueue = queue.Queue()

    if apache_path:
        for fileName in os.listdir(apache_path):
            if os.path.splitext(fileName)[1] != '.log':
                continue
            
            filePath = os.path.join(apache_path, fileName)

            newFile(filePath, active_generators, apacheParser())

        apache_handler = Handler(active_generators, newFileQueue, apacheParser)
        observer.schedule(apache_handler, path=apache_path, recursive=False)

    if nginx_path:
        for fileName in os.listdir(nginx_path):
            if os.path.split(fileName)[1] != '.log':
                continue
            
            filePath = os.path.join(nginx_path, fileName)

            newFile(filePath, active_generators, nginxParser())

        nginx_handler = Handler(active_generators, newFileQueue, nginxParser)
        observer.schedule(nginx_handler, path=nginx_path, recursive=False)

    if auth_path:
        for fileName in os.listdir(auth_path):
            if os.path.split(fileName)[1] != '.log':
                continue
            
            filePath = os.path.join(auth_path, fileName)

            newFile(filePath, active_generators, authParser())

        auth_handler = Handler(active_generators, newFileQueue, authParser)
        observer.schedule(auth_handler, path=auth_path, recursive=False)

    observer.start()

    try:
        last_flush = time.time()
        while True:
            try:
                parserObj, filePath = newFileQueue.get(timeout=1)
                newFile(filePath, active_generators, parserObj)
            except queue.Empty:
                pass

            if time.time() - last_flush >= 600:
                print("Updating the stats:")
                last_flush = time.time()
                flush_tasks = [flush(gen_obj, parserObj) for _,(gen_obj, parserObj) in active_generators.items()]
                await asyncio.gather(*flush_tasks)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        return

if __name__ == "__main__":
    asyncio.run(main())