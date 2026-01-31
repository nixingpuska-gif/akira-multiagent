"""Prompt usage tracking (ASCII only)."""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime
from typing import Any, Dict, Optional


class PromptTracker:
    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir
        self.path = os.path.join(self.data_dir, "prompt_usage.jsonl")
        os.makedirs(self.data_dir, exist_ok=True)
        self._lock = threading.Lock()

    def record(
        self,
        prompt_id: str,
        variant_id: str,
        user_id: str,
        success: bool,
        latency_ms: Optional[int] = None,
        error: Optional[str] = None,
        task: Optional[str] = None,
    ) -> None:
        payload: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "prompt_id": self._coerce_id(prompt_id),
            "variant_id": self._coerce_id(variant_id),
            "user_id": self._coerce_id(user_id),
            "success": bool(success),
            "latency_ms": latency_ms,
            "error": self._shorten(error),
            "task": self._shorten(task),
        }
        line = json.dumps(payload, ensure_ascii=True)
        with self._lock:
            try:
                with open(self.path, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
            except Exception:
                # Best-effort logging; avoid crashing caller.
                return

    @staticmethod
    def _shorten(text: Optional[str], limit: int = 200) -> str:
        if not text:
            return ""
        cleaned = " ".join(str(text).split())
        return cleaned[:limit]

    @staticmethod
    def _coerce_id(value: Any) -> str:
        if value is None:
            return "unknown"
        text = str(value).strip()
        return text if text else "unknown"
