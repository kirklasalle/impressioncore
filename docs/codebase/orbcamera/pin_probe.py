import ctypes
from ctypes import wintypes
import comtypes
import comtypes.client

# Interface IDs
IID_IKsControl = "{28F54881-2CD1-11D1-ADE2-00A0C9223196}"
IID_IBaseFilter = "{56A86895-0AD4-11CE-B03A-0020AF0BA770}"

class IEnumPins(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{56a86892-0ad4-11ce-b03a-0020af0ba770}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "Next",
                    (['in'], wintypes.ULONG, "celt"),
                    (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "rgelt"),
                    (['out'], ctypes.POINTER(wintypes.ULONG), "pceltFetched")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "Skip", (['in'], wintypes.ULONG, "celt")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "Reset"),
        comtypes.COMMETHOD([], comtypes.HRESULT, "Clone", (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppenum")),
    ]

# IBaseFilter.EnumPins is method 3
class IBaseFilter(comtypes.IUnknown):
    _iid_ = comtypes.GUID(IID_IBaseFilter)
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "EnumPins", (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppEnum")),
        # Add more if needed, but EnumPins is at index 3 in IBaseFilter (Inherits from IMediaFilter)
        # IMediaFilter: Stop(3), Pause(4), Run(5), GetState(6), SetSyncSource(7), GetSyncSource(8)
        # IBaseFilter: EnumPins(9), FindPin(10), QueryFilterInfo(11), JoinFilterGraph(12), QueryVendorInfo(13)
    ]

def probe():
    devenum = comtypes.client.CreateObject("{62BE5D10-60EB-11D0-BD3B-00A0C911CE86}", interface=comtypes.IUnknown)
    # ICreateDevEnum.CreateClassEnumerator is method 3
    create_enum = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, ctypes.POINTER(comtypes.GUID), ctypes.POINTER(ctypes.c_void_p), ctypes.c_ulong)(devenum._vtable[3])
    
    cat_video = comtypes.GUID("{860BB310-5D01-11D0-BD3B-00A0C911CE86}")
    enum_ptr = ctypes.c_void_p()
    if create_enum(devenum, ctypes.byref(cat_video), ctypes.byref(enum_ptr), 0) != 0:
        print("No video input devices.")
        return
        
    enum_mon = comtypes.IUnknown(enum_ptr)
    # IEnumMoniker.Next is method 3
    next_mon = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_ulong))(enum_mon._vtable[3])
    
    while True:
        mon_ptr = ctypes.c_void_p()
        fetched = ctypes.c_ulong(0)
        if next_mon(enum_mon, 1, ctypes.byref(mon_ptr), ctypes.byref(fetched)) != 0: break
        if fetched.value == 0: break
        
        mon = comtypes.IUnknown(mon_ptr)
        # IMoniker.BindToObject is method 8 (IPersist 3, IPersistStream 4,5,6,7)
        bind_obj = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(comtypes.GUID), ctypes.POINTER(ctypes.c_void_p))(mon._vtable[8])
        
        filt_ptr = ctypes.c_void_p()
        filter_iid = comtypes.GUID(IID_IBaseFilter)
        if bind_obj(mon, None, None, ctypes.byref(filter_iid), ctypes.byref(filt_ptr)) == 0:
            filt = comtypes.IUnknown(filt_ptr)
            print(f"\n--- Filter Probe ---")
            
            # 1. Try IKsControl on Filter
            try:
                iks_ptr = ctypes.c_void_p()
                if filt.QueryInterface(comtypes.GUID(IID_IKsControl), ctypes.byref(iks_ptr)) == 0:
                    print("  [+] Filter supports IKsControl")
            except: pass
            
            # 2. Enum Pins
            # IBaseFilter.EnumPins is method 9
            enum_pins_func = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))(filt._vtable[9])
            pins_ptr = ctypes.c_void_p()
            if enum_pins_func(filt, ctypes.byref(pins_ptr)) == 0:
                pins_enum = comtypes.IUnknown(pins_ptr)
                # IEnumPins.Next is method 3
                next_pin = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_ulong))(pins_enum._vtable[3])
                
                while True:
                    pin_ptr = ctypes.c_void_p()
                    p_fetched = ctypes.c_ulong(0)
                    if next_pin(pins_enum, 1, ctypes.byref(pin_ptr), ctypes.byref(p_fetched)) != 0: break
                    if p_fetched.value == 0: break
                    
                    pin = comtypes.IUnknown(pin_ptr)
                    print("  Checking Pin...")
                    try:
                        p_iks_ptr = ctypes.c_void_p()
                        if pin.QueryInterface(comtypes.GUID(IID_IKsControl), ctypes.byref(p_iks_ptr)) == 0:
                            print("    [+] Pin supports IKsControl!")
                    except: pass
                    
                    # Also try Topology from pin (unlikely)
                    try:
                        p_topo_ptr = ctypes.c_void_p()
                        if pin.QueryInterface(comtypes.GUID("{720D4AC0-4433-11D3-8634-00A0C90391D1}"), ctypes.byref(p_topo_ptr)) == 0:
                            print("    [+] Pin supports IKsTopologyInfo!")
                    except: pass
        
if __name__ == "__main__":
    probe()
