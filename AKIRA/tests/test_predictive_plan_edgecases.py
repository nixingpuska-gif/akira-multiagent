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
        "predictive_plan",
        {
            "task": "do risky things",
            "steps": "not-a-list",
            "user_id": None,
            "risk_threshold": "bad",
        },
    )
    assert isinstance(resp, dict)
    assert "steps" in resp and "removed" in resp and "warnings" in resp and "score" in resp
    assert isinstance(resp.get("warnings"), list)
    assert any("risk_threshold" in w for w in resp.get("warnings", []))

    resp2 = await reg.execute(
        "predictive_plan",
        {
            "task": "cleanup",
            "steps": [" ", None, 123, "delete system32"],
            "user_id": "",
            "risk_threshold": 2,
        },
    )
    assert isinstance(resp2, dict)
    assert "steps" in resp2 and "removed" in resp2 and "warnings" in resp2 and "score" in resp2
    assert any("risk_threshold" in w for w in resp2.get("warnings", []))
    assert any("Removed risky step" in w for w in resp2.get("warnings", []))


if __name__ == "__main__":
    asyncio.run(main())
