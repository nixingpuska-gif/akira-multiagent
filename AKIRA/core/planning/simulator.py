"""Simulation engine (ASCII only)."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .world_model import WorldModel


class SimulationEngine:
    def __init__(self, world_model: WorldModel):
        self.world_model = world_model

    def simulate_plan(self, task: str, steps: List[str], user_id: str) -> Dict[str, Any]:
        step_results: List[Dict[str, Any]] = []
        base_success = self.world_model.estimate_task_success(task, user_id=user_id)
        total_score = 0.0
        for step in steps:
            risk = self.world_model.estimate_step_risk(step)
            success_est = max(0.0, min(1.0, base_success * (1.0 - risk)))
            step_results.append(
                {
                    "step": step,
                    "risk": round(risk, 3),
                    "success_est": round(success_est, 3),
                }
            )
            total_score += success_est
        overall = total_score / max(len(steps), 1)
        return {
            "task": task,
            "steps": step_results,
            "overall_score": round(overall, 3),
        }

    def rank_alternatives(self, task: str, plans: List[List[str]], user_id: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for steps in plans:
            sim = self.simulate_plan(task, steps, user_id=user_id)
            results.append(sim)
        results.sort(key=lambda r: r.get("overall_score", 0.0), reverse=True)
        return results
