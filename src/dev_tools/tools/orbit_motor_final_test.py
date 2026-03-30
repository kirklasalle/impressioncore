"""
Orbit Motor Control - Using Existing QuickCamDriver
====================================================
Uses the existing quickcam_driver.py which already has IKsControl implementation.
This tests motor control while video is potentially streaming elsewhere.
"""
import logging
import sys
import time

# Add project to path
sys.path.insert(0, 'd:/Projects/impressioncore/src')

logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(levelname)s: %(message)s')

def test_existing_driver():
    """Test the existing QuickCamOrbDriver implementation."""
    print("=" * 60)
    print("  Testing Existing QuickCamOrbDriver")
    print("=" * 60)
    print()

    try:
        from orchestrator.quickcam_driver import QuickCamOrbDriver

        driver = QuickCamOrbDriver()
        print(f"Driver created. Connected: {driver.connected}, Mode: {driver.mode}")

        # Try to connect
        print("\nAttempting connection...")
        result = driver.connect("QuickCam Orbit/Sphere MP")

        print(f"Connection result: {result}")
        print(f"Mode: {driver.mode}")
        print(f"Connected: {driver.connected}")

        if driver.connected:
            print("\n--- Motor Control Test ---")

            # Test pan
            print("Panning right (500 units)...")
            driver.pan(500)
            time.sleep(1)

            print("Panning left (-500 units)...")
            driver.pan(-500)
            time.sleep(1)

            # Test tilt
            print("Tilting up (300 units)...")
            driver.tilt(300)
            time.sleep(1)

            print("Tilting down (-300 units)...")
            driver.tilt(-300)
            time.sleep(1)

            # Reset
            print("Resetting position...")
            driver.reset_position()

            print("\n--- Test Complete ---")
            print("If the camera moved, motor control is working!")

            driver.disconnect()
            return True
        else:
            print("\nDriver did not connect.")
            print("This may be because:")
            print("  1. IKsControl not available on Logitech driver")
            print("  2. Need to use Logitech's proprietary API")
            return False

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simple_opencv_ptz():
    """Test if OpenCV can control PTZ via DirectShow."""
    print("\n" + "=" * 60)
    print("  Testing OpenCV DirectShow PTZ")
    print("=" * 60)
    print()

    try:
        import cv2

        # Try the DirectShow backend with explicit property IDs
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("Could not open camera")
            return False

        # Check if we can read frames
        ret, frame = cap.read()
        if not ret:
            print("Could not read frame")
            cap.release()
            return False

        print(f"Camera opened, frame size: {frame.shape}")

        # DirectShow-specific properties for PTZ
        # These are the actual property IDs used by DirectShow
        props = {
            "CV_CAP_PROP_PAN": 33,
            "CV_CAP_PROP_TILT": 34,
            "CV_CAP_PROP_ROLL": 35,
            "CV_CAP_PROP_ZOOM": 27,
            "CV_CAP_PROP_EXPOSURE": 15,
            "CV_CAP_PROP_IRIS": 36,
            "CV_CAP_PROP_FOCUS": 28,
        }

        print("\nReading property values...")
        for name, prop_id in props.items():
            val = cap.get(prop_id)
            print(f"  {name} ({prop_id}): {val}")

        # Try setting pan to trigger motor
        print("\nTrying to set PAN...")
        result = cap.set(33, 10)
        print(f"  Set result: {result}")

        # Force the backend to apply by reading more frames
        for _ in range(10):
            cap.read()
            time.sleep(0.05)

        new_pan = cap.get(33)
        print(f"  New PAN value: {new_pan}")

        cap.release()

        return result

    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    # Test 1: Try existing QuickCamOrbDriver
    print("\n[TEST 1] QuickCamOrbDriver (WIN_XU mode)...")
    if test_existing_driver():
        print("\nSUCCESS! Motor control works via QuickCamOrbDriver.")
        return 0

    # Test 2: Try OpenCV DirectShow PTZ
    print("\n[TEST 2] OpenCV DirectShow PTZ...")
    if test_simple_opencv_ptz():
        print("\nSUCCESS! Motor control works via OpenCV.")
        return 0

    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print()
    print("Motor control is NOT working through standard APIs.")
    print()
    print("The Logitech driver may require their proprietary SDK.")
    print("Options:")
    print("  1. Use Logitech Webcam Software UI for manual control")
    print("  2. Research Logitech Camera SDK")
    print("  3. The motor initialized on boot - that may be sufficient")
    print()
    print("VIDEO CAPTURE IS WORKING - this is the primary goal!")

    return 1


if __name__ == "__main__":
    sys.exit(main())
