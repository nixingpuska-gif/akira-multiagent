import argparse
import asyncio
import datetime as dt
import json
import os
from collections import defaultdict
from typing import Any, Dict, List

from agent_registry import build_agents
from task_queue import get_ready_tasks, load_or_seed_queue, save_queue, update_task_status
from utils import ensure_dir, load_env, load_yaml_config
from providers import openai_compat, openai_responses, anthropic

PROVIDER_MAP = {
    "openai_compat": openai_compat.complete,
    "openai_responses": openai_responses.complete,
    "anthropic": anthropic.complete,
}


def load_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def load_project_spec(path: str, base_dir: str) -> str:
    if not path:
        return ""
    if not os.path.isabs(path):
        path = os.path.join(base_dir, path)
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def build_messages(system_prompt: str, task: Dict[str, Any], project_spec: str) -> List[Dict[str, str]]:
    user_content = [
        "You are working inside a multi-agent system.",
        "Produce actionable output in markdown.",
        "",
        "Project Spec:",
        project_spec,
        "",
        f"Task ID: {task.get('id')}",
        f"Task Title: {task.get('title')}",
    ]
    notes = task.get("notes")
    if notes:
        user_content.append(f"Notes: {notes}")
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "\n".join(user_content)},
    ]


def resolve_provider(config: Dict[str, Any], provider_name: str):
    provider_cfg = config["providers"][provider_name]
    provider_type = provider_cfg.get("type", "openai_compat")
    fn = PROVIDER_MAP.get(provider_type)
    if not fn:
        raise ValueError(f"Unsupported provider type: {provider_type}")
    return fn, provider_cfg


def agent_state_path(state_dir: str, agent_name: str) -> str:
    safe_name = agent_name.replace("/", "_")
    return os.path.join(state_dir, f"{safe_name}.md")


def output_path(output_dir: str, task_id: str, agent_name: str) -> str:
    safe_name = agent_name.replace("/", "_")
    return os.path.join(output_dir, f"{task_id}_{safe_name}.md")


async def run_task(
    semaphore: asyncio.Semaphore,
    config: Dict[str, Any],
    task: Dict[str, Any],
    agent: Dict[str, Any],
    project_spec: str,
    state_dir: str,
    output_dir: str,
) -> Dict[str, Any]:
    async with semaphore:
        system_prompt = load_prompt(agent["system_prompt"])
        messages = build_messages(system_prompt, task, project_spec)

        fn, provider_cfg = resolve_provider(config, agent["provider"])
        api_key_env = provider_cfg.get("api_key_env")
        api_key = os.getenv(api_key_env or "")
        if not api_key:
            raise RuntimeError(f"Missing API key env: {api_key_env}")
        base_url = provider_cfg.get("base_url", "")
        request_cfg = provider_cfg.get("request", {})

        result_text = await fn(base_url, api_key, request_cfg, messages)

        timestamp = dt.datetime.utcnow().isoformat()
        result = {
            "task": task,
            "agent": agent,
            "timestamp": timestamp,
            "result": result_text,
        }

        ensure_dir(output_dir)
        out_path = output_path(output_dir, task["id"], agent["name"])
        with open(out_path, "w", encoding="utf-8") as handle:
            handle.write(f"# {task['id']} - {task['title']}\n")
            handle.write(f"Agent: {agent['name']}\n")
            handle.write(f"Role: {agent['role']}\n")
            handle.write(f"Timestamp: {timestamp}\n\n")
            handle.write(result_text)
            handle.write("\n")

        ensure_dir(state_dir)
        state_path = agent_state_path(state_dir, agent["name"])
        with open(state_path, "a", encoding="utf-8") as handle:
            handle.write(f"\n## {timestamp} - {task['id']} {task['title']}\n")
            handle.write(result_text)
            handle.write("\n")

        return result


async def run_orchestrator(config_path: str) -> None:
    load_env()
    config = load_yaml_config(config_path)

    root_dir = os.path.abspath(os.path.join(os.path.dirname(config_path), ".."))
    queue_path = config["queue_path"]
    if not os.path.isabs(queue_path):
        queue_path = os.path.join(root_dir, queue_path)
    seed_path = os.path.join(os.path.dirname(config_path), "queue_seed.json")
    tasks = load_or_seed_queue(queue_path, seed_path)

    agents = build_agents(config)
    agents_by_role = defaultdict(list)
    for agent in agents:
        agents_by_role[agent["role"]].append(agent)

    project_spec = load_project_spec(config.get("project_spec", ""), root_dir)

    ready_tasks = get_ready_tasks(tasks)
    if not ready_tasks:
        print("No tasks in inbox.")
        return

    semaphore = asyncio.Semaphore(int(config.get("max_concurrency", 10)))
    state_dir = config["state_dir"]
    if not os.path.isabs(state_dir):
        state_dir = os.path.join(root_dir, state_dir)
    output_dir = config["output_dir"]
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(root_dir, output_dir)

    role_index: Dict[str, int] = defaultdict(int)
    running = []

    for task in ready_tasks:
        role = task.get("role")
        candidates = agents_by_role.get(role)
        if not candidates:
            candidates = agents
        idx = role_index[role] % len(candidates)
        agent = candidates[idx]
        role_index[role] += 1

        update_task_status(tasks, task["id"], "in_progress")
        save_queue(queue_path, tasks)

        task_future = asyncio.create_task(
            run_task(
                semaphore,
                config,
                task,
                agent,
                project_spec,
                state_dir,
                output_dir,
            )
        )
        task_future.set_name(task["id"])
        task_future.task_id = task["id"]
        running.append(task_future)

    for coro in asyncio.as_completed(running):
        try:
            result = await coro
            update_task_status(tasks, result["task"]["id"], "completed")
        except Exception as exc:
            task_id = getattr(coro, "task_id", None)
            if not task_id and hasattr(coro, "get_name"):
                task_id = coro.get_name()
            if not task_id:
                task_id = "unknown"
            if isinstance(exc, RuntimeError):
                print(str(exc))
            update_task_status(tasks, task_id, "blocked")
        finally:
            save_queue(queue_path, tasks)


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-agent orchestrator")
    parser.add_argument(
        "--config",
        default="automation/config.yaml",
        help="Path to config.yaml",
    )
    args = parser.parse_args()

    asyncio.run(run_orchestrator(args.config))


if __name__ == "__main__":
    main()
