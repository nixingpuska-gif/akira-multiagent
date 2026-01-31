# TZ to Coder

Title: S7 Tool Generation - minimal creator/validator/library
Stage: S7 Tool Generation

Goal
- Implement minimal tool generation pipeline: create tool specs, validate them, store in a local library.

Context
- Project: C:\Users\Nicita\Desktop\AKIRA
- Roadmap expects new modules:
  - core/tools/creator.py
  - core/tools/validator.py
  - core/tools/library.py

Scope
In scope:
- Define a simple ToolSpec dataclass (name, description, args_schema, code, created_at, tags).
- Implement ToolCreator to build a tool stub (code template) from ToolSpec.
- Implement ToolValidator to validate spec fields and basic safety checks.
- Implement ToolLibrary to persist tool specs to JSON (data/tools_library.json in data_dir).
- Add minimal tests for create/validate/store/load.

Out of scope:
- Dynamic runtime registration into ToolRegistry.
- Complex security sandboxing.
- UI/Telegram integration.

Acceptance criteria
- ToolValidator rejects invalid names, empty code, or missing args_schema.
- ToolLibrary can add, list, and get tool specs by name.
- ToolCreator produces deterministic stub code (ASCII only).
- Tests pass on Windows.

Constraints
- ASCII only.
- No secrets in repo.
- Do not execute generated code.

Files / modules
- core/tools/creator.py
- core/tools/validator.py
- core/tools/library.py
- tests/test_tools_generation.py

Tests
- python C:\Users\Nicita\Desktop\AKIRA\tests\test_tools_generation.py

Deliverables
- Implemented modules + tests.
- Short report with pass/fail.
