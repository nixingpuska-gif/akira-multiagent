"""Cross-project pattern extraction (ASCII only)."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List


class PatternExtractor:
    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir
        self.cache_path = os.path.join(self.data_dir, "cross_project_cache.json")

    def extract(self, limit: int = 5, cache: Dict[str, Any] | None = None) -> Dict[str, Any]:
        cache_data = cache if isinstance(cache, dict) else self._load_cache()
        projects = cache_data.get("projects", {}) if isinstance(cache_data, dict) else {}
        lang_counts: Dict[str, int] = {}
        tech_counts: Dict[str, int] = {}
        dep_counts: Dict[str, int] = {}
        for entry in projects.values():
            for lang, count in (entry.get("languages", {}) or {}).items():
                if isinstance(count, int):
                    lang_counts[lang] = lang_counts.get(lang, 0) + count
            for tech in entry.get("tech_stack", []) or []:
                tech_counts[tech] = tech_counts.get(tech, 0) + 1
            for dep in (entry.get("dependencies", {}) or {}).keys():
                dep_counts[dep] = dep_counts.get(dep, 0) + 1
        return {
            "top_languages": self._top_items(lang_counts, limit),
            "top_tech_stack": self._top_items(tech_counts, limit),
            "top_dependencies": self._top_items(dep_counts, limit),
            "project_count": len(projects),
        }

    def _load_cache(self) -> Dict[str, Any]:
        if not os.path.exists(self.cache_path):
            return {"projects": {}, "updated_at": ""}
        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {"projects": {}, "updated_at": ""}
        except Exception:
            return {"projects": {}, "updated_at": ""}

    @staticmethod
    def _top_items(counts: Dict[str, int], limit: int) -> List[Dict[str, Any]]:
        items = [{"name": k, "count": v} for k, v in counts.items() if isinstance(k, str)]
        items.sort(key=lambda x: (-int(x["count"]), x["name"]))
        return items[: max(0, int(limit))]
