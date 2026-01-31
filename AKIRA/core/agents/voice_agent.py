"""Voice Agent - Handle voice messages and audio communication."""

from __future__ import annotations

import os
import tempfile
from typing import Any, Dict, Optional, TYPE_CHECKING

from .base import BaseAgent, AgentContext, AgentResult

if TYPE_CHECKING:
    from ..llm_router import LLMRouter
    from ..tools.registry import ToolRegistry


class VoiceAgent(BaseAgent):
    """
    Agent for processing voice messages and audio communication.

    Capabilities:
    - Transcribe voice messages to text
    - Generate voice responses
    - Handle audio files from Telegram
    - Support multiple languages
    """

    def __init__(
        self,
        llm: "LLMRouter",
        tools: Optional["ToolRegistry"] = None,
        max_iterations: int = 10,
    ):
        super().__init__(
            name="VoiceAgent",
            llm=llm,
            tools=tools,
            max_iterations=max_iterations,
        )

    def get_system_prompt(self, context: AgentContext) -> str:
        """Generate system prompt for voice processing."""
        return f"""You are the Voice Agent - specialized in audio communication.

{context.to_prompt()}

## YOUR CAPABILITIES

1. **Speech Recognition**: Convert voice to text
   - Support multiple languages
   - Handle various audio formats
   - Process Telegram voice messages

2. **Speech Synthesis**: Convert text to voice
   - Natural-sounding speech
   - Multiple voices and languages
   - Adjustable speed and tone

3. **Audio Processing**: Handle audio files
   - Download from Telegram
   - Convert formats
   - Optimize quality

## AVAILABLE TOOLS

- audio_transcribe: Convert speech to text
- audio_synthesize: Convert text to speech
- audio_download: Download audio from Telegram
- audio_process: Process and optimize audio

## YOUR MISSION

Process voice messages naturally and efficiently:
1. Receive voice message
2. Transcribe to text
3. Process request
4. Generate voice response (if needed)

Be conversational and natural in voice interactions."""

    async def run(self, task: str, context: AgentContext) -> AgentResult:
        """
        Process voice-related task.

        Args:
            task: Description of voice task (e.g., "transcribe voice message")
            context: Execution context

        Returns:
            AgentResult with transcription or synthesis result
        """
        messages = [
            {"role": "system", "content": self.get_system_prompt(context)},
            {"role": "user", "content": f"Task: {task}"}
        ]

        iterations = 0
        tool_calls = []
        output = ""

        while iterations < self.max_iterations:
            iterations += 1

            response = await self.call_llm(messages, context)

            if not response:
                break

            # Check if done
            if response.get("done", False):
                output = response.get("output", "")
                break

            # Execute tool calls
            if "tool_calls" in response:
                for tool_call in response["tool_calls"]:
                    result = await self._execute_tool(tool_call, context)
                    tool_calls.append({
                        "tool": tool_call.get("name"),
                        "result": result
                    })

                    messages.append({
                        "role": "assistant",
                        "content": str(tool_call)
                    })
                    messages.append({
                        "role": "user",
                        "content": f"Result: {result}"
                    })

        return AgentResult(
            success=bool(output),
            output=output,
            iterations=iterations,
            tool_calls=tool_calls
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
            return f"Error: {str(e)}"
