"""Enhanced memory store for AKIRA 2.0 (ASCII only)."""

import os
import json
import sqlite3
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from .indexer import ProjectIndexer

try:
    from mem0 import Memory
except Exception:
    Memory = None


class MemoryType(Enum):
    """Memory types."""
    INTERACTION = "interaction"
    EPISODE = "episode"
    PATTERN = "pattern"
    PROJECT = "project"
    FACT = "fact"
    LESSON = "lesson"


@dataclass
class Episode:
    """Episode record."""
    id: Optional[int] = None
    user_id: str = "default"
    task: str = ""
    plan: str = ""
    actions: str = ""  # JSON list of actions
    result: str = ""
    success: bool = False
    error: Optional[str] = None
    duration_sec: float = 0.0
    created_at: str = ""
    updated_at: str = ""
    tags: str = ""  # JSON list of tags


@dataclass
class Pattern:
    """Pattern record."""
    id: Optional[int] = None
    user_id: str = "default"
    name: str = ""
    description: str = ""
    task_type: str = ""  # coding, browser, search, etc.
    trigger: str = ""  #  
    strategy: str = ""  # JSON 
    success_rate: float = 0.0
    usage_count: int = 0
    created_at: str = ""
    updated_at: str = ""
    tags: str = ""  # JSON list of tags


@dataclass
class Project:
    """Project metadata."""
    id: Optional[int] = None
    user_id: str = "default"
    path: str = ""
    name: str = ""
    tech_stack: str = ""  # JSON list
    structure: str = ""  # JSON 
    entry_points: str = ""  # JSON  
    dependencies: str = ""  # JSON 
    indexed_at: str = ""
    fingerprint: str = ""
    file_count: int = 0
    total_lines: int = 0
    created_at: str = ""
    updated_at: str = ""
    tags: str = ""  # JSON list of tags


class EnhancedMemoryStore:
    """Enhanced memory store."""

    def __init__(
        self,
        data_dir: str,
        primary_api_base: str,
        primary_api_key: str,
        model: str
    ):
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, "akira_memory.db")
        self._init_sqlite()

        #  Mem0   
        self.mem0 = None
        if Memory is not None:
            self._init_mem0(primary_api_base, primary_api_key, model)

    def _init_mem0(self, api_base: str, api_key: str, model: str):
        """ Mem0  ChromaDB"""
        try:
            os.environ.setdefault("MEM0_DIR", os.path.join(self.data_dir, "mem0"))
            os.environ.setdefault("OPENAI_API_KEY", api_key)
            os.environ.setdefault("OPENAI_BASE_URL", api_base)

            config = {
                "history_db_path": os.path.join(self.data_dir, "mem0_history.db"),
                "llm": {
                    "provider": "openai",
                    "config": {
                        "api_key": api_key,
                        "openai_base_url": api_base,
                        "model": model,
                    },
                },
                "embedder": {
                    "provider": "openai",
                    "config": {
                        "api_key": api_key,
                        "openai_base_url": api_base,
                        "model": "text-embedding-3-small",
                        "embedding_dims": 1536,
                    },
                },
                "vector_store": {
                    "provider": "chroma",
                    "config": {
                        "path": os.path.join(self.data_dir, "chroma"),
                        "collection_name": "akira_mem",
                    },
                },
            }
            self.mem0 = Memory.from_config(config)
        except Exception:
            self.mem0 = None

    
    def _mem0_add_text(self, user_id: str, mem_type: str, source_id: str, text: str):
        if not self.mem0 or not text:
            return
        content_hash = hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()
        conn = sqlite3.connect(self.db_path)
        try:
            existing = conn.execute(
                "SELECT content_hash FROM mem0_index WHERE user_id = ? AND mem_type = ? AND source_id = ?",
                (user_id, mem_type, source_id),
            ).fetchone()
            if existing and existing[0] == content_hash:
                return
            try:
                self.mem0.add([{"role": "assistant", "content": text}], user_id=user_id)
            except Exception:
                return
            now = datetime.utcnow().isoformat()
            if existing:
                conn.execute(
                    "UPDATE mem0_index SET content_hash = ?, created_at = ? "
                    "WHERE user_id = ? AND mem_type = ? AND source_id = ?",
                    (content_hash, now, user_id, mem_type, source_id),
                )
            else:
                conn.execute(
                    "INSERT INTO mem0_index (user_id, mem_type, source_id, content_hash, created_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (user_id, mem_type, source_id, content_hash, now),
                )
            conn.commit()
        except Exception:
            pass
        finally:
            conn.close()

    def _ensure_columns(self, conn: sqlite3.Connection, table: str, columns: List[str]):
        existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
        for ddl in columns:
            name = ddl.split()[0]
            if name not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")

    def _init_sqlite(self):
        """ SQLite   """
        os.makedirs(self.data_dir, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        try:
            #   ()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            #  
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    task TEXT NOT NULL,
                    plan TEXT,
                    actions TEXT,
                    result TEXT,
                    success INTEGER DEFAULT 0,
                    error TEXT,
                    duration_sec REAL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    tags TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS episode_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    episode_id INTEGER NOT NULL,
                    related_episode_id INTEGER NOT NULL,
                    relation TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    created_at TEXT NOT NULL
                )
            """)

            #  
            conn.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL DEFAULT 'default',
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    task_type TEXT,
                    trigger TEXT,
                    strategy TEXT,
                    success_rate REAL DEFAULT 0,
                    usage_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    tags TEXT
                )
            """)

            #  
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL DEFAULT 'default',
                    path TEXT NOT NULL UNIQUE,
                    name TEXT,
                    tech_stack TEXT,
                    structure TEXT,
                    entry_points TEXT,
                    dependencies TEXT,
                    indexed_at TEXT,
                    fingerprint TEXT,
                    file_count INTEGER DEFAULT 0,
                    total_lines INTEGER DEFAULT 0,
                    created_at TEXT,
                    updated_at TEXT,
                    tags TEXT
                )
            """)

            #   ( )
            conn.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    category TEXT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    source TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    tags TEXT
                )
            """)

            #   (  )
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    episode_id INTEGER,
                    user_id TEXT NOT NULL DEFAULT 'default',
                    error_type TEXT,
                    cause TEXT,
                    solution TEXT,
                    prevention TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    tags TEXT,
                    FOREIGN KEY (episode_id) REFERENCES episodes(id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS mem0_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    mem_type TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            #    
            # Ensure new columns exist for older databases.
            self._ensure_columns(conn, "episodes", [
                "user_id TEXT DEFAULT 'default'",
                "created_at TEXT",
                "updated_at TEXT",
                "tags TEXT",
            ])
            self._ensure_columns(conn, "episode_links", [
                "user_id TEXT",
                "episode_id INTEGER",
                "related_episode_id INTEGER",
                "relation TEXT",
                "confidence REAL DEFAULT 1.0",
                "created_at TEXT",
            ])
            self._ensure_columns(conn, "patterns", [
                "user_id TEXT DEFAULT 'default'",
                "created_at TEXT",
                "updated_at TEXT",
                "tags TEXT",
            ])
            self._ensure_columns(conn, "projects", [
                "user_id TEXT DEFAULT 'default'",
                "name TEXT",
                "tech_stack TEXT",
                "structure TEXT",
                "entry_points TEXT",
                "dependencies TEXT",
                "indexed_at TEXT",
                "fingerprint TEXT",
                "file_count INTEGER DEFAULT 0",
                "total_lines INTEGER DEFAULT 0",
                "created_at TEXT",
                "updated_at TEXT",
                "tags TEXT",
            ])
            self._ensure_columns(conn, "facts", [
                "user_id TEXT DEFAULT 'default'",
                "category TEXT",
                "value TEXT",
                "confidence REAL DEFAULT 1.0",
                "source TEXT",
                "created_at TEXT",
                "updated_at TEXT",
                "tags TEXT",
            ])
            self._ensure_columns(conn, "lessons", [
                "user_id TEXT DEFAULT 'default'",
                "created_at TEXT",
                "updated_at TEXT",
                "tags TEXT",
            ])
            self._ensure_columns(conn, "mem0_index", [
                "user_id TEXT",
                "mem_type TEXT",
                "source_id TEXT",
                "content_hash TEXT",
                "created_at TEXT",
            ])

            conn.execute("CREATE INDEX IF NOT EXISTS idx_episodes_user ON episodes(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_episodes_success ON episodes(success)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_patterns_user ON patterns(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(task_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_facts_user ON facts(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_facts_category ON facts(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_lessons_user ON lessons(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_lessons_error ON lessons(error_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_episode_links_user ON episode_links(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_episode_links_episode ON episode_links(episode_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_episode_links_related ON episode_links(related_episode_id)")
            conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_episode_links_unique "
                "ON episode_links(user_id, episode_id, related_episode_id, relation)"
            )
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_mem0_unique "
                         "ON mem0_index(user_id, mem_type, source_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_mem0_hash "
                         "ON mem0_index(user_id, content_hash)")

            conn.commit()
        finally:
            conn.close()

    # ==================== INTERACTIONS ====================

    def add_turn(self, user_id: str, user_text: str, assistant_text: str):
        """  """
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

        #    
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
        """    """
        if self.mem0:
            try:
                results = self.mem0.search(query, user_id=user_id, limit=limit)
                memories = results.get("results", [])
                return [{"memory": m.get("memory", "")} for m in memories if m.get("memory")]
            except Exception:
                pass

        # SQLite fallback
        conn = sqlite3.connect(self.db_path)
        try:
            rows = conn.execute(
                "SELECT role, content FROM interactions WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (user_id, limit * 2),
            ).fetchall()
            return [{"memory": f"{role}: {content}"} for role, content in rows[::-1]]
        finally:
            conn.close()

    # ==================== EPISODES ====================

    def save_episode(self, episode: Episode) -> int:
        """  """
        now = datetime.utcnow().isoformat()
        created_at = episode.created_at or now
        updated_at = episode.updated_at or now
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                """INSERT INTO episodes
                   (user_id, task, plan, actions, result, success, error, duration_sec, created_at, updated_at, tags)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    episode.user_id,
                    episode.task,
                    episode.plan,
                    episode.actions,
                    episode.result,
                    1 if episode.success else 0,
                    episode.error,
                    episode.duration_sec,
                    created_at,
                    updated_at,
                    episode.tags,
                ),
            )
            conn.commit()
            row_id = cursor.lastrowid
            text = f"Episode: {episode.task}\nPlan: {episode.plan}\nResult: {episode.result}\nSuccess: {episode.success}"
            if episode.error:
                text += f"\nError: {episode.error}"
            self._mem0_add_text(episode.user_id, "episode", f"episode:{row_id}", text)
            return row_id
        finally:
            conn.close()

    def get_similar_episodes(
        self,
        task: str,
        limit: int = 5,
        user_id: Optional[str] = None,
    ) -> List[Episode]:
        """?????????? ?????????????? ?????????????? ???? ????????????"""
        conn = sqlite3.connect(self.db_path)
        try:
            words = task.lower().split()[:5]
            if not words:
                return []
            conditions = " OR ".join(["task LIKE ?" for _ in words])
            params = [f"%{w}%" for w in words]
            if user_id:
                rows = conn.execute(
                    f"""SELECT id, user_id, task, plan, actions, result, success,
                               error, duration_sec, created_at, updated_at, tags
                        FROM episodes
                        WHERE user_id = ? AND ({conditions})
                        ORDER BY success DESC, created_at DESC LIMIT ?""",
                    [user_id] + params + [limit],
                ).fetchall()
            else:
                rows = conn.execute(
                    f"""SELECT id, user_id, task, plan, actions, result, success,
                               error, duration_sec, created_at, updated_at, tags
                        FROM episodes WHERE {conditions}
                        ORDER BY success DESC, created_at DESC LIMIT ?""",
                    params + [limit],
                ).fetchall()
            return [self._row_to_episode(row) for row in rows]
        finally:
            conn.close()

    def get_recent_episodes(self, user_id: str, limit: int = 50) -> List[Episode]:
        """Return recent episodes for a user."""
        conn = sqlite3.connect(self.db_path)
        try:
            rows = conn.execute(
                """SELECT id, user_id, task, plan, actions, result, success,
                          error, duration_sec, created_at, updated_at, tags
                   FROM episodes WHERE user_id = ?
                   ORDER BY id DESC LIMIT ?""",
                (user_id, limit),
            ).fetchall()
            return [self._row_to_episode(row) for row in rows]
        finally:
            conn.close()

    def link_episodes(
        self,
        user_id: str,
        episode_id: int,
        related_episode_id: int,
        relation: str,
        confidence: float = 1.0,
    ) -> None:
        """Create a link between episodes."""
        now = datetime.utcnow().isoformat()
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """INSERT OR IGNORE INTO episode_links
                   (user_id, episode_id, related_episode_id, relation, confidence, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, episode_id, related_episode_id, relation, confidence, now),
            )
            conn.commit()
        finally:
            conn.close()

    def get_episode_links(self, user_id: str, episode_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch episode links for a given episode."""
        conn = sqlite3.connect(self.db_path)
        try:
            rows = conn.execute(
                """SELECT related_episode_id, relation, confidence, created_at
                   FROM episode_links
                   WHERE user_id = ? AND episode_id = ?
                   ORDER BY id DESC LIMIT ?""",
                (user_id, episode_id, limit),
            ).fetchall()
            return [
                {
                    "related_episode_id": row[0],
                    "relation": row[1],
                    "confidence": row[2],
                    "created_at": row[3],
                }
                for row in rows
            ]
        finally:
            conn.close()

    def get_episode_chain(self, user_id: str, start_episode_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Return a simple chain following latest links."""
        chain: List[Dict[str, Any]] = []
        current = start_episode_id
        visited = set()
        while current and len(chain) < limit and current not in visited:
            visited.add(current)
            conn = sqlite3.connect(self.db_path)
            try:
                row = conn.execute(
                    """SELECT related_episode_id, relation, confidence, created_at
                       FROM episode_links
                       WHERE user_id = ? AND episode_id = ?
                       ORDER BY id DESC LIMIT 1""",
                    (user_id, current),
                ).fetchone()
            finally:
                conn.close()
            if not row:
                break
            link = {
                "episode_id": current,
                "related_episode_id": row[0],
                "relation": row[1],
                "confidence": row[2],
                "created_at": row[3],
            }
            chain.append(link)
            current = row[0]
        return chain

    def _row_to_episode(self, row) -> Episode:
        """Convert DB row to Episode."""
        return Episode(
            id=row[0], user_id=row[1], task=row[2], plan=row[3],
            actions=row[4], result=row[5], success=bool(row[6]),
            error=row[7], duration_sec=row[8], created_at=row[9], updated_at=row[10], tags=row[11],
        )

    # ==================== PATTERNS ====================

    def save_pattern(self, pattern: Pattern) -> int:
        """  """
        now = datetime.utcnow().isoformat()
        created_at = pattern.created_at or now
        updated_at = pattern.updated_at or now
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                """INSERT OR REPLACE INTO patterns
                   (user_id, name, description, task_type, trigger, strategy,
                    success_rate, usage_count, created_at, updated_at, tags)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (pattern.user_id, pattern.name, pattern.description, pattern.task_type,
                 pattern.trigger, pattern.strategy, pattern.success_rate,
                 pattern.usage_count, created_at, updated_at, pattern.tags),
            )
            conn.commit()
            row_id = cursor.lastrowid
            text = (
                f"Pattern: {pattern.name}\n{pattern.description}\n"
                f"Task type: {pattern.task_type}\nTrigger: {pattern.trigger}\n"
                f"Strategy: {pattern.strategy}"
            )
            self._mem0_add_text(pattern.user_id, "pattern", f"pattern:{pattern.name}", text)
            return row_id
        finally:
            conn.close()

    def get_patterns_for_task(self, task_type: str) -> List[Pattern]:
        """    """
        conn = sqlite3.connect(self.db_path)
        try:
            rows = conn.execute(
                """SELECT id, user_id, name, description, task_type, trigger, strategy,
                          success_rate, usage_count, created_at, updated_at, tags
                   FROM patterns WHERE task_type = ?
                   ORDER BY success_rate DESC""",
                (task_type,),
            ).fetchall()
            return [self._row_to_pattern(row) for row in rows]
        finally:
            conn.close()

    def _row_to_pattern(self, row) -> Pattern:
        return Pattern(
            id=row[0], user_id=row[1], name=row[2], description=row[3], task_type=row[4],
            trigger=row[5], strategy=row[6], success_rate=row[7],
            usage_count=row[8], created_at=row[9], updated_at=row[10], tags=row[11],
        )

    def search_patterns(self, query: str, user_id: Optional[str] = None, limit: int = 5) -> List[Pattern]:
        """Keyword search for patterns by text fields."""
        conn = sqlite3.connect(self.db_path)
        try:
            q = f"%{query}%"
            if user_id:
                rows = conn.execute(
                    """SELECT id, user_id, name, description, task_type, trigger, strategy,
                              success_rate, usage_count, created_at, updated_at, tags
                       FROM patterns
                       WHERE user_id = ? AND (
                         name LIKE ? OR description LIKE ? OR trigger LIKE ? OR strategy LIKE ?
                       )
                       ORDER BY success_rate DESC, usage_count DESC LIMIT ?""",
                    (user_id, q, q, q, q, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT id, user_id, name, description, task_type, trigger, strategy,
                              success_rate, usage_count, created_at, updated_at, tags
                       FROM patterns
                       WHERE name LIKE ? OR description LIKE ? OR trigger LIKE ? OR strategy LIKE ?
                       ORDER BY success_rate DESC, usage_count DESC LIMIT ?""",
                    (q, q, q, q, limit),
                ).fetchall()
            return [self._row_to_pattern(row) for row in rows]
        finally:
            conn.close()


    # ==================== PROJECTS ====================

    def index_project(self, path: str, user_id: str = "default") -> Project:
        indexer = ProjectIndexer()
        meta = indexer.index_project(path)
        project = Project(
            user_id=user_id,
            path=meta.path,
            name=meta.name,
            tech_stack=json.dumps(meta.tech_stack),
            structure=json.dumps(meta.structure),
            entry_points=json.dumps(meta.entry_points),
            dependencies=json.dumps(meta.dependencies),
            indexed_at=meta.indexed_at,
            fingerprint=meta.fingerprint,
            file_count=meta.file_count,
            total_lines=meta.total_lines,
        )
        self.save_project(project)
        return project

    def save_project(self, project: Project) -> int:
        """  """
        now = datetime.utcnow().isoformat()
        created_at = project.created_at or now
        updated_at = project.updated_at or now
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                """INSERT OR REPLACE INTO projects
                   (user_id, path, name, tech_stack, structure, entry_points,
                    dependencies, indexed_at, fingerprint, file_count, total_lines,
                    created_at, updated_at, tags)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (project.user_id, project.path, project.name, project.tech_stack,
                 project.structure, project.entry_points, project.dependencies,
                 project.indexed_at or now, project.fingerprint, project.file_count,
                 project.total_lines, created_at, updated_at, project.tags),
            )
            conn.commit()
            row_id = cursor.lastrowid
            title = project.name or project.path
            text = f"Project: {title}\nPath: {project.path}\nTech: {project.tech_stack}"
            self._mem0_add_text(project.user_id, "project", f"project:{project.path}", text)
            return row_id
        finally:
            conn.close()

    def get_project(self, path: str) -> Optional[Project]:
        """   """
        conn = sqlite3.connect(self.db_path)
        try:
            row = conn.execute(
                """SELECT id, user_id, path, name, tech_stack, structure,
                          entry_points, dependencies, indexed_at, fingerprint,
                          file_count, total_lines, created_at, updated_at, tags
                   FROM projects WHERE path = ?""",
                (path,),
            ).fetchone()
            return self._row_to_project(row) if row else None
        finally:
            conn.close()

    def _row_to_project(self, row) -> Project:
        return Project(
            id=row[0], user_id=row[1], path=row[2], name=row[3], tech_stack=row[4],
            structure=row[5], entry_points=row[6], dependencies=row[7],
            indexed_at=row[8], fingerprint=row[9], file_count=row[10], total_lines=row[11],
            created_at=row[12], updated_at=row[13], tags=row[14],
        )

    def search_projects(self, query: str, user_id: Optional[str] = None, limit: int = 5) -> List[Project]:
        """Keyword search for projects by path/name/metadata."""
        conn = sqlite3.connect(self.db_path)
        try:
            q = f"%{query}%"
            if user_id:
                rows = conn.execute(
                    """SELECT id, user_id, path, name, tech_stack, structure,
                              entry_points, dependencies, indexed_at, fingerprint,
                              file_count, total_lines, created_at, updated_at, tags
                       FROM projects
                       WHERE user_id = ? AND (
                         path LIKE ? OR name LIKE ? OR tech_stack LIKE ? OR structure LIKE ?
                         OR entry_points LIKE ? OR dependencies LIKE ?
                       )
                       ORDER BY updated_at DESC LIMIT ?""",
                    (user_id, q, q, q, q, q, q, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT id, user_id, path, name, tech_stack, structure,
                              entry_points, dependencies, indexed_at, fingerprint,
                              file_count, total_lines, created_at, updated_at, tags
                       FROM projects
                       WHERE path LIKE ? OR name LIKE ? OR tech_stack LIKE ? OR structure LIKE ?
                         OR entry_points LIKE ? OR dependencies LIKE ?
                       ORDER BY updated_at DESC LIMIT ?""",
                    (q, q, q, q, q, q, limit),
                ).fetchall()
            return [self._row_to_project(row) for row in rows]
        finally:
            conn.close()


    # ==================== FACTS ====================

    def save_fact(self, user_id: str, category: str, key: str, value: str,
                  confidence: float = 1.0, source: str = None, tags: str = "") -> int:
        """ """
        now = datetime.utcnow().isoformat()
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                """INSERT INTO facts (user_id, category, key, value,
                   confidence, source, created_at, updated_at, tags)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, category, key, value, confidence, source, now, now, tags),
            )
            conn.commit()
            row_id = cursor.lastrowid
            text = f"Fact ({category}): {key} = {value}"
            self._mem0_add_text(user_id, "fact", f"fact:{user_id}:{category}:{key}", text)
            return row_id
        finally:
            conn.close()

    def get_facts(self, user_id: str, category: str = None) -> List[Dict]:
        """  """
        conn = sqlite3.connect(self.db_path)
        try:
            if category:
                rows = conn.execute(
                    "SELECT key, value, confidence FROM facts WHERE user_id = ? AND category = ?",
                    (user_id, category),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT key, value, confidence FROM facts WHERE user_id = ?",
                    (user_id,),
                ).fetchall()
            return [{"key": r[0], "value": r[1], "confidence": r[2]} for r in rows]
        finally:
            conn.close()

    def search_facts(self, query: str, user_id: str, limit: int = 5) -> List[Dict]:
        """Keyword search for facts by key/value/category."""
        conn = sqlite3.connect(self.db_path)
        try:
            q = f"%{query}%"
            rows = conn.execute(
                """SELECT key, value, confidence, category
                   FROM facts
                   WHERE user_id = ? AND (key LIKE ? OR value LIKE ? OR category LIKE ?)
                   ORDER BY confidence DESC LIMIT ?""",
                (user_id, q, q, q, limit),
            ).fetchall()
            return [
                {"key": r[0], "value": r[1], "confidence": r[2], "category": r[3]}
                for r in rows
            ]
        finally:
            conn.close()


    # ==================== LESSONS ====================

    def save_lesson(self, episode_id: int, error_type: str,
                    cause: str, solution: str, prevention: str,
                    user_id: str = "default", tags: str = "") -> int:
        """   """
        now = datetime.utcnow().isoformat()
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                """INSERT INTO lessons (episode_id, error_type, cause,
                   solution, prevention, created_at, updated_at, user_id, tags)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (episode_id, error_type, cause, solution, prevention, now, now, user_id, tags),
            )
            conn.commit()
            row_id = cursor.lastrowid
            key_hash = hashlib.sha256(
                f"{episode_id}|{error_type}|{cause}|{solution}|{prevention}".encode("utf-8", errors="ignore")
            ).hexdigest()
            text = (
                f"Lesson: {error_type}\nCause: {cause}\n"
                f"Solution: {solution}\nPrevention: {prevention}"
            )
            self._mem0_add_text(user_id, "lesson", f"lesson:{episode_id}:{error_type}:{key_hash}", text)
            return row_id
        finally:
            conn.close()

    def get_lessons(self, error_type: str = None) -> List[Dict]:
        """ """
        conn = sqlite3.connect(self.db_path)
        try:
            if error_type:
                rows = conn.execute(
                    "SELECT error_type, cause, solution, prevention FROM lessons WHERE error_type = ?",
                    (error_type,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT error_type, cause, solution, prevention FROM lessons"
                ).fetchall()
            return [{"error_type": r[0], "cause": r[1], "solution": r[2], "prevention": r[3]} for r in rows]
        finally:
            conn.close()

    def search_lessons(self, query: str, user_id: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """Keyword search for lessons by error/cause/solution/prevention."""
        conn = sqlite3.connect(self.db_path)
        try:
            q = f"%{query}%"
            if user_id:
                rows = conn.execute(
                    """SELECT error_type, cause, solution, prevention
                       FROM lessons
                       WHERE user_id = ? AND (
                         error_type LIKE ? OR cause LIKE ? OR solution LIKE ? OR prevention LIKE ?
                       )
                       ORDER BY created_at DESC LIMIT ?""",
                    (user_id, q, q, q, q, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT error_type, cause, solution, prevention
                       FROM lessons
                       WHERE error_type LIKE ? OR cause LIKE ? OR solution LIKE ? OR prevention LIKE ?
                       ORDER BY created_at DESC LIMIT ?""",
                    (q, q, q, q, limit),
                ).fetchall()
            return [{"error_type": r[0], "cause": r[1], "solution": r[2], "prevention": r[3]} for r in rows]
        finally:
            conn.close()


    # ==================== EXPORT/IMPORT ====================

    def export_json(self, path: str) -> str:
        """    JSON"""
        conn = sqlite3.connect(self.db_path)
        try:
            data = {
                "interactions": conn.execute(
                    "SELECT user_id, role, content, created_at FROM interactions"
                ).fetchall(),
                "episodes": conn.execute(
                    "SELECT * FROM episodes"
                ).fetchall(),
                "patterns": conn.execute(
                    "SELECT * FROM patterns"
                ).fetchall(),
            }
        finally:
            conn.close()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return path
