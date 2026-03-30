"""
Kinect HCEP Live Test Script
============================
Tests the complete pipeline:
1. Kinect initialization
2. Video streams (RGB, Depth, IR)
3. Face tracking
4. HCEP analysis
5. Facial recognition

Run this to verify everything works before using the Avatar server.

Author: ImpressionCore Team
Created: January 2026
"""

import logging
import os
import sys
import time

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_kinect_pipeline():
    """Full pipeline test"""
    print("=" * 60)
    print(" Kinect HCEP Live Test")
    print("=" * 60)

    # Import modules
    print("\n[1/5] Loading modules...")
    try:
        from src.vision.face_identity import FACE_LIB, FaceIdentityManager
        from src.vision.hcep import HCEPAnalyzer
        from tools.kinect_controller_app import KinectController
        print("  ✓ KinectController loaded")
        print("  ✓ HCEPAnalyzer loaded")
        print(f"  ✓ FaceIdentityManager loaded (using: {FACE_LIB})")
    except Exception as e:
        print(f"  ✗ Module load error: {e}")
        return False

    # Initialize Kinect
    print("\n[2/5] Initializing Kinect...")
    kinect = None
    try:
        kinect = KinectController(sensor_index=0)
        if kinect.open(use_color=True, use_depth=True, use_skeleton=True):
            print("  ✓ Kinect opened successfully")
            info = kinect.get_device_info()
            print(f"  ✓ Status: {info.get('status', 'unknown')}")
            print(f"  ✓ Color mode: {info.get('color_mode', 'unknown')}")
        else:
            print("  ✗ Failed to open Kinect")
            print("  → Check USB connection and SDK installation")
            return False
    except Exception as e:
        print(f"  ✗ Kinect init error: {e}")
        return False

    # Let hardware warm up
    time.sleep(1.0)

    # Test video streams
    print("\n[3/5] Testing video streams...")

    rgb = kinect.get_rgb_frame()
    if rgb is not None:
        print(f"  ✓ RGB: {rgb.shape}")
    else:
        print("  ✗ RGB: No frame")

    depth, depth_raw = kinect.get_depth_frame()
    if depth is not None:
        print(f"  ✓ Depth: {depth.shape}")
    else:
        print("  ✗ Depth: No frame")

    ir = kinect.get_ir_frame()
    if ir is not None:
        print(f"  ✓ IR: {ir.shape}")
    else:
        print("  ✗ IR: No frame")

    # Test skeleton
    print("\n[4/5] Testing skeleton tracking...")
    skeletons = kinect.get_skeleton_frame()
    if skeletons:
        print(f"  ✓ {len(skeletons)} skeleton(s) tracked")
        for skel in skeletons:
            pos = skel.position
            print(f"    → ID {skel.tracking_id}: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")
    else:
        print("  ○ No skeletons detected (stand 1.5-4m from sensor)")

    # Test motor
    print("\n[5/5] Testing motor & sensors...")
    tilt = kinect.get_tilt()
    print(f"  ✓ Current tilt: {tilt}°")

    accel = kinect.get_accelerometer()
    print(f"  ✓ Accelerometer: ({accel[0]:.2f}, {accel[1]:.2f}, {accel[2]:.2f})")

    # HCEP test
    print("\n[BONUS] HCEP Analysis Test...")
    hcep = HCEPAnalyzer()

    # Simulate head positions
    test_poses = [
        (0, 0, 0, "center"),
        (15, -20, 0, "up-left"),
        (-15, 20, 0, "down-right"),
    ]

    for pitch, yaw, roll, name in test_poses:
        reading = hcep.analyze("TestUser", pitch, yaw, roll)
        hcep.get_state_description(reading)
        print(f"  {name}: {reading.cognitive_state.name} ({reading.emotional_valence.name})")

    # Interactive mode
    print("\n" + "=" * 60)
    print(" INTERACTIVE MODE")
    print(" Press 'q' to quit, 's' to save frame")
    print("=" * 60)

    face_manager = FaceIdentityManager("test_faces.pkl")

    try:
        while True:
            rgb = kinect.get_rgb_frame()
            depth, _ = kinect.get_depth_frame()

            if rgb is not None:
                # Try face detection/recognition
                name, conf = face_manager.identify(rgb)

                # Overlay info
                cv2.putText(rgb, f"ID: {name} ({conf:.2f})", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                cv2.imshow("Kinect RGB", rgb)

            if depth is not None:
                cv2.imshow("Kinect Depth", depth)

            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s') and rgb is not None:
                filename = f"kinect_capture_{int(time.time())}.jpg"
                cv2.imwrite(filename, rgb)
                print(f"Saved: {filename}")

    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        kinect.close()
        print("\nKinect closed. Test complete!")

    return True


def test_simulation_mode():
    """Test without Kinect hardware"""
    print("=" * 60)
    print(" HCEP Simulation Test (No Kinect Required)")
    print("=" * 60)

    import math

    from src.vision.hcep import HCEPAnalyzer

    hcep = HCEPAnalyzer()

    print("\nSimulating head movement pattern...")
    print("(In real use, this comes from Kinect face tracking)")
    print()

    t = 0
    for i in range(20):
        # Simulate natural head movement
        pitch = 12 * math.sin(t * 0.5)
        yaw = 18 * math.cos(t * 0.3)
        roll = 4 * math.sin(t * 0.7)

        reading = hcep.analyze(
            identity="SimUser",
            pitch=pitch,
            yaw=yaw,
            roll=roll
        )

        hcep.get_state_description(reading)
        print(f"t={i:2d}: {reading.gaze_region.name:12s} → {reading.cognitive_state.name}")

        t += 0.3
        time.sleep(0.1)

    # Session summary
    session = hcep.get_session("SimUser")
    print("\nSession Summary:")
    print(f"  Readings: {len(session.readings)}")
    print(f"  Dominant: {session.dominant_state.name}")
    print(f"  Valence:  {session.average_valence:+.2f}")


if __name__ == "__main__":
    print()
    print("Select test mode:")
    print("  1. Full Kinect test (requires Kinect connected)")
    print("  2. Simulation only (no hardware needed)")
    print()

    choice = input("Enter 1 or 2 (default=2): ").strip() or "2"

    if choice == "1":
        test_kinect_pipeline()
    else:
        test_simulation_mode()
