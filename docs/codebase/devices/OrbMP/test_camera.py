import cv2
import sys

def list_cameras():
    """Attempt to list available cameras."""
    index = 0
    arr = []
    print("Scanning for cameras...")
    backends = [
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Media Foundation"),
        (cv2.CAP_VFW, "Video For Windows")
    ]
    
    for index in range(2): # Check first 2 indices
        for backend_id, backend_name in backends:
            print(f"Checking index {index} with {backend_name}...")
            cap = cv2.VideoCapture(index, backend_id)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    print(f"  SUCCESS: Found camera at index {index} using {backend_name}")
                    arr.append((index, backend_id))
                    cap.release()
                    break # Found this index, move to next
                else:
                    print("  Failed to read frame.")
            else:
                print("  Failed to open.")
            cap.release()
    return arr

def test_camera(index, backend=cv2.CAP_DSHOW):
    print(f"\nTesting camera at index {index}...")
    cap = cv2.VideoCapture(index, backend)
    
    if not cap.isOpened():
        print("Failed to open camera!")
        return

    # Check resolution
    w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"Resolution: {int(w)}x{int(h)}")
    
    # Check for Pan/Tilt support (Standard Properties)
    # Note: These often fail on consumer drivers, but worth checking
    pan = cap.get(cv2.CAP_PROP_PAN)
    tilt = cap.get(cv2.CAP_PROP_TILT)
    print(f"Standard Pan Support: {'Yes (Value: ' + str(pan) + ')' if pan != -1 else 'No'}")
    print(f"Standard Tilt Support: {'Yes (Value: ' + str(tilt) + ')' if tilt != -1 else 'No'}")

    print("Attempting to capture 10 frames...")
    for i in range(10):
        ret, frame = cap.read()
        if ret:
            print(f"  Frame {i+1}: OK")
        else:
            print(f"  Frame {i+1}: Failed")
    
    cap.release()

if __name__ == "__main__":
    cameras = list_cameras()
    if not cameras:
        print("No cameras found.")
    else:
        # Assuming the Orb MP is one of them, test the first found or user specified
        index, backend = cameras[0]
        test_camera(index, backend)
