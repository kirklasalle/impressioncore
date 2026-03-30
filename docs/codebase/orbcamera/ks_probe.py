import ctypes
from ctypes import wintypes
import comtypes
import comtypes.client

# Interface IDs
IID_IKsControl = "{28F54881-2CD1-11D1-ADE2-00A0C9223196}"
IID_IKsTopologyInfo = "{720D4AC0-4433-11D3-8634-00A0C90391D1}"
IID_IAMCameraControl = "{C6E13370-30AC-11D0-A18C-00A0C9118956}"
IID_IBaseFilter = "{56A86895-0AD4-11CE-B03A-0020AF0BA770}"

class ICreateDevEnum(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{29840822-5B84-11D0-BD3B-00A0C911CE86}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "CreateClassEnumerator",
                    (['in'], comtypes.GUID, "clsidDeviceClass"),
                    (['out', 'retval'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppEnumMoniker"),
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

class IMoniker(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{0000010c-0000-0000-C000-000000000046}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "RemoteBindToObject", (['in'], ctypes.c_void_p, "pbc"), (['in'], ctypes.c_void_p, "pmkToLeft"), (['in'], ctypes.POINTER(comtypes.GUID), "riidResult"), (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppvResult")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "RemoteBindToStorage", (['in'], ctypes.c_void_p, "pbc"), (['in'], ctypes.c_void_p, "pmkToLeft"), (['in'], ctypes.POINTER(comtypes.GUID), "riid"), (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppv")),
        # Simplified Bind methods that comtypes can handle via QueryInterface usually
        comtypes.COMMETHOD([], comtypes.HRESULT, "BindToObject", (['in'], ctypes.c_void_p, "pbc"), (['in'], ctypes.c_void_p, "pmkToLeft"), (['in'], ctypes.POINTER(comtypes.GUID), "riidResult"), (['out', 'retval'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppvResult")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "BindToStorage", (['in'], ctypes.c_void_p, "pbc"), (['in'], ctypes.c_void_p, "pmkToLeft"), (['in'], ctypes.POINTER(comtypes.GUID), "riid"), (['out', 'retval'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppv")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "Reduce"),
        comtypes.COMMETHOD([], comtypes.HRESULT, "ComposeWith"),
        comtypes.COMMETHOD([], comtypes.HRESULT, "Enum"),
        comtypes.COMMETHOD([], comtypes.HRESULT, "IsEqual"),
        comtypes.COMMETHOD([], comtypes.HRESULT, "Hash"),
        comtypes.COMMETHOD([], comtypes.HRESULT, "IsRunning"),
        comtypes.COMMETHOD([], comtypes.HRESULT, "GetTimeOfLastChange"),
        comtypes.COMMETHOD([], comtypes.HRESULT, "Inverse"),
        comtypes.COMMETHOD([], comtypes.HRESULT, "CommonPrefixWith"),
        comtypes.COMMETHOD([], comtypes.HRESULT, "RelativePathTo"),
        comtypes.COMMETHOD([], comtypes.HRESULT, "GetDisplayName",
                    (['in'], ctypes.c_void_p, "pbc"),
                    (['in'], ctypes.c_void_p, "pmkToLeft"),
                    (['out'], ctypes.POINTER(wintypes.LPWSTR), "ppszDisplayName")),
    ]

class IPropertyBag(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{55272a00-42cb-11ce-8135-00aa004bb851}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "Read", (['in'], wintypes.LPWSTR, "pszPropName"), (['out', 'retval'], ctypes.POINTER(comtypes.automation.VARIANT), "pVar"), (['in'], ctypes.c_void_p, "pErrorLog")),
    ]

# IAMCameraControl
class IAMCameraControl(comtypes.IUnknown):
    _iid_ = comtypes.GUID(IID_IAMCameraControl)
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "GetRange", 
                    (['in'], wintypes.LONG, "Property"), 
                    (['out'], ctypes.POINTER(wintypes.LONG), "pMin"), 
                    (['out'], ctypes.POINTER(wintypes.LONG), "pMax"), 
                    (['out'], ctypes.POINTER(wintypes.LONG), "pSteppingDelta"), 
                    (['out'], ctypes.POINTER(wintypes.LONG), "pDefault"), 
                    (['out'], ctypes.POINTER(wintypes.LONG), "pCapsFlags")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "Set", 
                    (['in'], wintypes.LONG, "Property"), 
                    (['in'], wintypes.LONG, "lValue"), 
                    (['in'], wintypes.LONG, "lFlags")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "Get", 
                    (['in'], wintypes.LONG, "Property"), 
                    (['out'], ctypes.POINTER(wintypes.LONG), "plValue"), 
                    (['out'], ctypes.POINTER(wintypes.LONG), "plFlags")),
    ]

# IKsTopologyInfo
class IKsTopologyInfo(comtypes.IUnknown):
    _iid_ = comtypes.GUID(IID_IKsTopologyInfo)
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "get_NumCategories", (['out'], ctypes.POINTER(wintypes.DWORD), "pdwNumCategories")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "get_Category", (['in'], wintypes.DWORD, "dwIndex"), (['out'], ctypes.POINTER(comtypes.GUID), "pCategory")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "get_NumNodes", (['out'], ctypes.POINTER(wintypes.DWORD), "pdwNumNodes")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "get_NodeType", (['in'], wintypes.DWORD, "dwNodeId"), (['out'], ctypes.POINTER(comtypes.GUID), "pNodeType")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "CreateNodeInstance", 
                    (['in'], wintypes.DWORD, "dwNodeId"), 
                    (['in'], ctypes.POINTER(comtypes.GUID), "iid"), 
                    (['out', 'retval'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppv")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "get_NodeName", (['out', 'retval'], ctypes.POINTER(comtypes.BSTR), "pbstrName")),
    ]

def probe():
    devenum = comtypes.client.CreateObject("{62BE5D10-60EB-11D0-BD3B-00A0C911CE86}", interface=ICreateDevEnum)
    cat_video = comtypes.GUID("{860BB310-5D01-11D0-BD3B-00A0C911CE86}")
    
    enum_ptr = devenum.CreateClassEnumerator(cat_video, 0)
    if not enum_ptr:
        print("No video input devices.")
        return
        
    enum_moniker = enum_ptr.QueryInterface(IEnumMoniker)
    while True:
        res = enum_moniker.Next(1)
        if not res: break
        moniker_ptr, fetched = res
        if fetched == 0: break
        moniker = moniker_ptr.QueryInterface(IMoniker)
        
        path = "Unknown"
        try:
            name_ptr = wintypes.LPWSTR()
            if moniker.GetDisplayName(None, None, ctypes.byref(name_ptr)) == 0:
                path = name_ptr.value
        except: pass
        name = "Unknown"
        try:
            bag = moniker.BindToStorage(None, None, ctypes.byref(IPropertyBag._iid_)).QueryInterface(IPropertyBag)
            name = bag.Read("FriendlyName")
        except: pass
        
        print(f"\n--- Checking Device: {name} ---")
        print(f"Path: {path}")

        try:
            filt = moniker.BindToObject(None, None, ctypes.byref(comtypes.GUID(IID_IBaseFilter)))
            
            # 1. IAMCameraControl
            print("  [Probing IAMCameraControl]")
            try:
                cam_ctrl = filt.QueryInterface(IAMCameraControl)
                for prop, pname in [(0, "Pan"), (1, "Tilt"), (2, "Roll"), (3, "Zoom")]:
                    try:
                        pmin, pmax, step, pdef, flags = cam_ctrl.GetRange(prop)
                        print(f"    {pname}: Range [{pmin}, {pmax}], Step: {step}, Default: {pdef}, Flags: {flags}")
                    except:
                        print(f"    {pname}: Not supported via IAMCameraControl")
            except:
                print("    IAMCameraControl not supported.")

            # 2. IKsControl on filter
            print("  [Probing IKsControl on Filter]")
            try:
                iks = filt.QueryInterface(comtypes.IUnknown, iid=IID_IKsControl)
                print("    IKsControl supported on Filter!")
            except:
                print("    IKsControl not supported on Filter.")

            # 3. Topology Scan
            print("  [Probing Topology Nodes]")
            try:
                topo = filt.QueryInterface(IKsTopologyInfo)
                num_nodes = topo.get_NumNodes()
                print(f"    Number of nodes: {num_nodes}")
                for i in range(num_nodes):
                    node_type = topo.get_NodeType(i)
                    try: node_name = topo.get_NodeName(i)
                    except: node_name = f"Node{i}"
                    print(f"    - {node_name} (Type: {node_type})")
                    
                    # Try IKsControl on this node
                    try:
                        node_ks = topo.CreateNodeInstance(i, ctypes.byref(comtypes.GUID(IID_IKsControl)))
                        print(f"      SUCCESS: IKsControl available on {node_name}!")
                    except:
                        pass
                    
                    # Try IAMCameraControl on this node (unlikely but possible)
                    try:
                        node_cam = topo.CreateNodeInstance(i, ctypes.byref(comtypes.GUID(IID_IAMCameraControl)))
                        print(f"      SUCCESS: IAMCameraControl available on {node_name}!")
                    except:
                        pass
            except:
                print("    IKsTopologyInfo not supported.")

        except Exception as e:
            print(f"  Error binding filter: {e}")

if __name__ == "__main__":
    probe()
