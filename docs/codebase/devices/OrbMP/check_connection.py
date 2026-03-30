import wmi

def check_usb_device():
    c = wmi.WMI()
    print("Scanning all PnP Entities for USB...")
    count = 0
    for item in c.Win32_PnPEntity():
        if item.DeviceID and "USB" in item.DeviceID:
            count += 1
            # Print identifying info
            caption = item.Caption or item.Name or "Unknown"
            print(f"Item: {caption}")
            print(f"  ID: {item.DeviceID}")
            print(f"  Status: {item.Status}")
            
    print(f"Scan complete. Found {count} USB-related entities.")

if __name__ == "__main__":
    check_usb_device()
