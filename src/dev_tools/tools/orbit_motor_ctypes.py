"""
Orbit Motor Control - Pure ctypes DirectShow
=============================================
Uses pure ctypes to access IAMCameraControl without comtypes type libraries.
This is the most reliable approach for DirectShow on Windows.
"""
import ctypes
import sys
import time
from ctypes import POINTER, byref, c_long, c_ulong, c_void_p, wintypes

# Load COM libraries
ole32 = ctypes.windll.ole32
oleaut32 = ctypes.windll.oleaut32

# Initialize COM
ole32.CoInitialize(None)

# --- GUID Helper ---
class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", wintypes.BYTE * 8)
    ]

    def __init__(self, guid_string=None):
        super().__init__()
        if guid_string:
            guid_string = guid_string.strip('{}')
            parts = guid_string.split('-')
            self.Data1 = int(parts[0], 16)
            self.Data2 = int(parts[1], 16)
            self.Data3 = int(parts[2], 16)
            data4 = parts[3] + parts[4]
            self.Data4 = (wintypes.BYTE * 8)(*[int(data4[i:i+2], 16) for i in range(0, 16, 2)])

# GUIDs
CLSID_SystemDeviceEnum = GUID("{62BE5D10-60EB-11d0-BD3B-00A0C911CE86}")
CLSID_VideoInputDeviceCategory = GUID("{860BB310-5D01-11d0-BD3B-00A0C911CE86}")
IID_ICreateDevEnum = GUID("{29840822-5B84-11D0-BD3B-00A0C911CE86}")
IID_IPropertyBag = GUID("{55272A00-42CB-11CE-8135-00AA004BB851}")
IID_IBaseFilter = GUID("{56A86895-0AD4-11CE-B03A-0020AF0BA770}")
IID_IAMCameraControl = GUID("{C6E13370-30AC-11d0-A18C-00A0C9118956}")

# Camera Control Properties
CameraControl_Pan = 0
CameraControl_Tilt = 1
CameraControl_Roll = 2
CameraControl_Zoom = 3

# Flags
CameraControl_Flags_Manual = 0x0002

# VARIANT structure (simplified)
class VARIANT(ctypes.Structure):
    _fields_ = [
        ("vt", wintypes.WORD),
        ("wReserved1", wintypes.WORD),
        ("wReserved2", wintypes.WORD),
        ("wReserved3", wintypes.WORD),
        ("bstrVal", wintypes.LPWSTR),
        ("padding", wintypes.DWORD),
    ]

# COM Interface helpers
class IUnknown(ctypes.Structure):
    pass

IUnknown._fields_ = [("lpVtbl", c_void_p)]

def make_QueryInterface(iid):
    """Create a QueryInterface call."""
    def query(self, ppv):
        vtbl = ctypes.cast(self.lpVtbl, POINTER(c_void_p * 3)).contents
        fn = ctypes.cast(vtbl[0], ctypes.WINFUNCTYPE(c_long, c_void_p, POINTER(GUID), POINTER(c_void_p)))
        return fn(ctypes.addressof(self), byref(iid), ppv)
    return query


def get_video_input_filter():
    """Find the Orbit camera filter using raw COM calls."""
    # Create device enumerator
    devenum = c_void_p()
    hr = ole32.CoCreateInstance(
        byref(CLSID_SystemDeviceEnum),
        None,
        1,  # CLSCTX_INPROC_SERVER
        byref(IID_ICreateDevEnum),
        byref(devenum)
    )
    if hr != 0:
        print(f"Failed to create SystemDeviceEnum: {hex(hr)}")
        return None

    print("Created SystemDeviceEnum")

    # Get ICreateDevEnum vtable
    # vtbl[0] = QueryInterface
    # vtbl[1] = AddRef
    # vtbl[2] = Release
    # vtbl[3] = CreateClassEnumerator

    vtbl_ptr = ctypes.cast(devenum, POINTER(c_void_p)).contents
    vtbl = ctypes.cast(vtbl_ptr, POINTER(c_void_p * 10)).contents

    # Call CreateClassEnumerator
    CreateClassEnumerator = ctypes.cast(
        vtbl[3],
        ctypes.WINFUNCTYPE(c_long, c_void_p, POINTER(GUID), POINTER(c_void_p), wintypes.DWORD)
    )

    enum_moniker = c_void_p()
    hr = CreateClassEnumerator(devenum, byref(CLSID_VideoInputDeviceCategory), byref(enum_moniker), 0)

    if hr != 0 or not enum_moniker:
        print(f"Failed to create class enumerator: {hex(hr)}")
        return None

    print("Created class enumerator")

    # Get IEnumMoniker vtable
    vtbl_ptr = ctypes.cast(enum_moniker, POINTER(c_void_p)).contents
    vtbl = ctypes.cast(vtbl_ptr, POINTER(c_void_p * 10)).contents

    # vtbl[3] = Next
    Next = ctypes.cast(
        vtbl[3],
        ctypes.WINFUNCTYPE(c_long, c_void_p, c_ulong, POINTER(c_void_p), POINTER(c_ulong))
    )

    # Enumerate monikers looking for Orbit
    while True:
        moniker = c_void_p()
        fetched = c_ulong()
        hr = Next(enum_moniker, 1, byref(moniker), byref(fetched))

        if hr != 0 or fetched.value == 0:
            break

        # Get moniker vtable
        vtbl_ptr = ctypes.cast(moniker, POINTER(c_void_p)).contents
        vtbl = ctypes.cast(vtbl_ptr, POINTER(c_void_p * 20)).contents

        # BindToStorage to get IPropertyBag (vtbl[8])
        BindToStorage = ctypes.cast(
            vtbl[8],
            ctypes.WINFUNCTYPE(c_long, c_void_p, c_void_p, c_void_p, POINTER(GUID), POINTER(c_void_p))
        )

        propbag = c_void_p()
        hr = BindToStorage(moniker, None, None, byref(IID_IPropertyBag), byref(propbag))

        if hr == 0 and propbag:
            # Read FriendlyName
            bag_vtbl_ptr = ctypes.cast(propbag, POINTER(c_void_p)).contents
            bag_vtbl = ctypes.cast(bag_vtbl_ptr, POINTER(c_void_p * 5)).contents

            # vtbl[3] = Read
            Read = ctypes.cast(
                bag_vtbl[3],
                ctypes.WINFUNCTYPE(c_long, c_void_p, wintypes.LPCWSTR, POINTER(VARIANT), c_void_p)
            )

            var = VARIANT()
            var.vt = 8  # VT_BSTR
            hr = Read(propbag, "FriendlyName", byref(var), None)

            if hr == 0 and var.bstrVal:
                name = var.bstrVal
                print(f"Found device: {name}")

                # Try all devices since name matching may be unreliable
                # BindToObject to get IBaseFilter (vtbl[7])
                BindToObject = ctypes.cast(
                    vtbl[7],
                    ctypes.WINFUNCTYPE(c_long, c_void_p, c_void_p, c_void_p, POINTER(GUID), POINTER(c_void_p))
                )

                base_filter = c_void_p()
                hr = BindToObject(moniker, None, None, byref(IID_IBaseFilter), byref(base_filter))

                if hr == 0 and base_filter:
                    print(f"Got IBaseFilter for: {name}")
                    return base_filter
        else:
            # Try even without reading name
            print("Trying device without name...")
            BindToObject = ctypes.cast(
                vtbl[7],
                ctypes.WINFUNCTYPE(c_long, c_void_p, c_void_p, c_void_p, POINTER(GUID), POINTER(c_void_p))
            )

            base_filter = c_void_p()
            hr = BindToObject(moniker, None, None, byref(IID_IBaseFilter), byref(base_filter))

            if hr == 0 and base_filter:
                print("Got IBaseFilter!")
                return base_filter


    return None


def test_camera_control(filter_ptr):
    """Query and test IAMCameraControl."""
    # Get filter vtable
    vtbl_ptr = ctypes.cast(filter_ptr, POINTER(c_void_p)).contents
    vtbl = ctypes.cast(vtbl_ptr, POINTER(c_void_p * 3)).contents

    # QueryInterface for IAMCameraControl
    QueryInterface = ctypes.cast(
        vtbl[0],
        ctypes.WINFUNCTYPE(c_long, c_void_p, POINTER(GUID), POINTER(c_void_p))
    )

    cam_control = c_void_p()
    hr = QueryInterface(filter_ptr, byref(IID_IAMCameraControl), byref(cam_control))

    if hr != 0 or not cam_control:
        print(f"IAMCameraControl not available: {hex(hr)}")
        return False

    print("Got IAMCameraControl!")

    # Get vtable
    cc_vtbl_ptr = ctypes.cast(cam_control, POINTER(c_void_p)).contents
    cc_vtbl = ctypes.cast(cc_vtbl_ptr, POINTER(c_void_p * 6)).contents

    # vtbl[3] = GetRange(Property, pMin, pMax, pSteppingDelta, pDefault, pCapsFlags)
    GetRange = ctypes.cast(
        cc_vtbl[3],
        ctypes.WINFUNCTYPE(c_long, c_void_p, c_long, POINTER(c_long), POINTER(c_long), POINTER(c_long), POINTER(c_long), POINTER(c_long))
    )

    # vtbl[4] = Set(Property, lValue, Flags)
    Set = ctypes.cast(
        cc_vtbl[4],
        ctypes.WINFUNCTYPE(c_long, c_void_p, c_long, c_long, c_long)
    )

    # vtbl[5] = Get(Property, plValue, plFlags)
    Get = ctypes.cast(
        cc_vtbl[5],
        ctypes.WINFUNCTYPE(c_long, c_void_p, c_long, POINTER(c_long), POINTER(c_long))
    )

    # Check pan range
    pMin, pMax, pStep, pDefault, pCaps = c_long(), c_long(), c_long(), c_long(), c_long()
    hr = GetRange(cam_control, CameraControl_Pan, byref(pMin), byref(pMax), byref(pStep), byref(pDefault), byref(pCaps))

    if hr != 0:
        print(f"GetRange(Pan) failed: {hex(hr)}")
        return False

    print(f"Pan range: min={pMin.value}, max={pMax.value}, step={pStep.value}, default={pDefault.value}")

    # Get current pan
    cur_pan, cur_flags = c_long(), c_long()
    hr = Get(cam_control, CameraControl_Pan, byref(cur_pan), byref(cur_flags))
    print(f"Current pan: {cur_pan.value}")

    # Move right
    print("\nMoving camera RIGHT...")
    new_pan = cur_pan.value + (pStep.value * 50)
    new_pan = min(new_pan, pMax.value)
    hr = Set(cam_control, CameraControl_Pan, new_pan, CameraControl_Flags_Manual)
    print(f"Set pan to {new_pan}: result={hex(hr) if hr else 'OK'}")

    time.sleep(1)

    # Check tilt
    hr = GetRange(cam_control, CameraControl_Tilt, byref(pMin), byref(pMax), byref(pStep), byref(pDefault), byref(pCaps))
    if hr == 0:
        print(f"\nTilt range: min={pMin.value}, max={pMax.value}, step={pStep.value}")

        cur_tilt = c_long()
        Get(cam_control, CameraControl_Tilt, byref(cur_tilt), byref(cur_flags))
        print(f"Current tilt: {cur_tilt.value}")

        # Move up
        print("\nMoving camera UP...")
        new_tilt = cur_tilt.value + (pStep.value * 30)
        new_tilt = min(new_tilt, pMax.value)
        hr = Set(cam_control, CameraControl_Tilt, new_tilt, CameraControl_Flags_Manual)
        print(f"Set tilt to {new_tilt}: result={hex(hr) if hr else 'OK'}")

        time.sleep(1)

    # Reset to center
    print("\nResetting to center...")
    Set(cam_control, CameraControl_Pan, 0, CameraControl_Flags_Manual)
    Set(cam_control, CameraControl_Tilt, 0, CameraControl_Flags_Manual)

    return True


def main():
    print("=" * 60)
    print("  Orbit Motor Control - Pure ctypes DirectShow")
    print("=" * 60)
    print()

    filter_ptr = get_video_input_filter()
    if not filter_ptr:
        print("Could not find Orbit camera")
        return 1

    print()
    if test_camera_control(filter_ptr):
        print()
        print("SUCCESS! Motor control works via IAMCameraControl.")
        print()
        print("The camera should have moved right, then up, then reset.")
        return 0
    else:
        print()
        print("IAMCameraControl not supported by this driver.")
        print("The Logitech driver may use proprietary methods.")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        ole32.CoUninitialize()
