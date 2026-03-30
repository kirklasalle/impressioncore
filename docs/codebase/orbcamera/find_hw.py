import wmi

def main():
    print("Full PnP ID Scan...")
    c = wmi.WMI()
    found = False
    target_vid = "046D"
    target_pid = "08C2"
    
    for device in c.Win32_PnPEntity():
        hw_ids = device.HardwareID
        if hw_ids:
            for hid in hw_ids:
                if target_vid in hid and target_pid in hid:
                    print(f"MATCH FOUND:")
                    print(f"  Name: {device.Name}")
                    print(f"  Description: {device.Description}")
                    print(f"  PNPDeviceID: {device.PNPDeviceID}")
                    print(f"  Class: {device.PNPClass}")
                    print(f"  Status: {device.Status}")
                    print(f"  HardwareIDs: {hw_ids}")
                    print("-" * 20)
                    found = True
                    break
        
        # Fallback search by name if ID fails
        name = str(device.Name).lower()
        if "logitech" in name and ("orb" in name or "sphere" in name):
             print(f"NANE MATCH FOUND:")
             print(f"  Name: {device.Name}")
             print(f"  PNPDeviceID: {device.PNPDeviceID}")
             print("-" * 20)
             found = True

    if not found:
        print("No matches for Logitech Orbit/Sphere (VID_046D & PID_08C2) found.")

if __name__ == "__main__":
    main()
