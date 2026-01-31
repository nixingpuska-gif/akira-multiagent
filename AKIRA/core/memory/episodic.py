"""Episodic memory utilities (ASCII only)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
import json
import threading

from .store import Episode, EnhancedMemoryStore


@dataclass
class EpisodeEvent:
    timestamp: str
    action: str
    result: str
    success: bool
    duration_sec: Optional[float] = None
    meta: Optional[Dict[str, Any]] = None


class EpisodicMemory:
    """Minimal episodic memory with per-user active episode tracking."""

    def __init__(self, memory_store: EnhancedMemoryStore):
        self.store = memory_store
        self._current: Dict[str, Dict[str, Any]] = {}
        self._last_episode: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def start_episode(self, user_id: str, task: str, plan: str = "") -> None:
        with self._lock:
            self._current[user_id] = {
                "task": task,
                "plan": plan,
                "start_ts": datetime.utcnow(),
                "events": [],
            }

    def record_event(
        self,
        user_id: str,
        action: str,
        result: str,
        success: bool,
        duration_sec: Optional[float] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        with self._lock:
            if user_id not in self._current:
                self._current[user_id] = {
                    "task": "unknown",
                    "plan": "",
                    "start_ts": datetime.utcnow(),
                    "events": [],
                }
            safe_meta = self._safe_json(meta) if meta is not None else None
            event = EpisodeEvent(
                timestamp=datetime.utcnow().isoformat(),
                action=action,
                result=result,
                success=bool(success),
                duration_sec=duration_sec,
                meta=safe_meta,
            )
            self._current[user_id]["events"].append(event)

    def finish_episode(
        self,
        user_id: str,
        result: str,
        error: Optional[str] = None,
        success: Optional[bool] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[int]:
        with self._lock:
            session = self._current.get(user_id)
            if not session:
                session = {"task": "unknown", "plan": "", "start_ts": datetime.utcnow(), "events": []}
            events: List[EpisodeEvent] = session.get("events", [])
            if success is None:
                if events:
                    success = all(e.success for e in events)
                else:
                    has_result = bool(result and str(result).strip())
                    success = bool(has_result and error is None)

            now = datetime.utcnow()
            start_ts: datetime = session.get("start_ts", now)
            duration_sec = max((now - start_ts).total_seconds(), 0.0)

            actions = []
            for e in events:
                actions.append(
                    {
                        "timestamp": e.timestamp,
                        "action": e.action,
                        "result": e.result,
                        "success": e.success,
                        "duration_sec": e.duration_sec,
                        "meta": self._safe_json(e.meta),
                    }
                )
            actions_json = json.dumps(actions, ensure_ascii=True)
            tags_json = json.dumps(tags or [], ensure_ascii=True)

            episode = Episode(
                user_id=user_id,
                task=session.get("task", ""),
                plan=session.get("plan", ""),
                actions=actions_json,
                result=result,
                success=bool(success),
                error=error,
                duration_sec=duration_sec,
                tags=tags_json,
            )

            episode_id = self.store.save_episode(episode)
            self._current.pop(user_id, None)

            task_type = self._classify_task_type(episode.task)
            prev = self._last_episode.get(user_id)
            if prev:
                try:
                    self.store.link_episodes(
                        user_id=user_id,
                        episode_id=episode_id,
                        related_episode_id=prev.get("id"),
                        relation="follows",
                        confidence=1.0,
                    )
                    if (prev.get("success") is False) and success and prev.get("task_type") == task_type:
                        self.store.link_episodes(
                            user_id=user_id,
                            episode_id=episode_id,
                            related_episode_id=prev.get("id"),
                            relation="fixes",
                            confidence=0.9,
                        )
                except Exception:
                    pass

            self._last_episode[user_id] = {
                "id": episode_id,
                "success": bool(success),
                "task_type": task_type,
            }
            return episode_id

    def get_recent(self, user_id: str, limit: int = 20) -> List[Episode]:
        return self.store.get_recent_episodes(user_id=user_id, limit=limit)

    def predict_success(self, user_id: str, task: str) -> float:
        task_type = self._classify_task_type(task)
        episodes = self.store.get_recent_episodes(user_id=user_id, limit=50)
        matched = [e for e in episodes if self._classify_task_type(e.task) == task_type]
        if not matched:
            return 0.0
        successes = sum(1 for e in matched if e.success)
        return max(0.0, min(1.0, successes / max(len(matched), 1)))

    @staticmethod
    def _safe_json(value: Any) -> Any:
        try:
            json.dumps(value, ensure_ascii=True)
            return value
        except Exception:
            return str(value)

    @staticmethod
    def _classify_task_type(task: str) -> str:
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
