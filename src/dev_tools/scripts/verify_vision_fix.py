import sys
from pathlib import Path

# Add src to path
project_root = Path(r"d:\Projects\impressioncore")
sys.path.append(str(project_root))

from src.orchestrator.orbcloud_vision import OrbCloudVision


def test_vision():
    print("Starting OrbCloudVision Test...")
    vision = OrbCloudVision()

    # Force run discovery to populate pnp_inventory
    from src.orchestrator.sensory_intelligence import sensory_intel
    sensory_intel.run_discovery(force=True)
    vision.pnp_inventory = sensory_intel.inventory

    success = vision.open()
    print(f"Vision Open Success: {success}")

    if success:
        print("\nDetected Cameras:")
        for idx, meta in vision.hardware_metadata.items():
            print(f"[{idx}] Model: {meta.get('model')} | Friendly: {meta.get('friendly_name')} | Status: {meta.get('status')}")
            if "Xbox Live Vision" in meta.get("model", ""):
                print(">>> SUCCESS: Xbox Live Vision correctly identified!")

        vision.close()
    else:
        print("\nFailed to detect any cameras.")
        # Print trace log from sensory_intel
        print("\nDiscovery Trace:")
        for entry in sensory_intel.trace_log:
            print(f"[{entry['level']}] {entry['message']}")

if __name__ == "__main__":
    test_vision()
