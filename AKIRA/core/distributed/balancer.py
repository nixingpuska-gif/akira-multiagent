"""Distributed node balancer (ASCII only)."""

from __future__ import annotations

from typing import List, Optional

from .nodes import Node


class NodeBalancer:
    def select_node(self, nodes: List[Node], required_caps: Optional[List[str]] = None) -> Optional[Node]:
        caps = [c.strip().lower() for c in (required_caps or []) if c]
        candidates = []
        for node in nodes:
            if node.status != "online":
                continue
            if self._has_caps(node, caps):
                candidates.append(node)
        if not candidates:
            return None
        candidates.sort(key=lambda n: n.node_id)
        return candidates[0]

    @staticmethod
    def _has_caps(node: Node, caps: List[str]) -> bool:
        if not caps:
            return True
        node_caps = set([c.strip().lower() for c in node.capabilities if c])
        return all(c in node_caps for c in caps)
