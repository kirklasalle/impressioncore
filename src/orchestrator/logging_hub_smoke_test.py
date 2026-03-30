import os
import sys
from pathlib import Path

# Add project root to PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent.parent))

import logging

from src.orchestrator.system_logger import sys_logger
from src.orchestrator.unified_triad import UnifiedBrainTriad

# We silence the console output here to focus on the Hub verification
logging.getLogger("ImpressionCore").setLevel(logging.WARNING)

def run_logging_hub_smoke_test():
    config_path = "src/core/src/core/config/nano_triad_config.json"

    print("--- ImpressionCore Logging Hub Verification ---")

    # Initialize
    triad = UnifiedBrainTriad(config_path)

    # Perform actions
    # 1. Vision Probe
    triad.vision.device_indices = [0]
    triad.vision.open()

    # 2. Generation Loop (Nexus + Reasoning)
    print("\nRunning generation loop...")
    triad.generate("Visual tracking check.")

    # 3. Retrieve and manipulate logs from the Hub
    print("\nAccessing System Hub...")
    logs = sys_logger.get_logs()
    print(f"Total Logs in Hub: {len(logs)}")

    # Filter by Component
    nexus_logs = sys_logger.get_logs(component="NEXUS")
    print(f"Nexus Component Logs: {len(nexus_logs)}")

    vision_logs = sys_logger.get_logs(component="VISION")
    print(f"Vision Component Logs: {len(vision_logs)}")

    # Verify Structure
    if logs:
        sample = logs[-1]
        print("\nSample Log Structure:")
        print(f"  Component: {sample['component']}")
        print(f"  Message:   {sample['message']}")
        print(f"  Timestamp: {sample['timestamp']}")
        if "pos" in str(sample['message']):
            print("  [SUCCESS] 3D Positioning captured in hub.")

    # 4. Check Persistent Storage
    print(f"\nVerifying JSONL Archive: {sys_logger.log_file}")
    if os.path.exists(sys_logger.log_file):
        with open(sys_logger.log_file) as f:
            lines = f.readlines()
            print(f"  Archive entries: {len(lines)}")
            print("  [SUCCESS] Persistent storage verified.")

    triad.vision.close()
    print("\n--- LOGGING HUB SMOKE TEST COMPLETE ---")

if __name__ == "__main__":
    run_logging_hub_smoke_test()
