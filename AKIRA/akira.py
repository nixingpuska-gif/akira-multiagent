"""
AKIRA-9 Main Entry Point
Autonomous AI Partner System
"""

import asyncio
import sys
from core.akira.akira_core import AKIRACore


async def main():
    """Main entry point for AKIRA system."""
    print("=" * 60)
    print("AKIRA-9 ONLINE")
    print("Autonomous AI Partner System")
    print("=" * 60)

    # Initialize AKIRA
    akira = AKIRACore()

    print("\n[SYSTEM] AKIRA-9 initialized successfully")
    print("[SYSTEM] All modules loaded")
    print(f"[SYSTEM] Financial balance: ${akira.financial_manager.current_balance}")
    print("\n[AKIRA] Ready for requests. Type 'exit' to quit.\n")

    # Main interaction loop
    while akira.active:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n[AKIRA] Shutting down. Goodbye!")
                break

            if user_input.lower() == 'status':
                status = akira.get_status()
                print(f"\n[STATUS] {status}\n")
                continue

            if user_input.lower() == 'ideas':
                print("\n[AKIRA] Generating business ideas...")
                ideas = await akira.generate_business_ideas()
                print(f"[AKIRA] Generated {len(ideas)} ideas\n")
                continue

            # Process request
            print("\n[AKIRA] Processing request...")
            result = await akira.process_request(user_input)

            if result.get("success"):
                print(f"\n[AKIRA] ✓ Task completed")
                print(f"[OUTPUT] {result.get('output', 'Done')}\n")
            else:
                print(f"\n[AKIRA] ✗ Error: {result.get('error', 'Unknown error')}\n")

        except KeyboardInterrupt:
            print("\n\n[AKIRA] Interrupted. Shutting down...")
            break
        except Exception as e:
            print(f"\n[ERROR] {str(e)}\n")


if __name__ == "__main__":
    asyncio.run(main())
