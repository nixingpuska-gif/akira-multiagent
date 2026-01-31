# TZ to Tester

Title: S13 Control Plane - test plan and verification
Stage: S13 Post-Roadmap Enhancements

Goal
- Verify deliberation pipeline, request budget enforcement, and 90-day log retention.

Context
- Modules: core/control/deliberation.py, core/control/budget.py, core/control/retention.py
- Test: tests/test_control_plane.py

What to test
- Deliberation: 3 internal steps invoked for a task (threats/plan/step1).
- Budget: enforce 10,000/day limit; correct error when exceeded.
- Retention: logs older than 90 days are deleted, newer logs remain.

Commands to run
1) python C:\Users\Nicita\Desktop\AKIRA\tests\test_control_plane.py

Expected results
- PASS, exit 0.

Constraints
- No secrets in repo.

Report format
- Short report with PASS/FAIL and any issues.
