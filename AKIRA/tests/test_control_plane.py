import asyncio
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


class BudgetedRouter:
    def __init__(self, budget):
        self.budget = budget
        self.calls = 0

    async def chat(self, messages):
        result = self.budget.consume(1)
        if not result.get("ok", False):
            return result.get("error", "ERROR: request budget exceeded.")
        self.calls += 1
        return "ok"


def main():
    from core.control.budget import RequestBudget
    from core.control.deliberation import DeliberationPipeline
    from core.control.retention import LogRetention
    import core.llm_router as llm_router
    from core.llm_router import LLMRouter

    td = tempfile.mkdtemp(prefix="akira_control_")

    # Budget basic behavior
    budget = RequestBudget(td, limit_per_day=3)
    assert budget.consume(1).get("ok") is True
    assert budget.consume(1).get("ok") is True
    assert budget.consume(1).get("ok") is True
    res = budget.consume(1)
    assert res.get("ok") is False
    assert "budget exceeded" in res.get("error", "")

    # Budget counts fallback calls (2 attempts for one chat)
    llm_router.litellm = None

    class FallbackRouter(LLMRouter):
        def __init__(self, budget):
            super().__init__(
                model="test",
                fallback_model="test",
                primary_base="http://primary",
                primary_key="k1",
                fallback_base="http://fallback",
                fallback_key="k2",
                timeout_s=1.0,
                wire_api="chat",
                fallback_wire_api="chat",
                budget_manager=budget,
            )
            self.calls = 0

        async def _post_chat(self, client, url, key, messages, model=None):
            err = self._consume_budget()
            if err:
                return err
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("primary failed")
            return "ok"

    td_fb = tempfile.mkdtemp(prefix="akira_control_fb_")
    budget_fb = RequestBudget(td_fb, limit_per_day=2)
    router_fb = FallbackRouter(budget_fb)
    resp = asyncio.run(router_fb.chat([{"role": "user", "content": "hi"}]))
    assert resp == "ok"
    assert budget_fb.remaining() == 0

    # Deliberation flow uses 3 internal calls
    budget2 = RequestBudget(td, limit_per_day=10)
    router = BudgetedRouter(budget2)
    pipeline = DeliberationPipeline(router)
    result = asyncio.run(pipeline.run("test task"))
    assert result.get("ok") is True
    assert router.calls == 3

    # Retention: remove old lines, keep recent
    log_path = os.path.join(td, "prompt_usage.jsonl")
    old_ts = (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=100)).isoformat()
    new_ts = (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)).isoformat()
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({"timestamp": old_ts, "msg": "old"}, ensure_ascii=True) + "\n")
        f.write(json.dumps({"timestamp": new_ts, "msg": "new"}, ensure_ascii=True) + "\n")
    retention = LogRetention(td, days=90)
    retention.purge()
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert any("new" in line for line in lines)
    assert not any("old" in line for line in lines)


if __name__ == "__main__":
    main()
