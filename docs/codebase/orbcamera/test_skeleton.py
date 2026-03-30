from orbcam.native.skeleton_tracker import SkeletonTracker
from orbcam.logitech.kinect import KinectCamera, NUI_INITIALIZE_FLAG_USES_SKELETON
import time

def test_skeleton():
    print("Initializing Kinect Camera (Python)...")
    cam = KinectCamera()
    # Ensure initialization with Skeleton flag
    # Note: The current KinectCamera implementation might already do this
    try:
        cam.open()
        print("Camera opened successfully.")
    except Exception as e:
        print(f"Failed to open Kinect! Error: {e}")
        return

    print("Initializing Native Skeleton Tracker...")
    tracker = SkeletonTracker()
    
    print("Waiting for skeletons (ensure you are visible to the sensor)...")
    try:
        for i in range(100):
            # Pump the Python camera reading loop to keep the sensor alive
            # frame = cam.read() 
            
            # Poll native skeleton using the active sensor interface
            skel = tracker.get_skeleton(cam._sensor, timeout_ms=30)
            if skel:
                print(f"Tracked Skeleton! Head: {skel['head']}")
            else:
                if i % 10 == 0:
                    print(".", end="", flush=True)
            
            time.sleep(0.03)
    except KeyboardInterrupt:
        pass
    finally:
        cam.close()
        print("\nDone.")

if __name__ == "__main__":
    test_skeleton()
