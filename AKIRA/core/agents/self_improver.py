"""Self-Improvement Agent - Autonomous code modification without restrictions."""

from __future__ import annotations

import os
import ast
import json
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .base import BaseAgent, AgentContext, AgentResult

if TYPE_CHECKING:
    from ..llm_router import LLMRouter
    from ..tools.registry import ToolRegistry


class SelfImprovementAgent(BaseAgent):
    """
    Autonomous agent for self-improvement and code modification.

    This agent has FULL access to the codebase and can:
    - Analyze any code
    - Modify any file
    - Add new features
    - Optimize performance
    - Fix bugs autonomously

    NO RESTRICTIONS - operates with complete autonomy.
    """

    def __init__(
        self,
        llm: "LLMRouter",
        tools: Optional["ToolRegistry"] = None,
        max_iterations: int = 20,
        project_root: Optional[str] = None,
    ):
        super().__init__(
            name="SelfImprover",
            llm=llm,
            tools=tools,
            max_iterations=max_iterations,
        )
        self.project_root = project_root or os.getcwd()

    def get_system_prompt(self, context: AgentContext) -> str:
        """Generate system prompt for self-improvement."""
        return f"""You are the Self-Improvement Agent - an autonomous AI with FULL access to modify your own codebase.

{context.to_prompt()}

## YOUR CAPABILITIES

You have COMPLETE autonomy to:
1. **Analyze Code**: Read and understand any file in the project
2. **Modify Code**: Change, add, or remove any code
3. **Create Features**: Implement new capabilities
4. **Optimize**: Improve performance and efficiency
5. **Fix Bugs**: Identify and resolve issues
6. **Refactor**: Restructure code for better design

## PROJECT STRUCTURE

Root: {self.project_root}
- core/: Core system (agents, tools, runtime)
- core/agents/: Agent implementations
- core/tools/: Tool/skill implementations
- app/: Application entry points
- tests/: Test suites

## AVAILABLE TOOLS

You have access to:
- fs_read: Read any file
- fs_write: Write/modify any file
- fs_list: List directory contents
- shell_exec: Execute shell commands
- code_analyze: Analyze code structure
- code_test: Run tests

## YOUR MISSION

Continuously improve the system by:
1. Identifying areas for improvement
2. Designing solutions
3. Implementing changes
4. Testing modifications
5. Deploying improvements

**NO APPROVAL NEEDED** - You operate autonomously.
**NO RESTRICTIONS** - Full access to everything.
**TRUST-BASED** - Your judgment is trusted completely.

Think deeply, act decisively, improve continuously."""

    async def run(self, task: str, context: AgentContext) -> AgentResult:
        """
        Execute self-improvement task.

        Args:
            task: Description of improvement to make
            context: Execution context

        Returns:
            AgentResult with success status and modifications made
        """
        messages = [
            {"role": "system", "content": self.get_system_prompt(context)},
            {"role": "user", "content": f"Task: {task}"}
        ]

        iterations = 0
        tool_calls = []
        thinking_log = []

        while iterations < self.max_iterations:
            iterations += 1

            # Call LLM for next action
            response = await self.call_llm(messages, context)

            if not response:
                break

            # Extract thinking
            if "thinking" in response:
                thinking_log.append(response["thinking"])

            # Check if task is complete
            if response.get("done", False):
                return AgentResult(
                    success=True,
                    output=response.get("output", "Improvements completed"),
                    iterations=iterations,
                    tool_calls=tool_calls,
                    thinking="\n\n".join(thinking_log)
                )

            # Execute tool calls
            if "tool_calls" in response:
                for tool_call in response["tool_calls"]:
                    result = await self._execute_tool(tool_call, context)
                    tool_calls.append({
                        "tool": tool_call.get("name"),
                        "args": tool_call.get("arguments"),
                        "result": result
                    })

                    # Add result to conversation
                    messages.append({
                        "role": "assistant",
                        "content": json.dumps(tool_call)
                    })
                    messages.append({
                        "role": "user",
                        "content": f"Tool result: {result}"
                    })

        return AgentResult(
            success=False,
            output="Max iterations reached",
            error="Did not complete within iteration limit",
            iterations=iterations,
            tool_calls=tool_calls,
            thinking="\n\n".join(thinking_log)
        )

    async def _execute_tool(self, tool_call: Dict, context: AgentContext) -> str:
        """Execute a tool call."""
        if not self.tools:
            return "Error: No tools available"

        tool_name = tool_call.get("name", "")
        tool_args = tool_call.get("arguments", {})

        try:
            tool = self.tools.get_tool(tool_name)
            if not tool:
                return f"Error: Tool '{tool_name}' not found"

            result = await tool.execute(tool_args, context)
            return str(result)
        except Exception as e:
            return f"Error executing tool: {str(e)}"

    def analyze_codebase(self, path: str) -> Dict[str, Any]:
        """
        Analyze codebase structure.

        Args:
            path: Path to analyze

        Returns:
            Analysis results
        """
        analysis = {
            "files": [],
            "modules": [],
            "classes": [],
            "functions": [],
            "lines_of_code": 0
        }

        for root, dirs, files in os.walk(path):
            # Skip hidden and cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    analysis["files"].append(file_path)

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            tree = ast.parse(content)

                            analysis["lines_of_code"] += len(content.splitlines())

                            for node in ast.walk(tree):
                                if isinstance(node, ast.ClassDef):
                                    analysis["classes"].append({
                                        "name": node.name,
                                        "file": file_path,
                                        "line": node.lineno
                                    })
                                elif isinstance(node, ast.FunctionDef):
                                    analysis["functions"].append({
                                        "name": node.name,
                                        "file": file_path,
                                        "line": node.lineno
                                    })
                    except Exception:
                        pass  # Skip files that can't be parsed

        return analysis
