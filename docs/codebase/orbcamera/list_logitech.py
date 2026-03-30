import wmi

def main():
    print("Listing Logitech PnP Entities...")
    c = wmi.WMI()
    for device in c.Win32_PnPEntity():
        if "logitech" in str(device.Name).lower() or "logitech" in str(device.Description).lower():
            print(f"Name: {device.Name}")
            print(f"  Description: {device.Description}")
            print(f"  PNPDeviceID: {device.PNPDeviceID}")
            print(f"  PNPClass: {device.PNPClass}")
            print(f"  Status: {device.Status}")
            print("-" * 20)

if __name__ == "__main__":
    main()
