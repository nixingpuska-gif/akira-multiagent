"""SwarmController - Distributed system coordination for multi-node deployment."""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class NodeStatus(Enum):
    """Node status states."""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"


@dataclass
class SwarmNode:
    """Represents a node in the swarm."""
    node_id: str
    hostname: str
    ip_address: str
    status: NodeStatus = NodeStatus.OFFLINE
    capabilities: List[str] = field(default_factory=list)
    current_task: Optional[str] = None
    last_heartbeat: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "current_task": self.current_task,
            "last_heartbeat": self.last_heartbeat,
            "metadata": self.metadata
        }


class SwarmController:
    """
    Distributed swarm controller for multi-node coordination.

    Manages:
    - Node registration and discovery
    - Task distribution
    - Load balancing
    - Fault tolerance
    - State synchronization
    """

    def __init__(self, node_id: str, is_master: bool = False):
        self.node_id = node_id
        self.is_master = is_master
        self.nodes: Dict[str, SwarmNode] = {}
        self.task_queue: List[Dict[str, Any]] = []
        self.completed_tasks: List[Dict[str, Any]] = []
        self.heartbeat_interval = 30  # seconds
        self.heartbeat_timeout = 90  # seconds

    def register_node(self, node: SwarmNode) -> bool:
        """Register a new node in the swarm."""
        if node.node_id in self.nodes:
            return False

        node.status = NodeStatus.ONLINE
        node.last_heartbeat = time.time()
        self.nodes[node.node_id] = node
        return True

    def unregister_node(self, node_id: str) -> bool:
        """Remove node from swarm."""
        if node_id not in self.nodes:
            return False

        del self.nodes[node_id]
        return True

    def update_heartbeat(self, node_id: str) -> bool:
        """Update node heartbeat timestamp."""
        if node_id not in self.nodes:
            return False

        self.nodes[node_id].last_heartbeat = time.time()
        return True

    def check_node_health(self) -> List[str]:
        """Check health of all nodes, return list of dead nodes."""
        current_time = time.time()
        dead_nodes = []

        for node_id, node in self.nodes.items():
            if current_time - node.last_heartbeat > self.heartbeat_timeout:
                node.status = NodeStatus.OFFLINE
                dead_nodes.append(node_id)

        return dead_nodes

    def get_available_nodes(self) -> List[SwarmNode]:
        """Get list of available nodes for task assignment."""
        return [
            node for node in self.nodes.values()
            if node.status == NodeStatus.ONLINE
        ]

    def assign_task(self, task: Dict[str, Any]) -> Optional[str]:
        """
        Assign task to available node.

        Returns node_id if assigned, None if no nodes available.
        """
        available_nodes = self.get_available_nodes()

        if not available_nodes:
            self.task_queue.append(task)
            return None

        # Simple load balancing - assign to first available
        node = available_nodes[0]
        node.status = NodeStatus.BUSY
        node.current_task = task.get("task_id")

        return node.node_id

    def complete_task(self, node_id: str, task_result: Dict[str, Any]) -> bool:
        """Mark task as completed and free up node."""
        if node_id not in self.nodes:
            return False

        node = self.nodes[node_id]
        node.status = NodeStatus.ONLINE
        node.current_task = None

        self.completed_tasks.append(task_result)

        # Process queued tasks
        if self.task_queue:
            next_task = self.task_queue.pop(0)
            self.assign_task(next_task)

        return True

    def get_swarm_status(self) -> Dict[str, Any]:
        """Get complete swarm status."""
        return {
            "master_node": self.node_id,
            "is_master": self.is_master,
            "total_nodes": len(self.nodes),
            "online_nodes": len([n for n in self.nodes.values() if n.status == NodeStatus.ONLINE]),
            "busy_nodes": len([n for n in self.nodes.values() if n.status == NodeStatus.BUSY]),
            "offline_nodes": len([n for n in self.nodes.values() if n.status == NodeStatus.OFFLINE]),
            "queued_tasks": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "nodes": [node.to_dict() for node in self.nodes.values()]
        }

    def broadcast_command(self, command: str, params: Dict[str, Any]) -> List[str]:
        """
        Broadcast command to all online nodes.

        Returns list of node_ids that received command.
        """
        recipients = []

        for node in self.get_available_nodes():
            # In real implementation, send via network
            recipients.append(node.node_id)

        return recipients

    def sync_state(self) -> Dict[str, Any]:
        """Synchronize state across all nodes."""
        state = {
            "timestamp": time.time(),
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()},
            "task_queue": self.task_queue,
            "completed_tasks": self.completed_tasks[-100:]  # Last 100 tasks
        }

        return state

    def load_state(self, state: Dict[str, Any]) -> bool:
        """Load state from synchronization."""
        try:
            # Restore nodes
            self.nodes = {}
            for node_id, node_data in state.get("nodes", {}).items():
                node = SwarmNode(
                    node_id=node_data["node_id"],
                    hostname=node_data["hostname"],
                    ip_address=node_data["ip_address"],
                    status=NodeStatus(node_data["status"]),
                    capabilities=node_data.get("capabilities", []),
                    current_task=node_data.get("current_task"),
                    last_heartbeat=node_data.get("last_heartbeat", 0.0),
                    metadata=node_data.get("metadata", {})
                )
                self.nodes[node_id] = node

            # Restore queues
            self.task_queue = state.get("task_queue", [])
            self.completed_tasks = state.get("completed_tasks", [])

            return True
        except Exception:
            return False
