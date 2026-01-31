import subprocess
from datetime import datetime
from pathlib import Path
from typing import Tuple


def list_workflows(chatdev_path: str) -> list[str]:
    base = Path(chatdev_path)
    candidates = list(base.glob("yaml_instance/*.yaml")) + list(base.glob("yaml_instance/*.yml"))
    return [str(p) for p in candidates]


def run_chatdev(
    prompt: str,
    chatdev_path: str,
    workflow_path: str,
    project_name: str,
    mode: str = "safe",
    timeout_s: int = 1800,
) -> str:
    if mode != "full":
        return "ERROR: ChatDev disabled in safe mode. Set AKIRA_MODE=full."
    base = Path(chatdev_path)
    if not base.exists():
        return f"ERROR: ChatDev path not found: {chatdev_path}"

    wf_path = Path(workflow_path)
    if not wf_path.is_absolute():
        wf_path = base / workflow_path

    cmd = [
        "python",
        "run.py",
        "--path",
        str(wf_path),
        "--name",
        project_name,
    ]
    try:
        proc = subprocess.run(
            cmd,
            input=prompt + "\n",
            text=True,
            cwd=str(base),
            capture_output=True,
            timeout=timeout_s,
        )
        output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        return output[-8000:] if output else "OK"
    except subprocess.TimeoutExpired:
        return "ERROR: ChatDev timeout"


def spawn_chatdev(
    prompt: str,
    chatdev_path: str,
    workflow_path: str,
    project_name: str,
    data_dir: str,
    mode: str = "safe",
) -> Tuple[subprocess.Popen, str] | str:
    if mode != "full":
        return "ERROR: ChatDev disabled in safe mode. Set AKIRA_MODE=full."
    base = Path(chatdev_path)
    if not base.exists():
        return f"ERROR: ChatDev path not found: {chatdev_path}"

    wf_path = Path(workflow_path)
    if not wf_path.is_absolute():
        wf_path = base / workflow_path

    log_dir = Path(data_dir) / "chatdev" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"{project_name}_{ts}.log"
    log_file = open(log_path, "w", encoding="utf-8")

    cmd = [
        "python",
        "run.py",
        "--path",
        str(wf_path),
        "--name",
        project_name,
    ]
    proc = subprocess.Popen(
        cmd,
        cwd=str(base),
        stdin=subprocess.PIPE,
        stdout=log_file,
        stderr=log_file,
        text=True,
    )
    try:
        if proc.stdin:
            proc.stdin.write(prompt + "\n")
            proc.stdin.close()
    except Exception:
        pass
    return proc, str(log_path)
