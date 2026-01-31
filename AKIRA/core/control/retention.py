"""Log retention (ASCII only)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


class LogRetention:
    def __init__(self, data_dir: str, days: int = 90) -> None:
        self.data_dir = data_dir
        self.days = max(1, int(days))
        self.state_path = os.path.join(self.data_dir, "retention_state.json")
        os.makedirs(self.data_dir, exist_ok=True)

    def maybe_purge(self) -> Dict[str, Any]:
        today = datetime.utcnow().date().isoformat()
        state = self._load_state()
        if state.get("last_run") == today:
            return {"skipped": True, "last_run": today, "purged": 0}
        result = self.purge()
        state = {"last_run": today}
        self._save_state(state)
        return result

    def purge(self) -> Dict[str, Any]:
        cutoff = datetime.utcnow() - timedelta(days=self.days)
        files = self._find_jsonl_files()
        removed_total = 0
        purged_files = 0
        errors: List[str] = []
        for path in files:
            removed, err = self._purge_file(path, cutoff)
            if err:
                errors.append(err)
                continue
            if removed > 0:
                purged_files += 1
                removed_total += removed
        return {
            "cutoff": cutoff.isoformat(),
            "files_checked": len(files),
            "files_purged": purged_files,
            "lines_removed": removed_total,
            "errors": errors,
        }

    def _find_jsonl_files(self) -> List[str]:
        results: List[str] = []
        for dirpath, dirnames, filenames in os.walk(self.data_dir):
            for name in filenames:
                if name.lower().endswith(".jsonl"):
                    results.append(os.path.join(dirpath, name))
        return results

    def _purge_file(self, path: str, cutoff: datetime) -> Tuple[int, Optional[str]]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as exc:
            return 0, f"Failed to read {path}: {exc}"
        kept: List[str] = []
        removed = 0
        for line in lines:
            ts = self._extract_timestamp(line)
            if ts is None:
                kept.append(line)
                continue
            if ts >= cutoff:
                kept.append(line)
            else:
                removed += 1
        if removed > 0:
            tmp = path + ".tmp"
            try:
                with open(tmp, "w", encoding="utf-8") as f:
                    f.writelines(kept)
                os.replace(tmp, path)
            except Exception as exc:
                return 0, f"Failed to write {path}: {exc}"
        return removed, None

    @staticmethod
    def _extract_timestamp(line: str) -> Optional[datetime]:
        try:
            obj = json.loads(line)
        except Exception:
            return None
        for key in ("timestamp", "created_at", "time", "ts"):
            value = obj.get(key)
            if not value:
                continue
            dt = LogRetention._parse_dt(str(value))
            if dt:
                return dt
        return None

    @staticmethod
    def _parse_dt(value: str) -> Optional[datetime]:
        text = value.strip()
        if text.endswith("Z"):
            text = text[:-1]
        try:
            return datetime.fromisoformat(text)
        except Exception:
            return None

    def _load_state(self) -> Dict[str, Any]:
        if not os.path.exists(self.state_path):
            return {}
        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save_state(self, data: Dict[str, Any]) -> None:
        tmp = self.state_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=True, indent=2, sort_keys=True)
        os.replace(tmp, self.state_path)
