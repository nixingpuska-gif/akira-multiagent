"""Workspace abstraction (ASCII only)."""

from __future__ import annotations

from typing import List


class Workspace:
    def list(self, path: str) -> List[str]:
        raise NotImplementedError

    def read(self, path: str, max_bytes: int = 200_000) -> str:
        raise NotImplementedError

    def write(self, path: str, content: str) -> None:
        raise NotImplementedError

    def exists(self, path: str) -> bool:
        raise NotImplementedError

    def realpath(self, path: str) -> str:
        raise NotImplementedError
