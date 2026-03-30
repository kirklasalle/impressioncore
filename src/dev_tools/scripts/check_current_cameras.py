import json

import wmi


def scan_cameras():
    c = wmi.WMI()
    cameras = []

    # Check for PnP Devices that might be cameras
    for device in c.Win32_PnPEntity():
        name = str(device.Name).lower()
        if "camera" in name or "video" in name or "vision" in name or "imaging" in name:
            cameras.append({
                "Name": device.Name,
                "DeviceID": device.DeviceID,
                "Status": device.Status,
                "Manufacturer": device.Manufacturer
            })

    return cameras

if __name__ == "__main__":
    print("Scanning for connected camera hardware...")
    found = scan_cameras()
    if found:
        print(f"Found {len(found)} candidate devices:")
        print(json.dumps(found, indent=4))
    else:
        print("No camera hardware found in PnP inventory.")
