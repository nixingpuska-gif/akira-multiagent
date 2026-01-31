"""Test suite for AKIRA advanced modules."""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_system_diagnostics():
    """Test SystemDiagnostics module."""
    print("\n=== Testing SystemDiagnostics ===")

    try:
        from core.tools.system_diagnostics import SystemDiagnosticsTool

        tool = SystemDiagnosticsTool()
        result = await tool.execute({"check_network": True, "check_tools": True}, None)

        print(f"[OK] SystemDiagnostics: {result.success}")
        if result.success:
            print(result.output[:500])  # First 500 chars
        else:
            print(f"[FAIL] Error: {result.error}")

        return result.success
    except Exception as e:
        print(f"[FAIL] SystemDiagnostics failed: {str(e)}")
        return False


async def test_swarm_controller():
    """Test SwarmController module."""
    print("\n=== Testing SwarmController ===")

    try:
        from core.distributed.swarm_controller import SwarmController, SwarmNode, NodeStatus

        # Create controller
        controller = SwarmController(node_id="master-001", is_master=True)

        # Register test nodes
        node1 = SwarmNode(
            node_id="node-001",
            hostname="laptop-01",
            ip_address="192.168.1.10",
            capabilities=["compute", "storage"]
        )

        node2 = SwarmNode(
            node_id="node-002",
            hostname="server-01",
            ip_address="192.168.1.20",
            capabilities=["compute", "network"]
        )

        controller.register_node(node1)
        controller.register_node(node2)

        # Get status
        status = controller.get_swarm_status()

        print(f"[OK] SwarmController initialized")
        print(f"  Total nodes: {status['total_nodes']}")
        print(f"  Online nodes: {status['online_nodes']}")

        return True
    except Exception as e:
        print(f"[FAIL] SwarmController failed: {str(e)}")
        return False


async def test_self_patching():
    """Test SelfPatchingEngine module."""
    print("\n=== Testing SelfPatchingEngine ===")

    try:
        from core.self_mod.self_patching import SelfPatchingEngine

        engine = SelfPatchingEngine(project_root=os.getcwd())

        # Test issue detection
        issue = engine.detect_issue(
            error_message="NameError: name 'foo' is not defined",
            traceback="File test.py, line 10"
        )

        print(f"[OK] SelfPatchingEngine initialized")
        print(f"  Issue detected: {issue['type']}")
        print(f"  Backup dir: {engine.backup_dir}")

        return True
    except Exception as e:
        print(f"[FAIL] SelfPatchingEngine failed: {str(e)}")
        return False


async def test_stealth_protocol():
    """Test StealthProtocol module."""
    print("\n=== Testing StealthProtocol ===")

    try:
        from core.tools.stealth_protocol import StealthProtocol, StealthConfig

        config = StealthConfig(
            randomize_timing=True,
            obfuscate_traffic=True,
            min_delay=0.1,
            max_delay=0.5
        )

        protocol = StealthProtocol(config)

        # Test obfuscation
        test_data = "secret_message"
        obfuscated = protocol.obfuscate_data(test_data)
        deobfuscated = protocol.deobfuscate_data(obfuscated)

        print(f"[OK] StealthProtocol initialized")
        print(f"  Session ID: {protocol.session_id}")
        print(f"  Obfuscation test: {'PASS' if deobfuscated == test_data else 'FAIL'}")

        return deobfuscated == test_data
    except Exception as e:
        print(f"[FAIL] StealthProtocol failed: {str(e)}")
        return False


async def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("AKIRA ADVANCED MODULES TEST SUITE")
    print("=" * 60)

    results = {
        "SystemDiagnostics": await test_system_diagnostics(),
        "SwarmController": await test_swarm_controller(),
        "SelfPatchingEngine": await test_self_patching(),
        "StealthProtocol": await test_stealth_protocol()
    }

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)

    for module, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {module}")

    total = len(results)
    passed = sum(results.values())

    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
