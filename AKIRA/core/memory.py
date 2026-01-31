import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

try:
    from mem0 import Memory  # type: ignore
except Exception:  # pragma: no cover
    Memory = None


class MemoryStore:
    def __init__(self, data_dir: str, primary_api_base: str, primary_api_key: str, model: str):
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, "akira_memory.db")
        self._init_sqlite()

        self.mem0 = None
        if Memory is not None:
            try:
                os.environ.setdefault("MEM0_DIR", os.path.join(data_dir, "mem0"))
                os.environ.setdefault("OPENAI_API_KEY", primary_api_key)
                os.environ.setdefault("OPENAI_BASE_URL", primary_api_base)

                config = {
                    "history_db_path": os.path.join(data_dir, "mem0_history.db"),
                    "llm": {
                        "provider": "openai",
                        "config": {
                            "api_key": primary_api_key,
                            "openai_base_url": primary_api_base,
                            "model": model,
                        },
                    },
                    "embedder": {
                        "provider": "openai",
                        "config": {
                            "api_key": primary_api_key,
                            "openai_base_url": primary_api_base,
                            "model": "text-embedding-3-small",
                            "embedding_dims": 1536,
                        },
                    },
                    "vector_store": {
                        "provider": "chroma",
                        "config": {
                            "path": os.path.join(data_dir, "chroma"),
                            "collection_name": "akira_mem",
                        },
                    },
                }
                self.mem0 = Memory.from_config(config)
            except Exception:
                # If mem0 init fails, continue with SQLite-only memory.
                self.mem0 = None

    def _init_sqlite(self):
        os.makedirs(self.data_dir, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def add_turn(self, user_id: str, user_text: str, assistant_text: str):
        now = datetime.utcnow().isoformat()
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                "INSERT INTO interactions (user_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (user_id, "user", user_text, now),
            )
            conn.execute(
                "INSERT INTO interactions (user_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (user_id, "assistant", assistant_text, now),
            )
            conn.commit()
        finally:
            conn.close()

        if self.mem0:
            try:
                self.mem0.add(
                    [
                        {"role": "user", "content": user_text},
                        {"role": "assistant", "content": assistant_text},
                    ],
                    user_id=user_id,
                )
            except Exception:
                pass

    def recall(self, user_id: str, query: str, limit: int = 5) -> List[Dict[str, str]]:
        if self.mem0:
            try:
                results = self.mem0.search(query, user_id=user_id, limit=limit)
                memories = results.get("results", [])
                return [{"memory": m.get("memory", "")} for m in memories if m.get("memory")]
            except Exception:
                pass

        # SQLite fallback: last N user/assistant turns
        conn = sqlite3.connect(self.db_path)
        try:
            rows = conn.execute(
                "SELECT role, content FROM interactions WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (user_id, limit * 2),
            ).fetchall()
            return [{"memory": f"{role}: {content}"} for role, content in rows[::-1]]
        finally:
            conn.close()

    def export_json(self, path: str) -> str:
        conn = sqlite3.connect(self.db_path)
        try:
            rows = conn.execute(
                "SELECT user_id, role, content, created_at FROM interactions ORDER BY id ASC"
            ).fetchall()
        finally:
            conn.close()
        data = [
            {"user_id": user_id, "role": role, "content": content, "created_at": created_at}
            for user_id, role, content, created_at in rows
        ]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return path

    def import_json(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        conn = sqlite3.connect(self.db_path)
        try:
            for item in data:
                conn.execute(
                    "INSERT INTO interactions (user_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                    (
                        item.get("user_id", "default"),
                        item.get("role", "user"),
                        item.get("content", ""),
                        item.get("created_at", datetime.utcnow().isoformat()),
                    ),
                )
            conn.commit()
        finally:
            conn.close()
        return "OK"
