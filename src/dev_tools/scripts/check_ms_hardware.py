import json

import wmi


def scan_microsoft_devices():
    c = wmi.WMI()
    devices = []

    # Check for ALL Microsoft PnP Devices (VID 045E)
    for device in c.Win32_PnPEntity():
        hw_id = str(device.DeviceID).upper()
        if "VID_045E" in hw_id:
            devices.append({
                "Name": device.Name,
                "DeviceID": device.DeviceID,
                "Status": device.Status,
                "Manufacturer": device.Manufacturer,
                "PNPDeviceID": device.PNPDeviceID
            })

    return devices

if __name__ == "__main__":
    print("Scanning for Microsoft (VID 045E) devices...")
    found = scan_microsoft_devices()
    if found:
        print(f"Found {len(found)} devices:")
        print(json.dumps(found, indent=4))
    else:
        print("No Microsoft hardware found.")
