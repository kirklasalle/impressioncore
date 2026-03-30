import cv2


def scan_cameras():
    print("--- OpenCV Comprehensive Camera Scan ---")
    backends = {
        "ANY": cv2.CAP_ANY,
        "DSHOW": cv2.CAP_DSHOW,
        "MSMF": cv2.CAP_MSMF
    }

    found_any = False
    for name, backend in backends.items():
        print(f"\nScanning backend: {name}...")
        for i in range(32):
            cap = cv2.VideoCapture(i, backend)
            if cap.isOpened():
                w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                print(f"  [FOUND] Index {i} | Res: {w}x{h}")
                cap.release()
                found_any = True
            else:
                pass # Not found at this index

    if not found_any:
        print("\nNo cameras detected by OpenCV in any backend.")
    else:
        print("\nScan complete.")

if __name__ == "__main__":
    scan_cameras()
