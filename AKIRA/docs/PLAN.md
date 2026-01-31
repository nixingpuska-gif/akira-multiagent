# Plan

## Stage S2: RAG Memory
Goal: Deliver foundational long-term memory with vector search and project indexing.
Owner: Nicita
Due date: 2026-01-28
Status: done (verified 2026-01-26)
Deliverables:
- Extend MemoryStore schema for episodes, patterns, and projects with timestamps/context.
- Implement vector search (ChromaDB collections + semantic search + caching).
- Implement project indexer for repo metadata and auto-reindex on changes.
- Implement context compressor for long dialogs.

Acceptance criteria:
- MemoryStore can create/read episodes, patterns, and projects with timestamps.
- Vector search returns relevant results on a small fixture set (manual verification).
- Project indexing produces metadata for this repo and updates on change (manual verification).
- Context compressor reduces size while preserving key facts (manual spot check).
- End-to-end flow works for at least 3 sample queries (manual effectiveness check).

Tests:
- python -m pytest (or project-specific test command; TBD)
- python -m app.main (optional smoke run; TBD)

Risks:
- Schema migration on existing DB.
- Embedding/model choice affects retrieval quality.
- Indexing large repos could be slow.

Dependencies:
- ChromaDB configured and reachable.
- Embedding provider keys configured.
