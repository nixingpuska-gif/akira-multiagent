# Multi-Agent Orchestrator

This folder contains an automated 50-agent system with 30 parallel workers.

## Setup

1) Create a virtual environment (optional)
2) Install dependencies:
```
pip install -r automation/requirements.txt
```
3) Copy env file:
```
copy .env.example .env
```
4) Edit .env with API keys and optional base URLs.

## Run
```
python automation/orchestrator.py --config automation/config.yaml
```

## Output
- Task queue: `.claude/tasks/auto-queue.json`
- Agent logs: `.claude/agents/*.md`
- Task outputs: `.claude/tasks/auto-output/`

## Notes
- Update `automation/config.yaml` to change models or providers.
- For Codex/Responses API use `CODEX_API_KEY` and `CODEX_BASE_URL` (see `.env.example`).
- `automation/queue_seed.json` defines initial tasks; edit if needed.
