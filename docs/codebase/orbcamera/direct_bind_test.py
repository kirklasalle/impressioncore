import comtypes
import comtypes.client
import ctypes
from ctypes import wintypes

class IBaseFilter(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{56A86895-0AD4-11CE-B03A-0020AF0BA770}")
    _methods_ = [] # Not full, just for QI

class IKsControl(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{28F54881-2CD1-11D1-ADE2-00A0C9223196}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "KsProperty",
                    (['in'], ctypes.c_void_p, "Property"),
                    (['in'], wintypes.ULONG, "PropertyLength"),
                    (['in', 'out'], ctypes.c_void_p, "PropertyData"),
                    (['in'], wintypes.ULONG, "DataLength"),
                    (['out'], ctypes.POINTER(wintypes.ULONG), "BytesReturned")),
    ]

def try_direct_bind():
    # Found in registry
    device_path = r"\\?\USB#VID_046D&PID_08C2&MI_00#6&16853086&1&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}"
    # DirectShow format for monikers usually starts with @device:pnp: or @device:sw:
    # Actually, for PnP devices it's often @device:pnp:\\?\USB#...
    moniker_str = f"@device:pnp:{device_path}"
    
    print(f"Attempting to bind to: {moniker_str}")
    
    ctypes.windll.ole32.CoInitialize(None)
    try:
        bind_ctx_ptr = ctypes.POINTER(comtypes.IUnknown)()
        ctypes.windll.ole32.CreateBindCtx(0, ctypes.byref(bind_ctx_ptr))
        
        moniker_ptr = ctypes.POINTER(comtypes.IUnknown)()
        eaten = wintypes.ULONG(0)
        hr = ctypes.windll.ole32.MkParseDisplayName(bind_ctx_ptr, moniker_str, ctypes.byref(eaten), ctypes.byref(moniker_ptr))
        
        if hr == 0 and moniker_ptr:
            print("Successfully parsed moniker.")
            # Now bind to object
            filter_iid = comtypes.GUID("{56A86895-0AD4-11CE-B03A-0020AF0BA770}")
            filter_ptr = ctypes.POINTER(comtypes.IUnknown)()
            # BindToObject(pbc, pmkToLeft, riid, ppv) - 5 methods into IMoniker
            # We can use comtypes to do this more easily if we have IMoniker
            class IMonikerLight(comtypes.IUnknown):
                _iid_ = comtypes.GUID("{0000010c-0000-0000-C000-000000000046}")
                _methods_ = [
                    # skipped some...
                    comtypes.STDMETHOD(comtypes.HRESULT, "BindToObject", [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(comtypes.GUID), ctypes.POINTER(ctypes.c_void_p)]),
                ]
            
            moniker = moniker_ptr.QueryInterface(IMonikerLight)
            p_filter = ctypes.c_void_p()
            hr = moniker.BindToObject(bind_ctx_ptr, None, ctypes.byref(filter_iid), ctypes.byref(p_filter))
            
            if hr == 0 and p_filter:
                print("Successfully bound to IBaseFilter.")
                # Try IKsControl
                filter_unk = comtypes.client.GetBestInterface(p_filter)
                try:
                    iks = filter_unk.QueryInterface(IKsControl)
                    print("SUCCESS: Acquired IKsControl!")
                except Exception as e:
                    print(f"Failed to get IKsControl: {e}")
            else:
                print(f"BindToObject failed: {hr:x}")
        else:
            print(f"MkParseDisplayName failed: {hr:x}")
            
    finally:
        ctypes.windll.ole32.CoUninitialize()

if __name__ == "__main__":
    try_direct_bind()
