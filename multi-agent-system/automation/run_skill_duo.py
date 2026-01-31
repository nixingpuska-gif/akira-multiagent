import argparse
import asyncio
import os
import sys
from pathlib import Path

from utils import load_env
from providers import openai_responses


PROMPTS = {
    "komunikator": [
        ("Komunikator-A (Plan/Docs)", ".claude/prompts/komunikator-plan.md"),
        ("Komunikator-B (Audit/Risks)", ".claude/prompts/komunikator-audit.md"),
    ],
    "koder": [
        ("Koder-A (Implementation)", ".claude/prompts/koder-impl.md"),
        ("Koder-B (Review/Risks)", ".claude/prompts/koder-review.md"),
    ],
}


def load_codex_config() -> dict:
    config_path = Path.home() / ".codex" / "config.toml"
    if not config_path.exists():
        return {}
    try:
        import tomllib
    except Exception:
        return {}
    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    provider_name = data.get("model_provider")
    providers = data.get("model_providers", {})
    provider_cfg = providers.get(provider_name, {}) if provider_name else {}
    return {
        "base_url": provider_cfg.get("base_url"),
        "api_key_env": provider_cfg.get("env_key"),
        "model": data.get("model"),
    }


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def build_messages(system_prompt: str, task_text: str, project_spec: str) -> list:
    parts = [
        "?? ????????? ? ?????????????? ?????? (2 ??????).",
        "??????? ?? ????, ????????????????, ? markdown.",
        "",
        "??????:",
        task_text,
    ]
    if project_spec:
        parts += ["", "???????? ???????:", project_spec]
    user_content = "
".join(parts)
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]


async def run_pair(args) -> int:
    load_env()
    codex_cfg = load_codex_config()

    base_url = args.base_url or os.getenv("CODEX_BASE_URL") or codex_cfg.get("base_url")
    if not base_url:
        raise RuntimeError("Base URL not found. Set CODEX_BASE_URL or configure ~/.codex/config.toml")

    api_key_env = args.api_key_env or codex_cfg.get("api_key_env") or "CODEX_API_KEY"
    api_key = os.getenv(api_key_env)
    if not api_key:
        raise RuntimeError(f"Missing API key in env: {api_key_env}")

    model = args.model or codex_cfg.get("model") or "gpt-5.2-codex"
    request_cfg = {
        "endpoint": args.endpoint,
        "model": model,
        "temperature": args.temperature,
        "max_output_tokens": args.max_output_tokens,
        "extra": {},
    }

    task_text = ""
    if args.task_file:
        task_text = load_text(Path(args.task_file))
    elif args.task:
        task_text = args.task.strip()
    else:
        task_text = "
".join([line for line in sys.stdin.read().splitlines() if line.strip()])
    if not task_text:
        raise RuntimeError("Task text is empty. Provide --task or --task-file or stdin.")

    project_spec = ""
    if args.project_spec:
        project_spec = load_text(Path(args.project_spec))

    prompt_entries = PROMPTS.get(args.skill)
    if not prompt_entries:
        raise RuntimeError("Unknown skill. Use komunikator or koder.")

    async def run_one(label: str, prompt_path: str):
        system_prompt = load_text(Path(prompt_path))
        messages = build_messages(system_prompt, task_text, project_spec)
        result = await openai_responses.complete(base_url, api_key, request_cfg, messages)
        return label, result.strip()

    tasks = [run_one(label, path) for label, path in prompt_entries]
    results = await asyncio.gather(*tasks)

    out_dir = Path(args.out_dir) if args.out_dir else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    for label, text in results:
        print(f"
# {label}
")
        print(text)
        if out_dir:
            safe_name = label.lower().replace(" ", "-").replace("/", "-")
            (out_dir / f"{args.skill}-{safe_name}.md").write_text(text + "
", encoding="utf-8")

    return 0


def parse_args():
    parser = argparse.ArgumentParser(description="Run 2-agent pair for komunikator or koder.")
    parser.add_argument("--skill", choices=["komunikator", "koder"], required=True)
    parser.add_argument("--task", help="Task text (quoted)")
    parser.add_argument("--task-file", help="Path to file with task text")
    parser.add_argument("--project-spec", help="Optional project spec file")
    parser.add_argument("--out-dir", help="Optional output directory for agent answers")
    parser.add_argument("--base-url", help="Override base URL (default: ~/.codex/config.toml)")
    parser.add_argument("--api-key-env", help="API key env var name (default: CODEX_API_KEY)")
    parser.add_argument("--model", help="Model name (default from codex config)")
    parser.add_argument("--endpoint", default="/responses", help="Responses API endpoint")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-output-tokens", type=int, default=1800)
    return parser.parse_args()


if __name__ == "__main__":
    import sys
    args = parse_args()
    try:
        raise SystemExit(asyncio.run(run_pair(args)))
    except Exception as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1)
