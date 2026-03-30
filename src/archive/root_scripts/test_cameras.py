
import cv2
from pygrabber.dshow_graph import FilterGraph

def test_discovery():
    print("--- PyGrabber Enumeration ---")
    devices = FilterGraph().get_input_devices()
    for i, name in enumerate(devices):
        print(f"Driver index {i}: {name}")

    print("\n--- OpenCV Probe (0-20) ---")
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    for i in range(21):
        found = False
        for backend in backends:
            b_name = "DSHOW" if backend == cv2.CAP_DSHOW else "MSMF" if backend == cv2.CAP_MSMF else "ANY"
            cap = cv2.VideoCapture(i, backend)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    name = devices[i] if i < len(devices) else "Unknown"
                    print(f"Index {i} ({b_name}) [SUCCESS]: {name} ({frame.shape})")
                    found = True
                    cap.release()
                    break
                cap.release()
        if not found:
            # print(f"Index {i} [FAILED]")
            pass

if __name__ == "__main__":
    test_discovery()
