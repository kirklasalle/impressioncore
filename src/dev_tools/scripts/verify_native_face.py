"""
Verify Native Kinect Face Tracking

This script verifies that the native C++ face tracking from kinect_bridge_enhanced.dll
is properly initialized and processing face data.

Created: January 18, 2026
Author: Agent0 (SAL)
"""
import sys
import time
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


def main():
    print("=== Native Kinect Face Tracking Verification ===\n")

    # 1. Check DLL availability
    print("--- Phase 1: DLL Availability ---")
    bin_dir = project_root / "bin"
    dll_path = bin_dir / "kinect_bridge_enhanced.dll"
    facetrack_dll = bin_dir / "FaceTrackLib.dll"

    print(f"  kinect_bridge_enhanced.dll: {'✅ Found' if dll_path.exists() else '❌ Missing'}")
    print(f"  FaceTrackLib.dll: {'✅ Found' if facetrack_dll.exists() else '❌ Missing'}")

    if not dll_path.exists():
        print("\nERROR: kinect_bridge_enhanced.dll not found. Cannot proceed.")
        return

    # 2. Check face data model path
    print("\n--- Phase 2: Face Model Data ---")
    model_paths = [
        project_root / "data" / "FaceTrackData",
        Path("C:/Program Files/Microsoft SDKs/Kinect/v1.8/Redist/FaceTrackData"),
        Path("C:/Windows/System32")
    ]

    model_found = None
    for mp in model_paths:
        if mp.exists() and (mp / "Face.susd").exists():
            model_found = mp
            break

    if model_found:
        print(f"  Face model data: ✅ Found at {model_found}")
    else:
        print("  Face model data: ❌ Not found in standard locations")
        print("  Checked: " + ", ".join(str(p) for p in model_paths))

    # 3. Test KinectConnector initialization
    print("\n--- Phase 3: KinectConnector Test ---")
    try:
        from src.orchestrator.kinect_connector import KinectConnector

        kc = KinectConnector()
        print("  KinectConnector created: ✅")
        print(f"  Bridge loaded: {'✅' if kc.bridge else '❌'}")
        print(f"  Face tracking initialized: {'✅' if getattr(kc, 'face_tracking_initialized', False) else '❌'}")

        if kc.bridge:
            # Check if ProcessFace is available
            has_process_face = hasattr(kc.bridge, 'ProcessFace')
            has_get_face_result = hasattr(kc.bridge, 'GetFaceResult')
            print(f"  ProcessFace function: {'✅' if has_process_face else '❌'}")
            print(f"  GetFaceResult function: {'✅' if has_get_face_result else '❌'}")

        # Try to open and test
        if kc.open():
            print("\n  Kinect opened: ✅")

            # Try to enable face tracking
            if hasattr(kc, 'set_stream_state'):
                try:
                    kc.set_stream_state('face', True)
                    print("  Face stream enabled: ✅")
                except Exception as e:
                    print(f"  Face stream enable: ❌ ({e})")

            time.sleep(1)  # Give time for sensor to stabilize

            # Try to get a face result
            if hasattr(kc, 'get_native_face'):
                face = kc.get_native_face()
                if face:
                    print(f"\n  Face detected! Pose: pitch={face.get('pitch', 0):.2f}, yaw={face.get('yaw', 0):.2f}")
                else:
                    print("\n  No face detected (sensor may need calibration or face not visible)")

            kc.close()
            print("\n  Kinect closed: ✅")
        else:
            print("  Kinect open: ❌ (Sensor may not be connected)")

    except ImportError as e:
        print(f"  Import error: {e}")
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n=== Verification Complete ===")


if __name__ == "__main__":
    main()
