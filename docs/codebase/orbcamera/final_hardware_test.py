"""
FINAL HARDWARE TEST
=====================
Uses the EXACT parameters found in logitech.xml for PID 08c2.
Bypasses topology scanning errors by using the filter's IKsControl directly.
"""
import logging
import time
import struct
import sys

# Enable debug logging for xu_control
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orbcam.logitech.xu_control")
logger.setLevel(logging.DEBUG)

from orbcam.logitech.xu_control import XUController

# EXACT VALUES FROM LOGITECH.XML
MOTOR_GUID = "63610682-5070-49ab-b8cc-b3855e8d2256"
SEL_RELATIVE = 1
SEL_RESET = 2

def main():
    print("="*60)
    print("  FINAL HARDWARE TEST (XML Values)")
    print("="*60)
    print(f"Target GUID: {MOTOR_GUID}")
    
    # Initialize controller
    xu = XUController()
    
    # Manually force the GUID matching the XML
    xu._working_guid = MOTOR_GUID
    
    # Check what interface we got
    if xu._ks_control:
        print("Using IKsControl interface")
    elif xu._ks_property_set:
        print("Using IKsPropertySet interface")
    else:
        print("ERROR: No interface found!")
        return
        
    # TEST 1: RESET (Simplest command, 1 byte)
    print("\n--- Sending RESET command ---")
    data = bytes([0x03]) # Reset both pan and tilt
    result = xu._send_command_raw(MOTOR_GUID, SEL_RESET, data)
    print(f"Reset Result: {result}")
    
    time.sleep(2)
    
    # TEST 2: PAN RIGHT (4 bytes: Pan, Tilt)
    print("\n--- Sending PAN RIGHT command ---")
    # 4 bytes: [Pan Low, Pan High, Tilt Low, Tilt High]
    # Unit: 1/64th degree. 640 = 10 degrees
    pan_val = 640
    tilt_val = 0
    data = struct.pack("<hh", pan_val, tilt_val)
    print(f"Data: {data.hex()}")
    
    result = xu._send_command_raw(MOTOR_GUID, SEL_RELATIVE, data)
    print(f"Pan Right Result: {result}")
    
    time.sleep(1)
    
    # TEST 3: PAN LEFT
    print("\n--- Sending PAN LEFT command ---")
    pan_val = -640
    data = struct.pack("<hh", pan_val, tilt_val)
    print(f"Data: {data.hex()}")
    
    result = xu._send_command_raw(MOTOR_GUID, SEL_RELATIVE, data)
    print(f"Pan Left Result: {result}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
