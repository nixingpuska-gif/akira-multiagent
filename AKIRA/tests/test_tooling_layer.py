import asyncio
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    from core.tools.schema import ToolDefinition
    from core.workspace.sandbox import SandboxWorkspace
    from core.tools.registry import ToolRegistry

    # ToolDefinition validation
    tdef = ToolDefinition(
        name="t",
        description="desc",
        args_schema={
            "properties": {"path": {"type": "string"}, "count": {"type": "integer"}},
            "required": ["path"],
        },
    )
    res = tdef.validate_args({"path": "x", "count": 2})
    assert res.get("ok") is True
    res2 = tdef.validate_args({"count": "bad"})
    assert res2.get("ok") is False

    # SandboxWorkspace blocks outside roots
    td = tempfile.mkdtemp(prefix="akira_ws_")
    ws = SandboxWorkspace(allowed_roots=[td])
    inside = os.path.join(td, "a.txt")
    with open(inside, "w", encoding="utf-8") as f:
        f.write("ok")
    assert ws.read(inside) == "ok"
    assert ws.read("a.txt") == "ok"
    blocked = False
    try:
        ws.read(os.path.join(os.path.dirname(td), "outside.txt"))
    except Exception:
        blocked = True
    assert blocked is True

    # ToolRegistry definitions list
    reg = ToolRegistry(mode="safe", mcp_roots=[td], data_dir=td)
    defs = reg.list_tool_definitions()
    names = [d.get("name") for d in defs]
    assert "fs_list" in names and "terminal_open" in names

    # ToolRegistry preserves workspace roots across mode changes
    td2 = tempfile.mkdtemp(prefix="akira_ws2_")
    inside2 = os.path.join(td2, "b.txt")
    with open(inside2, "w", encoding="utf-8") as f:
        f.write("ok2")
    reg2 = ToolRegistry(mode="full", mcp_roots=[td, td2], data_dir=td)
    reg2.set_mode("safe")
    resp2 = asyncio.run(reg2.execute("fs_read", {"path": inside2}))
    assert "ok2" in str(resp2)

    # Terminal sessions (safe blocked, full allowed)
    resp_safe = asyncio.run(reg.execute("terminal_open", {}))
    assert "ERROR" in str(resp_safe)

    reg_full = ToolRegistry(mode="full", mcp_roots=[td], data_dir=td)
    resp = asyncio.run(reg_full.execute("terminal_open", {}))
    session_id = resp.get("session_id")
    assert session_id
    out = asyncio.run(reg_full.execute("terminal_exec", {"session_id": session_id, "command": "echo hello"}))
    assert out.get("status") == "ok"
    assert "hello" in out.get("output", "")
    close_resp = asyncio.run(reg_full.execute("terminal_close", {"session_id": session_id}))
    assert "OK" in str(close_resp)


if __name__ == "__main__":
    main()
