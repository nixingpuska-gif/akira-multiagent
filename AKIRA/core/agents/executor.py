"""Executor agent - executes tools with parallel support."""

from __future__ import annotations

import asyncio
from typing import Dict, List, Any, TYPE_CHECKING

from .base import BaseAgent, AgentContext, AgentResult

if TYPE_CHECKING:
    from ..llm_router import LLMRouter
    from ..tools.registry import ToolRegistry


class ExecutorAgent(BaseAgent):
    """Agent that executes tools, supports parallel execution."""

    def __init__(self, llm: "LLMRouter", tools: "ToolRegistry"):
        super().__init__("executor", llm, tools, max_iterations=10)

    def get_system_prompt(self, context: AgentContext) -> str:
        return f"""You are the Executor agent. Execute tools precisely.

{context.to_prompt()}

Respond with JSON:
{{"action": "tool", "tool": "<name>", "args": {{...}}}}
or
{{"action": "done", "result": "summary"}}
"""

    async def run(self, task: str, context: AgentContext) -> AgentResult:
        """Execute a single task."""
        # If task is a dict with tool info, execute directly
        if isinstance(task, dict):
            tool = task.get("tool", "")
            args = task.get("args", {})
            result = await self.execute_tool(tool, args)
            return AgentResult(success=True, output=result)

        # Otherwise use LLM to determine action
        messages = [
            {"role": "system", "content": self.get_system_prompt(context)},
            {"role": "user", "content": task}
        ]

        response = await self.call_llm(messages, expect_json=True)
        parsed = self.extract_json(response)

        if not parsed:
            return AgentResult(success=False, output=response, error="Invalid JSON")

        if parsed.get("action") == "tool":
            result = await self.execute_tool(
                parsed.get("tool", ""),
                parsed.get("args", {})
            )
            return AgentResult(success=True, output=result)

        return AgentResult(success=True, output=parsed.get("result", response))

    async def run_parallel(
        self,
        tasks: List[Dict[str, Any]],
        context: AgentContext,
        max_concurrent: int = 3
    ) -> List[AgentResult]:
        """Execute multiple tasks in parallel."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run_with_limit(task: Dict) -> AgentResult:
            async with semaphore:
                return await self.run(task, context)

        results = await asyncio.gather(
            *[run_with_limit(t) for t in tasks],
            return_exceptions=True
        )

        return [
            r if isinstance(r, AgentResult)
            else AgentResult(success=False, output=None, error=str(r))
            for r in results
        ]
