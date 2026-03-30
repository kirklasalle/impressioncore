"""
Logitech XML GUID Scanner
==========================
Scans all GUIDs found in logitech.xml against 
ALL DirectShow topology nodes of the camera.
"""
import logging
import ctypes
from ctypes import wintypes
import comtypes
import comtypes.client

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# DirectShow Context
CLSID_SystemDeviceEnum = "{62BE5D10-60EB-11D0-BD3B-00A0C911CE86}"
CLSID_VideoInputDeviceCategory = "{860BB310-5D01-11D0-BD3B-00A0C911CE86}"
IID_IKsPropertySet = "{31EFAC30-515C-11D0-A9AA-00AA0061BE93}"
IID_IKsTopologyInfo = "{720D4AC0-7533-11D0-A5D6-28DB04C10000}"

# GUIDs from logitech.xml (Extracted)
LOGITECH_GUIDS = {
    "V1_USER_HW": "{63610682-5070-49ab-b8cc-b3855e8d221f}",
    "V1_VIDEO_PIPE": "{63610682-5070-49ab-b8cc-b3855e8d2250}",
    "V1_MOTOR_CONTROL": "{63610682-5070-49ab-b8cc-b3855e8d2256}",
    "V1_DEVICE_INFO": "{63610682-5070-49ab-b8cc-b3855e8d221e}",
    "V3_DEVICE_INFO": "{69678EE4-410F-40db-A850-7420D7D8240E}",
    "V3_VIDEO_PIPE": "{49E40215-F434-47fe-B158-0E885023E51B}",
    "V3_TEST_DEBUG": "{1F5D4CA9-DE11-4487-840D-50933C8EC8D1}",
    "V3_PERIPHERAL": "{FFE52D21-8030-4e2c-82D9-F587D00540BD}",
    "V3_CODEC": "{9ACD00B6-DC4A-4bbd-BDF8-5FFBB0C0D366}",
    "V3_CODEC_EX": "{49C532A0-4F15-4cfc-908A-5BCE154B1CEA}",
    # Also try the '662' variant seen online
    "V1_MOTOR_ALT": "{63610662-5070-49ab-b8cc-b3855e8d2256}",
}

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

def main():
    print("="*60)
    print("  Logitech Topology GUID Scanner")
    print("="*60)
    
    # Import internals
    from orbcam.logitech.xu_control import (
        ICreateDevEnum, IEnumMoniker, IMoniker, IKsPropertySet, IPropertyBag
    )

    devenum = comtypes.client.CreateObject(
        CLSID_SystemDeviceEnum,
        clsctx=comtypes.CLSCTX_INPROC_SERVER,
        interface=ICreateDevEnum
    )
    
    # Find Camera
    cat_guid = comtypes.GUID(CLSID_VideoInputDeviceCategory)
    enum_moniker = devenum.CreateClassEnumerator(cat_guid, 0).QueryInterface(IEnumMoniker)
    
    found = False
    moniker = None
    
    while True:
        try:
            res = enum_moniker.Next(1)
            if not res: break
            moniker_ptr, fetched = res
            if fetched == 0: break
            
            m = moniker_ptr.QueryInterface(IMoniker)
            IPropertyBag_IID = comtypes.GUID("{55272a00-42cb-11ce-8135-00aa004bb851}")
            p_bag = m.BindToStorage(None, None, ctypes.byref(IPropertyBag_IID)).QueryInterface(IPropertyBag)
            name = str(p_bag.Read("FriendlyName", None))
            
            if "logitech" in name.lower() or "orbit" in name.lower():
                print(f"Found Camera: {name}")
                moniker = m
                found = True
                break
        except: break
        
    if not found:
        print("Camera not found!")
        return

    # Bind to Filter
    IID_IBaseFilter = comtypes.GUID("{56a86895-0ad4-11ce-b03a-0020af0ba770}")
    filter_obj = moniker.BindToObject(None, None, ctypes.byref(IID_IBaseFilter))
    
    # Get Topology
    try:
        topology = filter_obj.QueryInterface(IKsTopologyInfo)
        num_nodes = topology.get_NumNodes()
        print(f"Topology has {num_nodes} nodes.")
        
        for i in range(num_nodes):
            print(f"\nScanning Node {i}...")
            
            # Try getting IKsPropertySet from node
            try:
                iid_propset = comtypes.GUID(IID_IKsPropertySet)
                node_ps = topology.CreateNodeInstance(i, ctypes.byref(iid_propset)).QueryInterface(IKsPropertySet)
                
                # Check ALL GUIDs on this node
                for name, guid_str in LOGITECH_GUIDS.items():
                    try:
                        guid = comtypes.GUID(guid_str)
                        # Check support for Property ID 1 (Common first property)
                        # or specifically ID 1/2 for Motor Control
                        res = node_ps.QuerySupported(guid, 1) # Check ID 1
                        if res:
                            print(f"  *** MATCH! Node {i} supports {name} ({guid_str}) property 1")
                        
                        res2 = node_ps.QuerySupported(guid, 2) # Check ID 2 (Reset?)
                        if res2:
                            print(f"  *** MATCH! Node {i} supports {name} ({guid_str}) property 2")
                            
                    except Exception:
                        pass
                        
            except Exception as e:
                print(f"  Node {i} does not support IKsPropertySet: {e}")
                
    except Exception as e:
        print(f"Failed to get topology info: {e}")
        # Valid fallback: Check filter itself
        print("\nChecking Filter Object itself...")
        try:
            ps = filter_obj.QueryInterface(IKsPropertySet)
            for name, guid_str in LOGITECH_GUIDS.items():
                    try:
                        guid = comtypes.GUID(guid_str)
                        if ps.QuerySupported(guid, 1):
                            print(f"  *** MATCH! Filter supports {name} ({guid_str})")
                    except: pass
        except: pass

if __name__ == "__main__":
    main()
