import json
import os
import threading
from typing import Any, Dict


def _safe_read_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except Exception:
        return {}
    return {}


def _safe_write_json(path: str, data: Dict[str, Any]) -> None:
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=True, indent=2)
    os.replace(tmp, path)


class LlmSettingsStore:
    def __init__(self, data_dir: str, filename: str = "llm_settings.json") -> None:
        self.data_dir = data_dir
        self.path = os.path.join(data_dir, filename)
        os.makedirs(self.data_dir, exist_ok=True)
        self._lock = threading.Lock()

    def get(self, user_id: str) -> Dict[str, Any]:
        return self.load_settings(user_id)

    def set(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        return self.save_settings(user_id, settings)

    def update(self, user_id: str, **fields: Any) -> Dict[str, Any]:
        settings = self.load_settings(user_id)
        settings.update({k: v for k, v in fields.items() if v is not None})
        return self.save_settings(user_id, settings)

    def reset(self, user_id: str) -> None:
        with self._lock:
            data = self._load_all()
            data.pop(str(user_id), None)
            self._save_all(data)

    def _load_all(self) -> Dict[str, Any]:
        return _safe_read_json(self.path)

    def _save_all(self, data: Dict[str, Any]) -> None:
        _safe_write_json(self.path, data)

    def load_settings(self, user_id: str) -> Dict[str, Any]:
        with self._lock:
            data = self._load_all()
            value = data.get(str(user_id), {})
            return value if isinstance(value, dict) else {}

    def save_settings(self, user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            data = self._load_all()
            data[str(user_id)] = settings
            self._save_all(data)
        return settings

    def set_provider(self, user_id: str, provider: str) -> Dict[str, Any]:
        return self.update(user_id, provider=provider)

    def set_model(self, user_id: str, model: str) -> Dict[str, Any]:
        return self.update(user_id, model=model)

    def set_openrouter_key(self, user_id: str, key: str) -> Dict[str, Any]:
        return self.update(user_id, openrouter_key=key)

    def set_primary_key(self, user_id: str, key: str) -> Dict[str, Any]:
        return self.update(user_id, primary_key=key)

    def set_custom_base(self, user_id: str, base: str) -> Dict[str, Any]:
        return self.update(user_id, custom_base=base)

    def set_custom_key(self, user_id: str, key: str) -> Dict[str, Any]:
        return self.update(user_id, custom_key=key)

    @staticmethod
    def _mask_key(key: str | None) -> str:
        if not key:
            return ""
        key = str(key)
        if len(key) <= 10:
            return "****"
        return f"{key[:7]}...{key[-4:]}"

    def mask_key(self, key: str | None) -> str:
        return self._mask_key(key)
