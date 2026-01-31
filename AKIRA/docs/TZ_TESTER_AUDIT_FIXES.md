# TZ for Tester

Title: Audit fixes regression check
Stage: Audit Fixes (post S13/S14)

Goal
- Verify that the audit fixes pass all targeted tests without errors.

Context
- Fixes applied in budget accounting, runtime deliberation, self-mod sandbox, workspace roots/paths, and cross-project symlink handling.

What to test
- Control plane budget fallback counting.
- Self-mod sandbox secret denylist.
- Sandbox workspace relative path resolution and root preservation.
- Cross-project symlink skip behavior.

Commands to run
1) python C:\Users\Nicita\Desktop\AKIRA\tests\test_control_plane.py
2) python C:\Users\Nicita\Desktop\AKIRA\tests\test_self_mod_pipeline.py
3) python C:\Users\Nicita\Desktop\AKIRA\tests\test_tooling_layer.py
4) python C:\Users\Nicita\Desktop\AKIRA\tests\test_cross_project_memory.py

Expected results
- All commands PASS (exit 0) with no exceptions.

Constraints
- Do not modify code during testing.
- Report warnings if any appear.

Report format
- Summary with PASS/FAIL per command.
- Any errors or anomalies.
- Optional follow-ups.
