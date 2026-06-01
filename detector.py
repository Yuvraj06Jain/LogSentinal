import re
import os
from auth_parser import auth_parsing
from apache_parser import apache_parsing
from nginx_parser import nginx_parsing


auth_pattern = r"^[a-zA-Z]"
nginx_pattern = r"(rt=\d+\.\d+)$"

def file_type_detection(path):
    try:
        with open(path,'r') as f:
            line = f.readline()
            if(re.search(auth_pattern,line)):
                return 1
            else:
                if(re.search(nginx_pattern,line)):
                    return 3
                else:
                    return 2
                
    except FileNotFoundError:
        print(f"No file found at {path}")
        return None
    except PermissionError:
        print("You don't have the permisson to read this file")
        return None
    except IsADirectoryError:
        print("A Directory")
        return None

"""
1 = An Auth log File
2 = An Apache log file
3 = A Nginx log File
"""

def helper(file_type, path):
    match file_type:
        case 1:
            print("File Type: Linux Auth log file\n")
            auth_parsing(path)
        case 2:
            print("File Type: Apache log file\n")
            apache_parsing(path)
        case 3:
            print("File Type: Nginx log file\n")
            nginx_parsing(path)
        case default:
            return


if __name__ == "__main__":
    path = input("Enter the path of the Folder / File to be Monitored:")

    if os.path.isfile(path):
        file_type = file_type_detection(path)
        helper(file_type,path)
    elif os.path.isdir(path):
        for filename in os.listdir(path):
            filePath = os.path.join(path, filename)

            file_type = file_type_detection(filePath)
            if file_type:
                helper(file_type, filePath)
                print("\n========================================================================================================================================\n")
