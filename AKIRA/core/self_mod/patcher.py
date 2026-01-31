"""Self-modification patcher (ASCII only)."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass
class PatchResult:
    patch_path: str
    request_id: str
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "patch_path": self.patch_path,
            "request_id": self.request_id,
            "created_at": self.created_at,
        }


class SelfModPatcher:
    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir
        self.patch_dir = os.path.join(self.data_dir, "self_mod", "patches")
        os.makedirs(self.patch_dir, exist_ok=True)

    def create_patch(self, target_path: str, issue: str, diff_text: str) -> PatchResult:
        content = self._normalize_text(diff_text)
        request_id = self._request_id(target_path, issue, content)
        filename = f"patch_{request_id}.diff"
        path = os.path.join(self.patch_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
            if not content.endswith("\n"):
                f.write("\n")
        return PatchResult(
            patch_path=path,
            request_id=request_id,
            created_at=datetime.utcnow().isoformat(),
        )

    @staticmethod
    def _request_id(target_path: str, issue: str, diff_text: str) -> str:
        raw = f"{target_path}\n{issue}\n{diff_text}".encode("utf-8", errors="ignore")
        return hashlib.sha256(raw).hexdigest()[:12]

    @staticmethod
    def _normalize_text(text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n")
