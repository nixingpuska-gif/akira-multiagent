import subprocess

import psutil


def list_processes(limit: int = 50):
    procs = []
    for p in psutil.process_iter(["pid", "name"]):
        procs.append({"pid": p.info["pid"], "name": p.info["name"]})
        if len(procs) >= limit:
            break
    return procs


def start_process(command: str, mode: str = "safe") -> str:
    if mode != "full":
        return "ERROR: Process start disabled in safe mode. Set AKIRA_MODE=full."
    subprocess.Popen(command, shell=True)
    return "OK"
