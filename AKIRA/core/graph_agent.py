import json
import os
import re
import time
from typing import Dict, List, Optional, TypedDict, Literal

from .llm_router import LLMRouter
from .memory import MemoryStore, EpisodicMemory
from .tools.registry import ToolRegistry
from .prompts import BASE_SYSTEM_PROMPT, TOOL_INSTRUCTIONS, get_system_context
from .prompts.library import PromptLibrary
from .prompts.adaptive import PromptTracker
from .learning.meta_learner import MetaLearner

try:
    from langgraph.graph import StateGraph, END  # type: ignore
except Exception:  # pragma: no cover
    StateGraph = None
    END = None

# Configuration
MAX_ITERATIONS = 15
MAX_JSON_RETRIES = 3


class GraphState(TypedDict):
    messages: List[Dict[str, str]]
    pending: Optional[dict]
    route: Optional[Literal["tool", "delegate", "end"]]
    iteration: int
    user_id: str


class GraphAgent:
    def __init__(self, router: LLMRouter, memory: MemoryStore, tools: ToolRegistry, deliberation=None):
        self.router = router
        self.memory = memory
        self.tools = tools
        self.deliberation = deliberation
        self.episodic = EpisodicMemory(self.memory)
        data_dir = getattr(self.memory, "data_dir", None) or getattr(self.tools, "data_dir", None) or os.getcwd()
        self.prompt_library = PromptLibrary(data_dir)
        self.prompt_tracker = PromptTracker(data_dir)
        self.meta_learner = MetaLearner(data_dir)
        self.graph = self._build_graph()

        self.subagents = {
            "coder": "You are the coder agent. Provide precise code edits and tests. Use correct OS paths.",
            "research": "You are the research agent. Search thoroughly and provide sources.",
            "ops": "You are the ops agent. Execute system operations safely. Check mode before actions.",
            "memory": "You are the memory agent. Extract and store important facts and preferences.",
            "n8n": "You are the n8n agent. Design workflows and output clean JSON only.",
            "chatdev": "You are the ChatDev agent. Produce clear prompts and run parameters.",
        }

    async def run(self, user_id: str, text: str) -> str:
        start_time = time.monotonic()
        base_prompt, base_variant = self.prompt_library.get_prompt("base_system", BASE_SYSTEM_PROMPT)
        tool_prompt, tool_variant = self.prompt_library.get_prompt("tool_instructions", TOOL_INSTRUCTIONS)
        strategy = self.meta_learner.select_strategy(text, user_id)
        self.episodic.start_episode(user_id, task=text)
        final_text = ""
        error_msg = None
        delib_summary = ""
        if self.deliberation is not None:
            try:
                delib = await self.deliberation.run(text)
                if not delib.get("ok", True):
                    final_text = delib.get("error", "ERROR: control plane blocked the request.")
                    self.episodic.record_event(
                        user_id=user_id,
                        action="control:deliberation",
                        result=self._shorten(final_text),
                        success=False,
                    )
                    self.episodic.finish_episode(user_id, result=final_text or "")
                    return final_text
                delib_summary = delib.get("summary", "")
            except Exception as exc:
                final_text = f"ERROR: deliberation failed: {exc}"
                self.episodic.record_event(
                    user_id=user_id,
                    action="control:deliberation",
                    result=self._shorten(final_text),
                    success=False,
                )
                self.episodic.finish_episode(user_id, result=final_text or "")
                return final_text
        # Get memories
        memories = self.memory.recall(user_id=user_id, query=text, limit=5)
        mem_list = [m.get("memory", str(m)) for m in memories] if memories else None

        # Build system prompt with dynamic context
        context = get_system_context(
            mode=self.tools.mode,
            current_dir=self.tools.data_dir,
            available_tools=list(self._get_available_tools()),
            memories=mem_list,
        )
        control_block = f"\n\n## CONTROL_PLANE\n{delib_summary}" if delib_summary else ""
        system = f"{base_prompt}{control_block}\n\n## STRATEGY\n{strategy.description}\n\n{context}\n\n{tool_prompt}"

        state: GraphState = {
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": text}],
            "pending": None,
            "route": None,
            "iteration": 0,
            "user_id": user_id,
        }

        if not self.graph:
            try:
                final_text = await self.router.chat(state["messages"])
                self.episodic.record_event(
                    user_id=user_id,
                    action="chat",
                    result=self._shorten(final_text),
                    success=not str(final_text).startswith("ERROR"),
                )
                return final_text
            except Exception as exc:
                error_msg = str(exc)
                raise
            finally:
                self._record_prompt_usage(
                    user_id=user_id,
                    task=text,
                    base_variant=base_variant,
                    tool_variant=tool_variant,
                    final_text=final_text,
                    error_msg=error_msg,
                    start_time=start_time,
                )
                self._record_strategy_outcome(
                    user_id=user_id,
                    task=text,
                    strategy_id=strategy.id,
                    final_text=final_text,
                    error_msg=error_msg,
                    start_time=start_time,
                )
                self.episodic.finish_episode(user_id, result=final_text or "")

        try:
            result = await self.graph.ainvoke(state)
            messages = result.get("messages", [])
            if messages:
                final_text = messages[-1]["content"]
                self.episodic.record_event(
                    user_id=user_id,
                    action="chat",
                    result=self._shorten(final_text),
                    success=not str(final_text).startswith("ERROR"),
                )
                return final_text
            final_text = "No response."
            self.episodic.record_event(
                user_id=user_id,
                action="chat",
                result=self._shorten(final_text),
                success=not str(final_text).startswith("ERROR"),
            )
            return final_text
        except Exception as exc:
            error_msg = str(exc)
            raise
        finally:
            self._record_prompt_usage(
                user_id=user_id,
                task=text,
                base_variant=base_variant,
                tool_variant=tool_variant,
                final_text=final_text,
                error_msg=error_msg,
                start_time=start_time,
            )
            self._record_strategy_outcome(
                user_id=user_id,
                task=text,
                strategy_id=strategy.id,
                final_text=final_text,
                error_msg=error_msg,
                start_time=start_time,
            )
            self.episodic.finish_episode(user_id, result=final_text or "")

    def _get_available_tools(self) -> List[str]:
        """Get list of available tools based on current mode."""
        all_tools = [
            "fs_list", "fs_read", "fs_write", "shell", "process_list", "process_start",
            "browser_goto", "browser_click", "browser_type", "browser_content",
            "desktop_screenshot", "desktop_click", "desktop_type", "desktop_hotkey",
            "mcp_list_tools", "mcp_call", "jobs_list", "jobs_kill"
        ]
        if self.tools.mode != "full":
            # Remove restricted tools in safe mode
            restricted = {"fs_write", "shell", "process_start", "desktop_screenshot",
                         "desktop_click", "desktop_type", "desktop_hotkey"}
            return [t for t in all_tools if t not in restricted]
        return all_tools

    @staticmethod
    def _shorten(text: str, limit: int = 200) -> str:
        cleaned = " ".join(str(text).split())
        if len(cleaned) > limit:
            return cleaned[:limit] + "..."
        return cleaned

    def _record_prompt_usage(
        self,
        user_id: str,
        task: str,
        base_variant: str,
        tool_variant: str,
        final_text: str,
        error_msg: str | None,
        start_time: float,
    ) -> None:
        latency_ms = int((time.monotonic() - start_time) * 1000)
        success = bool(final_text) and not str(final_text).startswith("ERROR") and error_msg is None
        try:
            self.prompt_tracker.record(
                "base_system",
                base_variant,
                user_id,
                success,
                latency_ms=latency_ms,
                error=error_msg,
                task=task,
            )
            self.prompt_tracker.record(
                "tool_instructions",
                tool_variant,
                user_id,
                success,
                latency_ms=latency_ms,
                error=error_msg,
                task=task,
            )
        except Exception:
            pass

    def _record_strategy_outcome(
        self,
        user_id: str,
        task: str,
        strategy_id: str,
        final_text: str,
        error_msg: str | None,
        start_time: float,
    ) -> None:
        latency_ms = int((time.monotonic() - start_time) * 1000)
        success = bool(final_text) and not str(final_text).startswith("ERROR") and error_msg is None
        try:
            self.meta_learner.record_outcome(
                strategy_id=strategy_id,
                task=task,
                success=success,
                latency_ms=latency_ms,
                user_id=user_id,
            )
        except Exception:
            pass

    def _build_graph(self):
        if StateGraph is None:
            return None

        async def manager(state: GraphState):
            iteration = state.get("iteration", 0) + 1
            user_id = state.get("user_id", "default")

            # Check iteration limit
            if iteration > MAX_ITERATIONS:
                return {
                    "messages": state["messages"] + [{
                        "role": "assistant",
                        "content": f"Reached maximum iterations ({MAX_ITERATIONS}). Stopping."
                    }],
                    "route": "end",
                    "iteration": iteration,
                    "user_id": user_id,
                }

            # Try to get valid JSON response with retries
            messages = state["messages"]
            parsed = None
            raw = ""

            for retry in range(MAX_JSON_RETRIES):
                raw = await self.router.chat(messages)
                parsed = self._try_json(raw)

                if parsed:
                    break

                # Add retry message
                if retry < MAX_JSON_RETRIES - 1:
                    messages = messages + [
                        {"role": "assistant", "content": raw},
                        {"role": "user", "content": "Invalid JSON. Please respond with valid JSON only."}
                    ]

            if not parsed:
                # Give up and return raw response
                return {
                    "messages": state["messages"] + [{"role": "assistant", "content": raw}],
                    "route": "end",
                    "iteration": iteration,
                    "user_id": user_id,
                }

            if parsed.get("type") == "final":
                return {
                    "messages": state["messages"] + [{"role": "assistant", "content": parsed.get("content", "")}],
                    "route": "end",
                    "iteration": iteration,
                    "user_id": user_id,
                }

            if parsed.get("type") == "action":
                return {"pending": parsed, "route": "tool", "iteration": iteration, "user_id": user_id}

            if parsed.get("type") == "delegate":
                return {"pending": parsed, "route": "delegate", "iteration": iteration, "user_id": user_id}

            return {
                "messages": state["messages"] + [{"role": "assistant", "content": raw}],
                "route": "end",
                "iteration": iteration,
                "user_id": user_id,
            }

        async def tool_node(state: GraphState):
            pending = state.get("pending") or {}
            tool = pending.get("tool", "")
            args = pending.get("args", {}) or {}
            iteration = state.get("iteration", 0)
            user_id = state.get("user_id", "default")

            try:
                start_ts = time.monotonic()
                result = await self.tools.execute(tool, args)
                duration = max(time.monotonic() - start_ts, 0.0)
            except Exception as e:
                result = f"ERROR: {str(e)}"
                duration = None

            self.episodic.record_event(
                user_id=user_id,
                action=f"tool:{tool}",
                result=self._shorten(str(result)),
                success=not str(result).startswith("ERROR"),
                duration_sec=duration,
            )
            messages = state["messages"] + [{"role": "user", "content": f"Observation: {result}"}]
            return {
                "messages": messages,
                "pending": None,
                "route": None,
                "iteration": iteration,
                "user_id": user_id,
            }

        async def delegate_node(state: GraphState):
            pending = state.get("pending") or {}
            agent = pending.get("agent")
            task = pending.get("task", "")
            iteration = state.get("iteration", 0)
            user_id = state.get("user_id", "default")

            prompt = self.subagents.get(agent or "", "You are a helper. Provide a brief answer.")
            try:
                start_ts = time.monotonic()
                reply = await self.router.chat(
                    [{"role": "system", "content": prompt}, {"role": "user", "content": task}]
                )
                duration = max(time.monotonic() - start_ts, 0.0)
            except Exception as e:
                reply = f"ERROR: Subagent failed: {str(e)}"
                duration = None

            self.episodic.record_event(
                user_id=user_id,
                action=f"agent:{agent}",
                result=self._shorten(str(reply)),
                success=not str(reply).startswith("ERROR"),
                duration_sec=duration,
            )
            messages = state["messages"] + [{"role": "user", "content": f"Observation: {reply}"}]
            return {
                "messages": messages,
                "pending": None,
                "route": None,
                "iteration": iteration,
                "user_id": user_id,
            }

        graph = StateGraph(GraphState)
        graph.add_node("manager", manager)
        graph.add_node("tool", tool_node)
        graph.add_node("delegate", delegate_node)

        def route(state: GraphState):
            if state.get("route") == "tool":
                return "tool"
            if state.get("route") == "delegate":
                return "delegate"
            return END

        graph.add_conditional_edges("manager", route, {"tool": "tool", "delegate": "delegate", END: END})
        graph.add_edge("tool", "manager")
        graph.add_edge("delegate", "manager")
        graph.set_entry_point("manager")
        return graph.compile()

    @staticmethod
    def _try_json(raw: str) -> Optional[dict]:
        """Extract JSON from response, handling markdown blocks."""
        raw = raw.strip()

        # Try direct parse first
        if raw.startswith("{"):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                pass

        # Try to extract from markdown code blocks
        patterns = [
            r'```json\s*([\s\S]*?)\s*```',
            r'```\s*([\s\S]*?)\s*```',
        ]

        for pattern in patterns:
            match = re.search(pattern, raw)
            if match:
                try:
                    return json.loads(match.group(1).strip())
                except json.JSONDecodeError:
                    continue

        # Try to find JSON object anywhere in text
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        return None
