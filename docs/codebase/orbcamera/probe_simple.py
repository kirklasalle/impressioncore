import cv2

def main():
    print("Direct Camera Probe...")
    # Try indices 0 to 5 with different backends
    backends = [
        ("Default (ANY)", cv2.CAP_ANY),
        ("MSMF", cv2.CAP_MSMF),
        ("DSHOW", cv2.CAP_DSHOW),
    ]
    
    for b_name, b_type in backends:
        print(f"\nProbing backend: {b_name}")
        for i in range(3):
            cap = cv2.VideoCapture(i, b_type)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"  [+] Index {i}: SUCCESS! ({frame.shape[1]}x{frame.shape[0]})")
                else:
                    print(f"  [-] Index {i}: Opened, but failed to read frame.")
                cap.release()
            else:
                pass

if __name__ == "__main__":
    main()
