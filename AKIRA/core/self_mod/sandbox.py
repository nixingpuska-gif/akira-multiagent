"""Self-modification sandbox checks (ASCII only)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Iterable, List, Optional


@dataclass
class SandboxResult:
    ok: bool
    errors: List[str]
    files: List[str]


class SelfModSandbox:
    FILE_LINE_RE = re.compile(r"^[+-]{3}\s+(.+)$")
    SECRET_BASENAMES = {
        "id_rsa",
        "id_dsa",
        "id_ed25519",
        "id_ecdsa",
        "credentials",
        ".npmrc",
        ".pypirc",
    }
    SECRET_SUFFIXES = (".pem", ".key", ".pfx", ".p12")

    def __init__(self, allowed_roots: Optional[Iterable[str]] = None) -> None:
        roots = [os.path.abspath(r) for r in (allowed_roots or [os.getcwd()])]
        self.allowed_roots = [r.rstrip("\\/") for r in roots]

    def validate_diff(self, diff_text: str) -> SandboxResult:
        errors: List[str] = []
        files = self._extract_files(diff_text)
        if not self._is_ascii(diff_text):
            errors.append("Diff contains non-ASCII characters.")
        if "\x00" in diff_text:
            errors.append("Diff contains binary null bytes.")
        for path in files:
            if not self._is_within_roots(path):
                errors.append(f"Path outside allowed roots: {path}")
            if self._is_secret_path(path):
                errors.append(f"Secret file modification blocked: {path}")
        return SandboxResult(ok=not errors, errors=errors, files=files)

    def validate_diff_file(self, path: str) -> SandboxResult:
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as exc:
            return SandboxResult(ok=False, errors=[f"Failed to read diff: {exc}"], files=[])
        return self.validate_diff(text)

    def _extract_files(self, diff_text: str) -> List[str]:
        files: List[str] = []
        for line in diff_text.splitlines():
            match = self.FILE_LINE_RE.match(line.strip())
            if not match:
                continue
            raw = match.group(1).strip()
            if raw == "/dev/null":
                continue
            path = self._normalize_diff_path(raw)
            if path:
                files.append(path)
        return files

    @staticmethod
    def _normalize_diff_path(path: str) -> str:
        if path.startswith("a/") or path.startswith("b/"):
            path = path[2:]
        return os.path.abspath(path)

    def _is_within_roots(self, path: str) -> bool:
        apath = os.path.abspath(path)
        for root in self.allowed_roots:
            try:
                if os.path.commonpath([apath, root]) == root:
                    return True
            except Exception:
                continue
        return False

    def _is_secret_path(self, path: str) -> bool:
        apath = os.path.abspath(path)
        lower = apath.replace("\\", "/").lower()
        base = os.path.basename(lower)
        if base.startswith(".env"):
            return True
        if base in self.SECRET_BASENAMES:
            return True
        if base.endswith(self.SECRET_SUFFIXES):
            return True
        if "/.aws/credentials" in lower:
            return True
        if "/.ssh/" in lower or lower.endswith("/.ssh"):
            return True
        return False

    @staticmethod
    def _is_ascii(text: str) -> bool:
        try:
            text.encode("ascii")
            return True
        except Exception:
            return False
