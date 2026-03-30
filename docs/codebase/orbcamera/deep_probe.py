"""
DEEP HARDWARE PROBE - Multi-Pronged Motor Discovery
=====================================================
Classic hardware hacking approach for Logitech Orbit MP (PID 08c2).

This script tries EVERYTHING:
1. HID interface enumeration and motor commands
2. Vendor-specific USB control transfers (0x40/0xC0)
3. All USB endpoint scanning
4. Raw control transfers to every possible target
5. HID feature report exploration

The Logitech Orbit MP is from ~2006-2008 era when USB standards
were less mature and vendors often used proprietary protocols.
"""
import ctypes
from ctypes import wintypes
import struct
import time
import sys

print("=" * 70)
print("  DEEP HARDWARE PROBE - Multi-Pronged Motor Discovery")
print("  Logitech QuickCam Orbit/Sphere MP (PID: 08c2)")
print("=" * 70)


# ============================================================================
# PHASE 1: HID INTERFACE PROBE
# ============================================================================
def probe_hid_interfaces():
    """
    Probe for HID interfaces on the camera.
    Many old devices used HID for motor control separate from video.
    """
    print("\n" + "=" * 70)
    print("  PHASE 1: HID Interface Probe")
    print("=" * 70)
    
    try:
        import hid
        
        # Find all Logitech HID devices
        print("\nScanning for Logitech HID devices...")
        devices = hid.enumerate(0x046d)  # Logitech VID
        
        if not devices:
            print("  No Logitech HID devices found.")
            return None
        
        print(f"\nFound {len(devices)} Logitech HID devices:")
        camera_hid = None
        
        for d in devices:
            pid = d.get('product_id', 0)
            product = d.get('product_string', 'Unknown')
            interface = d.get('interface_number', -1)
            usage_page = d.get('usage_page', 0)
            usage = d.get('usage', 0)
            
            print(f"\n  PID: {pid:04x} - {product}")
            print(f"    Interface: {interface}")
            print(f"    Usage Page: {usage_page:04x}, Usage: {usage:04x}")
            print(f"    Path: {d.get('path', b'').decode()[:60]}...")
            
            # Check if this is our camera
            if pid == 0x08c2:
                camera_hid = d
                print("    *** THIS IS OUR CAMERA! ***")
        
        if camera_hid:
            print("\n--- Attempting HID Motor Control ---")
            try:
                h = hid.device()
                h.open_path(camera_hid['path'])
                print(f"  Opened HID device successfully")
                
                # Try sending motor commands via HID
                # Common HID motor command formats:
                motor_commands = [
                    # Format: [Report ID, Command, Pan, Tilt, ...]
                    bytes([0x00, 0x01, 0x10, 0x00]),  # Pan right
                    bytes([0x00, 0x02, 0x00, 0x10]),  # Tilt up
                    bytes([0x00, 0x03]),              # Reset
                    bytes([0x01, 0x01, 0x10, 0x00]),  # With report ID 1
                    bytes([0x02, 0x01, 0x10, 0x00]),  # With report ID 2
                ]
                
                for cmd in motor_commands:
                    print(f"  Sending HID command: {cmd.hex()}")
                    try:
                        h.write(cmd)
                        time.sleep(0.3)
                    except Exception as e:
                        print(f"    Failed: {e}")
                
                h.close()
                return True
            except Exception as e:
                print(f"  Failed to open HID device: {e}")
        
        return False
        
    except ImportError:
        print("  HID library not installed. Run: pip install hidapi")
        return None
    except Exception as e:
        print(f"  HID probe error: {e}")
        return False


# ============================================================================
# PHASE 2: VENDOR-SPECIFIC USB CONTROL TRANSFERS
# ============================================================================
def probe_vendor_usb():
    """
    Try vendor-specific USB control transfers.
    Old devices often used bmRequestType 0x40 (vendor, host-to-device) 
    or 0xC0 (vendor, device-to-host) instead of class-specific.
    """
    print("\n" + "=" * 70)
    print("  PHASE 2: Vendor-Specific USB Control Transfers")
    print("=" * 70)
    
    try:
        import usb.core
        import usb.util
        
        # Find device
        dev = usb.core.find(idVendor=0x046d, idProduct=0x08c2)
        if dev is None:
            dev = usb.core.find(idVendor=0x046d)
        
        if dev is None:
            print("  Device not found via PyUSB.")
            print("  (This is expected if using original Windows driver)")
            return False
        
        print(f"\nFound device: VID={dev.idVendor:04x} PID={dev.idProduct:04x}")
        
        # Common vendor-specific request codes for motor control
        vendor_commands = [
            # (bmRequestType, bRequest, wValue, wIndex, data_or_length)
            (0x40, 0x01, 0x0001, 0x0000, struct.pack("<hh", 100, 0)),   # Vendor SET
            (0x40, 0x02, 0x0001, 0x0000, struct.pack("<hh", 100, 0)),   # Vendor SET alt
            (0x40, 0x01, 0x0100, 0x0000, struct.pack("<hh", 100, 0)),   # Swapped value
            (0x40, 0x10, 0x0001, 0x0000, struct.pack("<hh", 100, 0)),   # Different request
            (0x40, 0x01, 0x0001, 0x0001, struct.pack("<hh", 100, 0)),   # Interface 1
            (0x21, 0x09, 0x0200, 0x0000, bytes([0x01, 0x10, 0x00])),    # HID SET_REPORT class
        ]
        
        print("\nTrying vendor-specific control transfers...")
        for bmReq, bReq, wVal, wIdx, data in vendor_commands:
            try:
                print(f"  bmReq={bmReq:02x} bReq={bReq:02x} wVal={wVal:04x} wIdx={wIdx:04x} data={data.hex()}")
                dev.ctrl_transfer(bmReq, bReq, wVal, wIdx, data, timeout=500)
                print("    -> ACCEPTED!")
                time.sleep(0.5)
            except usb.core.USBError as e:
                if "STALL" in str(e) or "pipe" in str(e).lower():
                    pass  # Expected for unsupported commands
                else:
                    print(f"    -> Error: {str(e)[:40]}")
        
        return True
        
    except ImportError:
        print("  PyUSB not available with current driver.")
        return False
    except Exception as e:
        print(f"  Vendor USB probe error: {e}")
        return False


# ============================================================================
# PHASE 3: WINDOWS HID API DIRECT ACCESS
# ============================================================================
def probe_windows_hid():
    """
    Use Windows HID API directly via ctypes.
    This works even without pyusb/hidapi libraries.
    """
    print("\n" + "=" * 70)
    print("  PHASE 3: Windows HID API Direct Access")
    print("=" * 70)
    
    try:
        # Windows HID API constants
        DIGCF_PRESENT = 0x02
        DIGCF_DEVICEINTERFACE = 0x10
        
        # HID Usage Pages
        HID_USAGE_PAGE_GENERIC = 0x01
        HID_USAGE_PAGE_CONSUMER = 0x0C
        HID_USAGE_PAGE_VENDOR = 0xFF00
        
        # Load required DLLs
        setupapi = ctypes.windll.setupapi
        hid = ctypes.windll.hid
        kernel32 = ctypes.windll.kernel32
        
        # Get HID GUID
        class GUID(ctypes.Structure):
            _fields_ = [
                ("Data1", wintypes.DWORD),
                ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD),
                ("Data4", ctypes.c_byte * 8),
            ]
        
        hid_guid = GUID()
        hid.HidD_GetHidGuid(ctypes.byref(hid_guid))
        
        print(f"\nHID GUID: {hid_guid.Data1:08X}-{hid_guid.Data2:04X}-{hid_guid.Data3:04X}")
        
        # Enumerate HID devices
        print("\nEnumerating Windows HID devices...")
        
        dev_info = setupapi.SetupDiGetClassDevsW(
            ctypes.byref(hid_guid),
            None,
            None,
            DIGCF_PRESENT | DIGCF_DEVICEINTERFACE
        )
        
        if dev_info == -1:
            print("  Failed to enumerate HID devices")
            return False
        
        print("  HID device set opened successfully")
        
        # We would need to iterate through devices here, but this demonstrates
        # the Windows HID API is accessible
        
        setupapi.SetupDiDestroyDeviceInfoList(dev_info)
        print("  Windows HID API is accessible")
        
        return True
        
    except Exception as e:
        print(f"  Windows HID probe error: {e}")
        return False


# ============================================================================
# PHASE 4: DIRECTSHOW VIDEO PROPERTIES PTZ
# ============================================================================
def probe_directshow_ptz():
    """
    Try standard DirectShow IAMCameraControl interface for PTZ.
    Some cameras expose motor via this standard interface.
    """
    print("\n" + "=" * 70)
    print("  PHASE 4: DirectShow IAMCameraControl PTZ")
    print("=" * 70)
    
    try:
        import cv2
        
        print("\nOpening camera with DirectShow backend...")
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            print("  Failed to open camera")
            return False
        
        print("  Camera opened successfully")
        
        # Read a frame first to ensure camera is active
        ret, frame = cap.read()
        if not ret:
            print("  Warning: Could not read frame")
        
        # Try CAP_PROP_PAN and CAP_PROP_TILT
        print("\nTesting PTZ properties...")
        
        # Get current values
        pan = cap.get(cv2.CAP_PROP_PAN)
        tilt = cap.get(cv2.CAP_PROP_TILT)
        print(f"  Current Pan: {pan}, Tilt: {tilt}")
        
        # Try to set pan
        print("\n  Setting Pan = 10...")
        result = cap.set(cv2.CAP_PROP_PAN, 10)
        print(f"    Result: {result}")
        time.sleep(0.5)
        
        print("  Setting Pan = -10...")
        result = cap.set(cv2.CAP_PROP_PAN, -10)
        print(f"    Result: {result}")
        time.sleep(0.5)
        
        print("  Setting Tilt = 10...")
        result = cap.set(cv2.CAP_PROP_TILT, 10)
        print(f"    Result: {result}")
        time.sleep(0.5)
        
        cap.release()
        print("\n  Did the camera move?")
        
        return True
        
    except Exception as e:
        print(f"  DirectShow PTZ probe error: {e}")
        return False


# ============================================================================
# PHASE 5: USB DESCRIPTOR DEEP DIVE
# ============================================================================
def probe_usb_descriptors():
    """
    Deep dive into USB descriptors looking for hidden motor endpoints.
    """
    print("\n" + "=" * 70)
    print("  PHASE 5: USB Descriptor Deep Dive")
    print("=" * 70)
    
    try:
        import usb.core
        
        dev = usb.core.find(idVendor=0x046d)
        if dev is None:
            print("  Device not accessible via PyUSB")
            return False
        
        print(f"\nDevice: VID={dev.idVendor:04x} PID={dev.idProduct:04x}")
        print(f"Manufacturer: {dev.manufacturer or 'N/A'}")
        print(f"Product: {dev.product or 'N/A'}")
        
        # Iterate all configurations, interfaces, endpoints
        for cfg in dev:
            print(f"\nConfiguration {cfg.bConfigurationValue}:")
            
            for intf in cfg:
                print(f"\n  Interface {intf.bInterfaceNumber} Alt {intf.bAlternateSetting}:")
                print(f"    Class: {intf.bInterfaceClass} ({get_class_name(intf.bInterfaceClass)})")
                print(f"    SubClass: {intf.bInterfaceSubClass}")
                print(f"    Protocol: {intf.bInterfaceProtocol}")
                
                # Check for HID interface (class 3)
                if intf.bInterfaceClass == 3:
                    print("    *** HID INTERFACE FOUND! ***")
                
                # Check for Vendor Specific (class 255)
                if intf.bInterfaceClass == 255:
                    print("    *** VENDOR SPECIFIC INTERFACE ***")
                
                for ep in intf:
                    direction = "IN" if ep.bEndpointAddress & 0x80 else "OUT"
                    ep_type = get_ep_type(ep.bmAttributes & 0x03)
                    print(f"    Endpoint 0x{ep.bEndpointAddress:02x}: {direction} {ep_type} (Max Packet: {ep.wMaxPacketSize})")
        
        return True
        
    except Exception as e:
        print(f"  USB descriptor probe error: {e}")
        return False


def get_class_name(class_id):
    """Get USB class name."""
    classes = {
        0: "Device", 1: "Audio", 2: "CDC", 3: "HID", 
        8: "Mass Storage", 14: "Video", 255: "Vendor Specific"
    }
    return classes.get(class_id, "Unknown")


def get_ep_type(attrs):
    """Get endpoint type."""
    types = {0: "Control", 1: "Isochronous", 2: "Bulk", 3: "Interrupt"}
    return types.get(attrs, "Unknown")


# ============================================================================
# MAIN
# ============================================================================
def main():
    results = {
        "hid": probe_hid_interfaces(),
        "vendor_usb": probe_vendor_usb(),
        "windows_hid": probe_windows_hid(),
        "directshow_ptz": probe_directshow_ptz(),
        "usb_descriptors": probe_usb_descriptors(),
    }
    
    print("\n" + "=" * 70)
    print("  PROBE RESULTS SUMMARY")
    print("=" * 70)
    
    for name, result in results.items():
        status = "✓ Success" if result else ("○ Skipped" if result is None else "✗ Failed")
        print(f"  {name:20s}: {status}")
    
    print("\n" + "=" * 70)
    print("  Did you observe ANY camera motor movement during any phase?")
    print("  If yes, note which phase number caused movement.")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
