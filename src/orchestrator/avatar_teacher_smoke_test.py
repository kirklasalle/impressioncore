import sys
from pathlib import Path

# Add project root to PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent.parent))

import logging

from src.orchestrator.system_logger import sys_logger
from src.orchestrator.unified_triad import UnifiedBrainTriad

# Silence console for cleaner output
logging.getLogger("ImpressionCore").setLevel(logging.WARNING)

def run_avatar_teacher_smoke_test():
    config_path = "src/core/src/core/config/nano_triad_config.json"

    print("--- ImpressionCore Evolution: Avatar & Teacher Verification ---")

    # Initialize
    triad = UnifiedBrainTriad(config_path)
    sys_logger.clear_buffer()

    # Simulation: Multi-cam vision with face detected
    print("\nSimulating vision & teacher interaction...")
    triad.vision.simulate_frames(2)

    # Run Generation
    gen_out = triad.generate("Calibrate my avatar and provide reasoning.")

    print("\n--- RESULTS ---")
    print(f"Nexus/Teacher Info: {gen_out['nexus_logs']}")

    # Verification
    teacher_ok = len(gen_out['nexus_logs']) > 0
    pos = gen_out['avatar_update']['commands'][0]['data']
    pos_ok = pos[2] > 0 # Depth should be positive

    print(f"Signals Processed: {teacher_ok}")
    print(f"Positioning Lock: {pos_ok} (Pos: {pos})")
    print(f"Avatar Engine Sync: {gen_out['avatar_update']['avatar_id']}")

    # Check Hub for Avatar events
    avatar_logs = sys_logger.get_logs(component="AVATAR")
    print(f"Avatar Hub Events: {len(avatar_logs)}")

    print("\n--- AVATAR TEACHER SMOKE TEST COMPLETE ---")

if __name__ == "__main__":
    run_avatar_teacher_smoke_test()
