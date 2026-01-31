"""Health monitor for AKIRA (ASCII only)."""

import psutil
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class HealthMetrics:
    """Health metrics snapshot."""
    timestamp: datetime = field(default_factory=datetime.now)
    memory_percent: float = 0.0
    cpu_percent: float = 0.0
    disk_percent: float = 0.0
    error_count: int = 0
    warnings: List[str] = field(default_factory=list)
    status: str = "healthy"


class HealthMonitor:
    """Health monitor."""

    # Thresholds
    MEMORY_WARNING_THRESHOLD = 80.0
    MEMORY_CRITICAL_THRESHOLD = 95.0
    CPU_WARNING_THRESHOLD = 80.0
    CPU_CRITICAL_THRESHOLD = 95.0

    def __init__(self):
        self.logger = logging.getLogger("AKIRA.HealthMonitor")
        self._errors: List[Dict[str, Any]] = []
        self._metrics_history: List[HealthMetrics] = []
        self._max_history = 1000

    def check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage."""
        try:
            memory = psutil.virtual_memory()

            result = {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent,
                "status": "healthy"
            }

            if memory.percent >= self.MEMORY_CRITICAL_THRESHOLD:
                result["status"] = "critical"
                self.logger.error(f"Critical memory usage: {memory.percent}%")
            elif memory.percent >= self.MEMORY_WARNING_THRESHOLD:
                result["status"] = "warning"
                self.logger.warning(f"High memory usage: {memory.percent}%")

            return result

        except Exception as e:
            self._log_error("memory_check", str(e))
            return {"status": "error", "error": str(e)}

    def check_cpu_usage(self, interval: float = 1.0) -> Dict[str, Any]:
        """Check CPU usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=interval)
            cpu_count = psutil.cpu_count()

            result = {
                "percent": cpu_percent,
                "cores": cpu_count,
                "per_cpu": psutil.cpu_percent(percpu=True),
                "status": "healthy"
            }

            if cpu_percent >= self.CPU_CRITICAL_THRESHOLD:
                result["status"] = "critical"
                self.logger.error(f"Critical CPU usage: {cpu_percent}%")
            elif cpu_percent >= self.CPU_WARNING_THRESHOLD:
                result["status"] = "warning"
                self.logger.warning(f"High CPU usage: {cpu_percent}%")

            return result

        except Exception as e:
            self._log_error("cpu_check", str(e))
            return {"status": "error", "error": str(e)}

    def check_disk_usage(self, path: str = "/") -> Dict[str, Any]:
        """Check disk usage."""
        try:
            disk = psutil.disk_usage(path)

            return {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent,
                "status": "healthy" if disk.percent < 90 else "warning"
            }

        except Exception as e:
            self._log_error("disk_check", str(e))
            return {"status": "error", "error": str(e)}

    def check_errors(self) -> Dict[str, Any]:
        """Check recent errors."""
        recent_errors = [
            e for e in self._errors
            if (datetime.now() - e["timestamp"]).seconds < 3600
        ]

        return {
            "total_errors": len(self._errors),
            "recent_errors": len(recent_errors),
            "errors": recent_errors[-10:],  # last 10 errors
            "status": "healthy" if len(recent_errors) < 5 else "warning"
        }

    def get_metrics(self) -> HealthMetrics:
        """Get current health metrics."""
        memory = self.check_memory_usage()
        cpu = self.check_cpu_usage(interval=0.1)
        errors = self.check_errors()

        warnings = []
        status = "healthy"

        # Status aggregation
        statuses = [memory["status"], cpu["status"], errors["status"]]

        if "critical" in statuses:
            status = "critical"
        elif "warning" in statuses:
            status = "warning"

        # Warning list
        if memory["status"] != "healthy":
            warnings.append(f"Memory: {memory.get('percent', 'N/A')}%")
        if cpu["status"] != "healthy":
            warnings.append(f"CPU: {cpu.get('percent', 'N/A')}%")
        if errors["status"] != "healthy":
            warnings.append(f"Errors: {errors['recent_errors']}")

        disk = self.check_disk_usage()
        metrics = HealthMetrics(
            memory_percent=memory.get("percent", 0),
            cpu_percent=cpu.get("percent", 0),
            disk_percent=disk.get("percent", 0),
            error_count=errors["total_errors"],
            warnings=warnings,
            status=status
        )

        self._store_metrics(metrics)
        return metrics

    def _log_error(self, source: str, message: str):
        """Log an internal error."""
        error = {
            "timestamp": datetime.now(),
            "source": source,
            "message": message
        }
        self._errors.append(error)
        self.logger.error(f"[{source}] {message}")

    def _store_metrics(self, metrics: HealthMetrics):
        """Store metrics in memory."""
        self._metrics_history.append(metrics)

        # Trim history
        if len(self._metrics_history) > self._max_history:
            self._metrics_history = self._metrics_history[-self._max_history:]

    def get_history(self, limit: int = 100) -> List[HealthMetrics]:
        """Return recent metrics history."""
        return self._metrics_history[-limit:]
