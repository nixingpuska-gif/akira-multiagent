# TZ to Tester

Title: S10 Adaptive Prompts - test plan and verification
Stage: S10 Adaptive Prompts

Goal
- Verify adaptive prompt components behave correctly and are stable.

Context
- Modules: core/prompts/library.py, adaptive.py, optimizer.py
- Test: tests/test_prompts_adaptive.py

What to test
- Default prompt fallback when no variants.
- set_active changes selected variant.
- AB selection returns one of enabled variants.
- Optimizer selects best variant and apply_best updates active.
- Tracker writes jsonl entries without errors.

Commands to run
1) python C:\Users\Nicita\Desktop\AKIRA\tests\test_prompts_adaptive.py

Expected results
- Command exits 0 (PASS).
- No exceptions.

Constraints
- Do not add secrets to repo.

Report format
- Short report with PASS/FAIL, failures, and any follow-ups.
