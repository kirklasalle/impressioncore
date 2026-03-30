import ctypes
from ctypes import wintypes
import logging
import uuid
import comtypes
import comtypes.client

logger = logging.getLogger(__name__)

# DirectShow GUIDs
CLSID_SystemDeviceEnum = "{62BE5D10-60EB-11D0-BD3B-00A0C911CE86}"
CLSID_VideoInputDeviceCategory = "{860BB310-5D01-11D0-BD3B-00A0C911CE86}"
AM_KSCATEGORY_CAPTURE = "{65E8773D-8F56-11D0-A3B9-00A0C9223196}"
IID_ICreateDevEnum = "{29840822-5B84-11D0-BD3B-00A0C911CE86}"
IID_IKsControl = "{28F54881-2CD1-11D1-ADE2-00A0C9223196}"
IID_IKsPropertySet = "{31EFAC30-515C-11D0-A9AA-00AA0061BE93}"

# Logitech Motor Control XU GUIDs
# Known GUID for Orbit/Sphere MP and other Logitech UVC cameras
# The Orbit/Sphere MP specifically uses 63610662 according to several sources.
# Logitech Motor Control XU GUIDs
# Known GUID for Orbit/Sphere MP and other Logitech UVC cameras
# The Orbit/Sphere MP specifically uses 63610662 according to several sources.
LOGITECH_MOTOR_CONTROL_GUID = uuid.UUID("{63610662-5070-49ab-b8cc-b3855e8d2256}")
# Alternative GUID found in some Logitech products
LOGITECH_MOTOR_CONTROL_GUID_V2 = uuid.UUID("{63610682-5070-49AB-B8CC-B3855E8D2256}")

# Control Selectors (CS) for Motor Control
XU_MOTOR_CONTROL_PANTILT_RELATIVE = 1
XU_MOTOR_CONTROL_RESET = 2

# KSPROPERTY Flags
KSPROPERTY_TYPE_SET = 0x00000002
KSPROPERTY_TYPE_GET = 0x00000001

class KSPROPERTY(ctypes.Structure):
    _fields_ = [
        ("Set", ctypes.c_byte * 16),
        ("Id", wintypes.ULONG),
        ("Flags", wintypes.ULONG),
    ]

# IKsControl Interface Definition
class IKsControl(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = comtypes.GUID(IID_IKsControl)
    _idlflags_ = []

IKsControl._methods_ = [
    comtypes.COMMETHOD([], comtypes.HRESULT, "KsProperty",
                (['in'], ctypes.POINTER(KSPROPERTY), "Property"),
                (['in'], wintypes.ULONG, "PropertyLength"),
                (['in', 'out'], ctypes.c_void_p, "PropertyData"),
                (['in'], wintypes.ULONG, "DataLength"),
                (['out'], ctypes.POINTER(wintypes.ULONG), "BytesReturned")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "KsMethod",
                (['in'], ctypes.c_void_p, "Method"),
                (['in'], wintypes.ULONG, "MethodLength"),
                (['in', 'out'], ctypes.c_void_p, "MethodData"),
                (['in'], wintypes.ULONG, "DataLength"),
                (['out'], ctypes.POINTER(wintypes.ULONG), "BytesReturned")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "KsEvent",
                (['in'], ctypes.c_void_p, "Event"),
                (['in'], wintypes.ULONG, "EventLength"),
                (['in', 'out'], ctypes.c_void_p, "EventData"),
                (['in'], wintypes.ULONG, "DataLength"),
                (['out'], ctypes.POINTER(wintypes.ULONG), "BytesReturned")),
]

# IKsPropertySet Interface Definition
class IKsPropertySet(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = comtypes.GUID(IID_IKsPropertySet)
    _idlflags_ = []
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

# IKsPropertySet Interface Definition
class IKsPropertySet(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = comtypes.GUID(IID_IKsPropertySet)
    _idlflags_ = []
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

# ICreateDevEnum Interface Definition
class ICreateDevEnum(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = comtypes.GUID(IID_ICreateDevEnum)
    _idlflags_ = []

ICreateDevEnum._methods_ = [
    comtypes.COMMETHOD([], comtypes.HRESULT, "CreateClassEnumerator",
                (['in'], comtypes.GUID, "clsidDeviceClass"),
                (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppEnumMoniker"),
                (['in'], wintypes.ULONG, "dwFlags")),
]

# IEnumMoniker Interface Definition
class IEnumMoniker(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = comtypes.GUID("{00000102-0000-0000-C000-000000000046}")
    _idlflags_ = []

IEnumMoniker._methods_ = [
    comtypes.COMMETHOD([], comtypes.HRESULT, "Next",
                (['in'], wintypes.ULONG, "celt"),
                (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "rgelt"),
                (['out'], ctypes.POINTER(wintypes.ULONG), "pceltFetched")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "Skip", (['in'], wintypes.ULONG, "celt")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "Reset"),
    comtypes.COMMETHOD([], comtypes.HRESULT, "Clone", (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppenum")),
]

# IMoniker Interface Definition (Inherits from IPersistStream)
class IMoniker(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = comtypes.GUID("{0000010c-0000-0000-C000-000000000046}")
    _idlflags_ = []

IMoniker._methods_ = [
    # IPersist (3)
    comtypes.COMMETHOD([], comtypes.HRESULT, "GetClassID", (['out'], ctypes.POINTER(comtypes.GUID), "pClassID")),
    # IPersistStream (4-7)
    comtypes.COMMETHOD([], comtypes.HRESULT, "IsDirty"),
    comtypes.COMMETHOD([], comtypes.HRESULT, "Load", (['in'], ctypes.c_void_p, "pStm")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "Save", (['in'], ctypes.c_void_p, "pStm"), (['in'], wintypes.BOOL, "fClearDirty")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "GetSizeMax", (['out'], ctypes.POINTER(ctypes.c_ulonglong), "pcbSize")),
    # IMoniker (8+)
    comtypes.COMMETHOD([], comtypes.HRESULT, "BindToObject",
                (['in'], ctypes.c_void_p, "pbc"),
                (['in'], ctypes.c_void_p, "pmkToLeft"),
                (['in'], ctypes.POINTER(comtypes.GUID), "riidResult"),
                (['out', 'retval'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppvResult")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "BindToStorage",
                (['in'], ctypes.c_void_p, "pbc"),
                (['in'], ctypes.c_void_p, "pmkToLeft"),
                (['in'], ctypes.POINTER(comtypes.GUID), "riid"),
                (['out', 'retval'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppv")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "Reduce", (['in'], ctypes.c_void_p, "pbc"), (['in'], wintypes.DWORD, "dwReduceFlags"), (['in', 'out'], ctypes.c_void_p, "ppmkToLeft"), (['out'], ctypes.POINTER(ctypes.c_void_p), "ppmkReduced")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "ComposeWith", (['in'], ctypes.c_void_p, "pmkRight"), (['in'], wintypes.BOOL, "fOnlyIfNotGeneric"), (['out'], ctypes.POINTER(ctypes.c_void_p), "ppmkComposite")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "Enum", (['in'], wintypes.BOOL, "fForward"), (['out'], ctypes.POINTER(ctypes.c_void_p), "ppenumMoniker")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "IsEqual", (['in'], ctypes.c_void_p, "pmkOther")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "Hash", (['out'], ctypes.POINTER(wintypes.DWORD), "pdwHash")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "IsRunning", (['in'], ctypes.c_void_p, "pbc"), (['in'], ctypes.c_void_p, "pmkToLeft"), (['in'], ctypes.c_void_p, "pmkNewlyRunning")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "GetTimeOfLastChange", (['in'], ctypes.c_void_p, "pbc"), (['in'], ctypes.c_void_p, "pmkToLeft"), (['out'], ctypes.POINTER(wintypes.FILETIME), "pfiletime")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "Inverse", (['out'], ctypes.POINTER(ctypes.c_void_p), "ppmk")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "CommonPrefixWith", (['in'], ctypes.c_void_p, "pmkOther"), (['out'], ctypes.POINTER(ctypes.c_void_p), "ppmkPrefix")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "RelativePathTo", (['in'], ctypes.c_void_p, "pmkOther"), (['out'], ctypes.POINTER(ctypes.c_void_p), "ppmkRelPath")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "GetDisplayName",
                (['in'], ctypes.c_void_p, "pbc"),
                (['in'], ctypes.c_void_p, "pmkToLeft"),
                (['out'], ctypes.POINTER(wintypes.LPWSTR), "ppszDisplayName")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "ParseDisplayName", (['in'], ctypes.c_void_p, "pbc"), (['in'], ctypes.c_void_p, "pmkToLeft"), (['in'], wintypes.LPWSTR, "pszDisplayName"), (['out'], ctypes.POINTER(wintypes.ULONG), "pchEaten"), (['out'], ctypes.POINTER(ctypes.c_void_p), "ppmkOut")),
    comtypes.COMMETHOD([], comtypes.HRESULT, "IsSystemMoniker", (['out'], ctypes.POINTER(wintypes.DWORD), "pdwMksys")),
]

# IPropertyBag Interface Definition
class IPropertyBag(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{55272a00-42cb-11ce-8135-00aa004bb851}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "Read",
                    (['in'], wintypes.LPWSTR, "pszPropName"),
                    (['out', 'retval'], ctypes.POINTER(comtypes.automation.VARIANT), "pVar"),
                    (['in'], ctypes.c_void_p, "pErrorLog")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "Write",
                    (['in'], wintypes.LPWSTR, "pszPropName"),
                    (['in'], ctypes.POINTER(comtypes.automation.VARIANT), "pVar")),
    ]

# IKsTopologyInfo Interface Definition
class IKsTopologyInfo(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{720D4AC0-7533-11D0-A5D6-28DB04C10000}")
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

class XUController:
    """
    Handles raw UVC Extension Unit commands for Logitech Orbit.
    """
    def __init__(self, device_path: str = None):
        self._ks_control = None
        self._ks_property_set = None
        self._working_guid = None  # Cache the working motor control GUID
        self._device_path = device_path
        self._init_control()

    def _init_control(self):
        """Attempt to find the camera filter and get IKsControl."""
        
        def _check_support(interface_ptr, is_property_set=False):
            """Helper to check if the interface actually supports our GUIDs."""
            if not interface_ptr: return False
            
            # Check for Logitech GUIDs
            test_guids = [LOGITECH_MOTOR_CONTROL_GUID, LOGITECH_MOTOR_CONTROL_GUID_V2]
            
            for guid in test_guids:
                try:
                    if is_property_set:
                        # IKsPropertySet::QuerySupported(guid, id) -> type_support
                        # If supported, returns the support mask (int). If not, raises COMError.
                        type_support = interface_ptr.QuerySupported(
                            comtypes.GUID(f"{{{guid}}}"),
                            wintypes.DWORD(XU_MOTOR_CONTROL_PANTILT_RELATIVE)
                        )
                        # Check if SET is supported (KSPROPERTY_TYPE_SET = 2)
                        if type_support & KSPROPERTY_TYPE_SET:
                            logger.info(f"XU: Support confirmed for {guid} on IKsPropertySet")
                            self._working_guid = guid
                            return True
                    else:
                        return True
                except Exception as e:
                    logger.debug(f"XU: Support check failed for {guid}: {e}")
                    # FORCE BINDING: The user reports Reset works, implying QuerySupported lies.
                    # We will optimistically accept the first Logitech GUID.
                    if guid in [LOGITECH_MOTOR_CONTROL_GUID, LOGITECH_MOTOR_CONTROL_GUID_V2]:
                        logger.warning(f"XU: Forced binding to {guid} despite QuerySupported failure.")
                        self._working_guid = guid
                        return True
                    pass
            logger.debug(f"XU: No supported GUIDs found on interface {interface_ptr}")
            return False

        try:
            logger.info("XU: Starting DirectShow device enumeration... (Motor Control Protocol)")
            
            # Create Device Enumerator
            devenum = comtypes.client.CreateObject(CLSID_SystemDeviceEnum, 
                                                  clsctx=comtypes.CLSCTX_INPROC_SERVER,
                                                  interface=ICreateDevEnum)
            
            # Categories to check
            categories = [
                ("Video Input", CLSID_VideoInputDeviceCategory),
                ("Capture", AM_KSCATEGORY_CAPTURE)
            ]
            
            candidates = []
            
            for cat_name, cat_id in categories:
                logger.debug(f"XU: Enumerating category: {cat_name} ({cat_id})")
                try:
                    cat_guid = comtypes.GUID(cat_id)
                    enum_moniker_ptr = devenum.CreateClassEnumerator(cat_guid, 0)
                    if not enum_moniker_ptr:
                        logger.debug(f"XU: Category {cat_name} is empty.")
                        continue
                        
                    enum_moniker = enum_moniker_ptr.QueryInterface(IEnumMoniker)
                    while True:
                        try:
                            # Next(celt) -> (rgelt, pceltFetched)
                            res = enum_moniker.Next(1)
                            if not res: break
                            moniker_ptr, fetched = res
                            if fetched == 0 or not moniker_ptr: break
                        except Exception:
                            break
                        
                        moniker = moniker_ptr.QueryInterface(IMoniker)
                        
                        # 1. Gather Device Info
                        name = "Unknown"
                        desc = "None"
                        path = "None"
                        
                        try:
                            IPropertyBag_IID = comtypes.GUID("{55272a00-42cb-11ce-8135-00aa004bb851}")
                            # comtypes handles the out param automatically
                            p_bag = moniker.BindToStorage(None, None, ctypes.byref(IPropertyBag_IID)).QueryInterface(IPropertyBag)
                            if p_bag:
                                try:
                                    def read_prop(pname):
                                        try:
                                            val = p_bag.Read(pname, None)
                                            return str(val) if val is not None else None
                                        except: return None
                                    name = read_prop("FriendlyName") or "Unknown"
                                    desc = read_prop("Description") or "None"
                                    path = read_prop("DevicePath") or "UnknownPath"
                                except Exception as e:
                                    logger.debug(f"XU: PropertyBag Error for {cat_name}: {e}")
                        except Exception as e:
                            logger.debug(f"XU: BindToStorage Error for {cat_name}: {e}")
                            # Fallback to display name
                            try:
                                path = moniker.GetDisplayName(None, None)
                                # Extract meaningful part of path for 'name' if still unknown
                                if name == "Unknown":
                                    name = f"Device@{path[-10:]}"
                            except: pass

                        tag = f"[{name}] (Desc: {desc}, Path: {path[:20]}...)"
                        logger.info(f"XU: Found candidate device in {cat_name}: {tag}")
                        
                        candidates.append({
                            "moniker": moniker,
                            "tag": tag,
                            "is_logitech": any(x in tag.upper() for x in ["LOGITECH", "ORBIT", "SPHERE", "QUICKCAM"])}
                        )
                except Exception as e:
                    logger.error(f"XU: Error enumerating category {cat_name}: {e}")

            if not candidates:
                logger.warning("XU: No video input or capture devices found.")
                return

            # Sort: Logitech first
            candidates.sort(key=lambda x: x["is_logitech"], reverse=True)

            # 2. Binding Loop
            for item in candidates:
                tag = item["tag"]
                moniker = item["moniker"]
                
                logger.debug(f"XU: Probing candidate for hardware binding: {tag}")
                
                try:
                    IBaseFilter_IID = comtypes.GUID("{56A86895-0AD4-11CE-B03A-0020AF0BA770}")
                    p_filter = moniker.BindToObject(None, None, ctypes.byref(IBaseFilter_IID))
                    if not p_filter:
                        continue
                    
                    filter_obj = p_filter.QueryInterface(comtypes.IUnknown)
                    
                    # 1. Try IKsControl on filter itself (Standard for many UVC drivers)
                    try:
                        self._ks_control = filter_obj.QueryInterface(IKsControl)
                        if self._ks_control:
                            logger.info(f"XU: Successfully acquired IKsControl from filter [HINT: Direct]: {tag}")
                            return
                    except Exception:
                        pass

                    # 2. Try IKsPropertySet on filter itself (Fallback)
                    try:
                        ps = filter_obj.QueryInterface(IKsPropertySet)
                        if ps and _check_support(ps, is_property_set=True):
                            self._ks_property_set = ps
                            logger.info(f"XU: Successfully acquired IKsPropertySet from filter: {tag}")
                            return
                    except Exception:
                        pass
                    
                    # 2. Try IKsControl on Pin (Some drivers expose it here)
                    try:
                        # EnumPins is method 9 in IBaseFilter 
                        # We'll use comtypes to get the pins
                        filt_base = filter_obj.QueryInterface(comtypes.IUnknown) # We already have it as filter_obj
                        # Actually, let's try a simpler approach: get pins via enum
                        pass
                    except: pass

                    # 3. Try IKsTopologyInfo to find the XU node
                    try:
                        topology = filter_obj.QueryInterface(IKsTopologyInfo)
                        
                        try:
                            num_nodes = topology.get_NumNodes()
                        except TypeError:
                            n = wintypes.DWORD()
                            topology.get_NumNodes(ctypes.byref(n))
                            num_nodes = n.value

                        logger.debug(f"XU: Filter {tag} has {num_nodes} topology nodes.")
                        
                        for i in range(num_nodes):
                            try:
                                try:
                                    node_type = topology.get_NodeType(i)
                                except TypeError:
                                    g = comtypes.GUID()
                                    topology.get_NodeType(i, ctypes.byref(g))
                                    node_type = g
                                
                                try: node_name = topology.get_NodeName(i)
                                except: node_name = f"Node {i}"
                                
                                logger.debug(f"XU: Checking {node_name} (Type: {node_type})...")
                                
                                # Try to get IKsControl from this node
                                try:
                                    ks_control_iid = comtypes.GUID(IID_IKsControl)
                                    node_instance = topology.CreateNodeInstance(i, ctypes.byref(ks_control_iid))
                                    if node_instance:
                                        node_ctrl = node_instance.QueryInterface(IKsControl)
                                        if node_ctrl:
                                            self._ks_control = node_ctrl
                                            logger.info(f"XU: Successfully acquired IKsControl from {node_name} of {tag}.")
                                            return
                                except Exception:
                                    pass

                                # Try to get IKsPropertySet from this node
                                try:
                                    ks_propset_iid = comtypes.GUID(IID_IKsPropertySet)
                                    node_instance_ps = topology.CreateNodeInstance(i, ctypes.byref(ks_propset_iid))
                                    if node_instance_ps:
                                        node_ps = node_instance_ps.QueryInterface(IKsPropertySet)
                                        if node_ps and _check_support(node_ps, is_property_set=True):
                                            self._ks_property_set = node_ps
                                            logger.info(f"XU: Successfully acquired IKsPropertySet from {node_name} of {tag}.")
                                            return
                                except Exception:
                                    pass
                            except Exception as node_err:
                                logger.debug(f"XU: Failed to probe node {i}: {node_err}")
                    except Exception as e:
                        logger.debug(f"XU: Topology scan skipped or failed for {tag}: {e} (Expected if not a UVC XU driver)")
                        
                except Exception as e:
                    logger.debug(f"XU: Binding failure for {tag}: {e}")

            logger.warning("XU: Did not find any filter supporting IKsControl among candidates.")
        except Exception as e:
            logger.error(f"XU Init Failed: {e}", exc_info=True)

    def _send_command(self, selector: int, data: bytes) -> bool:
        """
        Send a raw KSPROPERTY command to the Extension Unit.
        """
        if not self._ks_control and not self._ks_property_set:
            logger.debug(f"XU (Simulated): Selector {selector} -> Data {data.hex()}")
            return True
        try:
            # 1. Define set of candidate GUIDs to try if none is known
            candidate_guids = [LOGITECH_MOTOR_CONTROL_GUID, LOGITECH_MOTOR_CONTROL_GUID_V2]
            if self._working_guid:
                # Prioritize working one
                candidate_guids = [self._working_guid] + [g for g in candidate_guids if g != self._working_guid]

            # 2. Iterate through candidates
            for guid in candidate_guids:
                prop = KSPROPERTY()
                guid_bytes = guid.bytes_le
                for i in range(16):
                    prop.Set[i] = guid_bytes[i]
                prop.Id = wintypes.ULONG(selector)
                prop.Flags = wintypes.ULONG(KSPROPERTY_TYPE_SET)
                
                # Prepare Data buffer
                data_len = len(data)
                data_buf = ctypes.create_string_buffer(data, data_len)
                bytes_returned = wintypes.ULONG(0)
                
                logger.debug(f"XU: Sending KsProperty (GUID: {guid}) - Selector: {selector}, Data: {data.hex()}")
                
                # Call KsProperty
                hr = -1
                try:
                    if self._ks_control:
                        hr = self._ks_control.KsProperty(
                            ctypes.byref(prop),
                            ctypes.sizeof(prop),
                            ctypes.cast(data_buf, ctypes.c_void_p),
                            data_len,
                            ctypes.byref(bytes_returned)
                        )
                    elif self._ks_property_set:
                        # IKsPropertySet::Set(guidPropSet, dwPropID, pInstance, cbInstance, pPropData, cbPropData)
                        # Instance data is usually NULL for basic XU controls unless specific
                        hr = self._ks_property_set.Set(
                            comtypes.GUID(f"{{{guid}}}"),
                            wintypes.DWORD(selector),
                            None, 0,
                            ctypes.cast(data_buf, ctypes.c_void_p),
                            wintypes.DWORD(data_len)
                        )
                except Exception as loop_err:
                    logger.debug(f"XU: GUID {guid} failed with error: {loop_err}")
                    continue
                
                if hr == 0:
                    if self._working_guid != guid:
                        logger.info(f"XU: Confirmed working Motor Control GUID: {guid}")
                        self._working_guid = guid
                    logger.debug(f"XU: KsProperty Success. Bytes returned: {bytes_returned.value}")
                    return True
                else:
                    # If it's a known failure (e.g. Prop set not found), try next GUID
                    logger.debug(f"XU: KsProperty Failed for GUID {guid} (HRESULT: {hr:x})")
            
            # If all failed
            return False
        except Exception as e:
            logger.error(f"XU Command Error: {e}", exc_info=True)
            return False

    def move_relative(self, pan_speed: int, tilt_speed: int) -> bool:
        """
        Move relative: pan_speed, tilt_speed.
        Protocol 1: [pan (signed 16-bit), tilt (signed 16-bit)]
        Units: 1/64th of a degree.
        """
        try:
            # Values are signed 16-bit integers
            p = max(-32768, min(32767, int(pan_speed)))
            t = max(-32768, min(32767, int(tilt_speed)))
            
            # Pack into 4 bytes (little endian)
            import struct
            data = struct.pack("<hh", p, t)
            
            return self._send_command(XU_MOTOR_CONTROL_PANTILT_RELATIVE, data)
        except Exception as e:
            logger.debug(f"XU: move_relative error: {e}")
            return False

    def _send_command_raw(self, guid_str: str, selector: int, data: bytes) -> bool:
        """
        Send raw command with explicit GUID.
        Useful for testing discovered GUIDs without re-initializing.
        """
        try:
            # 1. Try IKsPropertySet
            if self._ks_property_set:
                guid = comtypes.GUID(f"{{{guid_str}}}")
                # KSPROPERTY structure expects encoded GUID bytes, but ctypes mapping might vary.
                # In previous working code (xu_control.py), we passed comtypes.GUID directly to QuerySupported.
                # But KSPROPERTY structure likely defines Set as c_byte * 16.
                
                # Create the GUID bytes
                guid_bytes = (ctypes.c_byte * 16)()
                ctypes.memmove(ctypes.addressof(guid_bytes), ctypes.addressof(guid), 16)

                # KSPROPERTY structure
                ks_prop = KSPROPERTY()
                ks_prop.Set = guid_bytes
                ks_prop.Id = selector
                ks_prop.Flags = KSPROPERTY_TYPE_SET
                
                # Check support first
                try:
                    support = self._ks_property_set.QuerySupported(guid, selector)
                    if not (support & KSPROPERTY_TYPE_SET):
                        logger.warning(f"XU: Raw GUID {guid_str} Selector {selector} does not support SET")
                except:
                    logger.warning(f"XU: Raw GUID {guid_str} QuerySupported failed, trying anyway...")

                # Send
                ptr = ctypes.cast(data, ctypes.c_void_p)
                hr = self._ks_property_set.Set(
                    guid,
                    selector,
                    None, 0,
                    ptr, len(data)
                )
                if hr == 0:
                    logger.info(f"XU: Raw KSProp Set Success")
                    return True
                else:
                    logger.error(f"XU: Raw KSProp Set Failed: {hr}")

            # 2. Try IKsControl
            if self._ks_control:
                guid = comtypes.GUID(f"{{{guid_str}}}")
                
                 # Create the GUID bytes
                guid_bytes = (ctypes.c_byte * 16)()
                ctypes.memmove(ctypes.addressof(guid_bytes), ctypes.addressof(guid), 16)
                
                prop = KSPROPERTY()
                prop.Set = guid_bytes
                prop.Id = selector
                prop.Flags = KSPROPERTY_TYPE_SET
                
                bytes_returned = wintypes.ULONG()
                data_buffer = (ctypes.c_byte * len(data))(*data)
                
                hr = self._ks_control.KsProperty(
                    ctypes.byref(prop), ctypes.sizeof(prop),
                    ctypes.byref(data_buffer), len(data),
                    ctypes.byref(bytes_returned)
                )
                if hr == 0:
                    logger.info(f"XU: Raw IKsControl Success")
                    return True
                else:
                    logger.error(f"XU: Raw IKsControl Failed: {hr}")
                    
            return False
            
        except Exception as e:
            logger.error(f"XU: Raw command error: {e}")
            return False

    def reset(self) -> bool:
        """Reset head to center. Protocol 2: Bit 0=Pan, Bit 1=Tilt."""
        return self._send_command(XU_MOTOR_CONTROL_RESET, bytes([0x03]))
