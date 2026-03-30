import json
import os
import sys
from pathlib import Path
from typing import Any


class SwarmPresence:
    """
    Bridge between the Main ImpressionCore Application and the MCP Swarm.
    Allows for context-aware interactions with Goliath, IPA, EDS, IDS, and VRGC.
    """

    def __init__(self, mcp_root: str = "d:/Projects/impressioncore/.mcp"):
        self.mcp_root = Path(mcp_root)
        self.goliath_path = self.mcp_root / "impressioncore-goliath"
        self.swarm_active = False
        self.goliath_module = None

        # Add Goliath to path for direct bridge access (fallback mode)
        if str(self.goliath_path) not in sys.path:
            sys.path.append(str(self.goliath_path))

    def connect(self):
        """Standard connection to the Goliath Nerve Center."""
        try:
            import importlib.util
            goliath_file = self.goliath_path / "server.py"
            if not goliath_file.exists():
                print(f"⚠️ Goliath not found at {goliath_file}")
                return False

            spec = importlib.util.spec_from_file_location("goliath_server", str(goliath_file))
            self.goliath_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.goliath_module)

            # Initialize (fast start to avoid hangs)
            os.environ["GOLIATH_FAST_START"] = "1"
            self.goliath_module.initialize_goliath()
            self.swarm_active = True
            return True
        except Exception as e:
            print(f"❌ Swarm Connection Failed: {e}")
            return False

    def get_context_tags(self) -> list[str]:
        """Retrieve current active context tags from Swarm Memory."""
        if not self.swarm_active:
            return []
        try:
            state = self.goliath_module.swarm_memory.get_state()
            return state.get("active_context", [])
        except Exception:
            return []

    def synergize(self, key: str, value: Any, dna: str = "main-app-sync"):
        """Register a finding from the main application into Swarm Memory."""
        if not self.swarm_active:
            return
        try:
            self.goliath_module.swarm_memory.register_finding(
                source="main_app",
                key=key,
                value=value,
                dna=dna
            )
        except Exception as e:
            print(f"⚠️ Synergize Failed: {e}")

    async def execute_swarm_tool(self, bridge_name: str, tool_name: str, arguments: dict[str, Any]):
        """Directly execute an MCP tool via the Goliath Bridge."""
        if not self.swarm_active:
            return {"error": "Swarm Not Connected"}

        bridge = self.goliath_module.bridges.get(bridge_name)
        if not bridge:
            return {"error": f"Bridge {bridge_name} not found"}

        try:
            result = await bridge.execute_tool(tool_name, arguments)
            # Result is List[TextContent]
            if result and len(result) > 0:
                return json.loads(result[0].text)
            return {}
        except Exception as e:
            return {"error": str(e)}

# Singleton Instance for Global Access
swarm = SwarmPresence()
