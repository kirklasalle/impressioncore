import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Save originals, mock heavy modules for import, then RESTORE to prevent pollution
_mock_keys = ["torch", "torch.nn", "transformers", "cv2"]
_saved = {k: sys.modules.get(k) for k in _mock_keys}
for _k in _mock_keys:
    sys.modules[_k] = MagicMock()

from src.core.utils.swarm_presence import swarm

# Restore original modules immediately — import is complete
for _k in _mock_keys:
    if _saved[_k] is not None:
        sys.modules[_k] = _saved[_k]
    else:
        sys.modules.pop(_k, None)
del _saved, _mock_keys, _k


class TestLightweightSwarmBridge(unittest.TestCase):

    @patch('src.core.utils.swarm_presence.SwarmPresence.connect')
    def test_swarm_bridge_logic(self, mock_connect):
        """Verify the bridge logic and context retrieval."""
        mock_connect.return_value = True

        # Test connection
        connected = swarm.connect()
        self.assertTrue(connected)

        # Mock Goliath Module
        swarm.goliath_module = MagicMock()
        swarm.swarm_active = True

        # Mock Swarm Memory state
        mock_state = {"active_context": ["1050ti", "vram_limit", "stability"]}
        swarm.goliath_module.swarm_memory.get_state.return_value = mock_state

        # Test tag retrieval
        tags = swarm.get_context_tags()
        self.assertEqual(len(tags), 3)
        self.assertIn("1050ti", tags)

        # Test synergize
        swarm.synergize("unit_test", "passed")
        swarm.goliath_module.swarm_memory.register_finding.assert_called_once()

        print("✅ Lightweight Swarm Bridge Logic Validated.")

if __name__ == "__main__":
    unittest.main()
