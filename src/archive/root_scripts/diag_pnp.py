import wmi
import json

def dump_pnp():
    w = wmi.WMI()
    inventory = []
    for dev in w.Win32_PnPEntity():
        inventory.append({
            "name": dev.Name,
            "hw_id": dev.HardwareID[0] if dev.HardwareID else "N/A",
            "status": dev.Status,
            "service": dev.Service,
            "manufacturer": dev.Manufacturer,
            "device_id": dev.DeviceID
        })

    with open("pnp_dump.json", "w") as f:
        json.dump(inventory, f, indent=4)
    print(f"Dumped {len(inventory)} devices to pnp_dump.json")

if __name__ == "__main__":
    dump_pnp()
