
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer



from server import flush, sio
from starter import paths

#=============================================================================================================================================================================================

refresh = False

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
        
        await loop.run_in_executor(None, parserObj.analyze, line)

    data = parserObj.data_collection()
    
    if isinstance(parserObj, apacheParser):
        await sio.emit("Apache Logs Update" , data ,room= "apache")
    elif isinstance(parserObj, nginxParser):
        await sio.emit("Nginx Logs Update" , data ,room= "nginx")
    elif isinstance(parserObj, authParser):
        await sio.emit("Auth Logs Update" , data ,room= "auth")
    
    parserObj.data_clear()


def newFile(filePath, active_gen, parserObj):
    new_genObj = generator(filePath)

    active_gen[filePath] = (new_genObj, parserObj)

    asyncio.create_task(readPrevContents(active_gen, filePath))

async def start_monitoring():
    apache_path = paths.get("Apache")
    nginx_path = paths.get("Nginx")
    auth_path = paths.get("Auth")


    active_generators = {}
    observer = Observer()
    newFileQueue = asyncio.Queue()

    if apache_path:
        for fileName in os.listdir(apache_path):
            if os.path.split(fileName)[1] != '.log':
                continue
            
            filePath = os.path.join(apache_path, fileName)

            newFile(filePath, active_generators, apacheParser())

        apache_handler = Handler(active_generators, newFileQueue, apacheParser())
        observer.schedule(apache_handler, path=apache_path, recursive=False)

    if nginx_path:
        for fileName in os.listdir(nginx_path):
            if os.path.split(fileName)[1] != '.log':
                continue
            
            filePath = os.path.join(nginx_path, fileName)

            newFile(filePath, active_generators, nginxParser())

        nginx_handler = Handler(active_generators, newFileQueue, nginxParser())
        observer.schedule(nginx_handler, path=nginx_path, recursive=False)

    if auth_path:
        for fileName in os.listdir(auth_path):
            if os.path.split(fileName)[1] != '.log':
                continue
            
            filePath = os.path.join(auth_path, fileName)

            newFile(filePath, active_generators, authParser())

        auth_handler = Handler(active_generators, newFileQueue, authParser())
        observer.schedule(auth_handler, path=auth_path, recursive=False)

    observer.start()
    paused = False

    try:
        last_flush = time.time()
        while True:
            try:
                parserObj, filePath = await newFileQueue.get()
                newFile(filePath, active_generators, parserObj)
            except queue.Empty:
                pass

            if (time.time() - last_flush >= 600) or refresh:
                print("Updating the stats:")
                last_flush = time.time()
                flush_tasks = [flush(gen_obj, parserObj,apacheParser, nginxParser, authParser) for _,(gen_obj, parserObj) in active_generators.items()]
                await asyncio.gather(*flush_tasks)

                refresh = False

    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        return
