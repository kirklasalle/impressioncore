"""
Probe USB Descriptors for Extension Unit IDs
==============================================
Analyzes the camera's USB descriptors to find the correct Extension Unit
for motor control.
"""
import usb.core
import usb.util

VID, PID = 0x046d, 0x08c2


def probe_descriptors():
    """Probe USB descriptors to find Extension Units."""
    print("=" * 60)
    print("  USB Descriptor Probe for Logitech Orbit Motor Control")
    print("=" * 60)
    
    devs = list(usb.core.find(find_all=True, idVendor=VID, idProduct=PID))
    print(f"\nFound {len(devs)} devices with VID={VID:04x} PID={PID:04x}\n")
    
    for dev_idx, dev in enumerate(devs):
        print(f"\n{'='*60}")
        print(f"Device {dev_idx}: Bus={dev.bus} Address={dev.address}")
        print(f"{'='*60}")
        
        # Device descriptor
        print(f"\nDevice Descriptor:")
        print(f"  bcdUSB: {dev.bcdUSB:04x}")
        print(f"  bDeviceClass: {dev.bDeviceClass}")
        print(f"  bDeviceSubClass: {dev.bDeviceSubClass}")
        print(f"  bDeviceProtocol: {dev.bDeviceProtocol}")
        
        try:
            cfg = dev.get_active_configuration()
            print(f"\nConfiguration {cfg.bConfigurationValue}:")
            print(f"  bNumInterfaces: {cfg.bNumInterfaces}")
            
            for intf in cfg:
                print(f"\n  Interface {intf.bInterfaceNumber} (Alt {intf.bAlternateSetting}):")
                print(f"    bInterfaceClass: {intf.bInterfaceClass} ({get_class_name(intf.bInterfaceClass)})")
                print(f"    bInterfaceSubClass: {intf.bInterfaceSubClass}")
                print(f"    bInterfaceProtocol: {intf.bInterfaceProtocol}")
                print(f"    bNumEndpoints: {intf.bNumEndpoints}")
                
                # Look for extra descriptors (UVC Extension Units are here)
                if hasattr(intf, 'extra_descriptors') and intf.extra_descriptors:
                    print(f"    Extra Descriptors: {len(intf.extra_descriptors)} bytes")
                    parse_uvc_descriptors(intf.extra_descriptors)
                
                for ep in intf:
                    print(f"    Endpoint 0x{ep.bEndpointAddress:02x}: {get_ep_type(ep.bmAttributes)}")
        
        except Exception as e:
            print(f"  Error reading config: {e}")
        
        # Try to read raw interface descriptor
        print("\n--- Probing for Extension Units ---")
        probe_extension_units(dev)


def get_class_name(class_id):
    """Get USB class name."""
    classes = {
        0: "Device",
        1: "Audio",
        2: "CDC",
        3: "HID",
        8: "Mass Storage",
        14: "Video",
        255: "Vendor Specific"
    }
    return classes.get(class_id, "Unknown")


def get_ep_type(attrs):
    """Get endpoint type."""
    types = {0: "Control", 1: "Isochronous", 2: "Bulk", 3: "Interrupt"}
    return types.get(attrs & 0x03, "Unknown")


def parse_uvc_descriptors(data):
    """Parse UVC class-specific descriptors looking for Extension Units."""
    # UVC descriptor subtypes
    VS_UNDEFINED = 0x00
    VS_EXTENSION_UNIT = 0x06
    
    i = 0
    while i < len(data) - 2:
        length = data[i]
        desc_type = data[i+1]
        
        if length < 2:
            break
        
        if desc_type == 0x24:  # CS_INTERFACE
            subtype = data[i+2] if i+2 < len(data) else 0
            print(f"      CS_INTERFACE: subtype={subtype}, len={length}")
            
            if subtype == 6:  # EXTENSION_UNIT
                if length >= 24:
                    unit_id = data[i+3]
                    guid = data[i+4:i+20]
                    print(f"        *** EXTENSION UNIT ID: {unit_id} ***")
                    print(f"        GUID: {guid.hex()}")
        
        i += length


def probe_extension_units(dev):
    """Try to probe for extension units by trying different unit IDs."""
    import struct
    
    # Try different XU Unit IDs
    for xu_id in range(1, 20):
        for intf in [0, 1, 2, 3]:
            # Try GET_CUR on XU
            bmRequestType = 0xA1  # Device-to-host, Class, Interface (GET)
            bRequest = 0x81      # GET_CUR
            wValue = 0x0100      # CS=1 (PT Relative)
            wIndex = (xu_id << 8) | intf
            
            try:
                result = dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, 4, timeout=100)
                print(f"  GET_CUR XU={xu_id} Interface={intf}: {result.tobytes().hex()} <- RESPONDED!")
            except usb.core.USBError:
                pass  # Expected - most won't respond
            except Exception as e:
                pass


if __name__ == "__main__":
    probe_descriptors()
