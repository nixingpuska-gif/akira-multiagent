# TZ to Coder

Title: S10 Adaptive Prompts - verification and hardening
Stage: S10 Adaptive Prompts

Goal
- Verify adaptive prompt components (library, tracker, optimizer) and harden edge cases.

Context
- Modules: core/prompts/library.py, adaptive.py, optimizer.py
- Tests: tests/test_prompts_adaptive.py

Scope
In scope:
- Review PromptLibrary behavior (active variant, AB selection).
- Review PromptTracker logging format and safety.
- Review PromptOptimizer selection logic for min_samples and tie-breaks.
- Ensure ASCII-only outputs and no secret leakage.

Out of scope:
- UI/Telegram integration.
- New providers or storage backends.

Acceptance criteria
- PromptLibrary returns default when no variant.
- set_active works and get_prompt returns correct variant.
- AB selection returns one of configured variants.
- PromptTracker writes jsonl with expected keys.
- PromptOptimizer selects best by success rate and respects min_samples.

Constraints
- ASCII only.
- No secrets in repo.

Files / modules
- core/prompts/library.py
- core/prompts/adaptive.py
- core/prompts/optimizer.py
- tests/test_prompts_adaptive.py

Tests
- python C:\Users\Nicita\Desktop\AKIRA\tests\test_prompts_adaptive.py

Deliverables
- Report with pass/fail + any issues.
- If bugs found: fix + tests.
