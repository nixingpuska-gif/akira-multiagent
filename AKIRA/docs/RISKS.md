# Risks

- RAG components may be functional but low quality without clear evaluation criteria (level: medium) - owner: Nicita - mitigation: define small fixture set + manual relevance checks.
- Embedding/model choice may reduce retrieval effectiveness (level: medium) - owner: Nicita - mitigation: validate on fixture set and adjust if needed.
- Indexing large repos could be slow or memory heavy (level: medium) - owner: Nicita - mitigation: add incremental indexing and basic caching.
- Phases 5/6/10 appear implemented but are not explicitly confirmed (level: low) - owner: Nicita - mitigation: run focused checks or accept as partial.
- Self-mod sandbox denylist may block legitimate config edits (level: low) - owner: Nicita - mitigation: allowlist safe config paths if needed.
- Relative paths in sandbox resolve to first allowed root; other roots require absolute paths (level: low) - owner: Nicita - mitigation: document usage in tooling notes.
- Symlink skipping may miss projects reachable only via symlink/junction (level: low) - owner: Nicita - mitigation: index real paths explicitly.
