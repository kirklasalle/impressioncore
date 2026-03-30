import cv2
import time

def probe_camera(index=0):
    print(f"Probing camera at index {index}...")
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Failed to open camera.")
        return

    props = [
        ("Pan", cv2.CAP_PROP_PAN),
        ("Tilt", cv2.CAP_PROP_TILT),
        ("Zoom", cv2.CAP_PROP_ZOOM),
        ("Focus", cv2.CAP_PROP_FOCUS),
        ("Brightness", cv2.CAP_PROP_BRIGHTNESS),
        ("Contrast", cv2.CAP_PROP_CONTRAST),
        ("Saturation", cv2.CAP_PROP_SATURATION),
        ("Hue", cv2.CAP_PROP_HUE),
        ("Gain", cv2.CAP_PROP_GAIN),
        ("Exposure", cv2.CAP_PROP_EXPOSURE),
    ]

    print("\nProperty current values:")
    for name, prop_id in props:
        val = cap.get(prop_id)
        print(f"  {name:10} : {val}")

    print("\nAttempting to change values (if supported)...")
    # Try to set pan/tilt to see if it moves or returns True
    test_movements = [
        ("Pan", cv2.CAP_PROP_PAN, 10),
        ("Tilt", cv2.CAP_PROP_TILT, 10),
        ("Zoom", cv2.CAP_PROP_ZOOM, 20),
    ]

    for name, prop_id, val in test_movements:
        success = cap.set(prop_id, val)
        new_val = cap.get(prop_id)
        print(f"  Set {name:10} to {val:2} : {'Success' if success else 'Failed'} (New value: {new_val})")

    cap.release()

if __name__ == "__main__":
    probe_camera(0)
