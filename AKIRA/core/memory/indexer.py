"""
Project Indexer for AKIRA 2.0
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileInfo:
    """File metadata."""
    path: str
    name: str
    extension: str
    size: int
    lines: int
    language: str


@dataclass
class ProjectMetadata:
    """Project metadata summary."""
    path: str
    name: str
    tech_stack: List[str]
    languages: Dict[str, int]
    structure: Dict[str, List[str]]
    entry_points: List[str]
    dependencies: Dict[str, str]
    file_count: int
    total_lines: int
    indexed_at: str
    fingerprint: str


class ProjectIndexer:
    """Index and summarize project structure."""

    LANG_EXTENSIONS = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".cpp": "cpp",
        ".c": "c",
        ".cs": "csharp",
        ".rb": "ruby",
        ".php": "php",
        ".swift": "swift",
        ".kt": "kotlin",
        ".vue": "vue",
        ".svelte": "svelte",
    }

    IGNORE_DIRS = {
        ".git", ".svn", ".hg",
        "node_modules", "__pycache__", ".venv", "venv",
        "dist", "build", ".next", ".nuxt",
        ".idea", ".vscode", ".vs",
        "coverage", ".pytest_cache", ".mypy_cache",
    }

    TECH_MARKERS = {
        "package.json": "nodejs",
        "requirements.txt": "python",
        "pyproject.toml": "python",
        "Cargo.toml": "rust",
        "go.mod": "go",
        "pom.xml": "java",
        "build.gradle": "java",
        "Gemfile": "ruby",
        "composer.json": "php",
        "Dockerfile": "docker",
        "docker-compose.yml": "docker",
        ".env": "dotenv",
    }

    def __init__(self, max_file_size: int = 1_000_000):
        self.max_file_size = max_file_size

    def index_project(self, project_path: str) -> ProjectMetadata:
        path = Path(project_path)
        if not path.exists():
            raise ValueError(f"Path does not exist: {project_path}")

        files: List[FileInfo] = []
        languages: Dict[str, int] = {}
        structure: Dict[str, List[str]] = {}
        tech_stack: Set[str] = set()

        for file_path in self._walk_files(path):
            info = self._analyze_file(file_path)
            if info:
                files.append(info)
                languages[info.language] = languages.get(info.language, 0) + 1
                rel_dir = str(file_path.parent.relative_to(path))
                if rel_dir not in structure:
                    structure[rel_dir] = []
                structure[rel_dir].append(info.name)

        tech_stack = self._detect_tech_stack(path)
        entry_points = self._find_entry_points(path, files)
        dependencies = self._parse_dependencies(path)
        fingerprint = self._fingerprint_files(files)

        return ProjectMetadata(
            path=str(path),
            name=path.name,
            tech_stack=list(tech_stack),
            languages=languages,
            structure=structure,
            entry_points=entry_points,
            dependencies=dependencies,
            file_count=len(files),
            total_lines=sum(f.lines for f in files),
            indexed_at=datetime.utcnow().isoformat(),
            fingerprint=fingerprint,
        )

    def index_if_changed(self, project_path: str, store, user_id: str = "default"):
        meta = self.index_project(project_path)
        existing = store.get_project(meta.path)
        if existing and getattr(existing, "fingerprint", "") == meta.fingerprint:
            return None
        return store.index_project(meta.path, user_id=user_id)

    def _walk_files(self, root: Path):
        for item in root.iterdir():
            if item.name in self.IGNORE_DIRS:
                continue
            if item.is_dir():
                yield from self._walk_files(item)
            elif item.is_file():
                yield item

    def _analyze_file(self, file_path: Path) -> Optional[FileInfo]:
        try:
            stat = file_path.stat()
            if stat.st_size > self.max_file_size:
                return None
            ext = file_path.suffix.lower()
            lang = self.LANG_EXTENSIONS.get(ext, "other")
            lines = 0
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = sum(1 for _ in f)
            except Exception:
                pass
            return FileInfo(
                path=str(file_path),
                name=file_path.name,
                extension=ext,
                size=stat.st_size,
                lines=lines,
                language=lang,
            )
        except Exception:
            return None

    def _detect_tech_stack(self, path: Path) -> Set[str]:
        stack = set()
        for marker, tech in self.TECH_MARKERS.items():
            if (path / marker).exists():
                stack.add(tech)
        return stack

    def _find_entry_points(self, path: Path, files: List[FileInfo]) -> List[str]:
        entry_points = []
        common_entries = ["main.py", "app.py", "index.js", "index.ts", "main.go"]
        for f in files:
            if f.name in common_entries:
                entry_points.append(f.path)
        return entry_points

    def _parse_dependencies(self, path: Path) -> Dict[str, str]:
        deps: Dict[str, str] = {}
        req_file = path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "==" in line:
                                name, ver = line.split("==", 1)
                                deps[name] = ver
                            else:
                                deps[line.split("[")[0]] = "*"
            except Exception:
                pass

        pkg_file = path / "package.json"
        if pkg_file.exists():
            try:
                with open(pkg_file, "r", encoding="utf-8", errors="ignore") as f:
                    data = json.load(f)
                    deps.update(data.get("dependencies", {}))
            except Exception:
                pass
        return deps

    @staticmethod
    def _fingerprint_files(files: List[FileInfo]) -> str:
        parts = []
        for f in sorted(files, key=lambda x: x.path):
            try:
                stat = os.stat(f.path)
                parts.append(f"{f.path}|{stat.st_size}|{int(stat.st_mtime)}")
            except Exception:
                parts.append(f"{f.path}|{f.size}|0")
        raw = "\n".join(parts).encode("utf-8", errors="ignore")
        return hashlib.sha256(raw).hexdigest()

