# TZ to Tester

Title: S8 Cross-Project Memory - test plan and verification
Stage: S8 Cross-Project Memory

Goal
- Verify cross-project indexing and pattern extraction.

Context
- Modules: core/memory/cross_project.py, core/memory/pattern_extractor.py
- Test: tests/test_cross_project_memory.py

What to test
- Indexing with multiple roots (including invalid path) does not crash.
- Projects are stored and searchable.
- Pattern extraction returns expected aggregates on fixture data.

Commands to run
1) python C:\Users\Nicita\Desktop\AKIRA\tests\test_cross_project_memory.py

Expected results
- PASS, exit 0.

Constraints
- No secrets in repo.

Report format
- Short report with PASS/FAIL and any issues.
