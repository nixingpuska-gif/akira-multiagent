"""
Quick AKIRA initialization test
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("AKIRA-9 INITIALIZATION TEST")
print("=" * 60)

try:
    print("\n[1/5] Importing AKIRA Core...")
    from core.akira.akira_core import AKIRACore
    print("[OK] Import successful")

    print("\n[2/5] Initializing AKIRA...")
    akira = AKIRACore()
    print("[OK] AKIRA initialized")

    print("\n[3/5] Checking modules...")
    print(f"  - Model Manager: {'OK' if akira.model_manager else 'FAIL'}")
    print(f"  - Interview Agent: {'OK' if akira.interview_agent else 'FAIL'}")
    print(f"  - Terminal Executor: {'OK' if akira.terminal_executor else 'FAIL'}")
    print(f"  - Financial Manager: {'OK' if akira.financial_manager else 'FAIL'}")
    print(f"  - Idea Generator: {'OK' if akira.idea_generator else 'FAIL'}")

    print("\n[4/5] Getting system status...")
    status = akira.get_status()
    print(f"  - Active: {status['active']}")
    print(f"  - Provider: {akira.model_manager.current_provider}")
    print(f"  - Balance: ${status['financial_status']['balance']}")

    print("\n[5/5] Testing model presets...")
    from core.akira.model_presets import ModelPresets
    presets = ModelPresets()
    print(f"  - Presets loaded: {len(presets.get_all_presets())} models")
    print(f"  - API key: {'Loaded' if presets.get_api_key() else 'Not found'}")

    print("\n" + "=" * 60)
    print("AKIRA-9 READY FOR OPERATION!")
    print("=" * 60)
    print("\nTo start interactive mode, run:")
    print("  python akira.py")

except Exception as e:
    print(f"\n[FAIL] Initialization failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
