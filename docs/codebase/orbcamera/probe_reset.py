
import logging
import comtypes
import ctypes
from comtypes import GUID
from ctypes import wintypes
import sys
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("probe_reset")

# Add project root
sys.path.append(os.path.abspath("d:/Projects/orbcamera"))

try:
    from orbcam.logitech.xu_control import (
        XUController, IKsPropertySet,
        LOGITECH_MOTOR_CONTROL_GUID, LOGITECH_MOTOR_CONTROL_GUID_V2
    )
    # We need to ensure comtypes.gen is available for types if needed, 
    # but XUController handles most of it.
except ImportError:
    print("Failed to import XUController. Run from project root.")
    sys.exit(1)

def probe_reset():
    print("==========================================")
    print("      RESET COMMAND PROBE (v2)")
    print("==========================================")
    
    # 1. Use our known-good controller to perform the scan/binding
    logger.info("Initializing XUController...")
    xu = XUController()
    
    # Force the device discovery path specifically for Orbit if needed
    # but the constructor does it automatically.
    
    # 2. Access internal objects (HACK)
    # The XUController should have _ks_property_set bound now due to our Force Bind fix.
    ps = xu._ks_property_set
    
    if not ps:
        print("No internal IKsPropertySet found on XUController.")
        print("This means even the Force Bind failed to acquire the interface.")
        return

    print("------------------------------------------")
    print(f"Acquired IKsPropertySet: {ps}")
    print(f"Current Working GUID: {xu._working_guid}")
    print("------------------------------------------")

    # 3. Test Reset
    print("\nAttempting Reset Loop with working GUID...")
    try:
        # XU_MOTOR_CONTROL_RESET = 2 for both V1 and V2 protocols usually
        # But let's check V1 specifically since that's what we forced.
        
        # Reset Packet: 0x03 (Bit 0=Pan, Bit 1=Tilt)
        payload = bytes([0x03]) 
        data_buf = ctypes.create_string_buffer(payload, len(payload))
        
        guid = GUID(f"{{{xu._working_guid}}}")
        
        print(f"Sending SET to Selector 2 with Data [0x03]...")
        
        hr = ps.Set(
            guid,
            2, # RESET
            None, 0,
            ctypes.cast(data_buf, ctypes.c_void_p),
            len(payload)
        )
        print(f"HRESULT: {hr} (0x{hr & 0xFFFFFFFF:x})")
        
        if hr == 0:
            print("\n>>> SUCCESS: Reset executed cleanly via XUController binding! <<<")
            print("The hardware ACCEPTED the command.")
        else:
            print("\n>>> FAILURE: HRESULT is not 0. <<<")
            
    except Exception as e:
        print(f"Reset Command Exception: {e}")

if __name__ == "__main__":
    probe_reset()
