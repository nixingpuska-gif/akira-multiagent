import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    from core.distributed.nodes import NodeRegistry
    from core.distributed.balancer import NodeBalancer
    from core.distributed.executor import DistributedExecutor

    reg = NodeRegistry()
    n1 = reg.add_node("local-1", "local", ["cpu"])
    n2 = reg.add_node("cloud-1", "cloud", ["gpu", "cpu"])

    # Deterministic IDs
    n1b = reg.add_node("local-1", "local", ["cpu"])
    assert n1.node_id == n1b.node_id

    nodes = reg.list_nodes()
    assert len(nodes) == 2

    balancer = NodeBalancer()
    pick_gpu = balancer.select_node(nodes, required_caps=["gpu"])
    assert pick_gpu is not None and pick_gpu.node_id == n2.node_id

    pick_cpu = balancer.select_node(nodes, required_caps=["cpu"])
    assert pick_cpu is not None

    reg.set_status(n2.node_id, "offline")
    pick_gpu_off = balancer.select_node(reg.list_nodes(), required_caps=["gpu"])
    assert pick_gpu_off is None

    executor = DistributedExecutor(reg, balancer=balancer)
    res = executor.dispatch("do work", required_caps=["cpu"])
    assert res.node_id == n1.node_id
    assert res.status == "ok"
    assert "local:do work" in res.output

    res2 = executor.dispatch("needs fpga", required_caps=["fpga"])
    assert res2.status == "no_node"
    assert res2.error

    assert reg.remove_node(n1.node_id) is True
    assert reg.remove_node("missing") is False


if __name__ == "__main__":
    main()
