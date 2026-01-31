"""Reflector agent - analyzes errors and improves system."""

from __future__ import annotations

from typing import TYPE_CHECKING
from .base import BaseAgent, AgentContext, AgentResult

if TYPE_CHECKING:
    from ..llm_router import LLMRouter
    from ..memory import MemoryStore


class ReflectorAgent(BaseAgent):
    """Agent that analyzes failures and suggests improvements."""

    def __init__(self, llm: "LLMRouter", memory: "MemoryStore" = None):
        super().__init__("reflector", llm, max_iterations=5)
        self.memory = memory

    def get_system_prompt(self, context: AgentContext) -> str:
        return f"""You are the Reflector agent. Analyze errors and suggest fixes.

{context.to_prompt()}

Respond with JSON:
{{"analysis": "what went wrong", "suggestion": "how to fix", "learned": "lesson for future"}}
"""

    async def run(self, task: str, context: AgentContext) -> AgentResult:
        messages = [
            {"role": "system", "content": self.get_system_prompt(context)},
            {"role": "user", "content": f"Analyze this situation: {task}"}
        ]

        response = await self.call_llm(messages, expect_json=True)
        parsed = self.extract_json(response)

        # Store learned lesson in memory
        if parsed and self.memory and "learned" in parsed:
            try:
                self.memory.add_turn(
                    context.user_id,
                    f"Error analysis: {task}",
                    f"Learned: {parsed['learned']}"
                )
            except Exception:
                pass

        if parsed:
            return AgentResult(
                success=True,
                output=parsed,
                thinking=parsed.get("analysis")
            )

        return AgentResult(success=True, output=response)
