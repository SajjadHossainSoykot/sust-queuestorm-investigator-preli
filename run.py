import uvicorn
import subprocess
import os
import signal
from app.config import settings

def kill_process_on_port(port: int):
    try:
        # lsof -t -i :<port> returns only the PIDs of processes using the port
        result = subprocess.run(
            ["lsof", "-t", f"-i:{port}"],
            capture_output=True,
            text=True,
            check=True
        )
        pids = [int(pid.strip()) for pid in result.stdout.strip().split("\n") if pid.strip()]
        for pid in pids:
            print(f"Port {port} is in use by PID {pid}. Terminating process...", flush=True)
            os.kill(pid, signal.SIGKILL)
    except subprocess.CalledProcessError:
        # lsof returns non-zero exit code if no process is using the port
        pass
    except Exception as e:
        print(f"Warning: Could not check or kill process on port {port}: {e}", flush=True)

if __name__ == "__main__":
    print(f"Checking port {settings.PORT}...", flush=True)
    kill_process_on_port(settings.PORT)

    print(f"Starting QueueStorm Investigator service on {settings.HOST}:{settings.PORT}...", flush=True)
    print(f"Debug Mode: {settings.DEBUG}", flush=True)
    if settings.GEMINI_API_KEY:
        print("Gemini API Key is configured. LLM analysis will be active.", flush=True)
    else:
        print("No Gemini API Key found. Service will run in LOCAL HEURISTIC mode.", flush=True)

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

