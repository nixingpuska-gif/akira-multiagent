"""Meta learner for strategy selection (ASCII only)."""

from __future__ import annotations

import math
import os
import random
from datetime import datetime
from typing import List, Optional

from .strategies import Strategy, StrategyOutcome, StrategyStore


class MetaLearner:
    def __init__(
        self,
        data_dir: str,
        strategies: Optional[List[Strategy]] = None,
        base_epsilon: float = 0.2,
        min_epsilon: float = 0.05,
    ) -> None:
        self.store = StrategyStore(data_dir)
        self.strategies = strategies or [
            Strategy("default", "Follow standard instructions and complete the task directly."),
            Strategy("cautious", "Be careful with risky steps and validate before acting."),
        ]
        self.base_epsilon = base_epsilon
        self.min_epsilon = min_epsilon

    def _classify_task_type(self, task: str) -> str:
        task_lower = (task or "").lower()
        keywords = {
            "coding": ["code", "bug", "fix", "refactor", "test", "python", "js", "typescript", "java"],
            "browser": ["browser", "site", "page", "url", "click", "download", "form", "web"],
            "search": ["search", "find", "lookup", "docs", "learn", "info"],
            "file": ["file", "folder", "directory", "read", "write", "delete", "copy", "move"],
            "system": ["command", "terminal", "shell", "process", "install", "run", "execute"],
            "analysis": ["analyze", "review", "check", "compare", "report", "metrics"],
        }
        best_type = "unknown"
        best_score = 0
        for task_type, keys in keywords.items():
            score = sum(1 for k in keys if k in task_lower)
            if score > best_score:
                best_score = score
                best_type = task_type
        return best_type

    def select_strategy(self, task: str, user_id: str) -> Strategy:
        ab = os.getenv("AKIRA_STRATEGY_AB", "")
        if ab:
            ids = [p.strip() for p in ab.split(",") if p.strip()]
            pool = [s for s in self.strategies if s.id in ids]
            if pool:
                return random.choice(pool)

        task_type = self._classify_task_type(task)
        data = self.store._load()
        totals = 0
        if "by_task_type" in data and task_type in data["by_task_type"]:
            bucket = data["by_task_type"][task_type]
            totals = sum(int(v.get("total", 0)) for v in bucket.values())
        elif "global" in data:
            totals = sum(int(v.get("total", 0)) for v in data["global"].values())

        epsilon = max(self.min_epsilon, self.base_epsilon / math.sqrt(totals + 1))
        if random.random() < epsilon:
            return random.choice(self.strategies)

        best = self._best_by_success(task_type, data)
        return best or random.choice(self.strategies)

    def _best_by_success(self, task_type: str, data: dict) -> Optional[Strategy]:
        def pick(bucket: dict) -> Optional[Strategy]:
            best_id = None
            best_rate = -1.0
            for strat_id, stats in bucket.items():
                total = int(stats.get("total", 0))
                if total == 0:
                    continue
                rate = int(stats.get("success", 0)) / max(total, 1)
                if rate > best_rate:
                    best_rate = rate
                    best_id = strat_id
            if not best_id:
                return None
            return next((s for s in self.strategies if s.id == best_id), None)

        if "by_task_type" in data and task_type in data["by_task_type"]:
            picked = pick(data["by_task_type"][task_type])
            if picked:
                return picked
        if "global" in data:
            return pick(data["global"])
        return None

    def record_outcome(
        self,
        strategy_id: str,
        task: str,
        success: bool,
        latency_ms: int,
        user_id: str,
    ) -> None:
        task_type = self._classify_task_type(task)
        outcome = StrategyOutcome(
            strategy_id=strategy_id,
            success=bool(success),
            latency_ms=latency_ms,
            task_type=task_type,
            user_id=user_id,
            timestamp=datetime.utcnow().isoformat(),
        )
        self.store.record_outcome(outcome)
