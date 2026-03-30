import wmi

def main():
    print("Full PnP Entity Scan...")
    c = wmi.WMI()
    found = False
    for device in c.Win32_PnPEntity():
        name = str(device.Name).lower()
        desc = str(device.Description).lower()
        if any(x in name or x in desc for x in ["camera", "video", "orb", "sphere", "imaging", "capture", "quickcam"]):
            print(f"Name: {device.Name}")
            print(f"  Description: {device.Description}")
            print(f"  PNPDeviceID: {device.PNPDeviceID}")
            print(f"  Class: {device.PNPClass}")
            print(f"  Status: {device.Status}")
            print("-" * 20)
            found = True
    if not found:
        print("No camera-related PnP entities found.")

if __name__ == "__main__":
    main()
