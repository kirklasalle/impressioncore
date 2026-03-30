"""
Agent0Core CLI Launcher

Created: January 13, 2026
Author: ImpressionCore Team

Command-line interface for Agent0Core.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent0core.config import default_config
from agent0core.core import create_agent


async def main():
    """Main CLI entry point."""
    print("=" * 60)
    print("  Agent0Core - ImpressionCore Agentic Intelligence Layer")
    print("  Governed by the Prime Directive (7 Laws)")
    print("=" * 60)
    print()

    # Create primary agent
    agent = create_agent()
    print(f"✅ Agent '{agent.name}' initialized")
    print("📜 Prime Directive: ACTIVE")
    print(f"🔒 Strict Mode: {default_config.prime_directive.strict_mode}")
    print()
    print("Type 'quit' or 'exit' to stop.")
    print("Type 'audit' to view governance audit log.")
    print("-" * 60)
    print()

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit"):
                print("\nGoodbye! Agent0Core shutting down.")
                break

            if user_input.lower() == "audit":
                audit_log = agent.get_audit_log()
                print(f"\n📋 Audit Log ({len(audit_log)} entries):")
                for i, entry in enumerate(audit_log[-5:], 1):
                    print(f"  {i}. [{entry['category']}] {entry['action'][:50]}...")
                print()
                continue

            # Process message
            response = await agent.process_message(user_input)
            print(f"\n{agent.name}: {response.content}\n")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
