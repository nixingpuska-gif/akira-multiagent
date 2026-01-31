"""Deliberation pipeline (ASCII only)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class DeliberationPipeline:
    def __init__(self, router, max_len: int = 800) -> None:
        self.router = router
        self.max_len = max(100, int(max_len))

    async def run(self, task: str) -> Dict[str, Any]:
        prompts = [
            (
                "Analyze threats and obstacles briefly. "
                "Return 3-5 bullet points only. No chain-of-thought."
            ),
            (
                "Provide an 8-10 step plan as numbered list. "
                "Be concise. No chain-of-thought."
            ),
            (
                "Execute step 1 only and verify quickly. "
                "Return a short result sentence. No chain-of-thought."
            ),
        ]
        outputs: List[str] = []
        for idx, prompt in enumerate(prompts):
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": task},
            ]
            resp = await self.router.chat(messages)
            text = self._shorten(resp)
            if text.startswith("ERROR:"):
                return {"ok": False, "error": text, "calls": idx + 1}
            outputs.append(text)
        return {
            "ok": True,
            "error": "",
            "threats": outputs[0],
            "plan": outputs[1],
            "step1_result": outputs[2],
            "summary": self._format_summary(outputs),
            "calls": 3,
        }

    def _shorten(self, text: Any) -> str:
        cleaned = " ".join(str(text).split())
        cleaned = cleaned.encode("ascii", errors="ignore").decode("ascii")
        if len(cleaned) > self.max_len:
            return cleaned[: self.max_len] + "..."
        return cleaned

    @staticmethod
    def _format_summary(parts: List[str]) -> str:
        return (
            "Deliberation summary:\n"
            f"Threats: {parts[0]}\n"
            f"Plan: {parts[1]}\n"
            f"Step1: {parts[2]}"
        )
