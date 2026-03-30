
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Save original, mock sounddevice for import, then restore to prevent pollution
_saved_sd = sys.modules.get("sounddevice")
sys.modules["sounddevice"] = MagicMock()

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestrator.audio_engine import AudioEngine

# Restore original module immediately — import is complete
if _saved_sd is not None:
    sys.modules["sounddevice"] = _saved_sd
else:
    sys.modules.pop("sounddevice", None)
del _saved_sd


class TestAudioEngineStartup(unittest.TestCase):
    def setUp(self):
        self.engine = AudioEngine()
        # Mock devices
        self.engine.devices = [{"index": 0, "name": "Mock Mic", "channels": 4, "rate": 48000, "is_eye": True}]

    @patch('src.orchestrator.audio_engine.log_event')
    @patch('src.orchestrator.audio_engine.sd.InputStream')
    def test_start_stream_no_name_error(self, mock_input_stream, mock_log_event):
        # This test ensures that log_event is found (no NameError)
        result = self.engine.start_stream(0)

        self.assertTrue(result)
        mock_log_event.assert_called_with("AUDIO", "Stream ACTIVE on device 0 (4ch)")
        self.assertTrue(self.engine.active)

        self.engine.stop_stream()

if __name__ == '__main__':
    unittest.main()
