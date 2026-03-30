import wmi


def identify_devices():
    print("--- ImpressionCore: Comprehensive PnP Device Scan ---")
    c = wmi.WMI()

    # 1. Search for everything related to "Camera", "Video", "PlayStation", "Sony", "Logitech"
    keywords = ["Camera", "Video", "PlayStation", "Sony", "Logitech", "Orbit", "Sphere", "Eye"]

    found_count = 0
    print("\n[PNP ENTITIES]")
    for dev in c.Win32_PnPEntity():
        name = str(dev.Name)
        if any(k.lower() in name.lower() for k in keywords):
            found_count += 1
            print(f"[{found_count}] Name: {name}")
            print(f"    HardwareID: {dev.HardwareID}")
            print(f"    Status: {dev.Status}")
            print(f"    Manufacturer: {dev.Manufacturer}")
            print(f"    Service: {dev.Service}")
            print("-" * 30)

    # 2. Specifically look for Video Controllers
    print("\n[VIDEO CONTROLLERS]")
    for dev in c.Win32_VideoController():
        print(f"Name: {dev.Name}")
        print(f"    AdapterRAM: {dev.AdapterRAM}")

    # 3. USB Hubs
    print("\n[USB HUBS / DEVICES]")
    for dev in c.Win32_USBHub():
        print(f"Name: {dev.Name}")
        print(f"    DeviceID: {dev.DeviceID}")

    print(f"\nScan complete. Found {found_count} potential relevant devices.")

if __name__ == "__main__":
    identify_devices()
