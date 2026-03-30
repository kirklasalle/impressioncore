
import cv2
import time
import sys

def verify_opencv_ptz():
    print("==========================================")
    print("      OpenCV PTZ Verification")
    print("==========================================")
    print("Testing standard UVC controls via cv2.CAP_PROP_PAN/TILT.")

    # Try to find a working camera index
    index = 0
    cap = None
    
    # Try DSHOW first as it maps properties best on Windows
    print("Opening camera (Index 0, DSHOW)...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("Failed to open Index 0 with DSHOW. Trying MSMF...")
        cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
        if not cap.isOpened():
            print("Failed to open camera.")
            return

    # Check if Pan is supported
    pan_val = cap.get(cv2.CAP_PROP_PAN)
    print(f"Current Pan Value: {pan_val}")
    
    if pan_val == -1.0: # OpenCV often returns -1 for unsupported, but sometimes 0
        print("WARNING: OpenCV reports Pan might be unsupported (-1). Continuing anyway...")
    
    print("\nTest 1: Reset to Center (0)")
    ret = cap.set(cv2.CAP_PROP_PAN, 0)
    print(f"Set Pan(0) -> Return: {ret}")
    time.sleep(2)
    
    print("\nTest 2: Pan Right (+10)")
    # Note: Units vary strictly by driver (degrees, steps, etc.)
    # We try a small integer.
    ret = cap.set(cv2.CAP_PROP_PAN, 10)
    print(f"Set Pan(10) -> Return: {ret}")
    time.sleep(2)
    
    print("\nTest 3: Pan Left (-10)")
    ret = cap.set(cv2.CAP_PROP_PAN, -10)
    print(f"Set Pan(-10) -> Return: {ret}")
    time.sleep(2)

    print("\nTest 4: Tilt Up (+10)")
    ret = cap.set(cv2.CAP_PROP_TILT, 10)
    print(f"Set Tilt(10) -> Return: {ret}")
    time.sleep(2)

    print("\nTest 5: Tilt Down (-10)")
    ret = cap.set(cv2.CAP_PROP_TILT, -10)
    print(f"Set Tilt(-10) -> Return: {ret}")
    time.sleep(2)

    print("\nTest 6: Reset Center")
    cap.set(cv2.CAP_PROP_PAN, 0)
    cap.set(cv2.CAP_PROP_TILT, 0)
    
    cap.release()
    print("\nDone. Did the camera move?")

if __name__ == "__main__":
    verify_opencv_ptz()
