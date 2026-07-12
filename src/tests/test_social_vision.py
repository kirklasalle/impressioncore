import asyncio
import sys
from pathlib import Path

import pytest

# Add project roots to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

pytest.importorskip("agent0core.core.tools", reason="agent0core.core.tools not available")
from agent0core.core.tools.vision_tool import VisionTool


@pytest.mark.anyio
async def test_pose_interpretation():
    print("--- [TEST] Social Vision Interpretation ---")
    vision = VisionTool()

    # Mock Skeleton Data
    # 1. STANDING Pose
    standing_skel = {
        "tracked": True,
        "id": 1,
        "joints": {
            "HEAD": {"x": 0.0, "y": 0.8, "z": 2.0},
            "HIP_CENTER": {"x": 0.0, "y": 0.0, "z": 2.0},
            "KNEE_LEFT": {"x": -0.1, "y": -0.4, "z": 2.0},
            "KNEE_RIGHT": {"x": 0.1, "y": -0.4, "z": 2.0},
            "ANKLE_LEFT": {"x": -0.1, "y": -0.8, "z": 2.0},
            "ANKLE_RIGHT": {"x": 0.1, "y": -0.8, "z": 2.0},
            "HAND_LEFT": {"x": -0.3, "y": 0.0, "z": 1.9},
            "HAND_RIGHT": {"x": 0.3, "y": 0.0, "z": 1.9}
        }
    }

    # Manually inject latest_skeleton into a mock vision layer if we want to test Tool.execute
    # But for a direct test, we can just call the interpreter or mock the vision layer.

    print("\n[SCENARIO 1] Standing naturally...")
    poses = vision._pose_interpreter.analyze(standing_skel)
    print(f"Detected Poses: {poses}")
    print(f"Summary: {vision._pose_interpreter.get_summary_string(poses)}")

    # 2. WAVING Pose
    waving_skel = standing_skel.copy()
    waving_skel["joints"] = standing_skel["joints"].copy()
    waving_skel["joints"]["HAND_RIGHT"] = {"x": 0.3, "y": 0.9, "z": 1.9} # Hand above head

    print("\n[SCENARIO 2] Waving hand...")
    poses = vision._pose_interpreter.analyze(waving_skel)
    print(f"Detected Poses: {poses}")
    print(f"Summary: {vision._pose_interpreter.get_summary_string(poses)}")

    # 3. SITTING Pose
    sitting_skel = standing_skel.copy()
    sitting_skel["joints"] = standing_skel["joints"].copy()
    sitting_skel["joints"]["HIP_CENTER"]["y"] = -0.3 # Hip dropped to knee level

    print("\n[SCENARIO 3] Sitting down...")
    poses = vision._pose_interpreter.analyze(sitting_skel)
    print(f"Detected Poses: {poses}")
    print(f"Summary: {vision._pose_interpreter.get_summary_string(poses)}")

    # 4. ARMS CROSSED
    crossed_skel = standing_skel.copy()
    crossed_skel["joints"] = standing_skel["joints"].copy()
    # Hands near opposite shoulders
    crossed_skel["joints"]["SHOULDER_LEFT"] = {"x": -0.2, "y": 0.5, "z": 2.0}
    crossed_skel["joints"]["SHOULDER_RIGHT"] = {"x": 0.2, "y": 0.5, "z": 2.0}
    crossed_skel["joints"]["WRIST_LEFT"] = {"x": 0.15, "y": 0.45, "z": 1.9}
    crossed_skel["joints"]["WRIST_RIGHT"] = {"x": -0.15, "y": 0.45, "z": 1.9}

    print("\n[SCENARIO 4] Crossing arms...")
    poses = vision._pose_interpreter.analyze(crossed_skel)
    print(f"Detected Poses: {poses}")
    print(f"Summary: {vision._pose_interpreter.get_summary_string(poses)}")

if __name__ == "__main__":
    asyncio.run(test_pose_interpretation())
