import asyncio
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


results = []


def ok(name, detail="OK"):
    results.append((name, True, detail))


def fail(name, detail):
    results.append((name, False, detail))


async def record_async(name, coro, timeout=20):
    try:
        await asyncio.wait_for(coro, timeout=timeout)
        ok(name)
    except Exception as exc:
        fail(name, f"{exc}")


# Config parsing
try:
    os.environ["AKIRA_SKIP_DOTENV"] = "1"
    os.environ["AKIRA_TELEGRAM_TOKEN"] = "test"
    os.environ["AKIRA_PRIMARY_API_BASE"] = "http://localhost:1234/v1"
    os.environ["AKIRA_PRIMARY_API_KEY"] = "testkey"
    os.environ["AKIRA_TELEGRAM_ALLOWLIST"] = "123;456"
    os.environ["AKIRA_UI_ALLOWLIST"] = "local"
    os.environ["AKIRA_MCP_ROOTS"] = "HOME"
    os.environ["AKIRA_CHATDEV_PATH"] = r"C:\Users\Nicita\ChatDev"

    from core.config import load_config

    cfg = load_config()
    assert cfg.telegram_allowlist == ["123", "456"]
    assert cfg.ui_allowlist == ["local"]
    assert cfg.mcp_roots and any("Users" in p for p in cfg.mcp_roots)
    ok("config.load_config")
except Exception as exc:
    fail("config.load_config", str(exc))


# Allowlist helper
try:
    from core.config import is_allowed

    assert is_allowed([], "user", True) is False
    assert is_allowed(["*"], "user", True) is True
    ok("config.is_allowed")
except Exception as exc:
    fail("config.is_allowed", str(exc))


# Memory sqlite fallback + enhanced store + retriever cache (force mem0 off)
try:
    import core.memory as mem
    import core.memory.store as mem_store

    mem.Memory = None
    mem_store.Memory = None
    td = tempfile.mkdtemp(prefix="akira_test_")
    store = mem.EnhancedMemoryStore(td, "http://localhost:1234/v1", "testkey", "gpt-4o")
    store.add_turn("u1", "hi", "hello")
    episode = mem.Episode(user_id="u1", task="make tea", plan="boil", actions="[]", result="done", success=True)
    episode_id = store.save_episode(episode)
    assert episode_id
    assert store.save_fact("u1", "pref", "color", "blue")
    episodes = store.get_similar_episodes("make", limit=5, user_id="u1")
    assert episodes
    facts = store.get_facts("u1")
    assert facts
    lesson_id = store.save_lesson(
        episode_id,
        "runtime_error",
        "bad_input",
        "validate_input",
        "add_tests",
        user_id="u1",
    )
    assert lesson_id
    ok("memory.save_lesson")
    rec = store.recall("u1", "hi", limit=5)
    assert rec
    ok("memory.sqlite_fallback")

    retriever = mem.MemoryRetriever(store)
    search_results = retriever.search("color", user_id="u1", search_type=mem.SearchType.KEYWORD, limit=5)
    assert search_results and ("content" in search_results[0] or "memory" in search_results[0])
    ok("memory.retriever.keyword_fallback")
    calls = retriever.keyword_calls
    search_results2 = retriever.search("color", user_id="u1", search_type=mem.SearchType.KEYWORD, limit=5)
    assert retriever.keyword_calls == calls
    assert retriever.cache_hits >= 1
    ok("memory.retriever_cache")
except Exception as exc:
    fail("memory.sqlite_fallback", str(exc))
    fail("memory.save_lesson", str(exc))
    fail("memory.retriever.keyword_fallback", str(exc))
    fail("memory.retriever_cache", str(exc))


# Project indexing
try:
    import core.memory as mem

    td_proj = tempfile.mkdtemp(prefix="akira_proj_")
    file_main = os.path.join(td_proj, "main.py")
    file_util = os.path.join(td_proj, "util.js")
    file_req = os.path.join(td_proj, "requirements.txt")
    os.makedirs(os.path.join(td_proj, "subdir"), exist_ok=True)
    file_sub = os.path.join(td_proj, "subdir", "mod.py")

    with open(file_main, "w", encoding="utf-8") as f:
        f.write("print('ok')\n")
    with open(file_util, "w", encoding="utf-8") as f:
        f.write("console.log('ok');\n")
    with open(file_req, "w", encoding="utf-8") as f:
        f.write("requests==2.31.0\n")
    with open(file_sub, "w", encoding="utf-8") as f:
        f.write("# sub module\n")

    indexer = mem.ProjectIndexer()
    meta = indexer.index_project(td_proj)
    assert meta.file_count == 4
    assert "python" in meta.tech_stack
    assert "python" in meta.languages
    assert "javascript" in meta.languages
    assert "." in meta.structure
    ok("memory.project_indexer")

    store = mem.EnhancedMemoryStore(td_proj, "http://localhost:1234/v1", "testkey", "gpt-4o")
    first = indexer.index_if_changed(td_proj, store, user_id="u1")
    assert first is not None
    second = indexer.index_if_changed(td_proj, store, user_id="u1")
    assert second is None
    ok("memory.project_index_if_changed")
except Exception as exc:
    fail("memory.project_indexer", str(exc))
    fail("memory.project_index_if_changed", str(exc))


# Context compressor
try:
    from core.memory.compressor import ContextCompressor

    messages = [
        {"role": "user", "content": "We must use SQLite. Decision: use cache. Prefer short output."},
        {"role": "assistant", "content": "Confirmed. Error: previous run failed. Requirement: no external deps."},
    ]
    comp = ContextCompressor(max_tokens=30)
    ctx = comp.compress(messages, max_tokens=30)
    assert ctx.summary
    assert any("Decision" in d or "use cache" in d for d in ctx.important_decisions)
    assert ctx.token_count <= 30
    ok("memory.compressor")
except Exception as exc:
    fail("memory.compressor", str(exc))


# LLMRouter litellm stub
try:
    import core.llm_router as lr

    class DummyLLM:
        def completion(self, **kwargs):
            return {"choices": [{"message": {"content": "ok"}}]}

    lr.litellm = DummyLLM()
    router = lr.LLMRouter(
        model="gpt-4o",
        fallback_model=None,
        primary_base="http://x",
        primary_key="k",
        fallback_base="http://y",
        fallback_key=None,
    )
    resp = asyncio.run(router.chat([{"role": "user", "content": "hi"}]))
    assert resp == "ok"
    ok("llm_router.litellm_stub")
except Exception as exc:
    fail("llm_router.litellm_stub", str(exc))

# LLM settings store roundtrip
try:
    from core.llm_settings import LlmSettingsStore

    td_llm = tempfile.mkdtemp(prefix="akira_llm_")
    store = LlmSettingsStore(td_llm)
    uid = "u1"
    store.set(uid, {"provider": "openrouter", "model": "m1", "openrouter_key": "sk-1234567890abcd"})
    loaded = store.get(uid)
    assert loaded.get("provider") == "openrouter"
    assert store._mask_key("sk-1234567890abcd") == "sk-1234...abcd"
    store.update(uid, model="m2")
    assert store.get(uid).get("model") == "m2"
    store.reset(uid)
    assert store.get(uid) == {}
    ok("llm_settings.store_roundtrip")
except Exception as exc:
    fail("llm_settings.store_roundtrip", str(exc))

# LLMRouter update_config
try:
    import core.llm_router as lr

    router = lr.LLMRouter(
        model="m1",
        fallback_model=None,
        primary_base="http://a",
        primary_key="k1",
        fallback_base="http://b",
        fallback_key="k2",
    )
    router.update_config(
        primary_base="http://c",
        primary_key="k3",
        model="m2",
        fallback_base="http://d",
        fallback_key=None,
        fallback_model="m3",
        wire_api="responses",
        fallback_wire_api="chat",
    )
    assert router.primary_base == "http://c"
    assert router.primary_key == "k3"
    assert router.model == "m2"
    assert router.fallback_base == "http://d"
    assert router.fallback_key is None
    assert router.fallback_model == "m3"
    assert router.wire_api == "responses"
    ok("llm_router.update_config")
except Exception as exc:
    fail("llm_router.update_config", str(exc))

# LLM settings apply
try:
    from core.config import load_config
    from core.runtime import AgentRuntime
    from core.llm_settings import LlmSettingsStore

    td_llm = tempfile.mkdtemp(prefix="akira_llm_apply_")
    os.environ["AKIRA_SKIP_DOTENV"] = "1"
    os.environ["AKIRA_TELEGRAM_TOKEN"] = "test"
    os.environ["AKIRA_PRIMARY_API_BASE"] = "http://localhost:1234/v1"
    os.environ["AKIRA_PRIMARY_API_KEY"] = "testkey"
    os.environ["AKIRA_DATA_DIR"] = td_llm
    os.environ["OPENROUTER_API_KEY"] = "openrouter_env_key"
    os.environ["OPENROUTER_BASE_URL"] = "http://openrouter.example/v1/chat/completions"

    cfg2 = load_config()
    rt = AgentRuntime(cfg2)
    store = LlmSettingsStore(cfg2.data_dir)
    uid = "u1"

    store.set(uid, {"provider": "openrouter", "model": "m1", "openrouter_key": "okey"})
    err = asyncio.run(rt.apply_llm_settings(uid))
    assert err is None
    assert rt.router.primary_base == cfg2.openrouter_base
    assert rt.router.primary_key == "okey"
    assert rt.router.model == "m1"
    assert rt.router.fallback_key is None

    store.set(uid, {"provider": "custom", "model": "m2", "custom_base": "http://custom", "custom_key": "ck"})
    err = asyncio.run(rt.apply_llm_settings(uid))
    assert err is None
    assert rt.router.primary_base == "http://custom"
    assert rt.router.primary_key == "ck"
    assert rt.router.model == "m2"

    store.set(uid, {"provider": "primary", "model": "m3"})
    err = asyncio.run(rt.apply_llm_settings(uid))
    assert err is None
    assert rt.router.primary_base == cfg2.primary_api_base
    assert rt.router.primary_key == cfg2.primary_api_key
    assert rt.router.model == "m3"
    ok("llm_settings.apply")
except Exception as exc:
    fail("llm_settings.apply", str(exc))


# Async tests
async def test_n8n():
    from core.tools.n8n import save_workflow, import_workflow, save_and_import_workflow

    td = tempfile.mkdtemp(prefix="akira_n8n_")
    path = save_workflow("test_workflow", {"nodes": []}, td, mode="full")
    assert path.endswith(".json")
    err = await import_workflow({"nodes": []}, None, None, mode="full")
    assert "ERROR" in err
    resp = await save_and_import_workflow("test_workflow2", {"nodes": []}, td, None, None, mode="full")
    assert "ERROR" in resp


async def test_browser():
    from core.tools.browser import BrowserTool

    bt = BrowserTool(headless=True)
    await bt.goto("data:text/html,<html><title>ok</title><body>hello</body></html>")
    html = await bt.content()
    assert "hello" in html
    await bt.close()


async def test_browser_proxy():
    from core.tools.browser import BrowserTool

    bt = BrowserTool(headless=True)
    await bt.set_proxy("socks5://127.0.0.1:9050")
    await bt.set_proxy(None)
    await bt.close()


async def test_mcp_time():
    from core.mcp_client import MCPManager

    mgr = MCPManager(roots=[os.getcwd()])
    tools = await mgr.list_tools("time")
    assert tools and hasattr(tools, "tools")
    await mgr.close_all()


async def test_mcp_roots_spaces():
    from core.tools.registry import ToolRegistry

    reg = ToolRegistry(mode="full", mcp_roots=[os.getcwd()])
    resp = await reg.execute("mcp_set_roots", {"roots": r"C:\Program Files;C:\Windows"})
    assert resp == "OK"


async def test_mcp_safe_mode():
    from core.tools.registry import ToolRegistry

    reg = ToolRegistry(mode="safe", mcp_roots=[os.getcwd()])
    resp = await reg.execute("mcp_call", {"server": "time", "tool": "time", "args": {}})
    assert resp == "ERROR: MCP disabled in safe mode. Set AKIRA_MODE=full."
    resp = await reg.execute("mcp_set_roots", {"roots": os.getcwd()})
    assert resp == "ERROR: MCP disabled in safe mode. Set AKIRA_MODE=full."


async def test_safe_mode_blocks():
    from core.tools.shell import run_command
    from core.tools.process import start_process
    from core.tools.desktop import screenshot

    assert "safe" in run_command("echo hi", mode="safe")
    assert "safe" in start_process("echo hi", mode="safe")
    assert "safe" in screenshot("x.png", mode="safe")


async def test_health_check():
    import json
    from core.tools.registry import ToolRegistry

    td = tempfile.mkdtemp(prefix="akira_health_")
    reg = ToolRegistry(mode="safe", data_dir=td, mcp_roots=[os.getcwd()])
    resp = await reg.execute("health_check", {"auto_heal": False})
    assert isinstance(resp, dict)
    assert "metrics" in resp and "summary" in resp
    path = os.path.join(td, "health_metrics.jsonl")
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        line = f.readline().strip()
    assert line
    obj = json.loads(line)
    assert "memory_percent" in obj


async def test_predictive_plan():
    from core.tools.registry import ToolRegistry
    from core.memory.episodic import EpisodicMemory
    from core.memory import EnhancedMemoryStore

    td = tempfile.mkdtemp(prefix="akira_plan_")
    store = EnhancedMemoryStore(td, "http://localhost:1234/v1", "testkey", "gpt-4o")
    epi = EpisodicMemory(store)

    epi.start_episode("u1", task="fix bug in code")
    epi.record_event("u1", "edit", "ok", True)
    epi.finish_episode("u1", result="done", success=True)

    epi.start_episode("u1", task="fix bug in code")
    epi.record_event("u1", "edit", "fail", False)
    epi.finish_episode("u1", result="fail", success=False)

    reg = ToolRegistry(mode="safe", data_dir=td, mcp_roots=[os.getcwd()])
    reg.memory = store
    resp = await reg.execute(
        "predictive_plan",
        {
            "task": "fix bug in code",
            "steps": ["open file", "delete system32", "run tests"],
            "user_id": "u1",
            "risk_threshold": 0.7,
        },
    )
    assert isinstance(resp, dict)
    assert "steps" in resp and "removed" in resp and "warnings" in resp and "score" in resp
    assert any("delete" in s for s in resp.get("removed", []))

    resp_empty = await reg.execute(
        "predictive_plan",
        {
            "task": "anything",
            "steps": [],
            "user_id": "",
            "risk_threshold": "bad",
        },
    )
    assert isinstance(resp_empty, dict)
    assert resp_empty.get("steps") == []
    assert resp_empty.get("removed") == []
    assert resp_empty.get("warnings")
    assert "score" in resp_empty

    resp_weird = await reg.execute(
        "predictive_plan",
        {
            "task": "cleanup",
            "steps": [None, 123, "   ", "delete temp files"],
            "user_id": None,
            "risk_threshold": 0.1,
        },
    )
    assert isinstance(resp_weird, dict)
    assert any("delete" in s for s in resp_weird.get("removed", []))


async def test_learning_meta():
    import os as _os
    from core.learning.strategies import Strategy
    from core.learning.meta_learner import MetaLearner

    td = tempfile.mkdtemp(prefix="akira_meta_")
    strategies = [
        Strategy("s1", "Strategy one"),
        Strategy("s2", "Strategy two"),
    ]
    learner = MetaLearner(td, strategies=strategies, base_epsilon=0.0, min_epsilon=0.0)
    for _ in range(5):
        learner.record_outcome("s1", "fix bug in code", True, 50, "u1")
    for _ in range(5):
        learner.record_outcome("s2", "fix bug in code", False, 50, "u1")
    picked = learner.select_strategy("fix bug in code", "u1")
    assert picked.id == "s1"
    assert _os.path.exists(_os.path.join(td, "strategy_stats.json"))

    _os.environ["AKIRA_STRATEGY_AB"] = "s2"
    picked_ab = learner.select_strategy("any task", "u1")
    assert picked_ab.id == "s2"
    _os.environ.pop("AKIRA_STRATEGY_AB", None)


async def test_parallel_reasoning():
    from core.reasoning.parallel import ReasoningResult, ReasoningVariant, ParallelReasoner
    from core.reasoning.judge import MetaJudge

    class StaticRouter:
        async def chat(self, messages):
            return "ok"

    class MixedRouter:
        async def chat(self, messages):
            sys_msg = messages[0].get("content", "")
            if "FAIL" in sys_msg:
                raise RuntimeError("boom")
            if "EMPTY" in sys_msg:
                return "   "
            if "SLOW" in sys_msg:
                await asyncio.sleep(0.05)
                return "late"
            return "risk warning\n- step 1"

    router = StaticRouter()
    variants = [
        ReasoningVariant("a", "A"),
        ReasoningVariant("b", "B"),
    ]
    reasoner = ParallelReasoner(router, max_workers=2, timeout_s=5)
    results = await reasoner.run("task", variants)
    assert len(results) == 2
    judge = MetaJudge(mode="heuristic")
    best = await judge.select_best("task", results)
    assert best in [r.name for r in results]

    tie_results = [
        ReasoningResult("b", "risk warning\n- item", 1),
        ReasoningResult("a", "risk warning\n- item", 1),
    ]
    best_tie = await judge.select_best("task", tie_results)
    assert best_tie == "a"

    mixed = MixedRouter()
    mixed_variants = [
        ReasoningVariant("fail", "FAIL"),
        ReasoningVariant("empty", "EMPTY"),
        ReasoningVariant("good", "GOOD"),
    ]
    reasoner2 = ParallelReasoner(mixed, max_workers=3, timeout_s=1)
    results2 = await reasoner2.run("task", mixed_variants)
    best2 = await judge.select_best("task", results2)
    assert best2 == "good"
    assert next(r for r in results2 if r.name == "fail").error
    assert next(r for r in results2 if r.name == "empty").error

    reasoner3 = ParallelReasoner(mixed, max_workers=1, timeout_s=0.01)
    results3 = await reasoner3.run("task", [ReasoningVariant("slow", "SLOW")])
    assert results3[0].error == "timeout"

    from core.tools.registry import ToolRegistry
    reg = ToolRegistry(mode="safe", mcp_roots=[os.getcwd()])
    reg.router = router
    resp = await reg.execute(
        "parallel_reasoning",
        {"task": "hello", "variants": [], "max_workers": 2, "judge_mode": "heuristic"},
    )
    assert isinstance(resp, dict)
    assert "best" in resp and "candidates" in resp and "best_text" in resp and "error" in resp
    assert resp.get("judge") == "heuristic"
    assert len(resp.get("candidates", [])) == 4
    names = [c.get("name") for c in resp.get("candidates", [])]
    assert set(names) == {"concise", "analytical", "risk_aware", "creative"}
    assert resp.get("best_text")
    assert resp.get("error", "") == ""

    reg2 = ToolRegistry(mode="safe", mcp_roots=[os.getcwd()])
    resp2 = await reg2.execute(
        "parallel_reasoning",
        {"task": "hello", "variants": [], "max_workers": 2, "judge_mode": "heuristic"},
    )
    assert isinstance(resp2, dict)
    assert resp2.get("error")
    assert resp2.get("best") == ""
    assert resp2.get("best_text") == ""
    assert resp2.get("judge") == "heuristic"
    assert resp2.get("candidates") == []


async def main_async():
    await record_async("n8n.save_import", test_n8n())
    await record_async("browser.data_url", test_browser())
    await record_async("browser.proxy", test_browser_proxy())
    await record_async("mcp.time", test_mcp_time(), timeout=30)
    await record_async("mcp.set_roots_spaces", test_mcp_roots_spaces())
    await record_async("mcp.safe_mode", test_mcp_safe_mode())
    await record_async("safe_mode.blocks", test_safe_mode_blocks())
    await record_async("health.check", test_health_check())
    await record_async("planning.predictive", test_predictive_plan())
    await record_async("learning.meta", test_learning_meta())
    await record_async("reasoning.parallel", test_parallel_reasoning())


asyncio.run(main_async())

print("\n=== TEST RESULTS ===")
for name, passed, detail in results:
    print(f"{name}: {'PASS' if passed else 'FAIL'} {'' if passed else detail}")
