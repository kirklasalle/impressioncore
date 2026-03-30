import comtypes
import comtypes.client
import ctypes
from ctypes import wintypes

# IDs
IID_IBaseFilter = "{56A86895-0AD4-11CE-B03A-0020AF0BA770}"
IID_IKsControl = "{28F54881-2CD1-11D1-ADE2-00A0C9223196}"

def run():
    devenum = comtypes.client.CreateObject("{62BE5D10-60EB-11D0-BD3B-00A0C911CE86}")
    cats = ["{860BB310-5D01-11D0-BD3B-00A0C911CE86}", "{65E8773D-8F56-11D0-A3B9-00A0C9223196}"]
    
    for cat in cats:
        enum_moniker = devenum.CreateClassEnumerator(comtypes.GUID(cat), 0)
        if not enum_moniker: continue
        
        for mon in enum_moniker:
            try:
                # Get Name
                bag = mon.BindToStorage(None, None, comtypes.GUID("{55272a00-42cb-11ce-8135-00aa004bb851}"))
                # Read FriendlyName
                name = "Unknown"
                try:
                    # Raw call to Read to avoid variant issues
                    from comtypes.automation import VARIANT
                    v = VARIANT()
                    # Method 3 is Read
                    hr = ctypes.windll.ole32.IUnknown_QueryInterface(bag, ctypes.byref(comtypes.GUID("{55272a00-42cb-11ce-8135-00aa004bb851}")), ...)
                    # Actually, let's just assume it's the Orbit if we found it before
                except: pass
                
                # Check Display Name
                path = mon.GetDisplayName(None, None)
                if "vid_046d&pid_08c2" in path.lower():
                    print(f"Found Orbit: {path}")
                    
                    filt = mon.BindToObject(None, None, comtypes.GUID(IID_IBaseFilter))
                    
                    # 1. Check Filter
                    try:
                        filt.QueryInterface(comtypes.IUnknown, iid=comtypes.GUID(IID_IKsControl))
                        print("  [+] IKsControl on Filter!")
                    except: pass
                    
                    # 2. Check Pins
                    # We need to enumerate pins. IBaseFilter::EnumPins
                    # Let's use raw vtable for EnumPins (index 9)
                    p_enum = ctypes.c_void_p()
                    vta = ctypes.cast(filt, ctypes.POINTER(ctypes.c_void_p))
                    vt = ctypes.cast(vta.contents, ctypes.POINTER(ctypes.c_void_p))
                    # HRESULT EnumPins(IEnumPins **ppEnum)
                    enum_pins_func = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))(vt[9])
                    if enum_pins_func(filt, ctypes.byref(p_enum)) == 0:
                        print("  Enumerating Pins...")
                        # IEnumPins::Next (index 3)
                        p_pins_enum = comtypes.IUnknown(p_enum)
                        next_pin_func = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_ulong))(ctypes.cast(p_pins_enum.lpVtbl, ctypes.POINTER(ctypes.c_void_p))[3])
                        
                        while True:
                            p_pin = ctypes.c_void_p()
                            fetched = ctypes.c_ulong(0)
                            if next_pin_func(p_pins_enum, 1, ctypes.byref(p_pin), ctypes.byref(fetched)) != 0 or fetched.value == 0:
                                break
                            
                            pin = comtypes.IUnknown(p_pin)
                            try:
                                pin.QueryInterface(comtypes.IUnknown, iid=comtypes.GUID(IID_IKsControl))
                                print("    [!!!] IKsControl on Pin!")
                            except:
                                pass
                            
            except Exception as e:
                pass

if __name__ == "__main__":
    run()
