import json
import os
from typing import Any, Dict, List


def load_or_seed_queue(queue_path: str, seed_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(queue_path):
        os.makedirs(os.path.dirname(queue_path), exist_ok=True)
        with open(seed_path, "r", encoding="utf-8") as handle:
            seed_data = json.load(handle)
        with open(queue_path, "w", encoding="utf-8") as handle:
            json.dump(seed_data, handle, ensure_ascii=False, indent=2)
        return seed_data

    with open(queue_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_queue(queue_path: str, tasks: List[Dict[str, Any]]) -> None:
    with open(queue_path, "w", encoding="utf-8") as handle:
        json.dump(tasks, handle, ensure_ascii=False, indent=2)


def get_ready_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ready = [t for t in tasks if t.get("status") == "inbox"]
    return sorted(ready, key=lambda t: (t.get("priority", 99), t.get("id")))


def update_task_status(tasks: List[Dict[str, Any]], task_id: str, status: str) -> None:
    for task in tasks:
        if task.get("id") == task_id:
            task["status"] = status
            return
