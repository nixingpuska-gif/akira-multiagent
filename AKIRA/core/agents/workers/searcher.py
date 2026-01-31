"""Searcher worker - web and local search."""

from __future__ import annotations

from typing import TYPE_CHECKING
from ..base import BaseAgent, AgentContext, AgentResult

if TYPE_CHECKING:
    from ...llm_router import LLMRouter
    from ...tools.registry import ToolRegistry


class SearcherWorker(BaseAgent):
    """Worker for search tasks - web and local."""

    def __init__(self, llm: "LLMRouter", tools: "ToolRegistry"):
        super().__init__("searcher", llm, tools, max_iterations=5)

    def get_system_prompt(self, context: AgentContext) -> str:
        return f"""You are the Searcher worker. Find information.

{context.to_prompt()}

Search methods:
- browser_goto to search engines
- fs_list/fs_read for local files
- mcp_call for MCP tools

Respond with JSON:
{{"action": "search", "method": "web|local|memory", "query": "..."}}
or
{{"action": "result", "findings": ["..."], "sources": ["..."]}}
"""

    async def run(self, task: str, context: AgentContext) -> AgentResult:
        messages = [
            {"role": "system", "content": self.get_system_prompt(context)},
            {"role": "user", "content": f"Search for: {task}"}
        ]

        response = await self.call_llm(messages, expect_json=True)
        parsed = self.extract_json(response)

        if parsed and parsed.get("action") == "search":
            method = parsed.get("method", "web")
            query = parsed.get("query", task)

            if method == "web":
                result = await self.execute_tool(
                    "browser_goto",
                    {"url": f"https://duckduckgo.com/?q={query}"}
                )
            elif method == "local":
                result = await self.execute_tool("fs_list", {"path": "."})
            else:
                result = "Search completed"

            return AgentResult(success=True, output=result)

        return AgentResult(success=True, output=response)
