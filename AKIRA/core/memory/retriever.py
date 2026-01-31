"""
Memory Retriever for AKIRA 2.0
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import OrderedDict


class SearchType(Enum):
    """Search type enum."""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"


@dataclass
class SearchResult:
    """Search result entry."""
    content: str
    source: str
    score: float
    metadata: Dict[str, Any]


class MemoryRetriever:
    """Memory retriever with semantic/keyword/hybrid search and LRU cache."""

    def __init__(self, memory_store, mem0_client=None, cache_size: int = 128):
        self.store = memory_store
        self.mem0 = mem0_client or getattr(memory_store, "mem0", None)
        self.cache_size = max(1, cache_size)
        self._cache: OrderedDict[Tuple[str, str, str, int], List[Dict[str, Any]]] = OrderedDict()
        self.cache_hits = 0
        self.cache_misses = 0
        self.semantic_calls = 0
        self.keyword_calls = 0

    def search(
        self,
        query: str,
        user_id: str = "default",
        search_type: SearchType = SearchType.HYBRID,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        if isinstance(search_type, str):
            try:
                search_type = SearchType(search_type)
            except Exception:
                search_type = SearchType.HYBRID
        cache_key = (query, user_id, search_type.value, limit)
        if cache_key in self._cache:
            self.cache_hits += 1
            self._cache.move_to_end(cache_key)
            return self._cache[cache_key]

        self.cache_misses += 1
        if search_type == SearchType.SEMANTIC:
            results = self._semantic_search(query, user_id, limit, allow_fallback=True)
        elif search_type == SearchType.KEYWORD:
            results = self._keyword_search(query, user_id, limit)
        else:
            results = self._hybrid_search(query, user_id, limit)

        results = self._deduplicate(results)
        results.sort(key=lambda x: x.score, reverse=True)
        packed = [self._result_to_dict(r) for r in results[:limit]]
        self._cache[cache_key] = packed
        if len(self._cache) > self.cache_size:
            self._cache.popitem(last=False)
        return packed

    def _semantic_search(
        self,
        query: str,
        user_id: str,
        limit: int,
        allow_fallback: bool = True,
    ) -> List[SearchResult]:
        if not self.mem0:
            return self._keyword_search(query, user_id, limit) if allow_fallback else []
        try:
            self.semantic_calls += 1
            response = self.mem0.search(query, user_id=user_id, limit=limit)
            memories = response.get("results", [])
            return [
                SearchResult(
                    content=m.get("memory", ""),
                    source="mem0",
                    score=m.get("score", 0.5),
                    metadata={"id": m.get("id")},
                )
                for m in memories if m.get("memory")
            ]
        except Exception:
            return self._keyword_search(query, user_id, limit) if allow_fallback else []

    def _keyword_search(self, query: str, user_id: str, limit: int) -> List[SearchResult]:
        results: List[SearchResult] = []
        self.keyword_calls += 1

        try:
            episodes = self.store.get_similar_episodes(query, limit, user_id=user_id)
        except TypeError:
            episodes = self.store.get_similar_episodes(query, limit)
        for ep in episodes:
            results.append(SearchResult(
                content=f"Task: {ep.task}\nResult: {ep.result}",
                source="episodes",
                score=0.7 if ep.success else 0.3,
                metadata={"id": ep.id, "success": ep.success},
            ))

        try:
            facts = self.store.search_facts(query, user_id, limit=limit)
        except Exception:
            facts = self.store.get_facts(user_id)
            q = query.lower()
            facts = [f for f in facts if q in f.get("key", "").lower() or q in f.get("value", "").lower()]
        for fact in facts:
            results.append(SearchResult(
                content=f"{fact.get('key', '')}: {fact.get('value', '')}",
                source="facts",
                score=fact.get("confidence", 0.5),
                metadata={"category": fact.get("category")},
            ))

        try:
            patterns = self.store.search_patterns(query, user_id=user_id, limit=limit)
        except Exception:
            patterns = []
        for pattern in patterns:
            score = pattern.success_rate if pattern.success_rate is not None else 0.4
            results.append(SearchResult(
                content=f"Pattern: {pattern.name}\n{pattern.description}",
                source="patterns",
                score=score,
                metadata={"task_type": pattern.task_type},
            ))

        try:
            projects = self.store.search_projects(query, user_id=user_id, limit=limit)
        except Exception:
            projects = []
        for project in projects:
            title = project.name or project.path
            results.append(SearchResult(
                content=f"Project: {title}\nPath: {project.path}",
                source="projects",
                score=0.4,
                metadata={"path": project.path},
            ))

        try:
            lessons = self.store.search_lessons(query, user_id=user_id, limit=limit)
        except Exception:
            lessons = []
        for lesson in lessons:
            results.append(SearchResult(
                content=f"Lesson: {lesson.get('error_type', '')}\n{lesson.get('solution', '')}",
                source="lessons",
                score=0.4,
                metadata={"error_type": lesson.get("error_type")},
            ))

        return results

    def _hybrid_search(self, query: str, user_id: str, limit: int) -> List[SearchResult]:
        results = []
        results.extend(self._semantic_search(query, user_id, limit, allow_fallback=False))
        results.extend(self._keyword_search(query, user_id, limit))
        return results

    def _deduplicate(self, results: List[SearchResult]) -> List[SearchResult]:
        seen = set()
        unique: List[SearchResult] = []
        for r in results:
            key = r.content[:100]
            if key not in seen:
                seen.add(key)
                unique.append(r)
        return unique

    @staticmethod
    def _result_to_dict(result: SearchResult) -> Dict[str, Any]:
        return {
            "content": result.content,
            "memory": result.content,
            "source": result.source,
            "score": result.score,
            "metadata": result.metadata,
        }

