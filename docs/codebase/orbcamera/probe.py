import cv2
import wmi

def main():
    print("Brute Force Camera Search...")
    backends = {
        "DSHOW": cv2.CAP_DSHOW,
        "MSMF": cv2.CAP_MSMF,
        "ANY": cv2.CAP_ANY,
    }
    
    for bname, bval in backends.items():
        print(f"\nProbing backend: {bname}")
        for i in range(5):
            cap = cv2.VideoCapture(i, bval)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"  [+] Found working camera at index {i}")
                    w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    print(f"      Resolution: {w}x{h}")
                else:
                    print(f"  [!] Index {i} opened but failed to read frame.")
                cap.release()
            else:
                pass

    print("\nListing all Imaging/Camera PnP Entities...")
    c = wmi.WMI()
    for device in c.Win32_PnPEntity():
        pclass = str(device.PNPClass).lower()
        if "image" in pclass or "camera" in pclass or "video" in str(device.Name).lower():
            print(f"Name: {device.Name}")
            print(f"  Class: {device.PNPClass}")
            print(f"  DeviceID: {device.DeviceID}")
            print(f"  Status: {device.Status}")
            print("-" * 20)

if __name__ == "__main__":
    main()
