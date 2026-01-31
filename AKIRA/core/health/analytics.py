"""Health analytics and manager (ASCII only)."""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from .monitor import HealthMonitor, HealthMetrics
from .healer import AutoHealer, Problem, FixResult


class HealthAnalytics:
    def __init__(self, data_dir: str, max_samples: int = 1000, persist: bool = True) -> None:
        self.data_dir = data_dir
        self.max_samples = max_samples
        self.persist = persist
        self._samples: List[HealthMetrics] = []
        self._path = os.path.join(self.data_dir, "health_metrics.jsonl")
        os.makedirs(self.data_dir, exist_ok=True)

    def record(self, metrics: HealthMetrics) -> None:
        self._samples.append(metrics)
        if len(self._samples) > self.max_samples:
            self._samples = self._samples[-self.max_samples :]
        if not self.persist:
            return
        payload = asdict(metrics)
        payload["timestamp"] = metrics.timestamp.isoformat()
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=True) + "\n")

    def summary(self) -> Dict[str, Any]:
        if not self._samples:
            return {
                "avg_cpu": 0.0,
                "avg_mem": 0.0,
                "avg_disk": 0.0,
                "error_rate": 0.0,
                "last_status": "unknown",
                "warnings": [],
            }
        avg_cpu = sum(s.cpu_percent for s in self._samples) / max(len(self._samples), 1)
        avg_mem = sum(s.memory_percent for s in self._samples) / max(len(self._samples), 1)
        avg_disk = sum(s.disk_percent for s in self._samples) / max(len(self._samples), 1)
        error_rate = sum(1 for s in self._samples if s.error_count > 0) / max(len(self._samples), 1)
        last_status = self._samples[-1].status
        warnings = self._samples[-1].warnings if self._samples else []
        return {
            "avg_cpu": round(avg_cpu, 2),
            "avg_mem": round(avg_mem, 2),
            "avg_disk": round(avg_disk, 2),
            "error_rate": round(error_rate, 3),
            "last_status": last_status,
            "warnings": warnings,
        }


class HealthManager:
    def __init__(
        self,
        data_dir: str,
        monitor: Optional[HealthMonitor] = None,
        healer: Optional[AutoHealer] = None,
        analytics: Optional[HealthAnalytics] = None,
    ) -> None:
        self.monitor = monitor or HealthMonitor()
        self.healer = healer or AutoHealer(self.monitor)
        self.analytics = analytics or HealthAnalytics(data_dir)

    def check(self, auto_heal: bool = False) -> Dict[str, Any]:
        metrics = self.monitor.get_metrics()
        self.analytics.record(metrics)
        summary = self.analytics.summary()
        report: Dict[str, Any] = {
            "metrics": {
                "timestamp": metrics.timestamp.isoformat(),
                "memory_percent": metrics.memory_percent,
                "cpu_percent": metrics.cpu_percent,
                "disk_percent": metrics.disk_percent,
                "error_count": metrics.error_count,
                "warnings": metrics.warnings,
                "status": metrics.status,
            },
            "summary": summary,
        }
        if auto_heal:
            problems = self.healer.detect_problems()
            fixes: List[Dict[str, Any]] = []
            for p in problems:
                result = self.healer.fix_problem(p)
                fixes.append(
                    {
                        "problem": p.type.value,
                        "severity": p.severity.name,
                        "description": p.description,
                        "success": result.success,
                        "action_taken": result.action_taken,
                    }
                )
            report["auto_heal"] = fixes
        return report
