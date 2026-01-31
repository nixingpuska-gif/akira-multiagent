Runbook (AKIRA)

Roles
- Main agent: owns project direction, writes specs, validates outcomes.
- Coder agent: implements features and fixes bugs per spec.
- Tester agent: prepares test plans, runs checks, reports results.

Env
- Copy .env.example to .env and fill:
  - AKIRA_TELEGRAM_TOKEN
  - AKIRA_TELEGRAM_ALLOWLIST (comma/semicolon-separated Telegram user IDs)
  - AKIRA_UI_ALLOWLIST (IDs for local UI; default 'local')
  - AKIRA_ALLOWLIST_REQUIRED (optional, default true)
    - If true and allowlist is empty, access is denied (deny-by-default)
    - Set to false to allow empty allowlists (legacy behavior)
  - AKIRA_PRIMARY_API_BASE
  - AKIRA_PRIMARY_API_KEY
  - AKIRA_WIRE_API (chat or responses)
  - AKIRA_DOTENV_OVERRIDE (optional, default true)
  - AKIRA_FALLBACK_WIRE_API (chat or responses)
  - AKIRA_FALLBACK_MODEL (optional, model to use on fallback)
  - AKIRA_DISABLE_SAFE_MODE (optional, force full mode)
  - OPENROUTER_API_KEY (optional)
  - AKIRA_MCP_ROOTS (directories MCP filesystem can access)
    - Use ALL for full disk access
    - Use HOME for user profile
    - Or semicolon-separated paths
  - AKIRA_BROWSER_PROXY or AKIRA_TOR_PROXY (optional, e.g. socks5://127.0.0.1:9050)

Telegram bot
1) pip install -r requirements.txt
2) python app/main.py

Telegram menu (LLM settings)
- /menu shows LLM controls:
  - LLM: provider, LLM: model, LLM: key, LLM: base, LLM: status, LLM: reset
- Keys and per-user settings are stored in data/llm_settings.json (gitignored).
- LLM status masks keys and shows provider/model/base. Do not store secrets in repo.
- Use /cancel (or /menu) to stop a pending input.

Local UI
1) pip install -r requirements.txt
2) uvicorn apps.local_ui.main:app --host 127.0.0.1 --port 8000
3) Local UI is restricted to localhost. Use Telegram for remote access.

Allowlist behavior
- "*" in allowlist grants access to all subjects.
- Empty allowlist denies access when AKIRA_ALLOWLIST_REQUIRED=true.

Modes
- Safe: AKIRA_MODE=safe (default, browser allowed)
- Full: AKIRA_MODE=full (full PC control)

Wire API
- chat: OpenAI-compatible /v1/chat/completions
- responses: OpenAI Responses API (/responses or /v1/responses, SSE)
Fallback wire API
- If primary fails, fallback uses AKIRA_FALLBACK_WIRE_API (default chat)

Disable safe mode
- Set AKIRA_DISABLE_SAFE_MODE=true to force full mode and hide safe switch in UI.

MCP servers
- MCP tools use stdio servers:
  - time: `mcp_server_time`
  - fetch: `mcp_server_fetch`
  - git: `mcp_server_git`
  - filesystem: `@modelcontextprotocol/server-filesystem` (requires Node)
- Dynamic MCP:
  - Tool: mcp_register_server {name, command, args, cwd, env}
  - Tool: mcp_set_roots {roots}

ChatDev
- Path: AKIRA_CHATDEV_PATH
- Tool: chatdev_run {prompt, workflow_path, project_name}
- Tool: chatdev_run_async {prompt, workflow_path, project_name}
- Jobs: jobs_list, jobs_kill {job_id}
- Workflows list: chatdev_list_workflows
- Make sure ChatDev deps are installed in that repo (see ChatDev requirements.txt)

n8n
- Tool: n8n_save_workflow {name, content} (saves JSON locally)
- Tool: n8n_import_workflow {content} (requires N8N_API_BASE + N8N_API_KEY)
- Tool: n8n_save_and_import {name, content} (save + import in one step)

Browser
- Uses Playwright (chromium). Ensure Playwright browsers are installed.
- Optional proxy:
  - Set AKIRA_BROWSER_PROXY or AKIRA_TOR_PROXY
  - Or call browser_set_proxy {proxy} / browser_clear_proxy {}

Tor (optional)
- Install Tor Browser or Tor service and expose a SOCKS proxy.
- Default Tor SOCKS port on Windows is often 9050:
  - socks5://127.0.0.1:9050

Health check tool
- Tool: health_check {auto_heal: bool}
- Writes metrics to data/health_metrics.jsonl

Adaptive prompts
- Prompt library: data/prompt_library.json (variants + active/AB)
- Usage log: data/prompt_usage.jsonl (per-request tracking, ASCII only)

Predictive planning tool
- Tool: predictive_plan {task, steps, user_id, risk_threshold}
- Returns filtered steps, removed steps, warnings, and score.

Parallel reasoning tool
- Tool: parallel_reasoning {task, variants, max_workers, judge_mode}
- Returns stable dict schema:
  - best: selected variant name (string, may be empty)
  - best_text: synthesized response (string, may be empty)
  - judge: judge mode (string)
  - candidates: list of results
  - error: non-empty string when router missing or no valid candidates

Meta learning (strategies)
- Stats file: data/strategy_stats.json
- Env: AKIRA_STRATEGY_AB="s1,s2" to enable equal A/B selection
- Epsilon-greedy uses base_epsilon / sqrt(total_samples+1)
