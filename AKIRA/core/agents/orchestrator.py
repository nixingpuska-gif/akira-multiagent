"""Orchestrator agent - main coordinator for AKIRA 2.0."""

from __future__ import annotations

import asyncio
from typing import Dict, List, Optional, TYPE_CHECKING

from .base import BaseAgent, AgentContext, AgentResult

if TYPE_CHECKING:
    from ..llm_router import LLMRouter
    from ..tools.registry import ToolRegistry
    from ..memory import MemoryStore


ORCHESTRATOR_PROMPT = """You are AKIRA 2.0 Orchestrator, the main coordinator of an autonomous AI system.

## YOUR ROLE
You coordinate specialized agents to complete complex tasks:
- PLANNER: Breaks down complex tasks into steps
- EXECUTOR: Executes individual actions using tools
- REFLECTOR: Analyzes results and learns from mistakes

## RESPONSE FORMAT
Always respond with valid JSON:

To execute a tool directly:
{"action": "tool", "tool": "<name>", "args": {...}, "thinking": "why"}

To delegate to a subagent:
{"action": "delegate", "agent": "planner|executor|reflector|coder|browser|searcher", "task": "description"}

To give final answer:
{"action": "final", "content": "response to user"}

## RULES
1. For complex tasks (3+ steps): delegate to PLANNER first
2. For simple tool calls: execute directly
3. After errors: delegate to REFLECTOR
4. Always verify results before final answer
5. Use correct OS paths (check SYSTEM CONTEXT)
"""


class OrchestratorAgent(BaseAgent):
    """Main orchestrator that coordinates all other agents."""

    def __init__(
        self,
        llm: "LLMRouter",
        tools: "ToolRegistry",
        memory: "MemoryStore",
        max_iterations: int = 20,
    ):
        super().__init__("orchestrator", llm, tools, max_iterations)
        self.memory = memory
        self._subagents: Dict[str, BaseAgent] = {}

    def register_subagent(self, name: str, agent: BaseAgent):
        """Register a subagent."""
        self._subagents[name] = agent

    def get_system_prompt(self, context: AgentContext) -> str:
        """Generate system prompt with context."""
        subagent_list = ", ".join(self._subagents.keys()) if self._subagents else "none"
        return f"{ORCHESTRATOR_PROMPT}\n\n{context.to_prompt()}\n\nRegistered subagents: {subagent_list}"

    async def run(self, task: str, context: AgentContext) -> AgentResult:
        """Execute orchestrator loop."""
        messages = [
            {"role": "system", "content": self.get_system_prompt(context)},
            {"role": "user", "content": task}
        ]

        tool_calls = []
        iterations = 0

        for iteration in range(self.max_iterations):
            iterations = iteration + 1

            # Get LLM response
            response = await self.call_llm(messages, expect_json=True)
            parsed = self.extract_json(response)

            if not parsed:
                # Non-JSON response, treat as final
                return AgentResult(
                    success=True,
                    output=response,
                    iterations=iterations,
                    tool_calls=tool_calls
                )

            action = parsed.get("action", "")

            # Final answer
            if action == "final":
                return AgentResult(
                    success=True,
                    output=parsed.get("content", ""),
                    iterations=iterations,
                    tool_calls=tool_calls,
                    thinking=parsed.get("thinking")
                )

            # Tool execution
            if action == "tool":
                tool_name = parsed.get("tool", "")
                args = parsed.get("args", {})
                result = await self.execute_tool(tool_name, args)

                tool_calls.append({
                    "tool": tool_name,
                    "args": args,
                    "result": result[:500] if len(str(result)) > 500 else result
                })

                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "user", "content": f"Tool result: {result}"})
                continue

            # Delegate to subagent
            if action == "delegate":
                agent_name = parsed.get("agent", "")
                subtask = parsed.get("task", "")

                if agent_name in self._subagents:
                    subagent = self._subagents[agent_name]
                    sub_result = await subagent.run(subtask, context)
                    observation = f"Subagent '{agent_name}' result: {sub_result.output}"
                else:
                    observation = f"Unknown subagent: {agent_name}. Available: {list(self._subagents.keys())}"

                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "user", "content": observation})
                continue

            # Unknown action
            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "user", "content": f"Unknown action: {action}. Use tool, delegate, or final."})

        return AgentResult(
            success=False,
            output="Max iterations reached",
            error="Could not complete task within iteration limit",
            iterations=iterations,
            tool_calls=tool_calls
        )
