import time

def hello(line: str):
    with open("./apache/apache1.log", "a") as f:
        f.write(line)

if __name__ == "__main__":
    with open("./sample.log") as f:
        for line in f:
            hello(line)
            print(line)
            time.sleep(10)