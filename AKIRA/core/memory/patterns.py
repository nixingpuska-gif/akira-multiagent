"""Pattern recognition utilities (ASCII only)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from collections import Counter, defaultdict
import json
import hashlib

from .store import Episode, Pattern, EnhancedMemoryStore


@dataclass
class CausalChain:
    cause: str
    effect: str
    confidence: float
    occurrences: int


@dataclass
class TaskClassification:
    task_type: str
    confidence: float
    keywords: List[str]


@dataclass
class ExtractedPattern:
    name: str
    action_sequence: List[str]
    frequency: int
    success_rate: float
    avg_duration: float


TASK_KEYWORDS = {
    "coding": ["code", "bug", "fix", "refactor", "test", "python", "js", "typescript", "java", "class"],
    "browser": ["browser", "site", "page", "url", "click", "download", "form", "web"],
    "search": ["search", "find", "lookup", "docs", "learn", "info"],
    "file": ["file", "folder", "directory", "read", "write", "delete", "copy", "move"],
    "system": ["command", "terminal", "shell", "process", "install", "run", "execute"],
    "analysis": ["analyze", "review", "check", "compare", "report", "metrics"],
}


class PatternRecognizer:
    """Extracts simple action patterns from episodes and stores them."""

    def __init__(self, memory_store: EnhancedMemoryStore):
        self.store = memory_store
        self._pattern_cache: Dict[str, List[ExtractedPattern]] = {}
        self._causal_cache: List[CausalChain] = []

    def classify_task(self, task: str) -> TaskClassification:
        task_lower = (task or "").lower()
        scores: Dict[str, Tuple[int, List[str]]] = {}
        for task_type, keywords in TASK_KEYWORDS.items():
            matched = [kw for kw in keywords if kw in task_lower]
            scores[task_type] = (len(matched), matched)

        best_type = "unknown"
        best_score = 0
        best_keywords: List[str] = []
        for task_type, (score, keywords) in scores.items():
            if score > best_score:
                best_score = score
                best_type = task_type
                best_keywords = keywords

        total = sum(s[0] for s in scores.values())
        confidence = best_score / max(total, 1)
        return TaskClassification(
            task_type=best_type,
            confidence=round(confidence, 2),
            keywords=best_keywords,
        )

    def extract_patterns(self, episodes: List[Episode]) -> List[ExtractedPattern]:
        if not episodes:
            return []

        sequences: List[Tuple[List[str], bool, float]] = []
        for ep in episodes:
            try:
                actions_data = json.loads(ep.actions) if ep.actions else []
                actions = [a.get("action", "") for a in actions_data if a.get("action")]
                if actions:
                    sequences.append((actions, ep.success, ep.duration_sec))
            except Exception:
                continue

        return self._find_subsequences(sequences)

    def _find_subsequences(
        self,
        sequences: List[Tuple[List[str], bool, float]],
    ) -> List[ExtractedPattern]:
        ngram_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"count": 0, "successes": 0, "durations": []}
        )

        for actions, success, duration in sequences:
            for n in range(2, min(5, len(actions) + 1)):
                for i in range(len(actions) - n + 1):
                    ngram = tuple(actions[i : i + n])
                    key = "->".join(ngram)
                    ngram_stats[key]["count"] += 1
                    if success:
                        ngram_stats[key]["successes"] += 1
                    ngram_stats[key]["durations"].append(duration)

        patterns: List[ExtractedPattern] = []
        for key, stats in ngram_stats.items():
            if stats["count"] >= 2:
                avg_dur = sum(stats["durations"]) / max(len(stats["durations"]), 1)
                patterns.append(
                    ExtractedPattern(
                        name=f"pattern_{len(patterns)}",
                        action_sequence=key.split("->"),
                        frequency=stats["count"],
                        success_rate=stats["successes"] / max(stats["count"], 1),
                        avg_duration=round(avg_dur, 2),
                    )
                )

        patterns.sort(key=lambda p: (p.frequency, p.success_rate), reverse=True)
        return patterns[:20]

    def update_patterns_for_user(self, user_id: str, limit: int = 200) -> List[int]:
        episodes = self.store.get_recent_episodes(user_id=user_id, limit=limit)
        patterns = self.extract_patterns(episodes)
        saved_ids: List[int] = []

        for pat in patterns:
            task_types = []
            for ep in episodes:
                if self._sequence_in_episode(pat.action_sequence, ep):
                    task_types.append(self.classify_task(ep.task).task_type)
            task_type = Counter(task_types).most_common(1)[0][0] if task_types else "unknown"

            name = self._pattern_name(user_id, pat.action_sequence)
            description = f"Sequence: {' -> '.join(pat.action_sequence)}"
            trigger = "action_sequence"
            strategy = json.dumps({"actions": pat.action_sequence}, ensure_ascii=True)

            pattern = Pattern(
                user_id=user_id,
                name=name,
                description=description,
                task_type=task_type,
                trigger=trigger,
                strategy=strategy,
                success_rate=pat.success_rate,
                usage_count=pat.frequency,
            )
            try:
                saved_ids.append(self.store.save_pattern(pattern))
            except Exception:
                continue

        return saved_ids

    @staticmethod
    def _sequence_in_episode(sequence: List[str], ep: Episode) -> bool:
        if not sequence or not ep.actions:
            return False
        try:
            actions_data = json.loads(ep.actions)
            actions = [a.get("action", "") for a in actions_data if a.get("action")]
        except Exception:
            return False
        if len(sequence) > len(actions):
            return False
        for i in range(len(actions) - len(sequence) + 1):
            if actions[i : i + len(sequence)] == sequence:
                return True
        return False

    @staticmethod
    def _pattern_name(user_id: str, sequence: List[str]) -> str:
        raw = f"{user_id}:" + "|".join(sequence)
        digest = hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()[:12]
        return f"{user_id}:{digest}"
