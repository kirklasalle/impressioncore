"""
Test PyUSB Motor Control for Logitech Orbit Camera
====================================================
Tests direct USB control transfer to the camera's motor.
"""

import usb.core
import usb.util
import struct
import time

# Logitech Orbit MP
VID = 0x046d
PID = 0x08c2  # Confirmed via PyUSB discovery

# UVC Extension Unit constants
XU_PT_RELATIVE = 0x01
XU_RESET = 0x02
XU_UNIT_ID = 0x09  # Logitech typical XU ID

# USB Control Transfer Types
USB_TYPE_CLASS = 0x20
USB_RECIP_INTERFACE = 0x01
USB_DIR_OUT = 0x00

SET_CUR = 0x01


def send_pt_command(dev, pan: int, tilt: int, interface: int = 0):
    """Send pan/tilt relative movement command."""
    bmRequestType = USB_TYPE_CLASS | USB_RECIP_INTERFACE | USB_DIR_OUT
    bRequest = SET_CUR
    wValue = (XU_PT_RELATIVE << 8) | 0x00
    wIndex = (XU_UNIT_ID << 8) | interface
    
    # Scale and pack as signed 16-bit little-endian
    pan_val = max(-32768, min(32767, int(pan * 64)))
    tilt_val = max(-32768, min(32767, int(tilt * 64)))
    data = struct.pack("<hh", pan_val, tilt_val)
    
    print(f"Sending PT command: pan={pan_val}, tilt={tilt_val}")
    print(f"  bmRequestType=0x{bmRequestType:02x}, bRequest=0x{bRequest:02x}")
    print(f"  wValue=0x{wValue:04x}, wIndex=0x{wIndex:04x}")
    print(f"  data={data.hex()}")
    
    try:
        dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data, timeout=1000)
        print("  -> SUCCESS!")
        return True
    except usb.core.USBError as e:
        print(f"  -> FAILED: {e}")
        return False


def send_reset_command(dev, interface: int = 0):
    """Send reset to center command."""
    bmRequestType = USB_TYPE_CLASS | USB_RECIP_INTERFACE | USB_DIR_OUT
    bRequest = SET_CUR
    wValue = (XU_RESET << 8) | 0x00
    wIndex = (XU_UNIT_ID << 8) | interface
    data = bytes([0x03])  # Reset both axes
    
    print(f"Sending RESET command")
    print(f"  wValue=0x{wValue:04x}, wIndex=0x{wIndex:04x}")
    
    try:
        dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data, timeout=1000)
        print("  -> SUCCESS!")
        return True
    except usb.core.USBError as e:
        print(f"  -> FAILED: {e}")
        return False


def main():
    print("=" * 50)
    print("  OrbOS Motor Control Test")
    print("=" * 50)
    
    # Find device
    dev = usb.core.find(idVendor=VID, idProduct=PID)
    if dev is None:
        # Try any Logitech device
        dev = usb.core.find(idVendor=VID)
    
    if dev is None:
        print("ERROR: Camera not found!")
        print("Make sure libusbK driver is installed via Zadig.")
        return 1
    
    print(f"\nFound device: VID={dev.idVendor:04x} PID={dev.idProduct:04x}")
    
    # List interfaces
    cfg = dev.get_active_configuration()
    print(f"\nInterfaces:")
    for intf in cfg:
        print(f"  Interface {intf.bInterfaceNumber}: Class={intf.bInterfaceClass}, SubClass={intf.bInterfaceSubClass}")
    
    # Try interface 0 (typical for UVC control)
    print("\n--- Testing Motor Commands ---\n")
    
    # Test 1: Small pan right
    print("[Test 1] Pan Right...")
    send_pt_command(dev, pan=5, tilt=0, interface=0)
    time.sleep(0.5)
    
    # Test 2: Small pan left  
    print("\n[Test 2] Pan Left...")
    send_pt_command(dev, pan=-5, tilt=0, interface=0)
    time.sleep(0.5)
    
    # Test 3: Tilt up
    print("\n[Test 3] Tilt Up...")
    send_pt_command(dev, pan=0, tilt=5, interface=0)
    time.sleep(0.5)
    
    # Test 4: Reset
    print("\n[Test 4] Reset to Center...")
    send_reset_command(dev, interface=0)
    
    print("\n" + "=" * 50)
    print("  Test Complete!")
    print("=" * 50)
    print("\nDid the camera head move? If not, we may need to adjust:")
    print("  - XU_UNIT_ID (currently: 0x09)")
    print("  - Interface number")
    print("  - Command format")
    
    return 0


if __name__ == "__main__":
    exit(main())
