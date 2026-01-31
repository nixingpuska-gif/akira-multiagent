"""Parallel reasoning (ASCII only)."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import List, Optional

from ..llm_router import LLMRouter


@dataclass
class ReasoningVariant:
    name: str
    system_prompt: str


@dataclass
class ReasoningResult:
    name: str
    response: str
    latency_ms: int
    error: Optional[str] = None

    def is_ok(self) -> bool:
        return bool((self.response or "").strip()) and not self.error

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "response": self.response,
            "latency_ms": self.latency_ms,
            "error": self.error,
            "ok": self.is_ok(),
        }


class ParallelReasoner:
    def __init__(self, router: LLMRouter, max_workers: int = 3, timeout_s: float = 60.0):
        self.router = router
        self.max_workers = max_workers
        self.timeout_s = timeout_s
        self._sem = asyncio.Semaphore(max_workers)

    async def run(self, task: str, variants: List[ReasoningVariant]) -> List[ReasoningResult]:
        if not variants:
            return []

        async def _run_variant(variant: ReasoningVariant) -> ReasoningResult:
            async with self._sem:
                start = time.monotonic()
                try:
                    messages = [
                        {"role": "system", "content": variant.system_prompt},
                        {"role": "user", "content": task},
                    ]
                    resp = await asyncio.wait_for(self.router.chat(messages), timeout=self.timeout_s)
                    latency = int((time.monotonic() - start) * 1000)
                    text = "" if resp is None else str(resp)
                    if not text.strip():
                        return ReasoningResult(variant.name, text, latency, error="empty_response")
                    return ReasoningResult(variant.name, text, latency)
                except asyncio.TimeoutError:
                    latency = int((time.monotonic() - start) * 1000)
                    return ReasoningResult(variant.name, "", latency, error="timeout")
                except Exception as exc:
                    latency = int((time.monotonic() - start) * 1000)
                    msg = str(exc) or exc.__class__.__name__
                    return ReasoningResult(variant.name, "", latency, error=msg)

        tasks = [_run_variant(v) for v in variants]
        return await asyncio.gather(*tasks)
