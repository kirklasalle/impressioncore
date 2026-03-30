import wmi
import time

def monitor_connect():
    c = wmi.WMI()
    print("Monitoring for new USB devices... (Ctrl+C to stop)")
    
    # Snapshot current state
    initial_devices = set()
    for item in c.Win32_PnPEntity():
        if item.DeviceID:
            initial_devices.add(item.DeviceID)
            
    print(f"Initial device count: {len(initial_devices)}")
    
    while True:
        current_devices = set()
        for item in c.Win32_PnPEntity():
            if item.DeviceID:
                current_devices.add(item.DeviceID)
        
        # Check added
        added = current_devices - initial_devices
        if added:
            print("\n[!] NEW DEIVCE DETECTED:")
            for dev_id in added:
                # Query details
                try:
                    dev = c.Win32_PnPEntity(DeviceID=dev_id)[0]
                    print(f"  Name: {dev.Name}")
                    print(f"  ID: {dev.DeviceID}")
                    print(f"  Status: {dev.Status}")
                except:
                    print(f"  ID: {dev_id} (Details fetch failed)")
            initial_devices = current_devices
            
        # Check removed
        removed = initial_devices - current_devices
        if removed:
            print("\n[-] Device Removed:")
            for dev_id in removed:
                print(f"  ID: {dev_id}")
            initial_devices = current_devices
            
        time.sleep(1.0)

if __name__ == "__main__":
    monitor_connect()
