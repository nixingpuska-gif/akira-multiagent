# TZ to Coder

Title: S11 Self-Modification - analysis + safe patch pipeline (MVP)
Stage: S11 Self-Modification

Goal
- Implement a minimal, safe self-modification pipeline with analysis, patch generation, and approval gating.

Context
- Roadmap expects new modules:
  - core/self_mod/analyzer.py
  - core/self_mod/patcher.py
  - core/self_mod/sandbox.py
  - core/self_mod/approval.py

Scope
In scope:
- Analyzer: accept a target path + issue description, output a structured analysis (files, risk level, suggested actions).
- Patcher: produce unified diff (no auto-apply) and store in data/self_mod/patches/.
- Sandbox: validate diff is ASCII, non-binary, and within allowed roots.
- Approval: require explicit user approval token before apply; store approval log.
- Add minimal tests for each module (no actual patch apply).

Out of scope:
- Automatic code application to repo.
- Running external commands.
- LLM integration for patch generation.

Acceptance criteria
- Analyzer returns structured dict with risk level.
- Patcher produces deterministic diff file path for a given request.
- Sandbox rejects diffs that touch files outside allowed roots.
- Approval requires explicit token and logs decisions.
- Tests pass on Windows.

Constraints
- ASCII only.
- No secrets in repo.
- Do not modify repo files automatically.

Files / modules
- core/self_mod/analyzer.py
- core/self_mod/patcher.py
- core/self_mod/sandbox.py
- core/self_mod/approval.py
- tests/test_self_mod_pipeline.py

Tests
- python C:\Users\Nicita\Desktop\AKIRA\tests\test_self_mod_pipeline.py

Deliverables
- Implemented modules + tests.
- Short report with pass/fail.
