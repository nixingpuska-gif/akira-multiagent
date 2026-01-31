"""Strategy tracking (ASCII only)."""

from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass
class Strategy:
    id: str
    description: str


@dataclass
class StrategyOutcome:
    strategy_id: str
    success: bool
    latency_ms: int | None
    task_type: str
    user_id: str
    timestamp: str


class StrategyStore:
    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir
        self.path = os.path.join(self.data_dir, "strategy_stats.json")
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

    def record_outcome(self, outcome: StrategyOutcome) -> None:
        with self._lock:
            data = self._load()
            data.setdefault("global", {})
            data.setdefault("by_task_type", {})

            self._update_stats(data["global"], outcome)
            task_bucket = data["by_task_type"].setdefault(outcome.task_type, {})
            self._update_stats(task_bucket, outcome)

            self._save(data)

    def _update_stats(self, bucket: Dict[str, Any], outcome: StrategyOutcome) -> None:
        strat = bucket.setdefault(outcome.strategy_id, {})
        total = int(strat.get("total", 0)) + 1
        success = int(strat.get("success", 0)) + (1 if outcome.success else 0)
        fail = int(strat.get("fail", 0)) + (0 if outcome.success else 1)
        avg_latency = float(strat.get("avg_latency", 0.0))
        if outcome.latency_ms is not None:
            avg_latency = ((avg_latency * (total - 1)) + outcome.latency_ms) / total

        strat.update(
            {
                "total": total,
                "success": success,
                "fail": fail,
                "avg_latency": round(avg_latency, 2),
                "last_used": outcome.timestamp,
            }
        )
