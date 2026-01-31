import asyncio
from typing import List, Dict
import uuid

from .config import AkiraConfig
from .llm_router import LLMRouter
from .llm_settings import LlmSettingsStore
from .memory import MemoryStore
from .agent import AgentCore
from .graph_agent import GraphAgent
from .tools.registry import ToolRegistry
from .agents import AgentContext
from .agents.orchestrator import OrchestratorAgent
from .agents.planner import PlannerAgent
from .agents.executor import ExecutorAgent
from .agents.reflector import ReflectorAgent
from .control import RequestBudget, DeliberationPipeline, LogRetention

try:
    from langgraph.graph import StateGraph, END  # type: ignore
    from typing import TypedDict
except Exception:  # pragma: no cover
    StateGraph = None
    END = None
    TypedDict = dict  # type: ignore


class AgentRuntime:
    def __init__(self, config: AkiraConfig):
        self.config = config
        self.router = LLMRouter(
            model=config.model,
            fallback_model=config.fallback_model,
            primary_base=config.primary_api_base,
            primary_key=config.primary_api_key,
            fallback_base=config.openrouter_base,
            fallback_key=config.openrouter_api_key,
            timeout_s=config.timeout_s,
            wire_api=config.wire_api,
            fallback_wire_api=config.fallback_wire_api,
            budget_manager=None,
        )
        self.budget = RequestBudget(config.data_dir, limit_per_day=10000)
        self.router.set_budget_manager(self.budget)
        self.retention = LogRetention(config.data_dir, days=90)
        self.settings = LlmSettingsStore(config.data_dir)
        self._llm_lock = asyncio.Lock()
        self.memory = MemoryStore(
            data_dir=config.data_dir,
            primary_api_base=config.primary_api_base,
            primary_api_key=config.primary_api_key,
            model=config.model,
        )
        self.tools = ToolRegistry(
            mode=config.mode,
            disable_safe_mode=config.disable_safe_mode,
            mcp_roots=config.mcp_roots,
            data_dir=config.data_dir,
            n8n_api_base=config.n8n_api_base,
            n8n_api_key=config.n8n_api_key,
            chatdev_path=config.chatdev_path,
            browser_proxy=config.browser_proxy,
        )
        self.tools.memory = self.memory
        # Use LangGraph manager if available, else fallback to simple core.
        self.deliberation = DeliberationPipeline(self.router)
        self.core = GraphAgent(self.router, self.memory, self.tools, deliberation=self.deliberation)
        self.graph = self._build_graph()

        # Initialize orchestrator with subagents
        self.orchestrator = self._init_orchestrator()

    def _init_orchestrator(self) -> OrchestratorAgent:
        """Initialize the orchestrator with all subagents."""
        orchestrator = OrchestratorAgent(
            self.router, self.tools, self.memory
        )

        # Register subagents
        orchestrator.register_subagent("planner", PlannerAgent(self.router))
        orchestrator.register_subagent("executor", ExecutorAgent(self.router, self.tools))
        orchestrator.register_subagent("reflector", ReflectorAgent(self.router, self.memory))

        return orchestrator

    async def _apply_llm_settings_no_lock(self, user_id: str) -> str | None:
        settings = self.settings.load_settings(user_id)
        provider = settings.get("provider") or "primary"
        model = settings.get("model") or self.config.model

        if provider == "primary":
            primary_base = self.config.primary_api_base
            primary_key = settings.get("primary_key") or self.config.primary_api_key
            fallback_base = self.config.openrouter_base
            fallback_key = self.config.openrouter_api_key
            fallback_model = self.config.fallback_model
        elif provider == "openrouter":
            primary_base = self.config.openrouter_base
            primary_key = settings.get("openrouter_key") or self.config.openrouter_api_key
            if not primary_key:
                return "ERROR: missing OpenRouter key. Set via LLM: key or env OPENROUTER_API_KEY."
            fallback_base = self.config.openrouter_base
            fallback_key = None
            fallback_model = None
        elif provider == "custom":
            primary_base = settings.get("custom_base")
            primary_key = settings.get("custom_key")
            if not primary_base:
                return "ERROR: custom base required. Use LLM: base."
            if not primary_key:
                return "ERROR: custom key required. Use LLM: key."
            fallback_base = primary_base
            fallback_key = None
            fallback_model = None
        else:
            return "ERROR: Unknown provider. Use LLM: primary/openrouter/custom."

        self.router.update_config(
            primary_base=primary_base,
            primary_key=primary_key,
            model=model,
            fallback_base=fallback_base,
            fallback_key=fallback_key,
            fallback_model=fallback_model,
        )
        return None

    async def apply_llm_settings(self, user_id: str) -> str | None:
        async with self._llm_lock:
            return await self._apply_llm_settings_no_lock(user_id)

    async def handle_message(self, user_id: str, text: str) -> str:
        async with self._llm_lock:
            try:
                self.retention.maybe_purge()
            except Exception:
                pass
            err = await self._apply_llm_settings_no_lock(user_id)
            if err:
                return err
            assistant_text = await self.core.run(user_id, text)
            self.memory.add_turn(user_id, text, assistant_text)
            return assistant_text

    def _build_graph(self):
        if StateGraph is None:
            return None

        class GraphState(TypedDict):
            messages: List[Dict[str, str]]

        async def llm_node(state: GraphState):
            messages = list(state.get("messages", []))
            if self.deliberation is not None:
                task = ""
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        task = msg.get("content", "")
                        break
                if not task and messages:
                    task = messages[-1].get("content", "")
                if task:
                    delib = await self.deliberation.run(task)
                    if not delib.get("ok", True):
                        assistant = delib.get("error", "ERROR: control plane blocked the request.")
                        return {"messages": messages + [{"role": "assistant", "content": assistant}]}
                    summary = delib.get("summary", "")
                    if summary:
                        messages = messages + [{"role": "system", "content": f"## CONTROL_PLANE\n{summary}"}]
            assistant = await self.router.chat(messages)
            return {"messages": messages + [{"role": "assistant", "content": assistant}]}

        graph = StateGraph(GraphState)
        graph.add_node("chat", llm_node)
        graph.add_edge("chat", END)
        graph.set_entry_point("chat")
        return graph.compile()
