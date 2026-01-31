"""Distributed executor (ASCII only)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .balancer import NodeBalancer
from .nodes import Node, NodeRegistry


@dataclass
class ExecutionResult:
    node_id: str
    status: str
    output: str
    error: str
    finished_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "status": self.status,
            "output": self.output,
            "error": self.error,
            "finished_at": self.finished_at,
        }


class DistributedExecutor:
    def __init__(self, registry: NodeRegistry, balancer: Optional[NodeBalancer] = None) -> None:
        self.registry = registry
        self.balancer = balancer or NodeBalancer()

    def dispatch(self, task: str, required_caps: Optional[List[str]] = None) -> ExecutionResult:
        nodes = self.registry.list_nodes()
        node = self.balancer.select_node(nodes, required_caps=required_caps)
        if not node:
            return ExecutionResult(
                node_id="",
                status="no_node",
                output="",
                error="No suitable node found.",
                finished_at=datetime.utcnow().isoformat(),
            )
        return self._execute_on_node(node, task)

    def _execute_on_node(self, node: Node, task: str) -> ExecutionResult:
        if node.kind == "local":
            output = f"local:{task}"
            return ExecutionResult(
                node_id=node.node_id,
                status="ok",
                output=output,
                error="",
                finished_at=datetime.utcnow().isoformat(),
            )
        return ExecutionResult(
            node_id=node.node_id,
            status="dispatched",
            output="",
            error="",
            finished_at=datetime.utcnow().isoformat(),
        )
