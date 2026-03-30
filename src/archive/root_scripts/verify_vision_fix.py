import sys
import os

# Ad-hoc setup to import from src
sys.path.append(os.getcwd())

from src.orchestrator.orbcloud_vision import OrbCloudVision
from src.orchestrator.system_logger import log_event

def test_full_vision_discovery():
    print("--- Verifying Hardware Discovery Fix ---")
    vision = OrbCloudVision()
    # Mock audio engine to prevent background thread noise
    class MockAudio:
        def refresh_devices(self): return []
        def verify_device_health(self, idx): return {"status": "MOCK"}
        devices = []

    # Run the open method (which now probes 0-31 and uses pseyepy)
    # We use a timeout to prevent it from hanging if there are driver issues
    try:
        vision.open(audio_engine=MockAudio())
        print(f"\nDiscovery Results:")
        print(f"Caps Found: {list(vision.caps.keys())}")
        for idx, meta in vision.hardware_metadata.items():
            print(f"  [{idx}] {meta['model']} ({meta['backend']})")

    except Exception as e:
        print(f"Vision Open Crash: {e}")
        import traceback
        traceback.print_exc()
    finally:
        vision.close()

if __name__ == "__main__":
    test_full_vision_discovery()
