import os
import sys
import unittest
from pathlib import Path

# Add project root to PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from src.orchestrator.sensory_intelligence import SensoryIntelligence


class TestHardwareSuppression(unittest.TestCase):
    def setUp(self):
        self.intel = SensoryIntelligence()
        self.intel.suppression_file = "config/test_hardware_suppression.json"
        if os.path.exists(self.intel.suppression_file):
            os.remove(self.intel.suppression_file)
        self.intel.suppressed_devices = []

    def tearDown(self):
        if os.path.exists(self.intel.suppression_file):
            os.remove(self.intel.suppression_file)

    def test_suppression_filtering(self):
        # Mock inventory with an "Error" device
        self.intel.inventory = [
            {"name": "Good Device", "status": "OK", "service": "uvc"},
            {"name": "Bad Device", "status": "Error", "service": "usb"}
        ]

        # Without suppression, should be DEGRADED
        diag = self.intel.get_diagnostics()
        self.assertEqual(diag["status"], "DEGRADED")
        self.assertEqual(len(diag["conflicts"]), 1)
        self.assertEqual(diag["conflicts"][0]["device"], "Bad Device")

        # Suppress the bad device
        self.intel.suppress_device("Bad Device")

        # Now should be HEALTHY
        diag = self.intel.get_diagnostics()
        self.assertEqual(diag["status"], "HEALTHY")
        self.assertEqual(len(diag["conflicts"]), 0)

    def test_persistence(self):
        self.intel.suppress_device("Persistent Bad Device")

        # Create a new instance and check if it loads the suppression
        new_intel = SensoryIntelligence()
        new_intel.suppression_file = self.intel.suppression_file
        new_intel.suppressed_devices = new_intel._load_suppression()

        self.assertIn("Persistent Bad Device", new_intel.suppressed_devices)

if __name__ == "__main__":
    unittest.main()
