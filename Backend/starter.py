import os

paths = {}

def starter():
    print("Hello, User")

    apache_path = input("Path for the Apache Log File [Just Hit Enter if you don't want to] : ")
    if apache_path and not os.path.exists(apache_path):
        print("Given Path is not valid.")
        print("Exiting the program...")
        return "EXIT"
    elif apache_path and not os.path.isdir(apache_path):
        print("Not a Directory.")
        print("Exiting the Program...")
        return "EXIT"

    nginx_path = input("Path for the Nginx Log File [Just Hit Enter if you don't want to] : ")
    if nginx_path and not os.path.exists(nginx_path):
        print("Given Path is not valid.")
        print("Exiting the program...")
        return "EXIT"
    elif nginx_path and not os.path.isdir(nginx_path):
        print("Not a Directory.")
        print("Exiting the Program...")
        return "EXIT"

    auth_path = input("Path for the Auth Log File [Just Hit Enter if you don't want to] : ")
    if auth_path and not os.path.exists(auth_path):
        print("Given Path is not valid.")
        print("Exiting the program...")
        return "EXIT"
    elif auth_path and not os.path.isdir(auth_path):
        print("Not a Directory.")
        print("Exiting the Program...")
        return "EXIT"

    paths.update({"Apache": apache_path, "Nginx": nginx_path, "Auth": auth_path})

    if not apache_path and not nginx_path and not auth_path:
        print("Didn't recieve any path.")
        print("Exiting the Program...")
        return "EXIT"
    
    ls(paths)

def ls(paths:dict):
    print()
    for dirs in paths.values():
        dirs = os.path.abspath(dirs)
        print(f"Files in the {os.path.basename(dirs)}: ")
        for fileName in os.listdir(dirs):
            print(fileName, end="   ")
        print("\n")
