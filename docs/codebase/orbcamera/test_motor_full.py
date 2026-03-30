"""
OrbOS Motor Control - Full Test Sequence
==========================================
Tests all PTZ movements with pauses to observe.
"""
import usb.core
import struct
import time
import sys

VID, PID = 0x046d, 0x08c2
INTERFACE = 2  # Confirmed working!
XU_UNIT_ID = 0x09

# Control Selectors
XU_PT_RELATIVE = 0x01
XU_RESET = 0x02


def send_motor_command(dev, selector, data):
    """Send motor command via USB control transfer."""
    bmRequestType = 0x21
    bRequest = 0x01
    wValue = (selector << 8) | 0x00
    wIndex = (XU_UNIT_ID << 8) | INTERFACE
    
    try:
        dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data, timeout=2000)
        return True
    except usb.core.USBError as e:
        print(f"  Error: {e}")
        return False


def pan_tilt(dev, pan: int, tilt: int):
    """Send pan/tilt relative movement."""
    # Scale to camera units (64 = 1 degree)
    p = max(-32768, min(32767, int(pan * 64)))
    t = max(-32768, min(32767, int(tilt * 64)))
    data = struct.pack("<hh", p, t)
    print(f"  Pan={pan:+4d}°, Tilt={tilt:+4d}° -> Data: {data.hex()}")
    return send_motor_command(dev, XU_PT_RELATIVE, data)


def reset(dev):
    """Reset to center position."""
    data = bytes([0x03])  # Reset both axes
    print(f"  Reset -> Data: {data.hex()}")
    return send_motor_command(dev, XU_RESET, data)


def main():
    print("=" * 50)
    print("  OrbOS Motor Control - Full Test")
    print("=" * 50)
    
    # Find devices
    devs = list(usb.core.find(find_all=True, idVendor=VID, idProduct=PID))
    print(f"\nFound {len(devs)} devices")
    
    if not devs:
        print("ERROR: Camera not found!")
        return 1
    
    # Use first device
    dev = devs[0]
    print(f"Using: Bus={dev.bus} Addr={dev.address}")
    
    print("\n--- Motor Test Sequence ---")
    print("Watch the camera head!\n")
    
    # Test 1: Pan Right
    print("[1/6] PAN RIGHT...")
    if pan_tilt(dev, +20, 0):
        print("  Sent! Watch for right movement...")
    time.sleep(1.5)
    
    # Test 2: Pan Left  
    print("\n[2/6] PAN LEFT...")
    if pan_tilt(dev, -40, 0):
        print("  Sent! Watch for left movement...")
    time.sleep(1.5)
    
    # Test 3: Return to center (pan)
    print("\n[3/6] PAN CENTER...")
    if pan_tilt(dev, +20, 0):
        print("  Sent! Returning towards center...")
    time.sleep(1.5)
    
    # Test 4: Tilt Up
    print("\n[4/6] TILT UP...")
    if pan_tilt(dev, 0, +20):
        print("  Sent! Watch for upward movement...")
    time.sleep(1.5)
    
    # Test 5: Tilt Down
    print("\n[5/6] TILT DOWN...")
    if pan_tilt(dev, 0, -40):
        print("  Sent! Watch for downward movement...")
    time.sleep(1.5)
    
    # Test 6: Reset
    print("\n[6/6] RESET TO CENTER...")
    if reset(dev):
        print("  Sent! Camera should return to center...")
    time.sleep(2)
    
    print("\n" + "=" * 50)
    print("  Test Complete!")
    print("=" * 50)
    print("\nDid the camera move as expected?")
    print("  - If YES: Motor control is working!")
    print("  - If NO: We may need to adjust protocol")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
