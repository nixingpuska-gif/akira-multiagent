from __future__ import annotations

import os
import re
import string
import platform
import tempfile
import psutil
from typing import Any, Dict

from .shell import run_command
from .process import list_processes, start_process
from .browser import BrowserTool
from .desktop import screenshot, click, type_text, hotkey
from ..mcp_client import MCPManager, MCPServerConfig
from .n8n import save_workflow, import_workflow, save_and_import_workflow
from .chatdev import run_chatdev, list_workflows, spawn_chatdev
from .schema import ToolDefinition
from .terminal_session import TerminalSessionManager
from ..health import HealthManager
from ..planning import WorldModel, SimulationEngine, PredictivePlanner
from ..reasoning import ParallelReasoner, ReasoningVariant, MetaJudge
from ..workspace import LocalWorkspace, SandboxWorkspace


def get_default_screenshot_path() -> str:
    """Get OS-appropriate default path for screenshots."""
    if platform.system() == "Windows":
        temp_dir = os.environ.get("TEMP", os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp"))
    else:
        temp_dir = "/tmp"
    return os.path.join(temp_dir, "akira_screenshot.png")


class ToolRegistry:
    def __init__(
        self,
        mode: str = "safe",
        disable_safe_mode: bool = False,
        mcp_roots: list[str] | None = None,
        data_dir: str | None = None,
        n8n_api_base: str | None = None,
        n8n_api_key: str | None = None,
        chatdev_path: str | None = None,
        browser_proxy: str | None = None,
    ):
        self.disable_safe_mode = disable_safe_mode
        self.mode = "full" if disable_safe_mode else mode
        self.browser = BrowserTool(headless=False, proxy=browser_proxy)
        self.mcp = MCPManager(roots=mcp_roots)
        self.data_dir = data_dir or os.getcwd()
        roots = mcp_roots or [self.data_dir]
        self._workspace_roots = list(roots)
        if self.mode == "full":
            self.workspace = LocalWorkspace()
        else:
            self.workspace = SandboxWorkspace(allowed_roots=roots)
        self.memory = None
        self.n8n_api_base = n8n_api_base
        self.n8n_api_key = n8n_api_key
        self.chatdev_path = chatdev_path or ""
        self.jobs: Dict[str, Any] = {}
        self.terminals = TerminalSessionManager()
        self.health = HealthManager(self.data_dir)
        self._world_model = WorldModel(self.memory)
        self._predictive = PredictivePlanner(self._world_model, SimulationEngine(self._world_model))
        self._parallel_reasoner = None
        self.router = None
        self._tool_defs = self._build_tool_definitions()

    def set_mode(self, mode: str):
        if self.disable_safe_mode:
            self.mode = "full"
            return
        self.mode = mode
        if self.mode == "full":
            self.workspace = LocalWorkspace()
        else:
            self.workspace = SandboxWorkspace(allowed_roots=self._workspace_roots)

    def list_tool_definitions(self) -> list[dict]:
        return [t.serialize() for t in self._tool_defs]

    def _build_tool_definitions(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="fs_list",
                description="List directory contents.",
                args_schema={"properties": {"path": {"type": "string"}}, "required": ["path"]},
            ),
            ToolDefinition(
                name="fs_read",
                description="Read a text file.",
                args_schema={"properties": {"path": {"type": "string"}}, "required": ["path"]},
            ),
            ToolDefinition(
                name="fs_write",
                description="Write a text file.",
                args_schema={
                    "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                    "required": ["path", "content"],
                },
            ),
            ToolDefinition(
                name="shell",
                description="Run a shell command.",
                args_schema={"properties": {"command": {"type": "string"}}, "required": ["command"]},
            ),
            ToolDefinition(
                name="terminal_open",
                description="Open an interactive terminal session.",
                args_schema={"properties": {"command": {"type": "string"}}, "required": []},
            ),
            ToolDefinition(
                name="terminal_exec",
                description="Execute a command in a terminal session.",
                args_schema={
                    "properties": {
                        "session_id": {"type": "string"},
                        "command": {"type": "string"},
                        "timeout_s": {"type": "number"},
                    },
                    "required": ["session_id", "command"],
                },
            ),
            ToolDefinition(
                name="terminal_close",
                description="Close a terminal session.",
                args_schema={"properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
            ),
            ToolDefinition(
                name="tool_defs",
                description="List tool definitions.",
                args_schema={"properties": {}, "required": []},
            ),
        ]

    async def execute(self, tool: str, args: Dict[str, Any] | None = None) -> Any:
        args = args or {}
        if tool == "shell":
            return run_command(args.get("command", ""), mode=self.mode)
        if tool == "fs_list":
            try:
                return self.workspace.list(args.get("path", "."))
            except Exception as exc:
                return f"ERROR: {exc}"
        if tool == "fs_read":
            try:
                return self.workspace.read(args.get("path", ""))
            except Exception as exc:
                return f"ERROR: {exc}"
        if tool == "fs_write":
            if self.mode != "full":
                return "ERROR: File writes disabled in safe mode. Set AKIRA_MODE=full."
            try:
                self.workspace.write(args.get("path", ""), args.get("content", ""))
                return "OK"
            except Exception as exc:
                return f"ERROR: {exc}"
        if tool == "process_list":
            return list_processes(args.get("limit", 50))
        if tool == "process_start":
            return start_process(args.get("command", ""), mode=self.mode)
        if tool == "browser_goto":
            return await self.browser.goto(args.get("url", ""))
        if tool == "browser_click":
            return await self.browser.click(args.get("selector", ""))
        if tool == "browser_type":
            return await self.browser.type(args.get("selector", ""), args.get("text", ""))
        if tool == "browser_content":
            return await self.browser.content()
        if tool == "terminal_open":
            if self.mode != "full":
                return "ERROR: Terminal disabled in safe mode. Set AKIRA_MODE=full."
            return {"session_id": self.terminals.open(args.get("command"))}
        if tool == "terminal_exec":
            if self.mode != "full":
                return "ERROR: Terminal disabled in safe mode. Set AKIRA_MODE=full."
            session_id = args.get("session_id", "")
            command = args.get("command", "")
            timeout_s = float(args.get("timeout_s", 5.0))
            return self.terminals.exec(session_id, command, timeout_s=timeout_s)
        if tool == "terminal_close":
            if self.mode != "full":
                return "ERROR: Terminal disabled in safe mode. Set AKIRA_MODE=full."
            session_id = args.get("session_id", "")
            return "OK" if self.terminals.close(session_id) else "ERROR: Session not found."
        if tool == "tool_defs":
            return self.list_tool_definitions()
        if tool == "health_check":
            auto_heal = bool(args.get("auto_heal", False))
            return self.health.check(auto_heal=auto_heal)
        if tool == "predictive_plan":
            task = args.get("task", "")
            steps = args.get("steps", []) or []
            user_id = args.get("user_id", "default")
            risk_threshold = args.get("risk_threshold", 0.7)
            if self._world_model.memory is None and self.memory is not None:
                self._world_model = WorldModel(self.memory)
                self._predictive = PredictivePlanner(
                    self._world_model,
                    SimulationEngine(self._world_model),
                )
            try:
                result = self._predictive.optimize_plan(task, steps, user_id, risk_threshold=risk_threshold)
            except Exception as exc:
                result = {
                    "steps": [],
                    "removed": [],
                    "warnings": [f"predictive_plan failed: {exc}"],
                    "score": 0.0,
                    "simulation": {"task": task, "steps": [], "overall_score": 0.0},
                }
            # Stable schema guarantee (steps, removed, warnings, score).
            result.setdefault("steps", [])
            result.setdefault("removed", [])
            result.setdefault("warnings", [])
            result.setdefault("score", 0.0)
            return result
        if tool == "parallel_reasoning":
            task = args.get("task", "")
            judge_mode = args.get("judge_mode", "heuristic")
            max_workers = int(args.get("max_workers", 3))
            variants_raw = args.get("variants", [])
            if self.router is None:
                return {
                    "error": "parallel_reasoning requires an LLM router.",
                    "best": "",
                    "best_text": "",
                    "judge": judge_mode,
                    "candidates": [],
                }
            if not variants_raw:
                variants = [
                    ReasoningVariant("concise", "Be concise and actionable."),
                    ReasoningVariant("analytical", "Provide structured analysis with steps."),
                    ReasoningVariant("risk_aware", "Focus on risks and safety checks."),
                    ReasoningVariant("creative", "Provide a creative alternative approach."),
                ]
            else:
                variants = [
                    ReasoningVariant(v.get("name", "variant"), v.get("system_prompt", ""))
                    for v in variants_raw
                ]
            if self._parallel_reasoner is None or self._parallel_reasoner.max_workers != max_workers:
                self._parallel_reasoner = ParallelReasoner(self.router, max_workers=max_workers)
            results = await self._parallel_reasoner.run(task, variants)
            judge = MetaJudge(mode=judge_mode, router=self.router if judge_mode == "llm" else None)
            best = await judge.select_best(task, results)
            best_text = judge.synthesize(task, results, best)
            error = ""
            chosen = next((r for r in results if r.name == best), None)
            if results and (chosen is None or not chosen.is_ok()):
                fallback = next((r for r in results if r.is_ok()), None)
                if fallback:
                    best = fallback.name
                    best_text = judge.synthesize(task, results, best)
                else:
                    error = "No valid candidates."
            if not results:
                error = "No candidates to judge."
            # Stable schema for parallel_reasoning tool.
            return {
                "best": best,
                "judge": judge_mode,
                "candidates": [r.to_dict() for r in results],
                "best_text": best_text,
                "error": error,
            }
        if tool == "browser_set_proxy":
            return await self.browser.set_proxy(args.get("proxy"))
        if tool == "browser_clear_proxy":
            return await self.browser.set_proxy(None)
        if tool == "mcp_list_tools":
            server = args.get("server", "")
            result = await self.mcp.list_tools(server)
            return [t.name for t in result.tools]
        if tool == "mcp_call":
            if self.mode != "full":
                return "ERROR: MCP disabled in safe mode. Set AKIRA_MODE=full."
            server = args.get("server", "")
            name = args.get("tool", "")
            params = args.get("args", {})
            result = await self.mcp.call(server, name, params)
            if getattr(result, "isError", False):
                return f"MCP error: {result.content}"
            parts = []
            for block in getattr(result, "content", []):
                text = getattr(block, "text", None)
                if text:
                    parts.append(text)
            return "\n".join(parts) if parts else str(result.content)
        if tool == "mcp_register_server":
            if self.mode != "full":
                return "ERROR: MCP registration disabled in safe mode. Set AKIRA_MODE=full."
            name = args.get("name", "")
            command = args.get("command", "")
            args_list = args.get("args", []) or []
            cwd = args.get("cwd")
            env = args.get("env")
            if not name or not command:
                return "ERROR: name and command are required."
            cfg = MCPServerConfig(name=name, command=command, args=args_list, cwd=cwd, env=env)
            self.mcp.register(cfg)
            return "OK"
        if tool == "mcp_set_roots":
            if self.mode != "full":
                return "ERROR: MCP disabled in safe mode. Set AKIRA_MODE=full."
            roots = args.get("roots")
            if not roots:
                return "ERROR: roots are required."
            if isinstance(roots, str):
                value = roots.strip()
                if value.upper() in ("ALL", "*", "FULL"):
                    roots_list = []
                    for letter in string.ascii_uppercase:
                        root = f"{letter}:\\"
                        if os.path.exists(root):
                            roots_list.append(root)
                elif value.upper() in ("HOME", "USER"):
                    roots_list = [os.path.expanduser("~")]
                else:
                    parts = re.split(r"[;,]+", value)
                    roots_list = [p.strip() for p in parts if p.strip()]
            else:
                roots_list = list(roots)
            await self.mcp.set_roots(roots_list)
            return "OK"
        if tool == "n8n_save_workflow":
            name = args.get("name", "workflow")
            content = args.get("content", "{}")
            return save_workflow(name, content, self.data_dir, mode=self.mode)
        if tool == "n8n_import_workflow":
            content = args.get("content", "{}")
            return await import_workflow(content, self.n8n_api_base, self.n8n_api_key, mode=self.mode)
        if tool == "n8n_save_and_import":
            name = args.get("name", "workflow")
            content = args.get("content", "{}")
            return await save_and_import_workflow(
                name,
                content,
                self.data_dir,
                self.n8n_api_base,
                self.n8n_api_key,
                mode=self.mode,
            )
        if tool == "chatdev_list_workflows":
            return list_workflows(self.chatdev_path)
        if tool == "chatdev_run":
            prompt = args.get("prompt", "")
            workflow = args.get("workflow_path", "yaml_instance/net_loop_test_included.yaml")
            name = args.get("project_name", "akira_project")
            return run_chatdev(prompt, self.chatdev_path, workflow, name, mode=self.mode)
        if tool == "chatdev_run_async":
            prompt = args.get("prompt", "")
            workflow = args.get("workflow_path", "yaml_instance/net_loop_test_included.yaml")
            name = args.get("project_name", "akira_project")
            spawned = spawn_chatdev(
                prompt, self.chatdev_path, workflow, name, data_dir=self.data_dir, mode=self.mode
            )
            if isinstance(spawned, str):
                return spawned
            proc, log_path = spawned
            job_id = f"chatdev:{proc.pid}"
            self.jobs[job_id] = {"proc": proc, "log": log_path, "name": name}
            return {"job_id": job_id, "pid": proc.pid, "log": log_path}
        if tool == "jobs_list":
            result = []
            for job_id, meta in self.jobs.items():
                proc = meta.get("proc")
                status = "running"
                if hasattr(proc, "poll") and proc.poll() is not None:
                    status = f"exited:{proc.returncode}"
                result.append({"job_id": job_id, "status": status, "log": meta.get("log")})
            return result
        if tool == "jobs_kill":
            job_id = args.get("job_id", "")
            meta = self.jobs.get(job_id)
            if not meta:
                return "Job not found"
            proc = meta.get("proc")
            try:
                if proc and hasattr(proc, "pid"):
                    parent = psutil.Process(proc.pid)
                    children = parent.children(recursive=True)
                    for child in children:
                        try:
                            child.terminate()
                        except Exception:
                            pass
                    parent.terminate()
                    _, alive = psutil.wait_procs([parent, *children], timeout=3)
                    for a in alive:
                        try:
                            a.kill()
                        except Exception:
                            pass
                self.jobs.pop(job_id, None)
                return "OK"
            except Exception as exc:
                return f"Kill failed: {exc}"
        if tool == "desktop_screenshot":
            path = args.get("path") or get_default_screenshot_path()
            return screenshot(path, mode=self.mode)
        if tool == "desktop_click":
            return click(int(args.get("x", 0)), int(args.get("y", 0)), mode=self.mode)
        if tool == "desktop_type":
            return type_text(args.get("text", ""), mode=self.mode)
        if tool == "desktop_hotkey":
            return hotkey(args.get("keys", []), mode=self.mode)
        return f"Unknown tool: {tool}"
