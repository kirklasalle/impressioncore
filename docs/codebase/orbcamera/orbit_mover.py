import comtypes
import comtypes.client
import ctypes
from ctypes import wintypes
import time
import uuid

# IDs
IID_IBaseFilter = "{56A86895-0AD4-11CE-B03A-0020AF0BA770}"
IID_IKsControl = "{28F54881-2CD1-11D1-ADE2-00A0C9223196}"
GUID_MOTOR_CONTROL_1 = uuid.UUID("{63610682-5070-49AB-B8CC-B3855E8D2256}")

class KSPROPERTY(ctypes.Structure):
    _fields_ = [
        ("Set", ctypes.c_byte * 16),
        ("Id", wintypes.ULONG),
        ("Flags", wintypes.ULONG),
    ]

# Define IKsControl properly
class IKsControl(comtypes.IUnknown):
    _iid_ = comtypes.GUID(IID_IKsControl)
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "KsProperty",
                    (['in'], ctypes.POINTER(KSPROPERTY), "pProp"),
                    (['in'], wintypes.ULONG, "ulPropLen"),
                    (['in', 'out'], ctypes.c_void_p, "pData"),
                    (['in'], wintypes.ULONG, "ulDataLen"),
                    (['out'], ctypes.POINTER(wintypes.ULONG), "pBytesReturned")),
    ]

class IEnumMoniker(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{00000102-0000-0000-C000-000000000046}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "Next",
                    (['in'], wintypes.ULONG, "celt"),
                    (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "rgelt"),
                    (['out'], ctypes.POINTER(wintypes.ULONG), "pceltFetched")),
    ]

class ICreateDevEnum(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{29840822-5B84-11D0-BD3B-00A0C911CE86}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "CreateClassEnumerator",
                    (['in'], comtypes.GUID, "clsidDeviceClass"),
                    (['out'], ctypes.POINTER(ctypes.POINTER(IEnumMoniker)), "ppEnumMoniker"),
                    (['in'], wintypes.ULONG, "dwFlags")),
    ]

def run():
    print("Searching for Orbit and attempting direct move...")
    devenum = comtypes.client.CreateObject("{62BE5D10-60EB-11D0-BD3B-00A0C911CE86}", interface=ICreateDevEnum)
    cat_video = comtypes.GUID("{860BB310-5D01-11D0-BD3B-00A0C911CE86}")
    
    enum_moniker = devenum.CreateClassEnumerator(cat_video, 0)
    if not enum_moniker:
        print("No video devices.")
        return
        
    while True:
        try:
            # comtypes Next(1) returns (pointer, fetched)
            mon_ptr, fetched = enum_moniker.Next(1)
            if fetched == 0 or not mon_ptr: break
            
            mon = mon_ptr.QueryInterface(comtypes.IUnknown)
            # Bind to filter
            # IMoniker::BindToObject is method 8
            vt = ctypes.cast(mon.lpVtbl, ctypes.POINTER(ctypes.c_void_p))
            bind_to_obj = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(comtypes.GUID), ctypes.POINTER(ctypes.c_void_p))(vt[8])
            p_filt = ctypes.c_void_p()
            fiid = comtypes.GUID(IID_IBaseFilter)
            if bind_to_obj(mon, None, None, ctypes.byref(fiid), ctypes.byref(p_filt)) == 0:
                filt = comtypes.IUnknown(p_filt)
                print("  [+] Bound to Filter.")
                try:
                    iks = filt.QueryInterface(IKsControl)
                    print("  [+] IKsControl acquired!")
                    # Test move
                    prop = KSPROPERTY()
                    gb = GUID_MOTOR_CONTROL_1.bytes_le
                    for i in range(16): prop.Set[i] = gb[i]
                    prop.Id = 1; prop.Flags = 2; ret = wintypes.ULONG(0)
                    data = ctypes.create_string_buffer(bytes([0x80, 0x00, 0x00, 0x00]))
                    if iks.KsProperty(ctypes.byref(prop), ctypes.sizeof(prop), ctypes.cast(data, ctypes.c_void_p), 4, ctypes.byref(ret)) == 0:
                        print("  [!!!] SUCCESS! Move command sent via IKsControl.")
                except:
                    print("  [-] IKsControl selection failed on this filter.")
        except Exception as e:
            print(f"Error in iteration: {e}")
            break

if __name__ == "__main__":
    run()
