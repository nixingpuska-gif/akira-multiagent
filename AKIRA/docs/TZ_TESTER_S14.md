# TZ to Tester

Title: S14 Tooling Layer - test plan and verification
Stage: S14 Post-Roadmap Enhancements

Goal
- Verify ToolDefinition schema, Workspace abstraction, and interactive terminal sessions.

Context
- Modules: core/tools/schema.py, core/workspace/*, core/tools/terminal_session.py, core/tools/registry.py
- Test: tests/test_tooling_layer.py

What to test
- ToolDefinition validates required args and returns structured errors.
- SandboxWorkspace blocks paths outside allowed roots.
- LocalWorkspace allows normal read/write.
- Terminal sessions open/exec/close in full mode; blocked in safe mode.

Commands to run
1) python C:\Users\Nicita\Desktop\AKIRA\tests\test_tooling_layer.py

Expected results
- PASS, exit 0.

Constraints
- No secrets in repo.

Report format
- Short report with PASS/FAIL and any issues.
