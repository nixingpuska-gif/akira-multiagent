"""Local workspace (ASCII only)."""

from __future__ import annotations

import os
from typing import List

from .base import Workspace


class LocalWorkspace(Workspace):
    def list(self, path: str) -> List[str]:
        return os.listdir(path)

    def read(self, path: str, max_bytes: int = 200_000) -> str:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(max_bytes)

    def write(self, path: str, content: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def exists(self, path: str) -> bool:
        return os.path.exists(path)

    def realpath(self, path: str) -> str:
        return os.path.abspath(path)
