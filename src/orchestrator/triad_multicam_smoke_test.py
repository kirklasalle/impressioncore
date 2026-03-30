import sys
from pathlib import Path

# Add project root to PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent.parent))

import logging

from src.orchestrator.unified_triad import UnifiedBrainTriad

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_multi_cam_smoke_test():
    config_path = "src/core/src/core/config/nano_triad_config.json"

    # Initialize with two cameras (Indices 0 and 1)
    logger.info("Initializing Triad with Multi-Camera support (0, 1)...")
    triad = UnifiedBrainTriad(config_path)
    triad.vision.device_indices = [0, 1]
    triad.vision.open()

    # Check Hardware Status
    status = triad.get_hardware_status()
    logger.info(f"Hardware Status: {status}")

    # Execute generation with positioning logic
    logger.info("Executing generation with multi-camera 3D positioning...")
    gen_out = triad.generate("Calibrate 3D space with multiple cameras.")

    logger.info(f"Avatar Update: {gen_out['avatar_update']}")
    logger.info(f"Nexus Log positioning: {gen_out['nexus_logs'][-1]}")

    triad.vision.close()
    logger.info("MULTI-CAMERA SMOKE TEST COMPLETE.")

if __name__ == "__main__":
    run_multi_cam_smoke_test()
