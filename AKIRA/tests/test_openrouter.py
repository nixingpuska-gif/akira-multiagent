"""
Test OpenRouter Integration and Model Presets
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_openrouter_integration():
    """Test OpenRouter client and model presets."""
    print("=" * 60)
    print("OPENROUTER INTEGRATION TEST")
    print("=" * 60)

    try:
        # Test 1: Load model presets
        print("\n[TEST 1] Loading model presets...")
        from core.akira.model_presets import ModelPresets

        presets = ModelPresets()
        print(f"[OK] Presets loaded: {len(presets.get_all_presets())} models")

        # Test 2: Check API key
        print("\n[TEST 2] Checking API key...")
        api_key = presets.get_api_key()
        if api_key:
            print(f"[OK] API key loaded: {api_key[:20]}...")
        else:
            print("[WARN] No API key in config")

        # Test 3: Get preset models
        print("\n[TEST 3] Getting preset models...")
        for num in range(1, 5):
            preset = presets.get_preset(num)
            if preset:
                print(f"[OK] Preset {num}: {preset['name']} - {preset['model']}")

        # Test 4: Initialize Model Manager
        print("\n[TEST 4] Initializing Model Manager...")
        from core.akira.model_manager import ModelManager

        manager = ModelManager()
        print(f"[OK] Model Manager initialized")
        print(f"[OK] Current provider: {manager.current_provider}")

        # Test 5: Switch to OpenRouter
        print("\n[TEST 5] Switching to OpenRouter...")
        preset = presets.get_preset(1)
        if preset:
            manager.switch_provider("openrouter", preset['model'])
            print(f"[OK] Switched to: {preset['model']}")

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_openrouter_integration())
    sys.exit(0 if success else 1)
