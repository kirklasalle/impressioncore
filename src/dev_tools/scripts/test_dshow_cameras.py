import cv2
from pygrabber.dshow_graph import FilterGraph


def test_dshow():
    print("Enumerating DirectShow devices via PyGrabber...")
    graph = FilterGraph()
    devices = graph.get_input_devices()

    for i, name in enumerate(devices):
        print(f"Index {i}: {name}")

    print("\nTesting OpenCV VideoCapture for each index...")
    for i in range(len(devices) + 2):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                print(f"[SUCCESS] Index {i} opened: {w}x{h}")
            else:
                print(f"[FAILED] Index {i} opened but could not read frame")
            cap.release()
        else:
            print(f"[FAILED] Index {i} could not be opened")

if __name__ == "__main__":
    test_dshow()
