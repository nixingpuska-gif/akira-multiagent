# Stitching Plan (Monorepo)

Goal
- Combine the recommended agent stack into one workspace while keeping each project intact.
- Provide a single root with shared config, orchestration, and a unified run workflow.

Selected repos (vendors/)
- langgraph
- mem0
- chroma
- llama_index
- litellm
- servers (MCP)
- n8n
- composio

Strategy
- Monorepo with a thin integration layer.
- Keep upstream repos unmodified under `vendors/`.
- Build our own orchestration and UI in `apps/` and `core/`.

Planned layout
- apps/telegram_bot        -> existing Telegram bot (entrypoint)
- apps/local_ui            -> simple local web UI
- core/                    -> orchestration, tools, memory, config
- vendors/                 -> upstream repos (read-only)
- docs/                    -> architecture + runbooks

Integration map
- LLM routing: `litellm` proxy or SDK inside core (primary + fallback).
- Agent orchestration: `langgraph` for multi-agent flows.
- Memory: `mem0` for long-term memory + SQLite + Chroma for vectors.
- RAG: `llama_index` for retrieval over local data.
- Tools: MCP servers for files, git, time, fetch, etc.
- Automation: `n8n` optional workflow layer.
- 3rd-party tools: `composio` for 100+ integrations.

Risks / Hotspots
- Mixed tech stacks (Python + Node + Rust + Go).
- License variance (some repos are NOASSERTION/AGPL/Custom).
- Heavy dependency graphs (n8n, chroma, llama_index are large).
- Tool power is high: requires Safe/Full mode controls.

Immediate next steps
1) Create `core/` with config + LLM router + tool layer.
2) Refactor Telegram bot to use the new core.
3) Add simple local UI (FastAPI + minimal HTML).
4) Add memory stack (mem0 + SQLite + Chroma).
5) Add MCP server runner + Safe/Full mode toggle.

