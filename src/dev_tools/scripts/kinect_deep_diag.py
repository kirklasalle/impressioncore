import ctypes
import logging
import os
import sys
import time

# Ad-hoc setup to import from src
sys.path.append(os.getcwd())

from src.orchestrator.kinect_connector import INuiSensor, KinectConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KinectDeepDiag")

def test_kinect_nui():
    print("\n=== KINECT DEEP DIAGNOSTIC ===")

    # 1. Check for Kinect10.dll
    try:
        k10 = ctypes.WinDLL("Kinect10.dll")
        print("[OK] Kinect10.dll found and loaded.")
    except Exception as e:
        print(f"[FAIL] Kinect10.dll not found: {e}")
        return

    # 2. Sensor Count
    try:
        count = ctypes.c_int(0)
        k10.NuiGetSensorCount(ctypes.byref(count))
        print(f"[INFO] NuiGetSensorCount: {count.value}")
    except Exception as e:
        print(f"[ERROR] Failed to call NuiGetSensorCount: {e}")

    # 3. Individual Mode Initialization
    modes = [
        (0x02, "COLOR ONLY"),
        (0x20, "DEPTH ONLY"),
        (0x08, "SKELETON ONLY"),
        (0x02 | 0x20 | 0x08, "FULL (C+D+S)")
    ]

    for flags, name in modes:
        print(f"\nTesting mode: {name} (flags: {hex(flags)})")
        try:
            sensor_ptr = ctypes.POINTER(INuiSensor)()
            hr = k10.NuiCreateSensorByIndex(0, ctypes.byref(sensor_ptr))
            if hr != 0:
                print(f"  [FAIL] NuiCreateSensorByIndex(0) failed: {hex(hr & 0xFFFFFFFF)}")
                continue

            hr_init = sensor_ptr.NuiInitialize(flags)
            if hr_init == 0:
                print(f"  [PASS] NuiInitialize {name} Success.")
                sensor_ptr.NuiShutdown()
            else:
                masked_hr = hr_init & 0xFFFFFFFF
                print(f"  [FAIL] NuiInitialize {name} Error: {hex(masked_hr)}")
                if masked_hr == 0x82AC0009:
                    print("         -> E_NUI_NOTCONNECTED: Sensor not detected as 'connected' by SDK.")
                    print("         -> TIP: Check power supply (circular plug) and status LED.")
                elif masked_hr == 0x80070005:
                    print("         -> E_ACCESSDENIED: Another process is using the sensor.")
                elif masked_hr == 0x82AC0002:
                    print("         -> E_NUI_DEVICE_NOT_READY: Sensor available but not ready.")

        except Exception as e:
            print(f"  [CRASH] Test crashed: {e}")

    # 4. Face Tracking Bridge Check
    print("\nTesting Face Tracking Bridge...")
    conn = KinectConnector()
    if conn.bridge:
        print(f"[OK] Bridge DLL loaded from {os.path.basename(conn.bridge._name)}")
        # Test InitFaceTracking with various modes
        try:
            model_path = os.path.dirname(conn.bridge._name) + "\\"
            print(f"Testing InitFaceTracking with model_path: {model_path}")
            res = conn.bridge.InitFaceTracking(640, 480, model_path)
            print(f"Result: {hex(res & 0xFFFFFFFF)}")
        except Exception as e:
            print(f"InitFaceTracking test crash: {e}")
    else:
        print("[FAIL] Bridge DLL not available.")

    # 5. Native Mesh Probe
    print("\nTesting Native 87-Point Mesh Probe...")
    try:
        conn.open()
        time.sleep(1.0) # Wait for streams
        mesh = conn.get_face_mesh()
        if mesh and len(mesh) == 87:
            print("[SUCCESS] Retrieved 87-point facial mesh.")
            print(f"Sample Vertices (First 3): {mesh[:3]}")
        else:
            print(f"[FAIL] Mesh retrieval returned {len(mesh) if mesh else 'None'} points (Expected 87).")
        conn.close()
    except Exception as e:
        print(f"[CRASH] Mesh probe failed: {e}")

if __name__ == "__main__":
    test_kinect_nui()
