import comtypes
import comtypes.client
import ctypes
from ctypes import wintypes

class ICreateDevEnum(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{29840822-5B84-11D0-BD3B-00A0C911CE86}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "CreateClassEnumerator",
                    (['in'], comtypes.GUID, "clsidDeviceClass"),
                    (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppEnumMoniker"),
                    (['in'], wintypes.ULONG, "dwFlags")),
    ]

class IEnumMoniker(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{00000102-0000-0000-C000-000000000046}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "Next",
                    (['in'], wintypes.ULONG, "celt"),
                    (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "rgelt"),
                    (['out'], ctypes.POINTER(wintypes.ULONG), "pceltFetched")),
    ]

class IPropertyBag(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{55272a00-42cb-11ce-8135-00aa004bb851}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "Read",
                    (['in'], wintypes.LPWSTR, "pszPropName"),
                    (['in', 'out'], ctypes.POINTER(comtypes.automation.VARIANT), "pVar"),
                    (['in'], ctypes.c_void_p, "pErrorLog")),
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
        comtypes.COMMETHOD([], comtypes.HRESULT, "Inverse"),
        comtypes.COMMETHOD([], comtypes.HRESULT, "CommonPrefixWith"),
        comtypes.COMMETHOD([], comtypes.HRESULT, "RelativePathTo"),
        comtypes.COMMETHOD([], comtypes.HRESULT, "GetDisplayName",
                    (['in'], ctypes.c_void_p, "pbc"),
                    (['in'], ctypes.c_void_p, "pmkToLeft"),
                    (['out'], ctypes.POINTER(wintypes.LPWSTR), "ppszDisplayName")),
    ]

def scan():
    devenum = comtypes.client.CreateObject("{62BE5D10-60EB-11D0-BD3B-00A0C911CE86}", 
                                          clsctx=comtypes.CLSCTX_INPROC_SERVER,
                                          interface=ICreateDevEnum)
    
    # Common categories
    categories = {
        "Video Input": "{860BB310-5D01-11D0-BD3B-00A0C911CE86}",
        "Video Capture": "{E5323777-F976-4f5b-9C55-B94699C46E44}",
        "Audio Input": "{33D9A762-90C8-11D0-BD43-00A0C911CE86}",
        "External Render": "{71985930-1CA1-11d3-9CC8-00C04F7971E0}",
        "Device Control": "{71985936-1CA1-11d3-9CC8-00C04F7971E0}",
        "AM_KSCATEGORY_CAPTURE": "{65E8773D-8F56-11D0-A3B9-00A0C9223196}",
        "AM_KSCATEGORY_VIDEO": "{69917243-BD97-11D0-AB1E-00A0C9223196}",
    }

    for name, guid_str in categories.items():
        print(f"\n--- {name} ({guid_str}) ---")
        try:
            cat_guid = comtypes.GUID(guid_str)
            enum_ptr = devenum.CreateClassEnumerator(cat_guid, 0)
            if not enum_ptr:
                print("  No devices.")
                continue
            
            enum_moniker = enum_ptr.QueryInterface(IEnumMoniker)
            while True:
                res = enum_moniker.Next(1)
                if not res: break
                moniker_ptr, fetched = res
                if fetched == 0: break
                
                moniker = moniker_ptr.QueryInterface(IMoniker)
                
                # Get Display Name
                display_name = "Unknown"
                try:
                    display_name = moniker.GetDisplayName(None, None)
                    print(f"  [+] Device Path: {display_name}")
                except Exception:
                    pass

                # Try to bind IKsControl
                try:
                    # First BindToObject to IBaseFilter
                    IBaseFilter_IID = comtypes.GUID("{56A86895-0AD4-11CE-B03A-0020AF0BA770}")
                    p_filter_unk = moniker.BindToObject(None, None, ctypes.byref(IBaseFilter_IID))
                    if p_filter_unk:
                        print("      - Successfully bound to IBaseFilter")
                        try:
                            # Try IKsControl on filter
                            iks = p_filter_unk.QueryInterface(comtypes.IUnknown, iid="{28F54881-2CD1-11D1-ADE2-00A0C9223196}")
                            print("      - SUCCESS: Supports IKsControl on Filter!")
                        except Exception:
                            print("      - No IKsControl on Filter, checking topology...")
                            # Try IKsTopologyInfo
                            try:
                                topo_iid = comtypes.GUID("{720D4AC0-4433-11D3-8634-00A0C90391D1}")
                                topo = p_filter_unk.QueryInterface(comtypes.IUnknown, iid=topo_iid)
                                print("      - Supports IKsTopologyInfo")
                            except Exception:
                                print("      - No IKsTopologyInfo")
                    else:
                        print("      - BindToObject(IBaseFilter) failed")
                except Exception as e:
                    print(f"      - Binding error: {e}")
        except Exception as e:
            print(f"  Error scanning category: {e}")

if __name__ == "__main__":
    scan()
