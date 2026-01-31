"""Distributed nodes registry (ASCII only)."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Node:
    node_id: str
    name: str
    kind: str
    capabilities: List[str]
    status: str = "online"
    meta: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, str]:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "kind": self.kind,
            "capabilities": ",".join(self.capabilities),
            "status": self.status,
        }


class NodeRegistry:
    def __init__(self) -> None:
        self._nodes: Dict[str, Node] = {}

    @staticmethod
    def make_id(name: str, kind: str, capabilities: List[str]) -> str:
        caps = ",".join(sorted([c.strip().lower() for c in capabilities if c]))
        raw = f"{name}|{kind}|{caps}".encode("utf-8", errors="ignore")
        return hashlib.sha256(raw).hexdigest()[:12]

    def add_node(
        self,
        name: str,
        kind: str,
        capabilities: List[str],
        status: str = "online",
        meta: Optional[Dict[str, str]] = None,
    ) -> Node:
        node_id = self.make_id(name, kind, capabilities)
        node = Node(
            node_id=node_id,
            name=name,
            kind=kind,
            capabilities=[c.strip().lower() for c in capabilities if c],
            status=status,
            meta=meta or {},
        )
        self._nodes[node_id] = node
        return node

    def remove_node(self, node_id: str) -> bool:
        return self._nodes.pop(node_id, None) is not None

    def list_nodes(self) -> List[Node]:
        return [self._nodes[k] for k in sorted(self._nodes.keys())]

    def get_node(self, node_id: str) -> Optional[Node]:
        return self._nodes.get(node_id)

    def set_status(self, node_id: str, status: str) -> bool:
        node = self._nodes.get(node_id)
        if not node:
            return False
        node.status = status
        return True
