"""Tool library storage (ASCII only)."""

from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ToolSpec:
    name: str
    description: str
    args_schema: Dict[str, Any]
    code: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "args_schema": self.args_schema,
            "code": self.code,
            "created_at": self.created_at,
            "tags": list(self.tags),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ToolSpec":
        return ToolSpec(
            name=str(data.get("name", "")),
            description=str(data.get("description", "")),
            args_schema=data.get("args_schema", {}) if isinstance(data.get("args_schema", {}), dict) else {},
            code=str(data.get("code", "")),
            created_at=str(data.get("created_at", "")) or datetime.utcnow().isoformat(),
            tags=list(data.get("tags", [])) if isinstance(data.get("tags", []), list) else [],
        )


class ToolLibrary:
    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir
        self.path = os.path.join(self.data_dir, "tools_library.json")
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
            json.dump(data, f, ensure_ascii=True, indent=2, sort_keys=True)
        os.replace(tmp, self.path)

    def add(self, spec: ToolSpec) -> None:
        with self._lock:
            data = self._load()
            data[spec.name] = spec.to_dict()
            self._save(data)

    def get(self, name: str) -> Optional[ToolSpec]:
        with self._lock:
            data = self._load()
            entry = data.get(name)
            if not isinstance(entry, dict):
                return None
            return ToolSpec.from_dict(entry)

    def list_names(self) -> List[str]:
        with self._lock:
            data = self._load()
            return sorted([k for k in data.keys() if isinstance(k, str)])

    def list_specs(self) -> List[ToolSpec]:
        with self._lock:
            data = self._load()
            specs: List[ToolSpec] = []
            for key in data.keys():
                entry = data.get(key)
                if isinstance(entry, dict):
                    specs.append(ToolSpec.from_dict(entry))
            return specs
