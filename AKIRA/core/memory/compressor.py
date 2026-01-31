"""
Context Compressor for AKIRA 2.0
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class CompressedContext:
    """Compressed conversation context."""
    summary: str
    key_facts: List[str]
    important_decisions: List[str]
    token_count: int


class ContextCompressor:
    """Heuristic compressor without external dependencies."""

    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens

    def compress(self, messages: List[Dict], max_tokens: int | None = None) -> CompressedContext:
        if not messages:
            return CompressedContext("", [], [], 0)

        budget = self.max_tokens if max_tokens is None else max_tokens
        key_facts = self._extract_key_facts(messages)
        decisions = self._extract_decisions(messages)
        summary = self._create_summary(messages, key_facts, decisions, budget)
        token_count = self._estimate_tokens(summary)
        return CompressedContext(summary, key_facts, decisions, token_count)

    def _extract_lines(self, messages: List[Dict]) -> List[str]:
        lines: List[str] = []
        for msg in messages:
            content = str(msg.get("content", ""))
            for line in content.split("\n"):
                line = line.strip()
                if line:
                    lines.append(line[:300])
        return lines

    def _extract_key_facts(self, messages: List[Dict]) -> List[str]:
        facts: List[str] = []
        seen = set()
        keywords = [
            "prefer", "preference", "like", "dislike", "want", "need", "needs",
            "require", "requirement", "must", "should", "only", "avoid",
            "path", "env", "token", "id", "version", "api", "url", "host", "port"
        ]
        for line in self._extract_lines(messages):
            lower = line.lower()
            is_kv = ":" in line and len(line.split(":", 1)[0]) <= 40
            if is_kv or any(k in lower for k in keywords):
                if line not in seen:
                    seen.add(line)
                    facts.append(line)
        return facts[:20]

    def _extract_decisions(self, messages: List[Dict]) -> List[str]:
        decisions: List[str] = []
        seen = set()
        markers = [
            "decision", "decided", "choose", "chose", "will use", "use ",
            "approved", "we will", "plan to", "set to", "switch to",
            "must", "should", "do not", "dont", "avoid", "never",
            "constraint", "requirement", "error", "failed", "issue", "bug"
        ]
        for line in self._extract_lines(messages):
            lower = line.lower()
            if any(m in lower for m in markers):
                if line not in seen:
                    seen.add(line)
                    decisions.append(line)
        return decisions[:15]

    def _create_summary(
        self,
        messages: List[Dict],
        key_facts: List[str],
        decisions: List[str],
        max_tokens: int,
    ) -> str:
        parts: List[str] = []
        if decisions:
            parts.append("Decisions: " + "; ".join(decisions[:6]))
        if key_facts:
            parts.append("Facts: " + "; ".join(key_facts[:8]))
        if not parts:
            tail = []
            for msg in messages[-5:]:
                role = msg.get("role", "")
                content = str(msg.get("content", ""))[:200]
                tail.append(f"{role}: {content}")
            parts.append("\n".join(tail))
        summary = "\n".join(parts)
        summary = self._truncate_to_tokens(summary, max_tokens)
        if not summary.strip():
            fallback = str(messages[-1].get("content", ""))
            summary = self._truncate_to_tokens(fallback, max_tokens)
        return summary.strip()

    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        if max_tokens <= 0:
            return ""
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text
        trimmed = text[:max_chars].rstrip()
        if " " in trimmed:
            trimmed = trimmed.rsplit(" ", 1)[0]
        return trimmed

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        return len(text) // 4

