import os
import sqlite3

#Database Folder:
dbFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), "Databases"))

class starter():
    def __init__(self):
        self.paths = {}
        self.unreadOldFiles: dict[str, list] = {}
        self.logType: dict[str, str] = {}
        self.newestFiles: dict[str, tuple] = {}

    def begin(self):
        print("[LogSentinal] Hello, User\n")

        for log in ["Apache", "Nginx", "Auth"]:
            path = None
            
            while True:
                path = input(f"[LogSentinal] Please Enter the path for the {log} log file [Hit Enter if you don't want to] : ")
                if path=="":
                    path=None
                    break
                
                path = os.path.abspath(path)
                if not os.path.exists(path):
                    print("[LogSentinal] Path Invalid. Please Try Again...")
                    continue
                elif not os.path.isdir(path):
                    print("[LogSentinal] Given Path is not a Directory. Please Try Again...")
                    continue

                break

            self.paths[log] = path

        self.logType = {v : k for k,v in self.paths.items() if v is not None}
        self.unreadOldFiles = {k : [] for k,v in self.paths.items() if v is not None}

        if not self.logType:
            print("[LogSentinal] Didn't recieve any path.")
            print("[LogSentinal] Exiting the Application...")
            return "EXIT"
        
        self.checkFiles()

    def checkFiles(self):
        for fileType, folderPath in self.paths.items():
            if not folderPath:
                continue

            newestFile = max([os.path.join(folderPath, f) for f in os.listdir(folderPath)] , key=os.path.getmtime)

            try:
                if not folderPath:
                    continue

                db_path = os.path.abspath(os.path.join(dbFolder, f"{fileType}.db"))
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row

                curr = conn.cursor()
                
                curr.execute("SELECT * FROM fileCounter")
                files = {row["FileName"] : row["LinesProcessed"] for row in curr.fetchall()}

                self.newestFiles[fileType] = (newestFile, files[os.path.basename(newestFile)] + 1)
                
                for fileName in os.listdir(folderPath):
                    filePath = os.path.join(os.path.abspath(folderPath), fileName)
                    linesInFile = 0

                    with open(filePath) as f:
                        for line in f:
                            linesInFile+=1

                    if fileName not in files.keys() and filePath != os.path.abspath(newestFile):
                        self.unreadOldFiles[fileType].append((filePath, 1))
                    elif linesInFile != files[fileName] and filePath != newestFile:
                        self.unreadOldFiles[fileType].append((filePath,files[fileName] + 1))

            except:
                
                for fileName in os.listdir(folderPath):
                    filePath = os.path.join(os.path.abspath(folderPath), fileName)
                    linesInFile = 0
                    with open(filePath) as f:
                        for line in f:
                            linesInFile+=1

                    if filePath != os.path.abspath(newestFile):
                        self.unreadOldFiles[fileType].append((filePath, 1))

                self.newestFiles[fileType] = (newestFile, 1)

        print()
        for fileType in self.paths.keys():
            if not self.paths[fileType]:
                continue

            print(f"{fileType}: {self.paths[fileType]}")

            for fileName in os.listdir(self.paths[fileType]):
                filePath = os.path.join(os.path.abspath(self.paths[fileType]), fileName)

                status = "Newest File" if filePath == self.newestFiles[fileType][0] else "Unread" if any(t[0] == filePath for t in self.unreadOldFiles[fileType]) else "Read"

                print(f"{fileName} : {status}")

            print()


    def detectFileType(self, filePath: str) -> str:
        return self.logType[os.path.dirname(filePath)]