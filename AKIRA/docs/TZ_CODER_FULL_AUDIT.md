# TZ to Coder

Title: Full Project Audit (Phases 1-14 + S13)
Stage: Audit

Goal
- Perform a deep code audit across all phases starting from Phase 1.

Scope
- Review code for each phase and integration points:
  - Phase 1: core/prompts/__init__.py, core/graph_agent.py, core/tools/registry.py
  - Phase 2: core/memory/* (store/indexer/retriever/compressor)
  - Phase 3: core/memory/episodic.py, patterns.py
  - Phase 4: core/learning/*
  - Phase 5: core/reasoning/* + parallel_reasoning tool
  - Phase 6: core/planning/* + predictive_plan tool
  - Phase 7: core/tools/creator/validator/library
  - Phase 8: core/memory/cross_project.py, pattern_extractor.py
  - Phase 9: core/health/* + health_check tool
  - Phase 10: core/prompts/*
  - Phase 11: core/self_mod/*
  - Phase 12: core/distributed/*
  - S13: core/control/* + integration in llm_router/runtime/graph_agent
  - S14: core/tools/schema.py + terminal_session + workspace + ToolRegistry integration

Tasks
- Validate key contracts and edge cases.
- Confirm no regressions: especially parallel_reasoning router=None schema, budget enforcement, sandbox restrictions.
- Identify any missing items vs ROADMAP or hidden risks.

Deliverable
- Written audit report: PASS/FAIL per phase + risks + proposed fixes.

Constraints
- ASCII only, no secrets in repo.
