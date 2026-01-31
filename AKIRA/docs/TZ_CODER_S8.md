# TZ to Coder

Title: S8 Cross-Project Memory - indexing + pattern extraction
Stage: S8 Cross-Project Memory

Goal
- Implement cross-project indexing and pattern extraction across multiple project roots.

Context
- Existing: core/memory/indexer.py (ProjectIndexer), core/memory/store.py (projects table).
- Roadmap expects:
  - core/memory/cross_project.py
  - core/memory/pattern_extractor.py

Scope
In scope:
- Implement CrossProjectIndex to scan multiple roots and index projects via ProjectIndexer.
- Use MemoryStore to store per-project metadata (reusing projects table) and keep a lightweight cross-project cache (JSON) in data_dir.
- Implement PatternExtractor to compute aggregated patterns (top languages, tech stacks, common deps).
- Add cross-project search by name/path/tech stack.
- Add minimal tests for indexing and pattern extraction.

Out of scope:
- Distributed indexing.
- Heavy semantic search across all files.
- UI/Telegram integration.

Acceptance criteria
- Indexing accepts a list of roots and skips missing/invalid paths with warnings.
- Re-indexing uses fingerprint to avoid duplicate work where possible.
- PatternExtractor returns deterministic summary on fixed inputs.
- Tests pass on Windows.

Constraints
- ASCII only.
- No secrets in repo.
- Do not scan massive directories by default; include ignore list or depth limits.

Files / modules
- core/memory/cross_project.py
- core/memory/pattern_extractor.py
- tests/test_cross_project_memory.py

Tests
- python C:\Users\Nicita\Desktop\AKIRA\tests\test_cross_project_memory.py

Deliverables
- Implemented modules + tests.
- Short report with pass/fail.
