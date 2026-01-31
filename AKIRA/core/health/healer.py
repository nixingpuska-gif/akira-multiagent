"""Auto healer for AKIRA (ASCII only)."""

import gc
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class ProblemType(Enum):
    """Problem types."""
    MEMORY_HIGH = "memory_high"
    CPU_HIGH = "cpu_high"
    ERROR_OVERFLOW = "error_overflow"
    DISK_FULL = "disk_full"
    CONNECTION_LOST = "connection_lost"
    UNKNOWN = "unknown"


class ProblemSeverity(Enum):
    """Problem severity."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Problem:
    """Problem details."""
    type: ProblemType
    severity: ProblemSeverity
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False


@dataclass
class FixResult:
    """Fix result."""
    success: bool
    problem: Problem
    action_taken: str
    rollback_available: bool = False
    rollback_data: Any = None


class AutoHealer:
    """Auto healer with safe fix handlers."""

    def __init__(self, monitor=None):
        self.logger = logging.getLogger("AKIRA.AutoHealer")
        self.monitor = monitor
        self._problems: List[Problem] = []
        self._fix_history: List[FixResult] = []
        self._rollback_stack: List[FixResult] = []
        self._fix_handlers: Dict[ProblemType, Callable] = {
            ProblemType.MEMORY_HIGH: self._fix_memory,
            ProblemType.CPU_HIGH: self._fix_cpu,
            ProblemType.ERROR_OVERFLOW: self._fix_errors,
        }

    def detect_problems(self) -> List[Problem]:
        """Detect problems based on latest metrics."""
        problems = []

        if self.monitor:
            metrics = self.monitor.get_metrics()

            # Memory
            if metrics.memory_percent > 90:
                problems.append(Problem(
                    type=ProblemType.MEMORY_HIGH,
                    severity=ProblemSeverity.CRITICAL,
                    description=f"Memory usage critical: {metrics.memory_percent}%",
                    context={"memory_percent": metrics.memory_percent}
                ))
            elif metrics.memory_percent > 80:
                problems.append(Problem(
                    type=ProblemType.MEMORY_HIGH,
                    severity=ProblemSeverity.HIGH,
                    description=f"Memory usage high: {metrics.memory_percent}%",
                    context={"memory_percent": metrics.memory_percent}
                ))

            # CPU
            if metrics.cpu_percent > 90:
                problems.append(Problem(
                    type=ProblemType.CPU_HIGH,
                    severity=ProblemSeverity.HIGH,
                    description=f"CPU usage high: {metrics.cpu_percent}%",
                    context={"cpu_percent": metrics.cpu_percent}
                ))

            # Errors
            if metrics.error_count > 100:
                problems.append(Problem(
                    type=ProblemType.ERROR_OVERFLOW,
                    severity=ProblemSeverity.MEDIUM,
                    description=f"Too many errors: {metrics.error_count}",
                    context={"error_count": metrics.error_count}
                ))

        self._problems.extend(problems)
        self.logger.info(f"Detected {len(problems)} problems")
        return problems

    def fix_problem(self, problem: Problem) -> FixResult:
        """Fix a single problem with a safe handler."""
        handler = self._fix_handlers.get(problem.type)

        if not handler:
            self.logger.warning(f"No handler for problem type: {problem.type}")
            return FixResult(
                success=False,
                problem=problem,
                action_taken="No handler available"
            )

        try:
            result = handler(problem)
            self._fix_history.append(result)

            if result.rollback_available:
                self._rollback_stack.append(result)

            if result.success:
                problem.resolved = True
                self.logger.info(f"Fixed problem: {problem.type.value}")

            return result

        except Exception as e:
            self.logger.error(f"Failed to fix problem: {e}")
            return FixResult(
                success=False,
                problem=problem,
                action_taken=f"Error: {str(e)}"
            )

    def rollback(self) -> bool:
        """Rollback the last fix if possible."""
        if not self._rollback_stack:
            self.logger.warning("No rollback available")
            return False

        last_fix = self._rollback_stack.pop()

        try:
            if last_fix.rollback_data:
                self.logger.info(f"Rolling back: {last_fix.action_taken}")
                last_fix.problem.resolved = False
                return True
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")

        return False

    def _fix_memory(self, problem: Problem) -> FixResult:
        """Attempt to reduce memory pressure safely."""
        gc.collect()
        return FixResult(
            success=True,
            problem=problem,
            action_taken="gc.collect",
            rollback_available=False,
        )

    def _fix_cpu(self, problem: Problem) -> FixResult:
        """Attempt to reduce CPU usage via short sleep."""
        time.sleep(0.2)
        return FixResult(
            success=True,
            problem=problem,
            action_taken="sleep_throttle",
            rollback_available=False,
        )

    def _fix_errors(self, problem: Problem) -> FixResult:
        """Clear error history to avoid overflow."""
        self._problems = []
        return FixResult(
            success=True,
            problem=problem,
            action_taken="clear_error_history",
            rollback_available=False,
        )
