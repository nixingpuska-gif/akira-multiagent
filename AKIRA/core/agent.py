import json
from typing import Dict, List, Optional

from .llm_router import LLMRouter
from .memory import MemoryStore
from .prompts import BASE_SYSTEM_PROMPT, TOOL_INSTRUCTIONS
from .tools.registry import ToolRegistry


class AgentCore:
    def __init__(self, router: LLMRouter, memory: MemoryStore, tools: ToolRegistry):
        self.router = router
        self.memory = memory
        self.tools = tools

        self.subagents = {
            "coder": "You are the coder agent. Provide precise code edits and tests.",
            "research": "You are the research agent. Provide concise findings and sources if needed.",
            "ops": "You are the ops agent. Provide operational steps and safe commands.",
            "memory": "You are the memory agent. Extract concise facts, decisions, and preferences.",
            "n8n": "You are the n8n agent. Design a workflow autonomously and output clean JSON only.",
            "chatdev": "You are the ChatDev agent. Produce a clear prompt and run parameters.",
        }

    async def run(self, user_id: str, text: str) -> str:
        memories = self.memory.recall(user_id=user_id, query=text, limit=5)
        mem_lines = "\n".join(f"- {m['memory']}" for m in memories) if memories else ""
        system = BASE_SYSTEM_PROMPT + "\n" + TOOL_INSTRUCTIONS
        if mem_lines:
            system += f"\n\nMemory:\n{mem_lines}"

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ]

        for _ in range(5):
            raw = await self.router.chat(messages)
            parsed = self._try_json(raw)
            if not parsed:
                return raw

            if parsed.get("type") == "final":
                return str(parsed.get("content", ""))

            if parsed.get("type") == "delegate":
                agent = parsed.get("agent")
                task = parsed.get("task", "")
                result = await self._delegate(agent, task)
                messages.append({"role": "user", "content": f"Observation: {result}"})
                continue

            if parsed.get("type") == "action":
                tool = parsed.get("tool", "")
                args = parsed.get("args", {}) or {}
                result = await self.tools.execute(tool, args)
                messages.append({"role": "user", "content": f"Observation: {result}"})
                continue

            return raw

        return "Step limit reached. Please clarify the task."

    async def _delegate(self, agent: Optional[str], task: str) -> str:
        prompt = self.subagents.get(agent or "", "You are a helper. Provide a brief answer.")
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": task},
        ]
        return await self.router.chat(messages)

    @staticmethod
    def _try_json(raw: str) -> Optional[dict]:
        raw = raw.strip()
        if not raw.startswith("{"):
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None
