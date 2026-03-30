"""Minimal motor test - send command directly without full enumeration."""
import usb.core
import struct
import sys

VID, PID = 0x046d, 0x08c2

# Find all matching devices
devs = list(usb.core.find(find_all=True, idVendor=VID, idProduct=PID))
print(f"Found {len(devs)} devices with VID={VID:04x} PID={PID:04x}")

for idx, dev in enumerate(devs):
    print(f"\n--- Device {idx}: Bus={dev.bus} Addr={dev.address} ---")
    
    # Try Interface 0 control transfer directly
    bmRequestType = 0x21  # Host-to-device, Class, Interface
    bRequest = 0x01       # SET_CUR
    wValue = 0x0100       # XU_PT_RELATIVE << 8
    wIndex = 0x0900       # (XU_UNIT_ID 9 << 8) | Interface 0
    data = struct.pack("<hh", 500, 0)  # Pan right
    
    print(f"Sending Pan Right command to Interface 0...")
    try:
        dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data, timeout=2000)
        print(">>> SUCCESS! Camera should have moved! <<<")
        sys.exit(0)
    except usb.core.USBError as e:
        print(f"Failed on Interface 0: {e}")
    
    # Also try other interface numbers
    for intf_num in [1, 2, 3]:
        wIndex = (0x09 << 8) | intf_num
        print(f"Trying Interface {intf_num}...")
        try:
            dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data, timeout=500)
            print(f">>> SUCCESS on Interface {intf_num}! <<<")
            sys.exit(0)
        except usb.core.USBError as e:
            print(f"  Failed: {str(e)[:50]}")

print("\nNo successful motor command. May need different XU Unit ID or protocol.")
