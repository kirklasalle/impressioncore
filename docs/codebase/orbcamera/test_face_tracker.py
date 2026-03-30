from orbcam.native.face_tracker import FaceTracker
import numpy as np
import time

def test_tracker():
    print("Initializing Native Face Tracker...")
    tracker = FaceTracker()
    
    if tracker.initialize():
        print("Initialization SUCCESS.")
        
        # Create a dummy black frame (640x480x4 bytes)
        # The bridge expects FTIMAGEFORMAT_UINT8_B8G8R8X8 (32-bit BGRA)
        dummy_frame = np.zeros((480, 640, 4), dtype=np.uint8)
        
        print("Processing dummy frame...")
        start = time.time()
        result = tracker.process_frame(dummy_frame)
        end = time.time()
        
        print(f"Process time: {(end-start)*1000:.2f}ms")
        
        if result:
            print("Tracking Result:", result)
        else:
            print("Tracking Result: None (Expected for black frame, but call succeeded)")
            
        tracker.shutdown()
        print("Shutdown complete.")
    else:
        print("Initialization FAILED.")

if __name__ == "__main__":
    test_tracker()
