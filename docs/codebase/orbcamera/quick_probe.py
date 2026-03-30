import ctypes
from ctypes import wintypes
import comtypes
import comtypes.client

IID_IBaseFilter = "{56A86895-0AD4-11CE-B03A-0020AF0BA770}"
IID_IKsControl = "{28F54881-2CD1-11D1-ADE2-00A0C9223196}"
IID_IKsTopologyInfo = "{720D4AC0-4433-11D3-8634-00A0C90391D1}"

def run_probe():
    # 1. Get Device Moniker for Orbit
    devenum = comtypes.client.CreateObject("{62BE5D10-60EB-11D0-BD3B-00A0C911CE86}", interface=comtypes.IUnknown)
    # ICreateDevEnum::CreateClassEnumerator(clsidRole, ppEnumMoniker, dwFlags)
    # VTable: QueryInterface(0), AddRef(1), Release(2), CreateClassEnumerator(3)
    p_enum = ctypes.c_void_p()
    clsid_vidin = comtypes.GUID("{860BB310-5D01-11D0-BD3B-00A0C911CE86}")
    
    # helper to call vtable
    def call_v(ptr, idx, *args):
        vta = ctypes.cast(ptr, ctypes.POINTER(ctypes.c_void_p))
        vt = ctypes.cast(vta.contents, ctypes.POINTER(ctypes.c_void_p))
        proto = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, *[type(a) for a in args])
        return proto(vt[idx])(ptr, *args)

    hr = call_v(devenum, 3, ctypes.byref(clsid_vidin), ctypes.byref(p_enum), 0)
    if hr != 0 or not p_enum:
        print("Failed to create class enumerator.")
        return

    # IEnumMoniker::Next(celt, rgelt, pceltFetched)
    # VTable: 0,1,2, Next(3)
    while True:
        p_mon = ctypes.c_void_p()
        fetched = ctypes.c_ulong(0)
        hr = call_v(p_enum, 3, 1, ctypes.byref(p_mon), ctypes.byref(fetched))
        if hr != 0 or not fetched.value: break
        
        # Get Name
        name = "Unknown"
        # IMoniker::BindToStorage(pbc, pmkToLeft, riid, ppv) - index 9?
        # Let's use comtypes for property bag, it usually works
        mon = comtypes.IUnknown(p_mon).QueryInterface(comtypes.IUnknown)
        try:
            bag_iid = comtypes.GUID("{55272a00-42cb-11ce-8135-00aa004bb851}")
            p_bag = ctypes.c_void_p()
            hr = call_v(p_mon, 9, None, None, ctypes.byref(bag_iid), ctypes.byref(p_bag))
            if hr == 0:
                # IPropertyBag::Read(pszPropName, pVar, pErrorLog) - index 3
                bag = comtypes.IUnknown(p_bag)
                var = comtypes.automation.VARIANT()
                hr = call_v(p_bag, 3, "FriendlyName", ctypes.byref(var), None)
                if hr == 0:
                    name = str(var.value)
        except: pass
        
        if "Orbit" in name or "Sphere" in name:
            print(f"Found Orbit Device: {name}")
            
            # Bound Filter
            p_filt = ctypes.c_void_p()
            filt_iid = comtypes.GUID(IID_IBaseFilter)
            # IMoniker::BindToObject(pbc, pmkToLeft, riid, ppv) - index 8
            hr = call_v(p_mon, 8, None, None, ctypes.byref(filt_iid), ctypes.byref(p_filt))
            if hr == 0:
                print("  Successfully bound to Filter.")
                
                # Check IKsControl
                ks_iid = comtypes.GUID(IID_IKsControl)
                p_ks = ctypes.c_void_p()
                hr = call_v(p_filt, 0, ctypes.byref(ks_iid), ctypes.byref(p_ks))
                if hr == 0:
                    print("  [!!!] SUCCESS! IKsControl supported on Filter.")
                else:
                    print(f"  IKsControl NOT on filter (HR={hex(hr & 0xFFFFFFFF)})")
                
                # Check IKsTopologyInfo
                topo_iid = comtypes.GUID(IID_IKsTopologyInfo)
                p_topo = ctypes.c_void_p()
                hr = call_v(p_filt, 0, ctypes.byref(topo_iid), ctypes.byref(p_topo))
                if hr == 0:
                    print("  [+] IKsTopologyInfo supported on Filter.")
                    # Get Num Nodes
                    # IKsTopologyInfo::get_NumNodes(pdw) - index 5?
                    num = wintypes.DWORD(0)
                    call_v(p_topo, 5, ctypes.byref(num))
                    print(f"    Nodes: {num.value}")
                    # create node instances...
                else:
                    print(f"  IKsTopologyInfo NOT on filter (HR={hex(hr & 0xFFFFFFFF)})")

                # Check Pins
                # IBaseFilter::EnumPins(ppEnum) - index 9
                p_enpins = ctypes.c_void_p()
                hr = call_v(p_filt, 9, ctypes.byref(p_enpins))
                if hr == 0:
                    print("  Enumerating Pins...")
                    while True:
                        p_pin = ctypes.c_void_p()
                        pf = ctypes.c_ulong(0)
                        # IEnumPins::Next(3)
                        hr = call_v(p_enpins, 3, 1, ctypes.byref(p_pin), ctypes.byref(pf))
                        if hr != 0 or not pf.value: break
                        
                        # Check IKsControl on Pin
                        p_pks = ctypes.c_void_p()
                        hr = call_v(p_pin, 0, ctypes.byref(ks_iid), ctypes.byref(p_pks))
                        if hr == 0:
                            print("    [!!!] SUCCESS! IKsControl supported on Pin.")
                        else:
                            print(f"    No IKsControl on pin (HR={hex(hr & 0xFFFFFFFF)})")
        
if __name__ == "__main__":
    run_probe()
