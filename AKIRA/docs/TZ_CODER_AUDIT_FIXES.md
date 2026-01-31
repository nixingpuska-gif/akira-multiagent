# TZ for Coder

Title: Audit fixes verification (budget/deliberation/sandbox/workspace/symlink)
Stage: Audit Fixes (post S13/S14)

Goal
- Verify audit fixes are correct and do not introduce regressions.

Context
- Full audit found issues in budget fallback accounting, runtime graph deliberation, self-mod sandbox, workspace roots/paths, and symlink escapes.
- Fixes applied and targeted tests updated.

Scope
In scope:
- Review logic for budget consumption per outbound LLM attempt.
- Ensure runtime graph path enforces deliberation before LLM calls.
- Verify self-mod sandbox blocks secret files (env/keys/aws/ssh).
- Verify SandboxWorkspace resolves relative paths against base root and preserves allowed roots on mode change.
- Ensure cross-project scan skips symlinks and enforces root containment.
Out of scope:
- New features or refactors unrelated to audit findings.

Acceptance criteria
- Budget is consumed per outbound attempt (primary + fallback) and returns error if exceeded.
- Runtime graph uses deliberation pipeline (no bypass).
- Secret file diffs are rejected in self-mod sandbox.
- Safe workspace respects allowed roots and relative paths do not escape.
- Cross-project indexer does not traverse symlinks outside roots.
- Tests pass for updated areas.

Constraints
- Keep stable tool schemas (parallel_reasoning remains dict schema).
- ASCII-only outputs in code paths and tests.

Files / modules
- core/llm_router.py
- core/runtime.py
- core/self_mod/sandbox.py
- core/workspace/sandbox.py
- core/tools/registry.py
- core/memory/cross_project.py
- tests/test_control_plane.py
- tests/test_self_mod_pipeline.py
- tests/test_tooling_layer.py
- tests/test_cross_project_memory.py

Tests
- python C:\Users\Nicita\Desktop\AKIRA\tests\test_control_plane.py
- python C:\Users\Nicita\Desktop\AKIRA\tests\test_self_mod_pipeline.py
- python C:\Users\Nicita\Desktop\AKIRA\tests\test_tooling_layer.py
- python C:\Users\Nicita\Desktop\AKIRA\tests\test_cross_project_memory.py

Deliverables
- Review notes + PASS/FAIL.
- List of any issues or regressions found.
- Suggested fixes if needed.

Quality checklist
- Verify error handling paths.
- Check for path traversal or root escapes.
- Confirm tests align with requirements.
