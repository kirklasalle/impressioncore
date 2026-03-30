import comtypes
import comtypes.client
import ctypes
from ctypes import wintypes

class IPropertyBag(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{55272a00-42cb-11ce-8135-00aa004bb851}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "Read",
                    (['in'], wintypes.LPWSTR, "pszPropName"),
                    (['in', 'out'], ctypes.POINTER(comtypes.automation.VARIANT), "pVar"),
                    (['in'], ctypes.c_void_p, "pErrorLog")),
    ]

class IEnumMoniker(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{00000102-0000-0000-C000-000000000046}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "Next",
                    (['in'], wintypes.ULONG, "celt"),
                    (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "rgelt"),
                    (['out'], ctypes.POINTER(wintypes.ULONG), "pceltFetched")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "Skip", (['in'], wintypes.ULONG, "celt")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "Reset"),
        comtypes.COMMETHOD([], comtypes.HRESULT, "Clone", (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppenum")),
    ]

class IMoniker(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{0000010c-0000-0000-C000-000000000046}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "GetClassID", (['out'], ctypes.POINTER(comtypes.GUID), "pClassID")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "IsDirty"),
        comtypes.COMMETHOD([], comtypes.HRESULT, "Load", (['in'], ctypes.c_void_p, "pStm")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "Save", (['in'], ctypes.c_void_p, "pStm"), (['in'], wintypes.BOOL, "fClearDirty")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "GetSizeMax", (['out'], ctypes.POINTER(ctypes.c_ulonglong), "pcbSize")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "BindToObject",
                    (['in'], ctypes.c_void_p, "pbc"),
                    (['in'], ctypes.c_void_p, "pmkToLeft"),
                    (['in'], ctypes.POINTER(comtypes.GUID), "riidResult"),
                    (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppvResult")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "BindToStorage",
                    (['in'], ctypes.c_void_p, "pbc"),
                    (['in'], ctypes.c_void_p, "pmkToLeft"),
                    (['in'], ctypes.POINTER(comtypes.GUID), "riid"),
                    (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppv")),
        # ... other methods omitted for brevity as they are not used here ...
    ]

class ICreateDevEnum(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{29840822-5B84-11D0-BD3B-00A0C911CE86}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "CreateClassEnumerator",
                    (['in'], comtypes.GUID, "clsidDeviceClass"),
                    (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppEnumMoniker"),
                    (['in'], wintypes.ULONG, "dwFlags")),
    ]

def list_devices(cat_name, cat_guid_str):
    print(f"\nScanning Category: {cat_name} ({cat_guid_str})")
    try:
        devenum = comtypes.client.CreateObject("{62BE5D10-60EB-11D0-BD3B-00A0C911CE86}", 
                                              clsctx=comtypes.CLSCTX_INPROC_SERVER,
                                              interface=ICreateDevEnum)
        
        cat_guid = comtypes.GUID(cat_guid_str)
        try:
            enum_moniker_ptr = devenum.CreateClassEnumerator(cat_guid, 0)
        except Exception:
            print("  No devices found (Enumerator empty).")
            return
            
        if not enum_moniker_ptr:
            print("  No devices found (Enumerator null).")
            return

        enum_moniker = enum_moniker_ptr.QueryInterface(IEnumMoniker)
        
        while True:
            try:
                moniker_ptr, fetched = enum_moniker.Next(1)
            except Exception:
                break
                
            if fetched == 0 or not moniker_ptr:
                break
            
            moniker = moniker_ptr.QueryInterface(IMoniker)
            
            # Read properties
            bag_iid = comtypes.GUID("{55272a00-42cb-11ce-8135-00aa004bb851}")
            try:
                p_bag_unk = moniker.BindToStorage(None, None, ctypes.byref(bag_iid))
                if p_bag_unk:
                    bag = p_bag_unk.QueryInterface(IPropertyBag)
                    
                    def get_p(pname):
                        var = comtypes.automation.VARIANT()
                        if bag.Read(pname, ctypes.byref(var), None) == 0:
                            return str(var.value)
                        return "N/A"
                    
                    print(f"  [+] Device: {get_p('FriendlyName')}")
                    print(f"      Description: {get_p('Description')}")
                    print(f"      DevicePath: {get_p('DevicePath')}")
                else:
                    print("  [-] Could not bind to PropertyBag")
            except Exception as e:
                print(f"  [-] BindToStorage Error: {e}")
                
    except Exception as e:
        print(f"  Error: {e}")

def main():
    categories = {
        "Video Input": "{860BB310-5D01-11D0-BD3B-00A0C911CE86}",
        "Video Capture": "{E5323777-F976-4f5b-9C55-B94699C46E44}",
        "Audio Input": "{33D9A762-90C8-11d0-BD43-00A0C911CE86}",
    }
    for name, guid in categories.items():
        list_devices(name, guid)

if __name__ == "__main__":
    main()
