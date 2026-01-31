"""Predictive planning (ASCII only)."""

from __future__ import annotations

from typing import Any, Dict, List

import math

from .world_model import WorldModel
from .simulator import SimulationEngine


class PredictivePlanner:
    def __init__(self, world_model: WorldModel, simulator: SimulationEngine):
        self.world_model = world_model
        self.simulator = simulator

    @staticmethod
    def _default_simulation(task: str) -> Dict[str, Any]:
        return {
            "task": task,
            "steps": [],
            "overall_score": 0.0,
        }

    @staticmethod
    def _normalize_user_id(user_id: Any, warnings: List[str]) -> str:
        if isinstance(user_id, str) and user_id.strip():
            return user_id.strip()
        warnings.append("Invalid user_id; using default.")
        return "default"

    @staticmethod
    def _normalize_steps(steps: Any, warnings: List[str]) -> List[str]:
        if steps is None:
            warnings.append("No steps provided; using empty list.")
            return []
        if not isinstance(steps, list):
            warnings.append("Invalid steps; expected list. Using empty list.")
            return []
        cleaned: List[str] = []
        for idx, step in enumerate(steps):
            if isinstance(step, str):
                text = step.strip()
                if text:
                    cleaned.append(text)
                else:
                    warnings.append(f"Skipped empty step at index {idx}.")
            elif step is None:
                warnings.append(f"Skipped null step at index {idx}.")
            else:
                warnings.append(f"Skipped non-string step at index {idx}.")
        return cleaned

    @staticmethod
    def _normalize_risk_threshold(value: Any, warnings: List[str]) -> float:
        default = 0.7
        if value is None:
            warnings.append("risk_threshold missing; using default 0.7.")
            return default
        try:
            val = float(value)
        except (TypeError, ValueError):
            warnings.append("Invalid risk_threshold; using default 0.7.")
            return default
        if not math.isfinite(val):
            warnings.append("Non-finite risk_threshold; using default 0.7.")
            return default
        if val < 0.0 or val > 1.0:
            warnings.append("risk_threshold out of range; using default 0.7.")
            return default
        return val

    def optimize_plan(
        self,
        task: str,
        steps: List[str],
        user_id: str,
        risk_threshold: float = 0.7,
    ) -> Dict[str, Any]:
        warnings: List[str] = []
        safe_user_id = self._normalize_user_id(user_id, warnings)
        safe_steps = self._normalize_steps(steps, warnings)
        safe_threshold = self._normalize_risk_threshold(risk_threshold, warnings)
        kept: List[str] = []
        removed: List[str] = []
        for step in safe_steps:
            risk = self.world_model.estimate_step_risk(step)
            if risk > safe_threshold:
                removed.append(step)
                warnings.append(f"Removed risky step (risk={risk:.2f}): {step}")
            else:
                kept.append(step)
        try:
            sim = self.simulator.simulate_plan(task, kept, user_id=safe_user_id)
        except Exception as exc:
            warnings.append(f"Simulation failed: {exc}")
            sim = self._default_simulation(task)
        return {
            "steps": kept,
            "removed": removed,
            "warnings": warnings,
            "score": sim.get("overall_score", 0.0),
            "simulation": sim,
        }
