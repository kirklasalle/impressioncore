#!/usr/bin/env python3
"""
Launch B3 Embedding Integration Training (Path C)
================================================

Quick launcher for F: Drive embedding integration training.
Estimated timeline: 14-21 days (55 total epochs)

Usage:
    python launch_b3_embedding_integration.py

Created: October 6, 2025
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from training.b3_embedding_integration_trainer import main

if __name__ == "__main__":
    print("\n🚀 Launching Path C: F: Drive Embedding Integration Training")
    print("="*80)
    print("Target: 8.0-9.0/10.0 conversation quality (college to graduate level)")
    print("Timeline: 14-21 days (4 phases, 55 total epochs)")
    print("Hardware: GTX 1050 Ti (4GB VRAM) optimized")
    print("="*80 + "\n")

    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
        print("Checkpoints saved to: F:/models/checkpoints/b3/embedding_integration/")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
