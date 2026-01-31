"""Sandbox workspace (ASCII only)."""

from __future__ import annotations

import os
from typing import Iterable, List

from .base import Workspace


class SandboxWorkspace(Workspace):
    def __init__(self, allowed_roots: Iterable[str]):
        roots = [os.path.abspath(r) for r in (allowed_roots or [])]
        if not roots:
            roots = [os.getcwd()]
        self.allowed_roots = [r.rstrip("\\/") for r in roots]
        self.base_root = self.allowed_roots[0]

    def list(self, path: str) -> List[str]:
        apath = self._check(path)
        return os.listdir(apath)

    def read(self, path: str, max_bytes: int = 200_000) -> str:
        apath = self._check(path)
        with open(apath, "r", encoding="utf-8", errors="replace") as f:
            return f.read(max_bytes)

    def write(self, path: str, content: str) -> None:
        apath = self._check(path)
        os.makedirs(os.path.dirname(apath) or ".", exist_ok=True)
        with open(apath, "w", encoding="utf-8") as f:
            f.write(content)

    def exists(self, path: str) -> bool:
        apath = self._check(path)
        return os.path.exists(apath)

    def realpath(self, path: str) -> str:
        return self._resolve(path)

    def _resolve(self, path: str) -> str:
        if not path:
            path = "."
        if os.path.isabs(path):
            return os.path.abspath(path)
        return os.path.abspath(os.path.join(self.base_root, path))

    def _check(self, path: str) -> str:
        apath = self._resolve(path)
        for root in self.allowed_roots:
            try:
                if os.path.commonpath([apath, root]) == root:
                    return apath
            except Exception:
                continue
        raise PermissionError(f"Path outside allowed roots: {apath}")
