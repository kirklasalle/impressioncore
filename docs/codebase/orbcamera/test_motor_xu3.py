"""
Motor Test with Discovered Extension Unit ID 3
================================================
Uses the correct XU ID discovered from USB descriptors.
"""
import usb.core
import struct
import time
import sys

VID, PID = 0x046d, 0x08c2

# DISCOVERED from USB descriptors!
XU_UNIT_ID = 3  # Extension Unit ID found in Device 1
INTERFACE = 0   # Vendor Specific interface on Device 1

# Control Selectors (UVC standard for Pan/Tilt)
CS_PT_RELATIVE = 0x01
CS_PT_ABSOLUTE = 0x02  # Some cameras use absolute
CS_RESET = 0x03


def send_command(dev, xu_id, interface, selector, data):
    """Send UVC XU command."""
    bmRequestType = 0x21  # Host-to-device, Class, Interface
    bRequest = 0x01       # SET_CUR
    wValue = (selector << 8) | 0x00
    wIndex = (xu_id << 8) | interface
    
    print(f"  XU={xu_id} IF={interface} CS={selector:02x} Data={data.hex()}")
    try:
        dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data, timeout=2000)
        return True
    except usb.core.USBError as e:
        print(f"    Error: {e}")
        return False


def main():
    print("=" * 60)
    print("  Motor Test with XU ID 3 (from USB descriptors)")
    print("=" * 60)
    
    # Find ALL devices and pick the one with Interface 0 (Vendor Specific)
    devs = list(usb.core.find(find_all=True, idVendor=VID, idProduct=PID))
    print(f"\nFound {len(devs)} devices")
    
    # Find the Video Control device (Device 1 with Interface 0)
    target_dev = None
    for dev in devs:
        try:
            cfg = dev.get_active_configuration()
            for intf in cfg:
                if intf.bInterfaceClass == 255:  # Vendor Specific
                    target_dev = dev
                    print(f"Using Device: Bus={dev.bus} Addr={dev.address} (Vendor Specific)")
                    break
        except:
            pass
        if target_dev:
            break
    
    if not target_dev:
        print("ERROR: Could not find Vendor Specific interface device!")
        # Try first device anyway
        target_dev = devs[0] if devs else None
        if not target_dev:
            return 1
        print(f"Falling back to first device: Bus={target_dev.bus} Addr={target_dev.address}")
    
    print("\n--- Testing with XU ID 3, Interface 0 ---")
    
    # Test 1: Try different control selectors
    for cs in [0x01, 0x02, 0x03, 0x04, 0x05]:
        print(f"\n[CS={cs:02x}] Trying Pan Right...")
        data = struct.pack("<hh", 500, 0)  # Pan right
        if send_command(target_dev, 3, 0, cs, data):
            print("  Command accepted!")
            time.sleep(1)
    
    # Test 2: Also try on Interface 1
    print("\n--- Also testing on Interface 1 ---")
    for cs in [0x01, 0x02]:
        print(f"\n[CS={cs:02x}] Trying on Interface 1...")
        data = struct.pack("<hh", 500, 0)
        if send_command(target_dev, 3, 1, cs, data):
            print("  Command accepted!")
            time.sleep(1)
    
    # Test 3: Try reset command
    print("\n--- Testing Reset ---")
    send_command(target_dev, 3, 0, CS_RESET, bytes([0x03]))
    time.sleep(2)
    
    print("\n" + "=" * 60)
    print("  Test Complete - Did the camera move?")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
