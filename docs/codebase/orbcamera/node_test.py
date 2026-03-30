"""
Topology Node 3 Test
======================
Forces IKsControl creation on Topology Node 3.
Extension Units are often mapped to specific nodes, not the main filter.
"""
import logging
import ctypes
from ctypes import wintypes
import comtypes
import comtypes.client
import struct
import sys

# GUIDs
CLSID_SystemDeviceEnum = "{62BE5D10-60EB-11D0-BD3B-00A0C911CE86}"
CLSID_VideoInputDeviceCategory = "{860BB310-5D01-11D0-BD3B-00A0C911CE86}"
IID_IKsTopologyInfo = "{720D4AC0-7533-11D0-A5D6-28DB04C10000}"
IID_IKsControl = "{28F54881-2CD1-11D1-ADE2-00A0C9223196}"

# Logitech Motor Control
MOTOR_GUID = "{63610682-5070-49ab-b8cc-b3855e8d2256}"
SEL_RELATIVE = 1

# KSPROPERTY structure
KSPROPERTY_TYPE_SET = 0x00000002

class KSPROPERTY(ctypes.Structure):
    _fields_ = [
        ("Set", ctypes.c_byte * 16),
        ("Id", wintypes.ULONG),
        ("Flags", wintypes.ULONG),
    ]

# IKsTopologyInfo Interface
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

# IKsControl Interface
class IKsControl(comtypes.IUnknown):
    _iid_ = comtypes.GUID(IID_IKsControl)
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "KsProperty",
                    (['in'], ctypes.POINTER(KSPROPERTY), "Property"),
                    (['in'], wintypes.ULONG, "PropertyLength"),
                    (['in', 'out'], ctypes.c_void_p, "PropertyData"),
                    (['in'], wintypes.ULONG, "DataLength"),
                    (['out'], ctypes.POINTER(wintypes.ULONG), "BytesReturned")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "KsMethod"),
        comtypes.COMMETHOD([], comtypes.HRESULT, "KsEvent"),
    ]

def main():
    print("="*60)
    print("  Topology Node Target Test")
    print("="*60)
    
    # Import internals
    from orbcam.logitech.xu_control import (
        ICreateDevEnum, IEnumMoniker, IMoniker, IPropertyBag
    )

    devenum = comtypes.client.CreateObject(
        CLSID_SystemDeviceEnum,
        clsctx=comtypes.CLSCTX_INPROC_SERVER,
        interface=ICreateDevEnum
    )
    
    # Find Camera
    cat_guid = comtypes.GUID(CLSID_VideoInputDeviceCategory)
    enum_moniker = devenum.CreateClassEnumerator(cat_guid, 0).QueryInterface(IEnumMoniker)
    
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
                break
        except: break

    if not moniker:
        print("Camera not found")
        return

    # Bind to Filter
    IID_IBaseFilter = comtypes.GUID("{56a86895-0ad4-11ce-b03a-0020af0ba770}")
    filter_obj = moniker.BindToObject(None, None, ctypes.byref(IID_IBaseFilter))
    
    topology = filter_obj.QueryInterface(IKsTopologyInfo)
    num_nodes = topology.get_NumNodes()
    print(f"Topology has {num_nodes} nodes.")
    
    # Try creating instance on Node 0-6
    for i in range(num_nodes):
        print(f"\n--- Trying Node {i} ---")
        try:
            # Try to get IKsControl
            iid_kscontrol = comtypes.GUID(IID_IKsControl)
            try:
                node_inst = topology.CreateNodeInstance(i, ctypes.byref(iid_kscontrol))
                node_ctrl = node_inst.QueryInterface(IKsControl)
                print(f"  Acquired IKsControl on Node {i}")
                
                # Try sending command
                guid = comtypes.GUID(MOTOR_GUID)
                guid_bytes = (ctypes.c_byte * 16)()
                ctypes.memmove(ctypes.addressof(guid_bytes), ctypes.addressof(guid), 16)
                
                prop = KSPROPERTY()
                prop.Set = guid_bytes
                prop.Id = SEL_RELATIVE
                prop.Flags = KSPROPERTY_TYPE_SET
                
                # Pan 10 degrees
                data = struct.pack("<hh", 640, 0)
                data_buffer = (ctypes.c_byte * len(data))(*data)
                bytes_returned = wintypes.ULONG()
                
                hr = node_ctrl.KsProperty(
                    ctypes.byref(prop), ctypes.sizeof(prop),
                    ctypes.byref(data_buffer), len(data),
                    ctypes.byref(bytes_returned)
                )
                
                if hr == 0:
                    print("  SUCCESS! Command accepted.")
                    break
                else:
                    print(f"  Command failed: {hr}")
                    
            except Exception as e:
                print(f"  Failed to get IKsControl: {e}")
                
        except Exception as e:
            print(f"  Node error: {e}")

if __name__ == "__main__":
    main()
