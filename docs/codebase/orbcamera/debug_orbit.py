import comtypes
import comtypes.client
import ctypes
from ctypes import wintypes

# IDs
IID_IBaseFilter = "{56A86895-0AD4-11CE-B03A-0020AF0BA770}"
IID_IKsControl = "{28F54881-2CD1-11D1-ADE2-00A0C9223196}"
IID_IKsTopologyInfo = "{720D4AC0-4433-11D3-8634-00A0C90391D1}"
IID_IPropertyBag = "{55272a00-42cb-11ce-8135-00aa004bb851}"

class IPropertyBag(comtypes.IUnknown):
    _iid_ = comtypes.GUID(IID_IPropertyBag)
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "Read",
                    (['in'], wintypes.LPWSTR, "pszPropName"),
                    (['out', 'retval'], ctypes.POINTER(comtypes.automation.VARIANT), "pVar"),
                    (['in'], ctypes.c_void_p, "pErrorLog")),
    ]

def debug_filter(filt, name):
    print(f"\n--- Debugging Filter: {name} ---")
    
    # Check Interfaces
    interfaces = {
        "IKsControl": IID_IKsControl,
        "IKsTopologyInfo": IID_IKsTopologyInfo,
        "IAMCameraControl": "{C6E13370-30AC-11D0-A18C-00A0C9118956}",
        "IKsPropertySet": "{31EFAC30-515C-11D0-A9AA-00AA0061BE93}",
    }
    
    for iname, iid_str in interfaces.items():
        try:
            filt.QueryInterface(comtypes.IUnknown, iid=comtypes.GUID(iid_str))
            print(f"  [+] Supports {iname}")
        except:
            pass
            
    # Topology Details
    try:
        topo = filt.QueryInterface(comtypes.client.GetModule("quartz.dll").IKsTopologyInfo) 
        # wait, quartz.dll might not have it. Let's use our definition.
    except:
        pass

    # Pins
    try:
        # We need a proper IBaseFilter definition or use raw vtable
        pass
    except: pass

def run():
    devenum = comtypes.client.CreateObject("{62BE5D10-60EB-11D0-BD3B-00A0C911CE86}")
    # Use categories
    cats = [
        ("{860BB310-5D01-11D0-BD3B-00A0C911CE86}", "Video Input"),
        ("{65E8773D-8F56-11D0-A3B9-00A0C9223196}", "Capture"),
    ]
    
    for cat_iid, cat_name in cats:
        print(f"\nScanning {cat_name}...")
        try:
            enum_moniker = devenum.CreateClassEnumerator(comtypes.GUID(cat_iid), 0)
            if not enum_moniker: continue
            
            for mon in enum_moniker:
                name = "Unknown"
                try:
                    bag = mon.BindToStorage(None, None, comtypes.GUID(IID_IPropertyBag)).QueryInterface(IPropertyBag)
                    name = bag.Read("FriendlyName")
                except: pass
                
                if "Orbit" in name or "Sphere" in name or "Logitech" in name:
                    print(f"Candidate: {name}")
                    try:
                        filt = mon.BindToObject(None, None, comtypes.GUID(IID_IBaseFilter))
                        debug_filter(filt, name)
                    except Exception as e:
                        print(f"  Failed to bind: {e}")
        except Exception as e:
            print(f"Error scanning {cat_name}: {e}")

if __name__ == "__main__":
    run()
