import os
import sys
from pathlib import Path

import torch

# Add project root to PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent.parent))

import logging

from src.orchestrator.unified_triad import load_unified_triad

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_wrapper_smoke_test():
    config_path = "src/core/src/core/config/nano_triad_config.json"

    # Ensure config exists (fallback to default if not found)
    if not os.path.exists(config_path):
        logger.error(f"Config not found at {config_path}")
        return

    logger.info("Initializing UnifiedBrainTriad...")
    triad = load_unified_triad(config_path)

    # 1. Test .forward()
    logger.info("Testing .forward() pass...")
    dummy_input = torch.randint(0, 50257, (1, 16))
    dummy_image = torch.randn(1, 128) # Matches image_embed_dim

    with torch.no_grad():
        out = triad(dummy_input, image_features=dummy_image)

    logger.info("Forward pass successful.")
    logger.info(f"Integration Status: {out['integration']['latent_os']['system_status']}")

    # 2. Test .generate() with Nexus Loop
    logger.info("Testing .generate() with Nexus protocol...")
    gen_out = triad.generate("Hello, Unified Brain. What is your status?")

    logger.info(f"Response: {gen_out['response']}")
    logger.info("Nexus Logs:")
    for log in gen_out['nexus_logs']:
        logger.info(f"  - {log}")

    # 3. Test Hardware Status
    hw_status = triad.get_hardware_status()
    logger.info(f"Hardware Status: {hw_status}")

    logger.info("SMOKE TEST COMPLETE: UNIFIED TRIAD WRAPPER IS OPERATIONAL.")

if __name__ == "__main__":
    run_wrapper_smoke_test()
