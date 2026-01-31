"""Prompt library storage (ASCII only)."""

from __future__ import annotations

import json
import os
import threading
import uuid
import random
from typing import Any, Dict, List, Tuple


class PromptLibrary:
    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir
        self.path = os.path.join(self.data_dir, "prompt_library.json")
        os.makedirs(self.data_dir, exist_ok=True)
        self._lock = threading.Lock()

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            return {}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save(self, data: Dict[str, Any]) -> None:
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=True, indent=2)
        os.replace(tmp, self.path)

    def get_prompt(self, prompt_id: str, default: str) -> Tuple[str, str]:
        with self._lock:
            data = self._load()
            entry = data.get(prompt_id, {}) if isinstance(data, dict) else {}
            variants = entry.get("variants", {}) if isinstance(entry.get("variants", {}), dict) else {}
            ab_list = entry.get("ab", []) if isinstance(entry.get("ab", []), list) else []
            variant_id = entry.get("active")

            if ab_list:
                candidates = [vid for vid in ab_list if vid in variants]
                if candidates:
                    variant_id = random.choice(candidates)

            if variant_id and variant_id in variants:
                text = variants[variant_id].get("text", default)
                return text, variant_id

        return default, "default"

    def add_variant(self, prompt_id: str, text: str, meta: Dict[str, Any] | None = None) -> str:
        with self._lock:
            data = self._load()
            entry = data.setdefault(prompt_id, {})
            variants = entry.setdefault("variants", {})
            variant_id = f"v_{uuid.uuid4().hex[:8]}"
            variants[variant_id] = {"text": text, "meta": meta or {}}
            self._save(data)
        return variant_id

    def set_active(self, prompt_id: str, variant_id: str) -> None:
        with self._lock:
            data = self._load()
            entry = data.setdefault(prompt_id, {})
            entry["active"] = variant_id
            self._save(data)

    def enable_ab(self, prompt_id: str, variant_ids: List[str]) -> None:
        with self._lock:
            data = self._load()
            entry = data.setdefault(prompt_id, {})
            entry["ab"] = list(variant_ids)
            self._save(data)

    def reset(self, prompt_id: str) -> None:
        with self._lock:
            data = self._load()
            data.pop(prompt_id, None)
            self._save(data)
