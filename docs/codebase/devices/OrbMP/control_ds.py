import sys
import ctypes
from comtypes import *
from comtypes.client import CreateObject, GetModule
import directshow_utils as ds

def main():
    print("Initializing DirectShow Control...")
    
    # Create System Device Enumerator
    sys_enum = CreateObject(ds.CLSID_SystemDeviceEnum, interface=ds.ICreateDevEnum)
    
    # Create Class Enumerator for Video Input Devices
    # enum_moniker is returned by the logic because of ['out'] tag
    try:
        enum_moniker = sys_enum.CreateClassEnumerator(ds.CLSID_VideoInputDeviceCategory, 0)
    except Exception as e:
        print(f"Error creating enumerator: {e}")
        return
    
    if not enum_moniker:
        print("No video devices found.")
        return

    print("Scanning Video Devices...")
    moniker = POINTER(ds.IMoniker)()
    fetched = c_ulong()
    
    while True:
        try:
            moniker, fetched = enum_moniker.Next(1)
        except ValueError: # Stop iteration? Or S_FALSE returns (None, 0)?
             break
        if fetched == 0:
            break
            
        # Get Friendly Name
        try:
            prop_bag = moniker.BindToStorage(None, None, ds.IPropertyBag._iid_)
            
            var_name = ds.VARIANT()
            prop_bag.Read("FriendlyName", byref(var_name), None)
            friendly_name = var_name.value
            print(f"Device: {friendly_name}")
            
            if "Logitech" in friendly_name or "QuickCam" in friendly_name or "Composite" in friendly_name: # Broad match for testing
                print("  [+] Target Candidate Found")
                test_device_node(moniker)
        except Exception as e:
            print(f"  Error inspecting device: {e}")
            
        # moniker is a POINTER, but comtypes wraps it. Release() might be automatic or explicit.
        # moniker.Release()

def test_device_node(moniker):
    # Bind to Filter
    try:
        base_filter = moniker.BindToObject(None, None, ds.IBaseFilter._iid_)
    except Exception as e:
        print(f"  Failed to bind filter: {e}")
        return
    
    # Clean up IBaseFilter later? Python GC usually handles Release if we don't manually.
    
    # Query for IKsTopologyInfo
    try:
        topo_info = base_filter.QueryInterface(ds.IKsTopologyInfo)
    except:
        print("  [-] IKsTopologyInfo NOT supported on this filter.")
        return

    print("  [+] IKsTopologyInfo Supported")
    
    
    num_nodes = topo_info.get_NumNodes()
    print(f"  Nodes: {num_nodes}")
    
    found_node = -1
    
    for i in range(num_nodes):
        node_type = topo_info.get_NodeType(i)
        
        # Check against Logitech GUID
        # {63610682-5070-49AB-B8CC-B3855E8D2256}
        if str(node_type) == str(ds.LOGITECH_XU_GUID):
            print(f"    [!] FOUND LOGITECH XU NODE at Index {i}")
            found_node = i
            break
        else:
            # print(f"    Node {i}: {node_type}")
            pass
            
    if found_node != -1:
        # Get IKsControl for the Node
        # QueryInterface on the FILTER gives us IKsControl for the FILTER.
        # But for XU, we often need to target the Node specifically via the NodeID in KSP_NODE.
        # So we use the Filter's IKsControl, but specify the NodeId.
        
        try:
            ks_control = base_filter.QueryInterface(ds.IKsControl)
        except:
            print("    [-] IKsControl not supported on Filter.")
            return
            
        print("    [+] IKsControl Acquired")
        
        # Try to READ a property (Get Pan/Tilt?)
        # Let's try Control 1 (or 2, 4...)
        # KSP_NODE setup
        
        KSPROPERTY_TYPE_GET = 0x00000001
        
        # Test a few controls
        for ctrl_id in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            ksp = ds.KSP_NODE()
            ksp.Set = ds.LOGITECH_XU_GUID
            ksp.Id = ctrl_id
            ksp.Flags = KSPROPERTY_TYPE_GET | 0x80000000 # KSPROPERTY_TYPE_TOPOLOGY
            # Wait, standard XU access usually requires KSPROPERTY_TYPE_TOPOLOGY flag?
            # Or just GET?
            # If targeting a Node, we MUST set KSPROPERTY_TYPE_TOPOLOGY (0x80000000) usually? 
            # Or simply fill NodeId.
            # Docs say: If requests are directed to a node, include KSPROPERTY_TYPE_TOPOLOGY in Flags.
            ksp.Flags = KSPROPERTY_TYPE_GET | 0x10000000 # KSPROPERTY_TYPE_TOPOLOGY? No 0x10000000 is generic?
            # Let's look up constant.
            # ks.h: KSPROPERTY_TYPE_TOPOLOGY = 0x10000000
            
            ksp.Flags = KSPROPERTY_TYPE_GET | 0x10000000
            ksp.NodeId = found_node
            ksp.Reserved = 0
            
            # Prepare buffer
            data = c_ulong(0) # Assume 4 byte (or 2 byte?)
            bytes_returned = c_ulong(0)
            
            hr = ks_control.KsProperty(
                byref(ksp), ctypes.sizeof(ksp),
                byref(data), ctypes.sizeof(data),
                byref(bytes_returned)
            )
            
            if hr == 0:
                print(f"      Control {ctrl_id}: Value = {data.value} (Size {bytes_returned.value})")
            else:
                # print(f"      Control {ctrl_id}: Failed (HR={hex(hr)})")
                pass

if __name__ == "__main__":
    main()
