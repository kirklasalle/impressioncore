"""
BRUTE FORCE Motor Control Scanner
===================================
Sends control commands to EVERY possible XU ID, Interface, and Control Selector
combination to find what makes the motor move.

Watch the camera head while this runs!
"""
import usb.core
import struct
import time
import sys

VID, PID = 0x046d, 0x08c2


def main():
    print("=" * 70)
    print("  BRUTE FORCE Motor Control Scanner")
    print("  Watch the camera head - ANY movement means we found something!")
    print("=" * 70)
    
    # Find ALL devices
    devs = list(usb.core.find(find_all=True, idVendor=VID, idProduct=PID))
    print(f"\nFound {len(devs)} Logitech devices\n")
    
    if not devs:
        print("ERROR: No camera found!")
        return 1
    
    # Motor command data - pan right by a small amount
    pan_data = struct.pack("<hh", 1000, 0)  # Larger value for more noticeable movement
    
    # Also try single-byte and different data formats
    test_data_variants = [
        ("Pan right (4 bytes)", struct.pack("<hh", 1000, 0)),
        ("Pan left (4 bytes)", struct.pack("<hh", -1000, 0)),
        ("Tilt up (4 bytes)", struct.pack("<hh", 0, 1000)),
        ("Reset (1 byte 0x03)", bytes([0x03])),
        ("Reset (1 byte 0xFF)", bytes([0xFF])),
        ("Custom (2 bytes)", struct.pack("<h", 1000)),
        ("Raw 0x01010101", bytes([0x01, 0x01, 0x01, 0x01])),
    ]
    
    commands_sent = 0
    
    for dev_idx, dev in enumerate(devs):
        print(f"\n{'='*70}")
        print(f"Device {dev_idx}: Bus={dev.bus} Address={dev.address}")
        print(f"{'='*70}")
        
        # Get valid interfaces for this device
        try:
            cfg = dev.get_active_configuration()
            valid_interfaces = set()
            for intf in cfg:
                valid_interfaces.add(intf.bInterfaceNumber)
            print(f"Valid interfaces: {sorted(valid_interfaces)}")
        except Exception as e:
            print(f"Could not get config: {e}")
            valid_interfaces = {0, 1, 2, 3}
        
        # Test XU IDs 1-15
        for xu_id in [3, 9, 1, 2, 4, 5, 6, 7, 8, 10]:  # Start with likely ones
            # Test on all valid interfaces
            for interface in sorted(valid_interfaces):
                # Test control selectors 1-10
                for cs in range(1, 8):
                    # Just use pan_data for speed
                    bmRequestType = 0x21  # Host-to-device, Class, Interface
                    bRequest = 0x01       # SET_CUR
                    wValue = (cs << 8) | 0x00
                    wIndex = (xu_id << 8) | interface
                    
                    try:
                        dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, pan_data, timeout=100)
                        commands_sent += 1
                        print(f"  [OK] XU={xu_id:2d} IF={interface} CS={cs}: Accepted")
                        time.sleep(0.3)  # Brief pause to observe movement
                    except usb.core.USBError as e:
                        if "STALL" in str(e) or "pipe" in str(e).lower():
                            pass  # Expected - command not supported
                        else:
                            pass  # Other error
    
    print(f"\n{'='*70}")
    print(f"  Scan Complete! Sent {commands_sent} commands.")
    print(f"{'='*70}")
    print("\nDid you see ANY camera movement during the scan?")
    print("If yes, check the console output for the last [OK] message before movement!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
