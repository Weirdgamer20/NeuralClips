import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_EXE = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
SCRIPT_PATH = os.path.join(BASE_DIR, "run_live_monitor.py")

def is_running():
    try:
        # Check running processes in Windows
        output = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", 
             "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*run_live_monitor.py*' } | Select-Object -ExpandProperty ProcessId"],
            text=True
        )
        pids = [line.strip() for line in output.splitlines() if line.strip()]
        return len(pids) > 0
    except Exception:
        return False

def start_daemon():
    if not is_running():
        print("[AUTOSTART] Launching NeuralClips background live stream monitor...")
        subprocess.Popen(
            [PYTHON_EXE, SCRIPT_PATH],
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("[AUTOSTART] Live monitor daemon launched successfully.")
    else:
        print("[AUTOSTART] Live monitor daemon is already running.")

if __name__ == "__main__":
    start_daemon()
