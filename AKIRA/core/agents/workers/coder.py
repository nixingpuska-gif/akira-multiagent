"""Coder worker - integrates with Codex CLI for programming tasks."""

from __future__ import annotations

import subprocess
import os
from typing import TYPE_CHECKING

from ..base import BaseAgent, AgentContext, AgentResult

if TYPE_CHECKING:
    from ...llm_router import LLMRouter


class CoderWorker(BaseAgent):
    """Worker that delegates coding tasks to Codex CLI."""

    def __init__(self, llm: "LLMRouter"):
        super().__init__("coder", llm, max_iterations=5)

    def get_system_prompt(self, context: AgentContext) -> str:
        return f"""You are the Coder worker. Handle programming tasks.

{context.to_prompt()}

For complex coding: delegate to Codex CLI
For simple edits: provide code directly

Respond with JSON:
{{"action": "codex", "task": "description", "project_path": "path"}}
or
{{"action": "code", "language": "python", "code": "..."}}
"""

    async def run(self, task: str, context: AgentContext) -> AgentResult:
        messages = [
            {"role": "system", "content": self.get_system_prompt(context)},
            {"role": "user", "content": task}
        ]

        response = await self.call_llm(messages, expect_json=True)
        parsed = self.extract_json(response)

        if parsed and parsed.get("action") == "codex":
            result = await self._run_codex(
                parsed.get("task", task),
                parsed.get("project_path", context.current_dir)
            )
            return AgentResult(success=True, output=result)

        return AgentResult(success=True, output=response)

    async def _run_codex(self, task: str, project_path: str) -> str:
        """Run Codex CLI with a task."""
        try:
            # Check if codex is available
            result = subprocess.run(
                ["codex", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                return "Codex CLI not available"

            # Run codex with task
            result = subprocess.run(
                ["codex", "-p", task],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout or result.stderr or "Codex completed"

        except FileNotFoundError:
            return "Codex CLI not installed"
        except subprocess.TimeoutExpired:
            return "Codex timed out"
        except Exception as e:
            return f"Codex error: {e}"
