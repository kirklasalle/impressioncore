import ctypes
from ctypes import wintypes

# SetupAPI constants
DIGCF_PRESENT = 0x00000002
DIGCF_ALLCLASSES = 0x00000004
DIGCF_DEVICEINTERFACE = 0x00000010

class SP_DEVINFO_DATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("ClassGuid", ctypes.c_byte * 16),
        ("DevInst", wintypes.DWORD),
        ("Reserved", ctypes.c_void_p),
    ]

def scan_setupapi():
    print("Enumerating all present devices for Logitech VID_046D & PID_08C2...")
    setupapi = ctypes.windll.setupapi
    
    # Get all present devices
    handle = setupapi.SetupDiGetClassDevsW(None, None, None, DIGCF_ALLCLASSES | DIGCF_PRESENT)
    if handle == -1:
        print("SetupDiGetClassDevsW failed")
        return

    try:
        devinfo = SP_DEVINFO_DATA()
        devinfo.cbSize = ctypes.sizeof(SP_DEVINFO_DATA)
        index = 0
        
        while setupapi.SetupDiEnumDeviceInfo(handle, index, ctypes.byref(devinfo)):
            index += 1
            
            # Get Device Instance ID
            buffer = ctypes.create_unicode_buffer(512)
            setupapi.SetupDiGetDeviceInstanceIdW(handle, ctypes.byref(devinfo), buffer, 512, None)
            instance_id = buffer.value
            
            if "VID_046D" in instance_id.upper():
                print(f"\n[+] Found Logitech Device: {instance_id}")
                
                # Get Friendly Name
                friendly_name = ctypes.create_unicode_buffer(512)
                if setupapi.SetupDiGetDeviceRegistryPropertyW(handle, ctypes.byref(devinfo), 12, # SPDRP_FRIENDLYNAME
                                                              None, friendly_name, 512, None):
                    print(f"    Friendly Name: {friendly_name.value}")
                else:
                    # Try DeviceDesc
                    setupapi.SetupDiGetDeviceRegistryPropertyW(handle, ctypes.byref(devinfo), 0, # SPDRP_DEVICEDESC
                                                              None, friendly_name, 512, None)
                    print(f"    Device Desc: {friendly_name.value}")
                
                # Get Service
                service = ctypes.create_unicode_buffer(512)
                if setupapi.SetupDiGetDeviceRegistryPropertyW(handle, ctypes.byref(devinfo), 4, # SPDRP_SERVICE
                                                              None, service, 512, None):
                    print(f"    Service: {service.value}")

                # List Interfaces for this device
                print("    Interfaces:")
                # We need to enumerate interfaces... this is harder but let's try a common list
                interface_guids = [
                    "{65e8773d-8f56-11d0-a3b9-00a0c9223196}", # KSCATEGORY_CAPTURE
                    "{69917243-BD97-11D0-AB1E-00A0C9223196}", # KSCATEGORY_VIDEO
                    "{E5323777-F976-4f5b-9B55-B94699C46E44}", # KSCATEGORY_DATACOMPRESSION
                    "{860BB310-5D01-11D0-BD3B-00A0C911CE86}", # Video Input
                    "{ad33c598-a15f-11d2-a722-0000f8757064}", # Logitech specific?
                ]
                
                # Better: Use SetupDiEnumDeviceInterfaces with our devinfo
                # But that requires knowing the interface class GUID.
                # Let's try to query the device interfaces directly for this devinfo.
                pass

    finally:
        setupapi.SetupDiDestroyDeviceInfoList(handle)

if __name__ == "__main__":
    scan_setupapi()
