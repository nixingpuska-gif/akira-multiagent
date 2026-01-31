"""Interactive terminal sessions (ASCII only)."""

from __future__ import annotations

import os
import queue
import threading
import time
import uuid
import subprocess
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class TerminalSession:
    session_id: str
    proc: subprocess.Popen
    output_queue: "queue.Queue[str]"
    thread: threading.Thread


class TerminalSessionManager:
    def __init__(self) -> None:
        self.sessions: Dict[str, TerminalSession] = {}

    def open(self, command: Optional[str] = None) -> str:
        if command is None:
            command = "cmd.exe" if os.name == "nt" else "/bin/bash"
        session_id = uuid.uuid4().hex[:10]
        proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        q: "queue.Queue[str]" = queue.Queue()
        t = threading.Thread(target=self._reader, args=(proc, q), daemon=True)
        t.start()
        self.sessions[session_id] = TerminalSession(session_id, proc, q, t)
        return session_id

    def exec(self, session_id: str, command: str, timeout_s: float = 5.0) -> Dict[str, str]:
        session = self.sessions.get(session_id)
        if not session or not session.proc or session.proc.poll() is not None:
            return {"status": "error", "output": "", "error": "Session not found or closed."}
        sentinel = f"__END__{uuid.uuid4().hex[:6]}__"
        line = f"{command}\n"
        end_line = f"echo {sentinel}\n"
        try:
            session.proc.stdin.write(line)
            session.proc.stdin.write(end_line)
            session.proc.stdin.flush()
        except Exception as exc:
            return {"status": "error", "output": "", "error": str(exc)}

        output_lines = []
        start = time.time()
        while time.time() - start < timeout_s:
            try:
                item = session.output_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            if sentinel in item:
                break
            output_lines.append(item.rstrip("\r\n"))
        output = "\n".join(output_lines)
        output = output.encode("ascii", errors="ignore").decode("ascii")
        return {"status": "ok", "output": output, "error": ""}

    def close(self, session_id: str) -> bool:
        session = self.sessions.pop(session_id, None)
        if not session:
            return False
        try:
            if session.proc and session.proc.poll() is None:
                session.proc.terminate()
                try:
                    session.proc.wait(timeout=2)
                except Exception:
                    session.proc.kill()
        except Exception:
            pass
        return True

    @staticmethod
    def _reader(proc: subprocess.Popen, q: "queue.Queue[str]") -> None:
        try:
            for line in proc.stdout:
                q.put(line)
        except Exception:
            return
