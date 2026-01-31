# TZ to Coder

Title: S13 Control Plane - deliberation + budget + log retention
Stage: S13 Post-Roadmap Enhancements

Goal
- Implement a control plane that enforces: (1) 3-step deliberation for every task, (2) global daily request budget, (3) 90-day log retention.

Context
- Requirement: 10,000 requests/day across the whole system; apply to ALL tasks.
- Requirement: retain logs for 90 days.
- Requirement: 3 internal LLM requests for every user task (threats, plan, first step).

Scope
In scope:
- Deliberation pipeline: 3 internal LLM calls for every task.
  1) Threats/obstacles analysis
  2) 8-10 step plan
  3) Execute step 1 + verify
- Request budget manager:
  - Persist daily counters in data_dir (e.g., data/request_budget.json)
  - Count every LLM call (including internal)
  - Hard stop when limit exceeded; return clear error
- Log retention:
  - Purge JSONL logs older than 90 days in data_dir
  - Apply to prompt_usage.jsonl, approval_log.jsonl, health_metrics.jsonl, and any *.jsonl in data_dir
- Add tests for budget limits, deliberation flow, retention deletion logic.

Out of scope:
- Hidden chain-of-thought storage.
- Network-level telemetry or external log shipping.

Acceptance criteria
- Every task triggers 3 internal LLM calls unless budget exhausted.
- Budget limit enforced (10,000/day) with deterministic error response.
- Logs older than 90 days are deleted; newer logs preserved.
- Tests pass on Windows.

Constraints
- ASCII only.
- No secrets in repo.
- Do not log chain-of-thought.

Files / modules (suggested)
- core/control/deliberation.py
- core/control/budget.py
- core/control/retention.py
- core/runtime.py and/or core/graph_agent.py for integration
- tests/test_control_plane.py

Tests
- python C:\Users\Nicita\Desktop\AKIRA\tests\test_control_plane.py

Deliverables
- Implemented modules + integration + tests.
- Short report with pass/fail and any issues.
