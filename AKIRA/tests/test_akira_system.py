"""
AKIRA System Basic Test
Tests initialization and basic functionality
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_akira_system():
    """Test AKIRA system initialization and basic functions."""
    print("=" * 60)
    print("AKIRA SYSTEM TEST")
    print("=" * 60)

    try:
        # Test 1: Import and initialize
        print("\n[TEST 1] Importing AKIRA Core...")
        from core.akira.akira_core import AKIRACore
        print("[OK] Import successful")

        print("\n[TEST 2] Initializing AKIRA...")
        akira = AKIRACore()
        print("[OK] Initialization successful")

        # Test 2: Check modules
        print("\n[TEST 3] Checking modules...")
        assert akira.model_manager is not None, "Model Manager not initialized"
        assert akira.interview_agent is not None, "Interview Agent not initialized"
        assert akira.terminal_executor is not None, "Terminal Executor not initialized"
        assert akira.financial_manager is not None, "Financial Manager not initialized"
        assert akira.idea_generator is not None, "Idea Generator not initialized"
        print("[OK] All modules initialized")

        # Test 3: Get status
        print("\n[TEST 4] Getting system status...")
        status = akira.get_status()
        print(f"[OK] Status: {status['active']}")
        print(f"[OK] Balance: ${status['financial_status']['balance']}")

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED")
        print("AKIRA-9 is ready for operation!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_akira_system())
    sys.exit(0 if success else 1)
