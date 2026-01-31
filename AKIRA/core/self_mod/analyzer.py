"""Self-modification analyzer (ASCII only)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class AnalysisResult:
    target_path: str
    issue: str
    files: List[str]
    risk_level: str
    suggested_actions: List[str]
    warnings: List[str]
    analyzed_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_path": self.target_path,
            "issue": self.issue,
            "files": list(self.files),
            "risk_level": self.risk_level,
            "suggested_actions": list(self.suggested_actions),
            "warnings": list(self.warnings),
            "analyzed_at": self.analyzed_at,
        }


class SelfModAnalyzer:
    def __init__(self, max_files: int = 50, max_depth: int = 3) -> None:
        self.max_files = max(1, int(max_files))
        self.max_depth = max(0, int(max_depth))

    def analyze(self, target_path: str, issue: str) -> AnalysisResult:
        warnings: List[str] = []
        files: List[str] = []
        path = os.path.abspath(target_path or "")
        if not path or not os.path.exists(path):
            warnings.append("Target path does not exist.")
        else:
            if os.path.isfile(path):
                files.append(path)
            elif os.path.isdir(path):
                files.extend(self._scan_dir(path, warnings))
            else:
                warnings.append("Target path is not a file or directory.")

        risk = self._assess_risk(issue)
        actions = self._suggest_actions(path, issue, files)
        return AnalysisResult(
            target_path=path,
            issue=str(issue or ""),
            files=files,
            risk_level=risk,
            suggested_actions=actions,
            warnings=warnings,
            analyzed_at=datetime.utcnow().isoformat(),
        )

    def _scan_dir(self, root: str, warnings: List[str]) -> List[str]:
        collected: List[str] = []
        base_depth = root.rstrip(os.sep).count(os.sep)
        for dirpath, dirnames, filenames in os.walk(root):
            depth = dirpath.count(os.sep) - base_depth
            if depth > self.max_depth:
                dirnames[:] = []
                continue
            for name in filenames:
                collected.append(os.path.join(dirpath, name))
                if len(collected) >= self.max_files:
                    warnings.append("File scan limit reached; results truncated.")
                    return collected
        return collected

    @staticmethod
    def _assess_risk(issue: str) -> str:
        text = (issue or "").lower()
        high = ["delete", "rm", "format", "wipe", "erase", "shutdown", "kill", "registry"]
        medium = ["refactor", "migration", "upgrade", "rename", "remove"]
        if any(k in text for k in high):
            return "high"
        if any(k in text for k in medium):
            return "medium"
        return "low"

    @staticmethod
    def _suggest_actions(path: str, issue: str, files: List[str]) -> List[str]:
        actions = [
            "Review scope and affected files.",
            "Create patch in isolated diff file.",
            "Request user approval before apply.",
        ]
        if files:
            actions.append(f"Inspect {min(len(files), 5)} target files before changes.")
        if not path:
            actions.append("Provide a valid target path.")
        if not issue:
            actions.append("Clarify the issue description.")
        return actions
