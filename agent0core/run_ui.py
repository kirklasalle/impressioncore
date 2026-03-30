"""
Agent0Core Web UI Launcher

Created: January 13, 2026
Author: ImpressionCore Team

Launches the Agent0Core Web UI with FastAPI backend.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent0core.config import default_config


def main():
    """Main UI entry point."""
    print("=" * 60)
    print("  Agent0Core Web UI")
    print("  Governed by the Prime Directive (7 Laws)")
    print("=" * 60)
    print()

    try:
        import uvicorn

        from agent0core.api import app

        if app is None:
            print("❌ FastAPI not available. Install with:")
            print("   pip install fastapi uvicorn")
            return

        print(f"🚀 Starting server at http://{default_config.ui_host}:{default_config.ui_port}")
        print()
        print("Features:")
        print("  • Chat with Agent0")
        print("  • Human-in-the-loop approval")
        print("  • Tool execution (vision, audio, training, knowledge, mcp)")
        print("  • Prime Directive enforcement")
        print()
        print("Press Ctrl+C to stop.")
        print()

        uvicorn.run(
            app,
            host=default_config.ui_host,
            port=default_config.ui_port,
        )

    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print()
        print("Install required packages:")
        print("   pip install fastapi uvicorn")
        print()
        print("Or use CLI mode instead:")
        print("   python -m agent0core.run_cli")


if __name__ == "__main__":
    main()
