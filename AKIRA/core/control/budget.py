"""Request budget manager (ASCII only)."""

from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class BudgetState:
    date: str
    limit: int
    used: int

    def to_dict(self) -> Dict[str, Any]:
        return {"date": self.date, "limit": self.limit, "used": self.used}


class RequestBudget:
    def __init__(self, data_dir: str, limit_per_day: int = 10000) -> None:
        self.data_dir = data_dir
        self.limit_per_day = max(1, int(limit_per_day))
        self.path = os.path.join(self.data_dir, "request_budget.json")
        os.makedirs(self.data_dir, exist_ok=True)
        self._lock = threading.Lock()

    def remaining(self) -> int:
        state = self._load_state()
        return max(state.limit - state.used, 0)

    def consume(self, count: int = 1) -> Dict[str, Any]:
        count = max(1, int(count))
        with self._lock:
            state = self._load_state_locked()
            if state.used + count > state.limit:
                return {
                    "ok": False,
                    "error": self._error_msg(state),
                    "state": state.to_dict(),
                }
            state.used += count
            self._save_state_locked(state)
            return {"ok": True, "error": "", "state": state.to_dict()}

    def _load_state(self) -> BudgetState:
        with self._lock:
            return self._load_state_locked()

    def _load_state_locked(self) -> BudgetState:
        today = datetime.utcnow().date().isoformat()
        if not os.path.exists(self.path):
            return BudgetState(date=today, limit=self.limit_per_day, used=0)
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            date = str(data.get("date", "")) or today
            limit = int(data.get("limit", self.limit_per_day))
            used = int(data.get("used", 0))
        except Exception:
            return BudgetState(date=today, limit=self.limit_per_day, used=0)
        if date != today:
            return BudgetState(date=today, limit=self.limit_per_day, used=0)
        if limit != self.limit_per_day:
            limit = self.limit_per_day
        return BudgetState(date=date, limit=limit, used=used)

    def _save_state_locked(self, state: BudgetState) -> None:
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, ensure_ascii=True, indent=2, sort_keys=True)
        os.replace(tmp, self.path)

    @staticmethod
    def _error_msg(state: BudgetState) -> str:
        return (
            f"ERROR: request budget exceeded for {state.date} "
            f"(used={state.used}, limit={state.limit})."
        )
