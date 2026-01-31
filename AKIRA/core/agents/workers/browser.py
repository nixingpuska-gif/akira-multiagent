"""Browser worker - web automation with Playwright."""

from __future__ import annotations

from typing import TYPE_CHECKING
from ..base import BaseAgent, AgentContext, AgentResult

if TYPE_CHECKING:
    from ...llm_router import LLMRouter
    from ...tools.registry import ToolRegistry


class BrowserWorker(BaseAgent):
    """Worker for web automation tasks."""

    def __init__(self, llm: "LLMRouter", tools: "ToolRegistry"):
        super().__init__("browser", llm, tools, max_iterations=10)

    def get_system_prompt(self, context: AgentContext) -> str:
        return f"""You are the Browser worker. Automate web tasks.

{context.to_prompt()}

Available browser tools:
- browser_goto {{url}}
- browser_click {{selector}}
- browser_type {{selector, text}}
- browser_content {{}}

Respond with JSON:
{{"action": "browse", "tool": "<name>", "args": {{...}}}}
or
{{"action": "done", "result": "summary"}}
"""

    async def run(self, task: str, context: AgentContext) -> AgentResult:
        messages = [
            {"role": "system", "content": self.get_system_prompt(context)},
            {"role": "user", "content": task}
        ]

        results = []
        for _ in range(self.max_iterations):
            response = await self.call_llm(messages, expect_json=True)
            parsed = self.extract_json(response)

            if not parsed or parsed.get("action") == "done":
                return AgentResult(
                    success=True,
                    output=parsed.get("result", response) if parsed else response,
                    tool_calls=results
                )

            if parsed.get("action") == "browse":
                tool = parsed.get("tool", "")
                args = parsed.get("args", {})
                result = await self.execute_tool(tool, args)
                results.append({"tool": tool, "result": result[:200]})

                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "user", "content": f"Result: {result}"})

        return AgentResult(success=True, output="Max iterations", tool_calls=results)
