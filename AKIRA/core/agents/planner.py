"""Planner agent - breaks down complex tasks into steps."""

from __future__ import annotations

from typing import TYPE_CHECKING
from .base import BaseAgent, AgentContext, AgentResult

if TYPE_CHECKING:
    from ..llm_router import LLMRouter


class PlannerAgent(BaseAgent):
    """Agent that creates execution plans for complex tasks."""

    def __init__(self, llm: "LLMRouter"):
        super().__init__("planner", llm, max_iterations=5)

    def get_system_prompt(self, context: AgentContext) -> str:
        return f"""You are the Planner agent. Break down tasks into clear steps.

{context.to_prompt()}

Respond with JSON:
{{"steps": ["step 1", "step 2", ...], "reasoning": "why this approach"}}
"""

    async def run(self, task: str, context: AgentContext) -> AgentResult:
        messages = [
            {"role": "system", "content": self.get_system_prompt(context)},
            {"role": "user", "content": f"Create a plan for: {task}"}
        ]

        response = await self.call_llm(messages, expect_json=True)
        parsed = self.extract_json(response)

        if parsed and "steps" in parsed:
            return AgentResult(
                success=True,
                output=parsed,
                thinking=parsed.get("reasoning")
            )

        return AgentResult(success=True, output=response)
