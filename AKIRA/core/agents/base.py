"""Base agent class for AKIRA 2.0 multi-agent system."""

from __future__ import annotations

import json
import re
import os
import platform
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..llm_router import LLMRouter
    from ..tools.registry import ToolRegistry


@dataclass
class AgentContext:
    """Execution context for an agent."""

    user_id: str
    session_id: str
    mode: str = "safe"
    current_dir: Optional[str] = None
    available_tools: List[str] = field(default_factory=list)
    memories: List[str] = field(default_factory=list)

    @property
    def os_type(self) -> str:
        return platform.system()

    @property
    def os_version(self) -> str:
        return platform.version()

    @property
    def user_home(self) -> str:
        return os.path.expanduser("~")

    @property
    def username(self) -> str:
        return os.path.basename(self.user_home)

    @property
    def timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def temp_dir(self) -> str:
        if self.os_type == "Windows":
            return os.environ.get("TEMP", os.path.join(self.user_home, "AppData", "Local", "Temp"))
        return "/tmp"

    def to_prompt(self) -> str:
        """Convert context to prompt string."""
        lines = [
            "## SYSTEM CONTEXT",
            f"- OS: {self.os_type} {self.os_version}",
            f"- User: {self.username}",
            f"- Home: {self.user_home}",
            f"- Current Directory: {self.current_dir or os.getcwd()}",
            f"- Temp Directory: {self.temp_dir}",
            f"- Time: {self.timestamp}",
            f"- Mode: {self.mode.upper()}",
        ]

        if self.mode == "full":
            lines.append("- Access: FULL (shell, files, desktop, browser, processes)")
        else:
            lines.append("- Access: SAFE (read-only, browser only)")

        if self.available_tools:
            lines.append(f"- Available Tools: {len(self.available_tools)}")

        if self.memories:
            lines.append("\n## RELEVANT MEMORIES")
            for mem in self.memories[:10]:
                lines.append(f"- {mem}")

        return "\n".join(lines)


@dataclass
class AgentResult:
    """Result from agent execution."""

    success: bool
    output: Any
    error: Optional[str] = None
    iterations: int = 0
    tool_calls: List[Dict] = field(default_factory=list)
    thinking: Optional[str] = None


class BaseAgent(ABC):
    """Base class for all AKIRA agents."""

    def __init__(
        self,
        name: str,
        llm: "LLMRouter",
        tools: Optional["ToolRegistry"] = None,
        max_iterations: int = 15,
        max_json_retries: int = 3,
        timeout: float = 300.0,
    ):
        self.name = name
        self.llm = llm
        self.tools = tools
        self.max_iterations = max_iterations
        self.max_json_retries = max_json_retries
        self.timeout = timeout

    @abstractmethod
    def get_system_prompt(self, context: AgentContext) -> str:
        """Generate system prompt for this agent."""
        pass

    @abstractmethod
    async def run(self, task: str, context: AgentContext) -> AgentResult:
        """Execute the agent's task."""
        pass

    async def call_llm(
        self,
        messages: List[Dict[str, str]],
        expect_json: bool = False,
    ) -> str:
        """Call LLM with optional JSON retry logic."""
        if not expect_json:
            return await self.llm.chat(messages)

        # Try to get valid JSON with retries
        current_messages = messages.copy()

        for attempt in range(self.max_json_retries):
            response = await self.llm.chat(current_messages)
            parsed = self.extract_json(response)

            if parsed is not None:
                return response

            # Add retry message
            if attempt < self.max_json_retries - 1:
                current_messages.append({"role": "assistant", "content": response})
                current_messages.append({
                    "role": "user",
                    "content": "Invalid JSON format. Please respond with valid JSON only."
                })

        return response  # Return last response even if not valid JSON

    @staticmethod
    def extract_json(text: str) -> Optional[Dict]:
        """Extract JSON from text, handling markdown blocks."""
        text = text.strip()

        # Try direct parse
        if text.startswith("{"):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass

        # Try markdown code blocks
        patterns = [
            r'```json\s*([\s\S]*?)\s*```',
            r'```\s*([\s\S]*?)\s*```',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return json.loads(match.group(1).strip())
                except json.JSONDecodeError:
                    continue

        # Try to find JSON object anywhere
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        return None

    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute a tool and return result."""
        if not self.tools:
            return "ERROR: No tools available"

        try:
            result = await self.tools.execute(tool_name, args)
            return str(result)
        except Exception as e:
            return f"ERROR: {str(e)}"
