"""
GUID Discovery Scanner
=======================
Scans the camera's DirectShow filter for all supported property set GUIDs
to find the actual motor control GUID.
"""
import logging
import uuid
import ctypes
from ctypes import wintypes
import comtypes
import comtypes.client

logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
logger = logging.getLogger(__name__)

# DirectShow GUIDs
CLSID_SystemDeviceEnum = "{62BE5D10-60EB-11D0-BD3B-00A0C911CE86}"
CLSID_VideoInputDeviceCategory = "{860BB310-5D01-11D0-BD3B-00A0C911CE86}"
IID_IKsPropertySet = "{31EFAC30-515C-11D0-A9AA-00AA0061BE93}"
KSPROPERTY_TYPE_SET = 0x00000002
KSPROPERTY_TYPE_GET = 0x00000001

# Known UVC extension unit GUIDs to try
GUIDS_TO_TRY = [
    # Logitech Motor Control
    "{63610662-5070-49Ab-B8CC-B3855E8D2256}",
    "{63610682-5070-49AB-B8CC-B3855E8D2256}",
    # Logitech UVC Camera Control
    "{A29E7641-DE04-47E3-8B2B-F4341AFF003B}",
    # Microsoft UVC Camera Control
    "{09A00CBB-8A47-4BCD-96DE-2B3CADC2C68D}",
    # UVC Pan/Tilt Absolute
    "{92F9A3C2-58C4-4C57-9FD0-C96F8E0D1E0E}",
    # Generic Logitech
    "{1F5D4CA4-6A9D-4D6F-8AA7-1C0B3B2D3E4F}",
    # ITU H.264 Extension Unit GUID
    "{A29E7641-DE04-47E3-8B2B-F4341AFF003B}",
    # Common Logitech Extensions
    "{28F03370-6311-13D0-B6A0-00A0C90F56C6}",
    # Pan/Tilt specific
    "{5786B5F0-58F8-11E0-8AB9-0024E8E3B98C}",
    # Another Logitech variant
    "{7AAD3E7B-6F4C-4FB1-8B95-6D6D14AD3F6E}",
]

# Standard UVC Processing Unit and Camera Terminal controls
UVC_STANDARD_CONTROLS = [
    # {GUID, Property ID, Name}
    ("{C6E13340-30AC-11D0-A18C-00A0C9118956}", 1, "VideoProcAmp_Brightness"),
    ("{C6E13340-30AC-11D0-A18C-00A0C9118956}", 2, "VideoProcAmp_Contrast"),
    ("{C6E13340-30AC-11D0-A18C-00A0C9118956}", 3, "VideoProcAmp_Hue"),
    ("{C6E13370-30AC-11D0-A18C-00A0C9118956}", 9, "CameraControl_Pan"),
    ("{C6E13370-30AC-11D0-A18C-00A0C9118956}", 10, "CameraControl_Tilt"),
    ("{C6E13370-30AC-11D0-A18C-00A0C9118956}", 14, "CameraControl_PanRelative"),
    ("{C6E13370-30AC-11D0-A18C-00A0C9118956}", 15, "CameraControl_TiltRelative"),
    ("{C6E13370-30AC-11D0-A18C-00A0C9118956}", 11, "CameraControl_Roll"),
]


def main():
    print("=" * 70)
    print("  GUID Discovery Scanner for Logitech Orbit Camera")
    print("  (Looking for motor control property sets)")
    print("=" * 70)
    
    # Import XUController classes
    from orbcam.logitech.xu_control import (
        ICreateDevEnum, IEnumMoniker, IMoniker, IKsPropertySet, IPropertyBag
    )
    
    # Create device enumerator
    devenum = comtypes.client.CreateObject(
        CLSID_SystemDeviceEnum,
        clsctx=comtypes.CLSCTX_INPROC_SERVER,
        interface=ICreateDevEnum
    )
    
    # Find Logitech camera
    print("\nSearching for Logitech camera...")
    cat_guid = comtypes.GUID(CLSID_VideoInputDeviceCategory)
    enum_moniker_ptr = devenum.CreateClassEnumerator(cat_guid, 0)
    
    if not enum_moniker_ptr:
        print("ERROR: No video devices found!")
        return 1
    
    enum_moniker = enum_moniker_ptr.QueryInterface(IEnumMoniker)
    
    camera_moniker = None
    while True:
        try:
            res = enum_moniker.Next(1)
            if not res:
                break
            moniker_ptr, fetched = res
            if fetched == 0 or not moniker_ptr:
                break
            
            moniker = moniker_ptr.QueryInterface(IMoniker)
            
            # Get device name
            try:
                IPropertyBag_IID = comtypes.GUID("{55272a00-42cb-11ce-8135-00aa004bb851}")
                p_bag = moniker.BindToStorage(None, None, ctypes.byref(IPropertyBag_IID)).QueryInterface(IPropertyBag)
                name = str(p_bag.Read("FriendlyName", None))
                
                if "logitech" in name.lower() or "orbit" in name.lower() or "quickcam" in name.lower():
                    print(f"Found: {name}")
                    camera_moniker = moniker
                    break
            except:
                pass
        except:
            break
    
    if not camera_moniker:
        print("ERROR: Logitech camera not found!")
        return 1
    
    # Bind to filter
    print("\nBinding to camera filter...")
    IID_IBaseFilter = comtypes.GUID("{56a86895-0ad4-11ce-b03a-0020af0ba770}")
    filter_obj = camera_moniker.BindToObject(None, None, ctypes.byref(IID_IBaseFilter))
    
    # Get IKsPropertySet
    IKsPropertySet_IID = comtypes.GUID(IID_IKsPropertySet)
    prop_set = filter_obj.QueryInterface(IKsPropertySet)
    
    print("\n" + "=" * 70)
    print("  Scanning for Supported GUIDs")
    print("=" * 70)
    
    found_guids = []
    
    # Test standard UVC Camera Control GUIDs
    print("\n--- Testing Standard UVC Camera Controls ---")
    for guid_str, prop_id, name in UVC_STANDARD_CONTROLS:
        try:
            guid = comtypes.GUID(guid_str)
            support = prop_set.QuerySupported(guid, prop_id)
            if support:
                action = []
                if support & KSPROPERTY_TYPE_GET:
                    action.append("GET")
                if support & KSPROPERTY_TYPE_SET:
                    action.append("SET")
                print(f"  FOUND: {name} ({guid_str}) - {'/'.join(action)}")
                found_guids.append((guid_str, prop_id, name, support))
        except Exception as e:
            pass  # Not supported
    
    # Test known extension GUIDs
    print("\n--- Testing Known Extension Unit GUIDs ---")
    for guid_str in GUIDS_TO_TRY:
        for prop_id in range(1, 5):  # Test property IDs 1-4
            try:
                guid = comtypes.GUID(guid_str)
                support = prop_set.QuerySupported(guid, prop_id)
                if support:
                    action = []
                    if support & KSPROPERTY_TYPE_GET:
                        action.append("GET")
                    if support & KSPROPERTY_TYPE_SET:
                        action.append("SET")
                    print(f"  FOUND: {guid_str} PropID={prop_id} - {'/'.join(action)}")
                    found_guids.append((guid_str, prop_id, f"XU_{prop_id}", support))
            except:
                pass
    
    print("\n" + "=" * 70)
    print("  Summary")
    print("=" * 70)
    
    if found_guids:
        print(f"\nFound {len(found_guids)} supported property sets:")
        for guid, prop_id, name, support in found_guids:
            can_set = "YES" if support & KSPROPERTY_TYPE_SET else "NO"
            print(f"  - {name}: GUID={guid}, PropID={prop_id}, Can SET: {can_set}")
        
        # Check for pan/tilt specifically
        ptz_controls = [g for g in found_guids if "Pan" in g[2] or "Tilt" in g[2]]
        if ptz_controls:
            print("\n*** FOUND PTZ CONTROLS! ***")
            for g in ptz_controls:
                print(f"  {g[2]}: {g[0]} PropID={g[1]}")
    else:
        print("\nNo supported property sets found. Camera may not expose motor via IKsPropertySet.")
    
    return 0


if __name__ == "__main__":
    exit(main())
