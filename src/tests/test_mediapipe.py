import os
import sys

import numpy as np

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.orchestrator.orbcloud_vision import OrbCloudVision


def test_mediapipe_detection():
    print("--- TESTING MEDIAPIPE DETECTION ---")
    vision = OrbCloudVision()

    # Create a dummy frame (black image)
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # Test detect_faces
    try:
        detections = vision.detect_faces({0: dummy_frame})
        print(f"Detection Success: {detections}")
    except Exception as e:
        print(f"Detection Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mediapipe_detection()
