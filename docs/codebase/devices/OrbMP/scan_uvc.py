import usb.core
import usb.util
import sys

# Logitech QuickCam Orbit MP
VID = 0x046d
PID = 0x08c2

# Logitech Motor Control GUID
LOGITECH_MOTOR_GUID = b'\x82\x06\x61\x63\x70\x50\xab\x49\xb8\xcc\xb3\x85\x5e\x8d\x22\x56'

def get_backend():
    import usb.backend.libusb1
    import os
    import sys
    
    # Check architecture
    is_64bits = sys.maxsize > 2**32
    arch_str = 'VS2015-x64' if is_64bits else 'VS2015-Win32'
    
    # Possible paths
    base_dir = os.path.dirname(__file__)
    candidate_paths = [
        # Extracted with top-level folder
        os.path.join(base_dir, 'libusb_dist', 'libusb-1.0.26-binaries', arch_str, 'dll', 'libusb-1.0.dll'),
        # Extracted flat (if that happened)
        os.path.join(base_dir, 'libusb_dist', arch_str, 'dll', 'libusb-1.0.dll'),
    ]
    
    for dll_path in candidate_paths:
        if os.path.exists(dll_path):
            print(f"Loading libusb from: {dll_path}")
            return usb.backend.libusb1.get_backend(find_library=lambda x: dll_path)
    
    print("Could not find libusb-1.0.dll in candidates:")
    for p in candidate_paths:
        print(f"  - {p}")
        
    return None

def find_device():
    print(f"Scanning for device {hex(VID)}:{hex(PID)}...")
    backend = get_backend()
    dev = usb.core.find(idVendor=VID, idProduct=PID, backend=backend)
    if dev is None:
        print("Device not found (or access denied).")
        return None
    print("Device found!")
    return dev

def parse_descriptors(dev):
    print("\nParsing Descriptors...")
    for cfg in dev:
        print(f"Configuration {cfg.bConfigurationValue}")
        for intf in cfg:
            print(f"  Interface {intf.bInterfaceNumber}, Alt {intf.bAlternateSetting}")
            print(f"    Class: {intf.bInterfaceClass}, SubClass: {intf.bInterfaceSubClass}")
            
            # Dump extra descriptors if present
            if intf.extra_descriptors:
                # pyusb might return an array/list of bytes
                raw_extras = bytes(intf.extra_descriptors)
                print(f"    Extra Descriptors ({len(raw_extras)} bytes):")
                # print hex dump
                import binascii
                print("      " + str(binascii.hexlify(raw_extras)))
                parse_vc_header(raw_extras)
            
            for ep in intf:
                print(f"    Endpoint {hex(ep.bEndpointAddress)}")

def parse_vc_header(descriptors):
    print("      Parsing VC Descriptors...")
    # This is a raw parse, just looking for the GUID in the stream
    # CS_INTERFACE (0x24) and VC_EXTENSION_UNIT (0x06)
    
    # Simple byte search for now as structured parsing without a library is verbose
    import binascii
    
    # We are looking for the GUID
    pos = descriptors.find(LOGITECH_MOTOR_GUID)
    if pos != -1:
        print(f"      [!] FOUND LOGITECH MOTOR GUID at offset {pos}")
        # The Unit ID is usually a few bytes before the GUID in the descriptor
        # Descriptor layout for Extension Unit:
        # bLength (1), bDescriptorType (1), bDescriptorSubtype (1), bUnitID (1), guidExtensionCode (16)
        # So GUID starts at byte 4. UnitID is at byte 3.
        
        # We need to find the start of the descriptor containing this GUID
        # Scan backward for bDescriptorSubtype == 0x06 and bDescriptorType == 0x24
        
        # Heuristic: The GUID is 16 bytes. The header is 4 bytes.
        # So the descriptor start should be pos - 4
        start_idx = pos - 4
        if start_idx >= 0:
            bLen = descriptors[start_idx]
            bType = descriptors[start_idx+1]
            bSubtype = descriptors[start_idx+2]
            bUnitID = descriptors[start_idx+3]
            
            print(f"        Descriptor Start: {start_idx}")
            print(f"        Type: {hex(bType)} (Expected 0x24)")
            print(f"        Subtype: {hex(bSubtype)} (Expected 0x06)")
            print(f"        Unit ID: {bUnitID} (This is the target ID!)")
            
            if bType == 0x24 and bSubtype == 0x06:
                print(f"      [***] TARGET UNIT ID: {bUnitID} [***]")
                return bUnitID
    else:
        print("      Logitech Motor GUID not found in this interface.")

if __name__ == "__main__":
    dev = find_device()
    if dev:
        try:
            parse_descriptors(dev)
        except Exception as e:
            print(f"Error parsing descriptors: {e}")
            print("Note: On Windows, this often requires a driver like libusb-win32 or WinUSB to be associated w/ the device via Zadig.")
