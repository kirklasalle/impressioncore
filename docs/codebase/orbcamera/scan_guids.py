
import logging
import comtypes
import ctypes
from comtypes import GUID
from ctypes import wintypes
import sys
import os

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("scan_guids")

# Add project root
sys.path.append(os.path.abspath("d:/Projects/orbcamera"))

try:
    from orbcam.logitech.xu_control import (
        XUController, IKsTopologyInfo, IKsPropertySet,
        LOGITECH_MOTOR_CONTROL_GUID, LOGITECH_MOTOR_CONTROL_GUID_V2
    )
except ImportError:
    print("Failed to import XUController. Run from project root.")
    sys.exit(1)

# Standard UVC and DirectShow GUIDs to test
KNOWN_GUIDS = {
    "Logitech_XU_V1": LOGITECH_MOTOR_CONTROL_GUID,
    "Logitech_XU_V2": LOGITECH_MOTOR_CONTROL_GUID_V2,
    "PROPSETID_VIDCAP_CAMERACONTROL": "C6E13360-30AC-11d0-A18C-00A0C9118956", # Standard Pan/Tilt
    "PROPSETID_VIDCAP_VIDEOPROCAMP": "C6E13370-30AC-11d0-A18C-00A0C9118956", # Brightness/Contrast
    "KSPROPERTYSETID_Topology": "720D4AC0-7533-11D0-A5D6-28DB04C10000"
}

def scan_topology():
    logger.info("Initializing XUController for device discovery...")
    xu = XUController()
    
    # We need to access the internal topology logic which is usually in _init_control
    # Since we can't easily hook into the middle of that, let's replicate the enumeration 
    # or just use the _init_control side effect if it saves a reference.
    # Currently XUController._init_control doesn't save the topology pointer, 
    # so we'll do a simplified enumeration here.
    
    # Ensure DirectShowLib is generated
    try:
        mod = GetModule("quartz.dll")
        import comtypes.gen
        # The module is likely named something like 'comtypes.gen.QuartzTypeLib'
        # We can find it by inspecting the module we just got
        logging.info(f"Generated module: {mod.__name__}")
        DirectShowLib = mod
    except Exception as e:
        logger.error(f"Failed to generate DirectShowLib: {e}")
        return
    
    CLSID_SystemDeviceEnum = GUID("{62BE5D10-60EB-11D0-BD3B-00A0C911CE86}")
    CLSID_VideoInputDeviceCategory = GUID("{860BB310-5D01-11D0-BD3B-00A0C911CE86}")
    IID_IBaseFilter = GUID("{56A86895-0AD4-11CE-B03A-0020AF0BA770}")

    dev_enum = CreateObject(CLSID_SystemDeviceEnum, interface=DirectShowLib.ICreateDevEnum)
    enum_moniker = dev_enum.CreateClassEnumerator(CLSID_VideoInputDeviceCategory, 0)
    
    if not enum_moniker:
        logger.error("No video devices found.")
        return

    moniker = ctypes.POINTER(DirectShowLib.IMoniker)()
    fetched = wintypes.ULONG()
    
    while enum_moniker.Next(1, ctypes.byref(moniker), ctypes.byref(fetched)) == 0:
        prop_bag = moniker.BindToStorage(None, None, DirectShowLib.IPropertyBag._iid_).QueryInterface(DirectShowLib.IPropertyBag)
        var = prop_bag.Read("FriendlyName", None)
        friendly_name = var
        
        if "Logitech" in friendly_name or "Orbit" in friendly_name:
            logger.info(f"Scanning Device: {friendly_name}")
            
            # Bind to Filter
            filter_obj = moniker.BindToObject(None, None, IID_IBaseFilter).QueryInterface(comtypes.IUnknown)
            
            # Check Topology
            try:
                topology = filter_obj.QueryInterface(IKsTopologyInfo)
                num_nodes = topology.get_NumNodes()
                logger.info(f"  Nodes found: {num_nodes}")
                
                for i in range(num_nodes):
                    node_name = f"Node {i}"
                    try: node_name = topology.get_NodeName(i)
                    except: pass
                    
                    try:
                        node_type = topology.get_NodeType(i)
                        logger.info(f"  [{i}] {node_name} - Type: {node_type}")
                    except:
                        logger.info(f"  [{i}] {node_name} - Type: ???")
                    
                    # Try to create node instance and query for supported GUIDs
                    try:
                        # Try to get IKsPropertySet
                        ks_propset_iid = GUID("{31EFAC30-515C-11d0-A9AA-00AA0061BE93}") # IKsPropertySet
                        node_inst = topology.CreateNodeInstance(i, ctypes.byref(ks_propset_iid))
                        node_ps = node_inst.QueryInterface(IKsPropertySet)
                        
                        logger.info(f"    -> Acquired IKsPropertySet on Node {i}")
                        
                        # Test Support
                        for name, guid_str in KNOWN_GUIDS.items():
                            try:
                                guid = GUID(f"{{{guid_str}}}")
                                type_support = wintypes.DWORD(0)
                                # QuerySupported(guid, id) -> type_support
                                # If supported, it returns the value (or None if void). If not, raises COMError.
                                type_support = node_ps.QuerySupported(guid, 1)
                                logger.info(f"    *** SUPPORTS {name} ({guid_str}) ***")
                            except Exception:
                                pass
                                
                    except Exception as e:
                        logger.debug(f"    -> Failed to access Node {i}: {e}")
                        
            except Exception as e:
                logger.error(f"  Failed to get Topology: {e}")
        
        moniker = None # Release

if __name__ == "__main__":
    scan_topology()
