import json
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    from core.prompts.library import PromptLibrary
    from core.prompts.adaptive import PromptTracker
    from core.prompts.optimizer import PromptOptimizer

    td = tempfile.mkdtemp(prefix="akira_prompts_")

    # PromptLibrary basic behavior
    lib = PromptLibrary(td)
    text, vid = lib.get_prompt("test_prompt", "DEFAULT")
    assert text == "DEFAULT"
    assert vid == "default"

    v1 = lib.add_variant("test_prompt", "A")
    v2 = lib.add_variant("test_prompt", "B")
    lib.set_active("test_prompt", v1)
    text2, vid2 = lib.get_prompt("test_prompt", "DEFAULT")
    assert text2 == "A"
    assert vid2 == v1

    # PromptTracker + PromptOptimizer
    tracker = PromptTracker(td)
    tracker.record("test_prompt", v1, "u1", True, latency_ms=10)
    tracker.record("test_prompt", v1, "u1", True, latency_ms=12)
    tracker.record("test_prompt", v2, "u1", False, latency_ms=20)

    usage_path = os.path.join(td, "prompt_usage.jsonl")
    assert os.path.exists(usage_path)
    with open(usage_path, "r", encoding="utf-8") as f:
        line = f.readline().strip()
    line.encode("ascii")
    obj = json.loads(line)
    for key in (
        "timestamp",
        "prompt_id",
        "variant_id",
        "user_id",
        "success",
        "latency_ms",
        "error",
        "task",
    ):
        assert key in obj

    optimizer = PromptOptimizer(tracker, lib)
    best = optimizer.select_best("test_prompt", min_samples=1)
    assert best == v1
    best_none = optimizer.select_best("test_prompt", min_samples=10)
    assert best_none is None
    applied = optimizer.apply_best("test_prompt", min_samples=1)
    assert applied == v1
    text3, vid3 = lib.get_prompt("test_prompt", "DEFAULT")
    assert text3 == "A"
    assert vid3 == v1

    # AB selection behavior (non-deterministic, validate membership)
    v3 = lib.add_variant("test_ab", "X")
    v4 = lib.add_variant("test_ab", "Y")
    lib.enable_ab("test_ab", [v3, v4])
    text4, vid4 = lib.get_prompt("test_ab", "DEFAULT")
    assert vid4 in (v3, v4)
    assert text4 in ("X", "Y")

    # Optimizer tie-break (deterministic by variant id)
    v5 = lib.add_variant("test_tie", "T1")
    v6 = lib.add_variant("test_tie", "T2")
    tracker.record("test_tie", v5, "u1", True, latency_ms=5)
    tracker.record("test_tie", v5, "u1", False, latency_ms=5)
    tracker.record("test_tie", v6, "u1", True, latency_ms=5)
    tracker.record("test_tie", v6, "u1", False, latency_ms=5)
    best_tie = optimizer.select_best("test_tie", min_samples=2)
    assert best_tie == min(v5, v6)


if __name__ == "__main__":
    main()
