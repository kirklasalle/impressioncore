
import sys
import os
import time
import cv2

# Add src to path
sys.path.append(os.path.abspath(os.getcwd()))

from src.orchestrator.kinect_connector import KinectConnector

def test_kinect():
    print("--- Starting Kinect Isolation Test ---")
    try:
        kinect = KinectConnector(0)
        print("Connector instantiated.")

        if kinect.open():
            print("Kinect OPENED successfully.")
        else:
            print("Kinect FAILED to open.")
            return

        # Try to read frames for 5 seconds
        start = time.time()
        frames = 0
        while time.time() - start < 5.0:
            ret, frame = kinect.read()
            if ret:
                print(f"Frame Captured! Shape: {frame.shape}")
                cv2.imwrite("kinect_test_frame.jpg", frame)
                frames += 1
                if frames >= 5:
                    print("Captured 5 frames. Stopping.")
                    break
            else:
                print(".", end="", flush=True)
            time.sleep(0.01)

        print(f"\nTotal Frames: {frames}")
        kinect.release()
        print("Kinect Released.")

    except Exception as e:
        print(f"\nEXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_kinect()
