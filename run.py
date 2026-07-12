import os
import subprocess
import sys
import socket

def getFreePort():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("",0))
        return s.getsockname()[1]


if __name__ == "__main__":
    print("[LogSentinal] Installing Dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])

    print("[LogSentinal] Finding a free port... ")
    port = getFreePort()
    env = os.environ.copy()
    env["PORT"] = str(port)

    print(f"[LogSentinal] Received a free port: {port}")
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "AppData", "Backend"))

    server = subprocess.Popen([sys.executable, "-m", "uvicorn", "server:app", "--host", "0.0.0.0",  "--port", f"{port}"], cwd = base_dir, env=env)

    try:
        server.wait()
    except (KeyboardInterrupt, Exception):
        print("\n================================================================\n")
        print("Thanks for using the app...\n")
    finally:
        if server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()