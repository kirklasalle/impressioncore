import sys
from pathlib import Path

import usb.core

# Add project root to PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.orchestrator.orbcloud_vision import OrbCloudVision


def hardware_probe():
    print("--- ImpressionCore: Real-World Hardware Probe ---")

    # 1. USB Search (Low Level)
    print("\n[USB PROBE]")
    try:
        # Check for Logitech
        logitech = usb.core.find(idVendor=0x046d)
        if logitech:
            print(f"  FOUND: Logitech Device (PID: {logitech.idProduct:04x})")
        else:
            print("  NOT FOUND: Logitech Devices")

        # Check for PS Eye
        pseye = usb.core.find(idVendor=0x1415)
        if pseye:
            print(f"  FOUND: PlayStation Eye (PID: {pseye.idProduct:04x})")
        else:
            print("  NOT FOUND: PS Eye Devices")
    except Exception as e:
        print(f"  USB Error: {e}")

    # 2. Vision Layer Probe
    print("\n[VISION PROBE]")
    vision = OrbCloudVision(device_indices=[0, 1, 2, 3, 4])
    if vision.open():
        intel = vision.get_hardware_intelligence()
        print(f"  Active Cameras: {list(intel.keys())}")
        for idx, meta in intel.items():
            print(f"  Cam {idx}: {meta['width']}x{meta['height']} @ {meta['fps']}fps | Type: {meta['ptz_capabilities']['hardware']}")

        # Test N-Camera Triangulation (if 2+ cams)
        if len(intel) >= 2:
            print("\n[TRIANGULATION TEST]")
            pos = vision.triangulate_position()
            print(f"  Result: {pos}")

        vision.close()
    else:
        print("  FAILED: No cameras opened.")

    print("\n--- PROBE COMPLETE ---")

if __name__ == "__main__":
    hardware_probe()
