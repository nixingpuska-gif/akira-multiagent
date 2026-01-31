"""Prompt optimizer (ASCII only)."""

from __future__ import annotations

import json
import os
from typing import Dict, Optional

from .adaptive import PromptTracker
from .library import PromptLibrary


class PromptOptimizer:
    def __init__(self, tracker: PromptTracker, library: PromptLibrary) -> None:
        self.tracker = tracker
        self.library = library

    def select_best(self, prompt_id: str, min_samples: int = 5) -> Optional[str]:
        min_samples = self._normalize_min_samples(min_samples)
        path = self.tracker.path
        if not os.path.exists(path):
            return None
        totals: Dict[str, int] = {}
        successes: Dict[str, int] = {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    if obj.get("prompt_id") != prompt_id:
                        continue
                    variant_id = obj.get("variant_id")
                    if not variant_id:
                        continue
                    totals[variant_id] = totals.get(variant_id, 0) + 1
                    if obj.get("success") is True:
                        successes[variant_id] = successes.get(variant_id, 0) + 1
        except Exception:
            return None

        best_id = None
        best_rate = -1.0
        best_count = 0
        for vid, count in totals.items():
            if count < min_samples:
                continue
            rate = successes.get(vid, 0) / max(count, 1)
            if rate > best_rate:
                best_rate = rate
                best_count = count
                best_id = vid
                continue
            if rate == best_rate:
                if count > best_count:
                    best_count = count
                    best_id = vid
                    continue
                if count == best_count and best_id is not None and vid < best_id:
                    best_id = vid
        return best_id

    def apply_best(self, prompt_id: str, min_samples: int = 5) -> Optional[str]:
        best = self.select_best(prompt_id, min_samples=min_samples)
        if best:
            self.library.set_active(prompt_id, best)
        return best

    @staticmethod
    def _normalize_min_samples(value: int) -> int:
        try:
            n = int(value)
        except (TypeError, ValueError):
            return 5
        return max(1, n)
