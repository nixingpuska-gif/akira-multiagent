"""World model utilities (ASCII only)."""

from __future__ import annotations

from ..memory.episodic import EpisodicMemory
from ..memory import MemoryStore


class WorldModel:
    def __init__(self, memory_store: MemoryStore | None):
        self.memory = memory_store
        self._episodic = EpisodicMemory(self.memory)

    def estimate_task_success(self, task: str, user_id: str, limit: int = 50) -> float:
        if self.memory is None:
            return 0.0
        episodes = self.memory.get_recent_episodes(user_id=user_id, limit=limit)
        task_type = self._episodic._classify_task_type(task)
        matched = [e for e in episodes if self._episodic._classify_task_type(e.task) == task_type]
        if not matched:
            return 0.0
        successes = sum(1 for e in matched if e.success)
        return max(0.0, min(1.0, successes / max(len(matched), 1)))

    def estimate_step_risk(self, step: str) -> float:
        text = (step or "").lower()
        dangerous = [
            "delete",
            "rm ",
            "rm -",
            "format",
            "registry",
            "poweroff",
            "shutdown",
            "kill",
            "wipe",
            "erase",
            "diskpart",
            "mkfs",
            "del ",
            "remove",
            "uninstall",
        ]
        score = 0.0
        for kw in dangerous:
            if kw in text:
                score = max(score, 0.9)
        if "sudo" in text or "admin" in text:
            score = max(score, 0.7)
        return max(0.0, min(1.0, score))
