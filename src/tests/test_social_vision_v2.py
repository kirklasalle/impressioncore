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
async def test_social_vision_v2():
    print("--- [TEST] Social Vision V2 (Body + Face) ---")
    vision = VisionTool()

    # 1. Mock Face Data (Engagement Scenario)
    face_data_engaged = {
        "identity_name": "Kirk",
        "head_pose": {"yaw": 2.0, "pitch": -1.0, "roll": 0.5}, # Looking at you
        "emotion": {"dominant_emotion": "happy", "dominant_confidence": 0.95},
        "landmarks": {
            "top_lip": [(10, 50)] * 12, # Simplified
            "bottom_lip": [(10, 55)] * 12,
            "chin": [(0, 0)] * 17
        }
    }

    # Manually inject smile into landmarks
    # Mouth width ~ 20. Face width ~ 40. ratio 0.5 > 0.45 = SMILING
    face_data_engaged["landmarks"]["top_lip"][0] = (20, 100) # Left corner
    face_data_engaged["landmarks"]["top_lip"][6] = (40, 100) # Right corner
    face_data_engaged["landmarks"]["chin"][0] = (10, 100)   # Left edge
    face_data_engaged["landmarks"]["chin"][16] = (50, 100)  # Right edge

    print("\n[SCENARIO 1] Kirk is happy, smiling, and looking at the camera.")
    tags = vision._face_interpreter.analyze(face_data_engaged)
    summary = vision._face_interpreter.get_summary_string(tags, "Kirk")
    print(f"Tags: {tags}")
    print(f"Summary: {summary}")

    # 2. Mock Face Data (Distracted Scenario)
    face_data_distracted = {
        "identity_name": "Kirk",
        "head_pose": {"yaw": 25.0, "pitch": -20.0, "roll": 0.0}, # Looking away and down
        "emotion": {"dominant_emotion": "neutral", "dominant_confidence": 0.8}
    }

    print("\n[SCENARIO 2] Kirk is looking away and down (distracted/neutral).")
    tags = vision._face_interpreter.analyze(face_data_distracted)
    summary = vision._face_interpreter.get_summary_string(tags, "Kirk")
    print(f"Tags: {tags}")
    print(f"Summary: {summary}")

if __name__ == "__main__":
    asyncio.run(test_social_vision_v2())
