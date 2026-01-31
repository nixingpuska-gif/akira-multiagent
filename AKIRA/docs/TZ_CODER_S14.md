# TZ to Coder

Title: S14 Tooling Layer - ToolDefinition + Workspace + Interactive Terminal
Stage: S14 Post-Roadmap Enhancements

Goal
- Implement a standardized tool schema layer, workspace abstraction, and interactive terminal sessions.

Context
- Current tools in core/tools/*.py use direct filesystem/shell calls.
- Need a ToolDefinition layer similar to OpenHands: validated args + stable tool contracts.

Scope
In scope:
1) ToolDefinition schema layer
- Define ToolDefinition dataclass (name, description, args_schema, output_schema optional).
- Provide validate_args() that checks required fields and basic types.
- Provide serialize() for listing tool metadata.
- Add registry method to list tool definitions.

2) Workspace abstraction
- Define Workspace base: list/read/write/exists/realpath.
- Implement LocalWorkspace (no restrictions) and SandboxWorkspace (allowed_roots only).
- Wire fs tools to use workspace (safe mode uses SandboxWorkspace).

3) Interactive terminal
- Implement TerminalSession manager: open/exec/close with session_id.
- Restrict to full mode; safe mode returns error.
- Store sessions in ToolRegistry (session dict).

Out of scope:
- Remote workspace (network).
- Persistence of terminal sessions across restarts.
- UI integration.

Acceptance criteria
- ToolDefinition validates args and returns structured errors.
- SandboxWorkspace blocks access outside allowed roots.
- Terminal sessions work in full mode and are blocked in safe mode.
- Tests pass on Windows.

Constraints
- ASCII only.
- No secrets in repo.
- No background daemons; simple session lifecycle.

Files / modules (suggested)
- core/tools/schema.py
- core/workspace/base.py
- core/workspace/local.py
- core/workspace/sandbox.py
- core/tools/terminal_session.py
- core/tools/registry.py (integration)
- tests/test_tooling_layer.py

Tests
- python C:\Users\Nicita\Desktop\AKIRA\tests\test_tooling_layer.py

Deliverables
- Implemented modules + integration + tests.
- Short report with pass/fail.
