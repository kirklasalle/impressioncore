import sys
import logging
from orbcam import OrbCamera, CameraError
from orbcam.logitech.devices import find_logitech_cameras

def main():
    logging.basicConfig(level=logging.INFO)
    print("Testing OrbCamera package structure...")
    
    try:
        cameras = find_logitech_cameras()
        print(f"Found {len(cameras)} Logitech cameras via WMI.")
    except Exception as e:
        print(f"FAILED to query WMI: {e}")
        return

    print("Success: Package imports and WMI queries are working.")

if __name__ == "__main__":
    main()
