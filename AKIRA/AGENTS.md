# AGENTS.md

Purpose
- Build a long-lived personal AI companion and partner.
- This is stage 1 of a multi-device agent network (PCs/laptops/servers).

Hardware / budget constraints
- RAM: 32 GB
- Storage: 500 GB SSD
- CPU: 2x Xeon E5-2670 v3
- Budget: minimal

LLM providers (OpenAI-compatible)
- Primary endpoint
  - Base URL: https://gpt4.mirbuds.com/codex
  - Env: AKIRA_PRIMARY_API_BASE (set to the URL above)
  - Env: AKIRA_PRIMARY_API_KEY (secret, do not commit)
- Fallback provider
  - OpenRouter base: https://openrouter.ai/api/v1/chat/completions
  - Env: OPENROUTER_API_KEY (secret, do not commit)

Security policy (must follow)
- Never store API keys or tokens in repo files or chat logs.
- Use local environment variables or a local .env file that is git-ignored.
- If running any remote setup scripts, download and inspect first.
- Restrict Telegram access with AKIRA_TELEGRAM_ALLOWLIST.
- Restrict Local UI access with AKIRA_UI_ALLOWLIST.

Operational goals
- Persistent memory (local DB + vector store later).
- Robust fallback when primary endpoint is down.
- Safe tool access (no unrestricted shell).

Runtime modes
- AKIRA_MODE=safe: read-only tools, no process start, no desktop actions (browser allowed).
- AKIRA_MODE=full: full PC control (shell, process, desktop, browser).

Browser proxy
- Optional: AKIRA_BROWSER_PROXY or AKIRA_TOR_PROXY (e.g. socks5://127.0.0.1:9050)

Mini-agents
- n8n agent: generates n8n workflow JSON and can save/import workflows.
- chatdev agent: launches ChatDev workflows from `AKIRA_CHATDEV_PATH`.
  - async runs supported; use jobs_list/jobs_kill to manage.
