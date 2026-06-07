import os
from parser.Auth import authParser
from parser.Nginx import nginxParser
from parser.Apache import apacheParser

def detector(filePath):
    file_type = int(input(f"""Enter the type of this "{os.path.basename(filePath)}" file : Auth Log File[1], Apache Log File[2], Nginx Log File[3], Other type[4]:\n"""))
    
    if file_type == 4:
        print(f"Skipping the file {os.path.basename(filePath)}...\n")
        return None

    return file_type

def line_generator(filePath):
    with open(filePath) as f:
        while True:
            line = f.readline().strip()
            yield line

def line_fwding(filePath, parser):
    gen = line_generator(filePath)
    parser_obj = parser()

    while True:
       line = next(gen)

       if not line:
           continue
       
       print(line)
       parser_obj.analyze(line)

def main():
    
    inputPath = input("Enter the path of the File/Folder to be montiored : ")
    
    if os.path.isdir(inputPath):
        print(f"{inputPath} is a Directory. Reading its Contents\n")
        
        try:
            for fileName in os.listdir(inputPath):
                
                filePath = os.path.join(inputPath, fileName)
                
                if os.path.isdir(filePath):
                    print(f"Encountered A Directory {fileName}. Skipping it.\n")
                    continue
                    
                file_type = detector(filePath)
                if not file_type:
                    continue
                
                match file_type:
                    case 1:
                        print("Starting Monitoring for an Auth File:\n")
                        line_fwding(filePath, authParser)
                    case 2:
                        print("Starting Monitoring for an Apache Log File:\n")
                        line_fwding(filePath, apacheParser)
                    case 3:
                        print("Starting Monitoring for an Ngninx Log File:\n")
                        line_fwding(filePath, nginxParser)
        except Exception as e:
            print(e)
    else:
        print(f"{inputPath} is a File.\n")
        file_type = detector(inputPath)
        if not file_type:
            print("Bye Bye")
        
        match file_type:
            case 1:
                print("Starting Monitoring for an Auth File:\n")
                line_fwding(inputPath, authParser)
            case 2:
                print("Starting Monitoring for an Apache Log File:\n")
                line_fwding(inputPath, apacheParser)
            case 3:
                print("Starting Monitoring for an Ngninx Log File:\n")
                line_fwding(inputPath,nginxParser)


if __name__ == "__main__":
    main()