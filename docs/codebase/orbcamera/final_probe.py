import comtypes
import comtypes.client
import comtypes.automation
import ctypes
from ctypes import wintypes
import uuid
import sys

# --- GUIDS and IDs ---
CLSID_SystemDeviceEnum = "{62BE5D10-60EB-11D0-BD3B-00A0C911CE86}"
CLSID_VideoInputDeviceCategory = "{860BB310-5D01-11D0-BD3B-00A0C911CE86}"

IID_IBaseFilter = "{56A86895-0AD4-11CE-B03A-0020AF0BA770}"
IID_IKsControl = "{28F54881-2CD1-11D1-ADE2-00A0C9223196}"
IID_IKsPropertySet = "{31EFAC30-515C-11D0-A9AA-00AA0061BE93}"
IID_IAMCameraControl = "{C6E13370-30AC-11D0-A18C-00A0C9118956}"
IID_IKsTopologyInfo = "{720D4AC0-7533-11D0-A5D6-28DB04C10000}"

# Logitech XU GUID Variants
LOGITECH_XU_GUIDS = [
    uuid.UUID("{63610662-5070-49ab-b8cc-b3855e8d2256}"), # Primary Motor Control
    uuid.UUID("{63610682-5070-49AB-B8CC-B3855E8D2256}"), # Variant 2
    uuid.UUID("{21236E26-F131-4892-B7F9-536E4D1A7A7B}"), # Video Properties
    uuid.UUID("{a123920c-c04d-11d2-9721-00105a1bcef8}"), # Older Logitech
]

# --- Structs ---
class KSPROPERTY(ctypes.Structure):
    _fields_ = [
        ("Set", ctypes.c_byte * 16),
        ("Id", wintypes.ULONG),
        ("Flags", wintypes.ULONG),
    ]

# --- Interfaces ---
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

class IKsPropertySet(comtypes.IUnknown):
    _iid_ = comtypes.GUID(IID_IKsPropertySet)
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "Set",
                    (['in'], comtypes.GUID, "guidPropSet"),
                    (['in'], wintypes.DWORD, "dwPropID"),
                    (['in'], ctypes.c_void_p, "pInstanceData"),
                    (['in'], wintypes.DWORD, "cbInstanceData"),
                    (['in'], ctypes.c_void_p, "pPropData"),
                    (['in'], wintypes.DWORD, "cbPropData")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "Get",
                    (['in'], comtypes.GUID, "guidPropSet"),
                    (['in'], wintypes.DWORD, "dwPropID"),
                    (['in'], ctypes.c_void_p, "pInstanceData"),
                    (['in'], wintypes.DWORD, "cbInstanceData"),
                    (['out'], ctypes.c_void_p, "pPropData"),
                    (['in'], wintypes.DWORD, "cbPropData"),
                    (['out'], ctypes.POINTER(wintypes.DWORD), "pcbReturned")),
         comtypes.COMMETHOD([], comtypes.HRESULT, "QuerySupported",
                    (['in'], comtypes.GUID, "guidPropSet"),
                    (['in'], wintypes.DWORD, "dwPropID"),
                    (['out'], ctypes.POINTER(wintypes.DWORD), "pTypeSupport")),
    ]

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
    ]

class IMoniker(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{0000000f-0000-0000-C000-000000000046}")
    _methods_ = [
        comtypes.STDMETHOD(comtypes.HRESULT, "GetClassID", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "IsDirty", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "Load", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "Save", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetSizeMax", []),
        comtypes.COMMETHOD([], comtypes.HRESULT, "BindToObject",
                    (['in'], ctypes.c_void_p, "pbc"),
                    (['in'], ctypes.c_void_p, "pmkToLeft"),
                    (['in'], comtypes.GUID, "riidResult"),
                    (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppvResult")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "BindToStorage",
                    (['in'], ctypes.c_void_p, "pbc"),
                    (['in'], ctypes.c_void_p, "pmkToLeft"),
                    (['in'], comtypes.GUID, "riid"),
                    (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppvObj")),
        comtypes.STDMETHOD(comtypes.HRESULT, "Reduce", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "ComposeWith", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "Enum", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "IsEqual", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "Hash", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "IsRunning", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetTimeOfLastChange", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "Inverse", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "CommonPrefixWith", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "RelativePathTo", []),
        comtypes.COMMETHOD([], comtypes.HRESULT, "GetDisplayName",
                    (['in'], ctypes.c_void_p, "pbc"),
                    (['in'], ctypes.c_void_p, "pmkToLeft"),
                    (['out', 'retval'], ctypes.POINTER(wintypes.LPWSTR), "ppszDisplayName")),
    ]

class ICreateDevEnum(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{29840822-5B84-11D0-BD3B-00A0C911CE86}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "CreateClassEnumerator",
                    (['in'], comtypes.GUID, "clsidDeviceClass"),
                    (['out'], ctypes.POINTER(ctypes.POINTER(IEnumMoniker)), "ppEnumMoniker"),
                    (['in'], wintypes.DWORD, "dwFlags")),
    ]

class IPin(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{56A86891-0AD4-11CE-B03A-0020AF0BA770}")
    _methods_ = [
        comtypes.STDMETHOD(comtypes.HRESULT, "Connect", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "ReceiveConnection", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "Disconnect", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "ConnectedTo", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "ConnectionMediaType", []),
        comtypes.COMMETHOD([], comtypes.HRESULT, "QueryPinInfo", (['out'], ctypes.c_void_p, "pInfo")),
        comtypes.STDMETHOD(comtypes.HRESULT, "QueryDirection", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "QueryId", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "QueryAccept", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "EnumMediaTypes", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "QueryInternalConnections", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "EndOfStream", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "BeginFlush", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "EndFlush", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "NewSegment", []),
    ]

class IEnumPins(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{56A86892-0AD4-11CE-B03A-0020AF0BA770}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "Next",
                    (['in'], wintypes.ULONG, "celt"),
                    (['out'], ctypes.POINTER(ctypes.POINTER(IPin)), "ppv"),
                    (['out'], ctypes.POINTER(wintypes.ULONG), "pceltFetched")),
    ]

class IBaseFilter(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{56A86895-0AD4-11CE-B03A-0020AF0BA770}")
    _methods_ = [
        comtypes.STDMETHOD(comtypes.HRESULT, "GetClassID", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "Stop", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "Pause", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "Run", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetState", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "SetSyncSource", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetSyncSource", []),
        comtypes.COMMETHOD([], comtypes.HRESULT, "EnumPins",
                    (['out'], ctypes.POINTER(ctypes.POINTER(IEnumPins)), "ppEnum")),
        comtypes.STDMETHOD(comtypes.HRESULT, "FindPin", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "QueryFilterInfo", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "JoinFilterGraph", []),
        comtypes.STDMETHOD(comtypes.HRESULT, "QueryVendorInfo", []),
    ]

class IKsTopologyInfo(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{720D4AC0-7533-11D0-A5D6-28DB04C10000}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "get_NumCategories", (['out'], ctypes.POINTER(wintypes.DWORD), "pdw")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "get_Category", (['in'], wintypes.DWORD, "idx"), (['out'], ctypes.POINTER(comtypes.GUID), "pguid")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "get_NumNodes", (['out'], ctypes.POINTER(wintypes.DWORD), "pdw")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "get_NodeType", (['in'], wintypes.DWORD, "idx"), (['out'], ctypes.POINTER(comtypes.GUID), "pguid")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "get_NodeName", (['in'], wintypes.DWORD, "idx"), (['out'], ctypes.POINTER(comtypes.BSTR), "pname")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "CreateNodeInstance",
                    (['in'], wintypes.DWORD, "idx"),
                    (['in'], ctypes.POINTER(comtypes.GUID), "riid"),
                    (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppv")),
    ]

# --- Probing ---

def check_obj(obj, label):
    print(f"    Checking {label}...")
    sys.stdout.flush()
    
    # Check IKsControl
    try:
        ks = obj.QueryInterface(IKsControl)
        print("      [+] Found IKsControl")
        for guid in LOGITECH_XU_GUIDS:
            for prop_id in range(21):
                prop = KSPROPERTY()
                gb = guid.bytes_le
                for i in range(16): prop.Set[i] = gb[i]
                prop.Id = prop_id
                prop.Flags = 0x100 # BASICSUPPORT
                returned = wintypes.ULONG(0)
                data = wintypes.DWORD(0)
                hr = ks.KsProperty(ctypes.byref(prop), ctypes.sizeof(prop), ctypes.byref(data), 4, ctypes.byref(returned))
                if hr == 0:
                    print(f"      [!!!] GUID {guid} Prop {prop_id} SUPPORTED via IKsControl!")
                elif hr != 0x80004001: # Not E_NOTIMPL
                    # print(f"      [?] GUID {guid} Prop {prop_id} returned {hr & 0xFFFFFFFF:08x}")
                    pass
    except: pass

    # Check IKsPropertySet
    try:
        kps = obj.QueryInterface(IKsPropertySet)
        print("      [+] Found IKsPropertySet")
        for guid in LOGITECH_XU_GUIDS:
            for prop_id in range(21):
                support = wintypes.DWORD(0)
                hr = kps.QuerySupported(comtypes.GUID(guid), prop_id, ctypes.byref(support))
                if hr == 0:
                    print(f"      [!!!] GUID {guid} Prop {prop_id} SUPPORTED via IKsPropertySet!")
    except: pass

    # Check IAMCameraControl
    try:
        obj.QueryInterface(comtypes.GUID(IID_IAMCameraControl))
        print("      [+] Found IAMCameraControl")
    except: pass
    sys.stdout.flush()

# Expanded Categories
CATEGORIES = [
    ("{860BB310-5D01-11D0-BD3B-00A0C911CE86}", "Video Input"),
    ("{65E8773D-8F56-11D0-A3B9-00A0C9223196}", "Capture"),
    ("{a799a800-a46d-11d0-a18c-00a0c9118956}", "Crossbar"),
    ("{FD0A5AF4-B41D-11d2-9C95-00C04F7971E0}", "External Renderer"),
    ("{4E6920E0-5022-11D1-946C-0000C05BAEBD}", "Video Effects"),
    ("{083863F1-70DE-11d0-BD40-00A0C911CE86}", "DirectShow Filters"),
]

LOGITECH_XU_GUIDS = [
    uuid.UUID("{63610662-5070-49ab-b8cc-b3855e8d2256}"), # Primary Motor Control
    uuid.UUID("{63610682-5070-49AB-B8CC-B3855E8D2256}"), # Variant 2
    uuid.UUID("{21236E26-F131-4892-B7F9-536E4D1A7A7B}"), # Video Properties
    uuid.UUID("{C6E13370-30AC-11D0-A18C-00A0C9118956}"), # PROPSETID_VIDCAP_CAMERACONTROL
]

def run():
    print("=== FINAL PROBE: Searching for Logitech Orbit Control Interface ===")
    sys.stdout.flush()
    devenum = comtypes.client.CreateObject(CLSID_SystemDeviceEnum, interface=ICreateDevEnum)
    
    for cat_guid_str, cat_name in CATEGORIES:
        print(f"\n--- Scanning Category: {cat_name} ---")
        try:
            enum_moniker = devenum.CreateClassEnumerator(comtypes.GUID(cat_guid_str), 0)
        except: continue
        if not enum_moniker: continue

        while True:
            res = enum_moniker.Next(1)
            if not res: break
            mon_ptr, fetched = res
            if not fetched: break
            mon = mon_ptr.QueryInterface(IMoniker)
            
            # Get FriendlyName
            name = "Unknown"
            try:
                bag_iid = comtypes.GUID("{55272a00-42cb-11ce-8135-00aa004bb851}")
                bag = mon.BindToStorage(None, None, bag_iid).QueryInterface(IPropertyBag)
                var = comtypes.automation.VARIANT()
                if bag.Read("FriendlyName", ctypes.byref(var), None) == 0:
                    name = str(var.value)
            except: pass
            
            path = "Unknown"
            try: path = mon.GetDisplayName(None, None)
            except: pass
            
            # Print if it's Orbit or if we are in diagnostic mode
            if "046D" in path.upper() and "08C2" in path.upper():
                print(f"\nProbing Hardware: {name}\nPath: {path}")
                sys.stdout.flush()
            else:
                continue
        
        try:
            p_filt_iid = comtypes.GUID(IID_IBaseFilter)
            filt_ptr = mon.BindToObject(None, None, p_filt_iid)
            filt = filt_ptr.QueryInterface(IBaseFilter)
            
            check_obj(filt, "Filter")
            
            print("    Enumerating Pins...")
            sys.stdout.flush()
            enum_pins = filt.EnumPins()
            while True:
                res_pin = enum_pins.Next(1)
                if not res_pin: break
                pin_ptr, f_pin = res_pin
                if not f_pin: break
                pin = pin_ptr.QueryInterface(IPin)
                check_obj(pin, "Pin")
                
            print("    Checking Topology...")
            sys.stdout.flush()
            try:
                topo = filt.QueryInterface(IKsTopologyInfo)
                num_nodes = topo.get_NumNodes()
                for i in range(num_nodes):
                    try:
                        ks_iid = comtypes.GUID(IID_IKsControl)
                        node_ptr = topo.CreateNodeInstance(i, ctypes.byref(ks_iid))
                        check_obj(node_ptr, f"Node {i}")
                    except: pass
            except: pass
            
        except Exception as e:
            print(f"Error: {e}")
            sys.stdout.flush()

if __name__ == "__main__":
    run()
