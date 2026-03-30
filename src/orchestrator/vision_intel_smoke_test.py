import os
import sys
from pathlib import Path

# Add project root to PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent.parent))

import json
import logging

from src.orchestrator.system_logger import sys_logger
from src.orchestrator.unified_triad import UnifiedBrainTriad

logging.getLogger("ImpressionCore").setLevel(logging.WARNING)

def run_vision_intelligence_smoke_test():
    config_path = "src/core/src/core/config/nano_triad_config.json"

    print("--- ImpressionCore Vision & Intelligence Verification ---")

    # Initialize
    triad = UnifiedBrainTriad(config_path)
    sys_logger.clear_buffer()
    if os.path.exists(triad.vision.hw_intel_file):
        os.remove(triad.vision.hw_intel_file)

    # 1. Simulate Vision & PTZ
    print("\nSimulating motorized vision...")
    triad.vision.simulate_frames(2)

    # 2. Injected Sensory Symbols (Moondream/Whisper)
    sensory_input = {
        "moondream": "A person sitting in front of a computer, looking focused.",
        "whisper": "[Ambient typing sounds and low humming]"
    }

    # 3. Generate with full context
    gen_out = triad.generate("Sync avatar to my current focus.", sensory_data=sensory_input)

    print("\n--- RESULTS ---")
    print(f"Moondream Logic in Nexus: {any('Moondream sees' in str(l) for l in gen_out['nexus_logs'])}")
    print(f"Whisper Logic in Nexus: {any('Whisper hears' in str(l) for l in gen_out['nexus_logs'])}")
    print(f"3D Position Lock: {gen_out['avatar_update']['commands'][0]['data']}")

    # 4. Check Hardware Intelligence Database
    db_path = triad.vision.hw_intel_file
    print(f"\nChecking Hardware Intelligence Database: {db_path}")
    if os.path.exists(db_path):
        with open(db_path) as f:
            data = json.load(f)
            print(f"  Total Intelligence Records: {len(data)}")
            print(f"  Latest System Profile: {data[-1]['system_profile']}")
            print("  [SUCCESS] Hardware RAG updated.")

    print("\n--- VISION INTELLIGENCE SMOKE TEST COMPLETE ---")

if __name__ == "__main__":
    run_vision_intelligence_smoke_test()
