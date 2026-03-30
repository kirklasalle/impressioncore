import sys
from pathlib import Path

# Add project root to PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent.parent))

import logging

from src.orchestrator.unified_triad import load_unified_triad

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_multimodal_smoke_test():
    config_path = "src/core/src/core/config/nano_triad_config.json"

    logger.info("Initializing Multimodal UnifiedBrainTriad...")
    triad = load_unified_triad(config_path)

    # Check Hardware Status
    status = triad.get_hardware_status()
    logger.info(f"Initial Hardware Status: {status}")

    # 1. Test .generate() with real Vision capture
    logger.info("Executing generation with live vision context...")
    gen_out = triad.generate("Visual check. Describe the user and update avatar.")

    logger.info(f"Response: {gen_out['response']}")
    logger.info(f"Avatar Status: {gen_out['avatar_update']['status']}")
    logger.info(f"Hardware Logic: {gen_out['avatar_update']['hardware_database']}")

    # 2. Test internal Nexus sequence
    logger.info("Nexus Reasoning Trail:")
    for log in gen_out['nexus_logs']:
        logger.info(f"  - {log}")

    # Cleanup
    triad.vision.close()
    logger.info("MULTIMODAL SMOKE TEST COMPLETE.")

if __name__ == "__main__":
    run_multimodal_smoke_test()
