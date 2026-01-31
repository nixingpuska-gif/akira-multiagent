import asyncio
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


async def main():
    from core.tools.registry import ToolRegistry

    reg = ToolRegistry(mode="safe", mcp_roots=[os.getcwd()])
    resp = await reg.execute(
        "parallel_reasoning",
        {"task": "hello", "variants": [], "max_workers": 2, "judge_mode": "heuristic"},
    )

    assert isinstance(resp, dict)
    assert resp.get("error"), "Expected error when router is missing"
    assert resp.get("best") == ""
    assert resp.get("best_text") == ""
    assert resp.get("judge") == "heuristic"
    assert resp.get("candidates") == []


if __name__ == "__main__":
    asyncio.run(main())
