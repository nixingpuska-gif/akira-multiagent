"""Cross-project indexing (ASCII only)."""

from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

from .indexer import ProjectIndexer, ProjectMetadata
from .store import EnhancedMemoryStore, Project


@dataclass
class CrossProjectResult:
    indexed: List[str]
    skipped: List[str]
    warnings: List[str]


class CrossProjectIndex:
    def __init__(
        self,
        store: EnhancedMemoryStore,
        data_dir: str,
        indexer: Optional[ProjectIndexer] = None,
        max_depth: int = 2,
        max_projects: int = 100,
        ignore_dirs: Optional[Iterable[str]] = None,
    ) -> None:
        self.store = store
        self.data_dir = data_dir
        self.indexer = indexer or ProjectIndexer()
        self.max_depth = max(0, int(max_depth))
        self.max_projects = max(1, int(max_projects))
        self.ignore_dirs = set(ignore_dirs or ProjectIndexer.IGNORE_DIRS)
        self.cache_path = os.path.join(self.data_dir, "cross_project_cache.json")
        os.makedirs(self.data_dir, exist_ok=True)
        self._lock = threading.Lock()

    def index_roots(self, roots: List[str], user_id: str = "default") -> CrossProjectResult:
        warnings: List[str] = []
        indexed: List[str] = []
        skipped: List[str] = []
        projects = self._scan_roots(roots, warnings)
        cache = self._load_cache()
        for path in projects:
            try:
                meta = self.indexer.index_project(path)
            except Exception as exc:
                warnings.append(f"Index failed for {path}: {exc}")
                continue
            existing = self.store.get_project(meta.path)
            if existing and getattr(existing, "fingerprint", "") == meta.fingerprint:
                skipped.append(meta.path)
                self._update_cache(cache, meta)
                continue
            project = self._meta_to_project(meta, user_id=user_id)
            self.store.save_project(project)
            indexed.append(meta.path)
            self._update_cache(cache, meta)
            if len(indexed) >= self.max_projects:
                warnings.append("Max projects limit reached; stopping.")
                break
        self._save_cache(cache)
        return CrossProjectResult(indexed=indexed, skipped=skipped, warnings=warnings)

    def search(self, query: str, user_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        seen: Set[str] = set()
        for proj in self.store.search_projects(query, user_id=user_id, limit=limit):
            item = {
                "path": proj.path,
                "name": proj.name,
                "tech_stack": self._safe_json_list(proj.tech_stack),
                "dependencies": self._safe_json_dict(proj.dependencies),
                "indexed_at": proj.indexed_at,
                "fingerprint": proj.fingerprint,
            }
            results.append(item)
            seen.add(proj.path)
        if len(results) >= limit:
            return results[:limit]
        cache = self._load_cache()
        projects = cache.get("projects", {})
        q = (query or "").lower()
        for path, entry in projects.items():
            if len(results) >= limit:
                break
            if path in seen:
                continue
            name = str(entry.get("name", ""))
            tech = " ".join(entry.get("tech_stack", []))
            if q in path.lower() or q in name.lower() or q in tech.lower():
                results.append(
                    {
                        "path": path,
                        "name": name,
                        "tech_stack": entry.get("tech_stack", []),
                        "dependencies": entry.get("dependencies", {}),
                        "indexed_at": entry.get("indexed_at", ""),
                        "fingerprint": entry.get("fingerprint", ""),
                    }
                )
        return results[:limit]

    def _scan_roots(self, roots: List[str], warnings: List[str]) -> List[str]:
        projects: List[str] = []
        seen: Set[str] = set()
        for root in roots:
            if not root:
                warnings.append("Empty root path skipped.")
                continue
            path = Path(root)
            if not path.exists() or not path.is_dir():
                warnings.append(f"Missing root: {root}")
                continue
            for proj in self._scan_dir(path, depth=0, base_root=path):
                if proj not in seen:
                    projects.append(proj)
                    seen.add(proj)
                if len(projects) >= self.max_projects:
                    warnings.append("Max projects limit reached; stopping scan.")
                    return projects
        return projects

    def _scan_dir(self, root: Path, depth: int, base_root: Path) -> Iterable[str]:
        if root.name in self.ignore_dirs:
            return []
        if root.is_symlink():
            return []
        if not self._is_within_root(root, base_root):
            return []
        if self._is_project_dir(root):
            return [str(root)]
        if depth >= self.max_depth:
            return []
        found: List[str] = []
        try:
            for item in root.iterdir():
                if item.is_dir() and item.name not in self.ignore_dirs and not item.is_symlink():
                    if self._is_within_root(item, base_root):
                        found.extend(self._scan_dir(item, depth + 1, base_root))
        except Exception:
            return []
        return found

    @staticmethod
    def _is_within_root(path: Path, base_root: Path) -> bool:
        try:
            base = base_root.resolve()
        except Exception:
            base = Path(os.path.abspath(str(base_root)))
        try:
            candidate = path.resolve()
        except Exception:
            candidate = Path(os.path.abspath(str(path)))
        try:
            return os.path.commonpath([str(candidate), str(base)]) == str(base)
        except Exception:
            return False

    def _is_project_dir(self, path: Path) -> bool:
        for marker in ProjectIndexer.TECH_MARKERS.keys():
            if (path / marker).exists():
                return True
        common_entries = ["main.py", "app.py", "index.js", "index.ts", "main.go"]
        for name in common_entries:
            if (path / name).exists():
                return True
        return False

    def _load_cache(self) -> Dict[str, Any]:
        if not os.path.exists(self.cache_path):
            return {"projects": {}, "updated_at": ""}
        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("projects", {}), dict):
                return data
        except Exception:
            pass
        return {"projects": {}, "updated_at": ""}

    def _save_cache(self, cache: Dict[str, Any]) -> None:
        cache["updated_at"] = datetime.utcnow().isoformat()
        tmp = self.cache_path + ".tmp"
        with self._lock:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=True, indent=2, sort_keys=True)
            os.replace(tmp, self.cache_path)

    def _update_cache(self, cache: Dict[str, Any], meta: ProjectMetadata) -> None:
        projects = cache.setdefault("projects", {})
        projects[meta.path] = {
            "name": meta.name,
            "tech_stack": list(meta.tech_stack),
            "languages": dict(meta.languages),
            "dependencies": dict(meta.dependencies),
            "indexed_at": meta.indexed_at,
            "fingerprint": meta.fingerprint,
        }

    @staticmethod
    def _meta_to_project(meta: ProjectMetadata, user_id: str) -> Project:
        return Project(
            user_id=user_id,
            path=meta.path,
            name=meta.name,
            tech_stack=json.dumps(meta.tech_stack, ensure_ascii=True),
            structure=json.dumps(meta.structure, ensure_ascii=True),
            entry_points=json.dumps(meta.entry_points, ensure_ascii=True),
            dependencies=json.dumps(meta.dependencies, ensure_ascii=True),
            indexed_at=meta.indexed_at,
            fingerprint=meta.fingerprint,
            file_count=meta.file_count,
            total_lines=meta.total_lines,
        )

    @staticmethod
    def _safe_json_list(text: str) -> List[str]:
        try:
            data = json.loads(text)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    @staticmethod
    def _safe_json_dict(text: str) -> Dict[str, Any]:
        try:
            data = json.loads(text)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
