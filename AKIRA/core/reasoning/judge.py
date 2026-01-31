"""Meta judge for parallel reasoning (ASCII only)."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import List, Optional

from ..llm_router import LLMRouter
from .parallel import ReasoningResult


class MetaJudge:
    def __init__(self, mode: str = "heuristic", router: Optional[LLMRouter] = None):
        self.mode = mode
        self.router = router

    async def select_best(self, task: str, results: List[ReasoningResult]) -> str:
        if not results:
            return ""
        if self.mode == "llm" and self.router:
            prompt = self._build_judge_prompt(task, results)
            messages = [{"role": "system", "content": prompt}]
            try:
                raw = await self.router.chat(messages)
                obj = json.loads(raw) if raw.strip().startswith("{") else {}
                best = obj.get("best")
                if best in [r.name for r in results]:
                    chosen = next((r for r in results if r.name == best), None)
                    if chosen and chosen.is_ok():
                        return best
            except Exception:
                pass
        return self._heuristic_pick(results)

    def synthesize(self, task: str, results: List[ReasoningResult], best: str) -> str:
        chosen = next((r for r in results if r.name == best), None)
        if not chosen or not chosen.is_ok():
            return "No valid response selected."
        text = (chosen.response or "").strip()
        if len(text) > 400:
            text = text[:400] + "..."
        return text

    def _heuristic_pick(self, results: List[ReasoningResult]) -> str:
        best_score = -1
        best_name = results[0].name if results else ""
        for r in results:
            score = 0
            text = (r.response or "").strip()
            if not text:
                score -= 2
            if len(text) >= 50:
                score += 1
            if "\n" in text or "-" in text or "1." in text:
                score += 1
            if "risk" in text.lower() or "warning" in text.lower():
                score += 1
            if r.error:
                score -= 3
            if score > best_score or (score == best_score and r.name < best_name):
                best_score = score
                best_name = r.name
        return best_name

    @staticmethod
    def _build_judge_prompt(task: str, results: List[ReasoningResult]) -> str:
        data = [asdict(r) for r in results]
        return (
            "You are a judge. Pick the best answer id.\n"
            "Return JSON only: {\"best\": \"<name>\"}\n"
            f"Task: {task}\n"
            f"Candidates: {json.dumps(data)}"
        )
