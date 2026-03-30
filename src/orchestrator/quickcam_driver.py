import contextlib
import ctypes
import logging
import os
import struct
import time
from threading import Lock

# Optional COM support for Windows Native Hack
try:
    # Manual ctypes imports
    from ctypes import POINTER, byref, c_void_p, cast

    import comtypes  # noqa: F401
    from comtypes import COMMETHOD, GUID, HRESULT, IUnknown, helpstring  # noqa: F401
    from comtypes.automation import VARIANT
    from comtypes.client import CreateObject
    with contextlib.suppress(ImportError):
        from pygrabber.dshow_core import ICaptureGraphBuilder2, ICreateDevEnum
    _HAS_COMTYPES = True
except ImportError:
    _HAS_COMTYPES = False

logger = logging.getLogger(__name__)

# --- Logitech USB constants ---
LOGITECH_VID = 0x046D
QUICKCAM_ORBIT_PIDs = [0x08C2, 0x0892, 0x0870, 0x08CC, 0x0994]

# --- UVC Extension Unit (XU) ---
# Official Logitech Motor Control GUID from uvcdynctrl logitech.xml
# UVC_GUID_LOGITECH_MOTOR_CONTROL_V1
LOGITECH_XU_GUID = "{63610682-5070-49AB-B8CC-B3855E8D2256}"
MOTOR_CONTROL_UNIT = 10
# Official selectors from logitech.xml
XU_MOTORCONTROL_PANTILT_RELATIVE = 0x01  # 4 bytes: pan[0:15], tilt[16:31]
XU_MOTORCONTROL_PANTILT_RESET = 0x02     # 1 byte: bit0=pan, bit1=tilt
# Legacy selector names for compatibility
PAN_RELATIVE_SELECTOR = 0x01
TILT_RELATIVE_SELECTOR = 0x02
PAN_RESET_SELECTOR = 0x03
TILT_RESET_SELECTOR = 0x04

# --- Windows IKsControl Definitions ---
IID_IKsControl = GUID("{28F54881-2461-11D1-ADB9-00C04FD8DB08}")
IID_IKsTopologyInfo = GUID("{720D4AC0-7533-11D0-A5D6-28DB04C10000}")
KSPROPERTY_TYPE_SET = 0x02

class KSPROPERTY(ctypes.Structure):
    _fields_ = [
        ("Set", GUID),
        ("Id", ctypes.c_ulong),
        ("Flags", ctypes.c_ulong)
    ]

class IKsTopologyInfo(IUnknown):
    _iid_ = IID_IKsTopologyInfo
    _methods_ = [
        COMMETHOD([], HRESULT, 'get_NumCategories', (['out'], POINTER(ctypes.c_ulong), 'pdwNumCategories')),
        COMMETHOD([], HRESULT, 'get_Category', (['in'], ctypes.c_ulong, 'dwIndex'), (['out'], POINTER(GUID), 'pCategory')),
        COMMETHOD([], HRESULT, 'get_NumConnections', (['out'], POINTER(ctypes.c_ulong), 'pdwNumConnections')),
        COMMETHOD([], HRESULT, 'get_ConnectionInfo', (['in'], ctypes.c_ulong, 'dwIndex'), (['out'], POINTER(c_void_p), 'pConnectionInfo')),
        COMMETHOD([], HRESULT, 'get_NodeName', (['in'], ctypes.c_ulong, 'dwIndex'), (['out'], POINTER(ctypes.c_wchar_p), 'pwchNodeName'), (['in'], ctypes.c_ulong, 'dwBufSize'), (['out'], POINTER(ctypes.c_ulong), 'pdwNameLen')),
        COMMETHOD([], HRESULT, 'get_NumNodes', (['out'], POINTER(ctypes.c_ulong), 'pdwNumNodes')),
        COMMETHOD([], HRESULT, 'get_NodeType', (['in'], ctypes.c_ulong, 'dwIndex'), (['out'], POINTER(GUID), 'pNodeType')),
        COMMETHOD([], HRESULT, 'CreateNodeInstance', (['in'], ctypes.c_ulong, 'dwNodeId'), (['in'], POINTER(GUID), 'iid'), (['out'], POINTER(POINTER(IUnknown)), 'ppvObject')),
    ]

IPIN_INPUT = 0
IPIN_OUTPUT = 1

# Debug flag for exploring Windows Native Driver functionality
# Set to True only for debugging. Known to fail on standard Logitech drivers.
_ENABLE_WIN_XU_DEBUG = True

if _HAS_COMTYPES:
    # --- Kernel Streaming Definitions ---
    # (Defs kept for reference)
    class IKsControl(IUnknown):
        _iid_ = IID_IKsControl
        _methods_ = [
            COMMETHOD([], HRESULT, "KsProperty",
                      (['in'], ctypes.POINTER(KSPROPERTY), "Property"),
                      (['in'], ctypes.c_ulong, "PropertyLength"),
                      (['in', 'out'], ctypes.c_void_p, "PropertyData"),
                      (['in'], ctypes.c_ulong, "DataLength"),
                      (['out'], ctypes.POINTER(ctypes.c_ulong), "BytesReturned")),
            COMMETHOD([], HRESULT, "KsMethod",
                      (['in'], ctypes.c_void_p, "Method"),
                      (['in'], ctypes.c_ulong, "MethodLength"),
                      (['in', 'out'], ctypes.c_void_p, "MethodData"),
                      (['in'], ctypes.c_ulong, "DataLength"),
                      (['out'], ctypes.POINTER(ctypes.c_ulong), "BytesReturned")),
            COMMETHOD([], HRESULT, "KsEvent",
                      (['in'], ctypes.c_void_p, "Event"),
                      (['in'], ctypes.c_ulong, "EventLength"),
                      (['in', 'out'], ctypes.c_void_p, "EventData"),
                      (['in'], ctypes.c_ulong, "DataLength"),
                      (['out'], ctypes.POINTER(ctypes.c_ulong), "BytesReturned")),
        ]

    # --- Manual COM Interface Definitions ---

    class IPropertyBag(IUnknown):
        _iid_ = GUID("{55272A00-42CB-11CE-8135-00AA004BB851}")
        _methods_ = [
            COMMETHOD([], HRESULT, 'Read',
                      (['in'], ctypes.c_wchar_p, 'pszPropName'),
                      (['out'], ctypes.POINTER(VARIANT), 'pVar'),
                      (['in'], ctypes.c_void_p, 'pErrorLog')),
            COMMETHOD([], HRESULT, 'Write',
                      (['in'], ctypes.c_wchar_p, 'pszPropName'),
                      (['in'], ctypes.POINTER(VARIANT), 'pVar')),
        ]

    class IPin(IUnknown):
        _iid_ = GUID("{56A86891-0AD4-11CE-B03A-0020AF0BA770}")
        _methods_ = []

    class IEnumPins(IUnknown):
        _iid_ = GUID("{56A86892-0AD4-11CE-B03A-0020AF0BA770}")
        _methods_ = [
            COMMETHOD([], HRESULT, 'Next',
                      (['in'], ctypes.c_ulong, 'cPins'),
                      (['in'], POINTER(c_void_p), 'ppPins'),
                      (['in'], POINTER(ctypes.c_ulong), 'pcFetched')),
            COMMETHOD([], HRESULT, 'Skip', (['in'], ctypes.c_ulong, 'cPins')),
            COMMETHOD([], HRESULT, 'Reset'),
            COMMETHOD([], HRESULT, 'Clone', (['out'], POINTER(POINTER(IUnknown)), 'ppEnum')),
        ]

    class IBaseFilter(IUnknown):
        _iid_ = GUID("{56A86895-0AD4-11CE-B03A-0020AF0BA770}")
        _methods_ = [
            COMMETHOD([], HRESULT, 'GetClassID', (['out'], POINTER(GUID), 'pClassID')),
            COMMETHOD([], HRESULT, 'Stop'),
            COMMETHOD([], HRESULT, 'Pause'),
            COMMETHOD([], HRESULT, 'Run', (['in'], ctypes.c_longlong, 'tStart')),
            COMMETHOD([], HRESULT, 'GetState', (['in'], ctypes.c_ulong, 'dwMilliSecsTimeout'), (['out'], POINTER(ctypes.c_ulong), 'State')),
            COMMETHOD([], HRESULT, 'SetSyncSource', (['in'], POINTER(IUnknown), 'pClock')),
            COMMETHOD([], HRESULT, 'GetSyncSource', (['out'], POINTER(POINTER(IUnknown)), 'pClock')),
            # Use out with c_void_p
            COMMETHOD([], HRESULT, 'EnumPins', (['out'], POINTER(c_void_p), 'ppEnum')),
        ]

    # --- DirectShow Graph Definitions ---
    CLSID_FilterGraph = GUID("{E436EBB3-524F-11CE-9F53-0020AF0BA770}")
    CLSID_CaptureGraphBuilder2 = GUID("{BF87B6E1-8C27-11D0-B3F0-00AA003761C5}")
    IID_IGraphBuilder = GUID("{56A868A9-0AD4-11CE-B03A-0020AF0BA770}")
    IID_ICaptureGraphBuilder2 = GUID("{BF87B6E1-8C27-11D0-B3F0-00AA003761C5}")

    class IGraphBuilder(IUnknown):
        _iid_ = IID_IGraphBuilder
        _methods_ = [
            COMMETHOD([], HRESULT, 'AddFilter', (['in'], POINTER(IBaseFilter), 'pFilter'), (['in'], ctypes.c_wchar_p, 'pName')),
            COMMETHOD([], HRESULT, 'RemoveFilter', (['in'], POINTER(IBaseFilter), 'pFilter')),
            COMMETHOD([], HRESULT, 'EnumFilters', (['out'], POINTER(POINTER(IUnknown)), 'ppEnum')),
            COMMETHOD([], HRESULT, 'FindFilterByName', (['in'], ctypes.c_wchar_p, 'pName'), (['out'], POINTER(POINTER(IBaseFilter)), 'ppFilter')),
            COMMETHOD([], HRESULT, 'ConnectDirect', (['in'], POINTER(IPin), 'ppinOut'), (['in'], POINTER(IPin), 'ppinIn'), (['in'], POINTER(c_void_p), 'pmt')),
            COMMETHOD([], HRESULT, 'Reconnect', (['in'], POINTER(IPin), 'ppin')),
            COMMETHOD([], HRESULT, 'Disconnect', (['in'], POINTER(IPin), 'ppin')),
            COMMETHOD([], HRESULT, 'SetDefaultSyncSource'),
        ]

    class ICaptureGraphBuilder2(IUnknown):
        _iid_ = IID_ICaptureGraphBuilder2
        _methods_ = [
            COMMETHOD([], HRESULT, 'SetFiltergraph', (['in'], POINTER(IGraphBuilder), 'pfg')),
            COMMETHOD([], HRESULT, 'GetFiltergraph', (['out'], POINTER(POINTER(IGraphBuilder)), 'ppfg')),
            COMMETHOD([], HRESULT, 'SetOutputFileName', (['in'], POINTER(GUID), 'pType'), (['in'], ctypes.c_wchar_p, 'lpstrFile'), (['out'], POINTER(POINTER(IUnknown)), 'ppf'), (['out'], POINTER(POINTER(IUnknown)), 'ppSink')),
            COMMETHOD([], HRESULT, 'FindInterface', (['in'], POINTER(GUID), 'pCategory'), (['in'], POINTER(GUID), 'pType'), (['in'], POINTER(IBaseFilter), 'pf'), (['in'], POINTER(GUID), 'riid'), (['out'], POINTER(POINTER(IUnknown)), 'ppint')),
        ]

# Pan/Tilt ranges
PAN_MIN, PAN_MAX = -4480, 4480
TILT_MIN, TILT_MAX = -1920, 1920

class QuickCamOrbDriver:
    """
    Driver for Logitech QuickCam Orb/Sphere MP motorized control.
    Supports PyUSB (Linux/Zadig) and Windows Native (IKsControl) hacks.
    """
    def __init__(self):
        self.device = None
        self.ks_control = None # Windows Native Interface
        self.connected = False
        self.mode = "NONE" # "USB" or "WIN_XU"
        self._current_pan = 0
        self._current_tilt = 0
        self._lock = Lock()

    def connect(self, friendly_name: str = "") -> bool:
        """Attempts to find the device via USB or Windows DirectShow.
        :return: True if successful, False otherwise
        """
        with self._lock:
            logger.info(f"QuickCam: Attempting connection (hint={friendly_name})...")
            # 1. Try Windows Native Hack (IKsControl via DShow)
            if _HAS_COMTYPES and os.name == 'nt':
                logger.debug("QuickCam: Trying Windows Native XU Hack...")
                if self._connect_windows_xu(friendly_name):
                    self.mode = "WIN_XU"
                    self.connected = True
                    logger.info("QuickCam: Connected via WIN_XU mode.")
                    return True
                else:
                    logger.debug("QuickCam: WIN_XU Hack failed.")

            # 2. Fallback to PyUSB (Requires LibUSB/Zadig)
            logger.debug("QuickCam: Trying PyUSB fallback...")
            if self._connect_pyusb():
                self.mode = "USB"
                self.connected = True
                logger.info("QuickCam: Connected via USB mode.")
                return True

            logger.warning("QuickCam: Connection FAILED (No compatible device found).")
            return False

    def _connect_windows_xu(self, name_hint: str) -> bool:
        """Finds the camera via DirectShow and queries IKsControl."""
        if not _ENABLE_WIN_XU_DEBUG:
            logger.debug("QuickCam: Windows Native XU Hack disabled logic invoked (dead end).")
            return False

        try:
            from pygrabber.dshow_graph import FilterGraph
            graph = FilterGraph()
            devices = graph.get_input_devices()
            logger.debug(f"QuickCam: DShow discovered {len(devices)} devices: {devices}")

            # Find matching device
            target_idx = -1
            if name_hint:
                for idx, name in enumerate(devices):
                    if name_hint.lower() in name.lower() or name.lower() in name_hint.lower():
                        target_idx = idx
                        logger.debug(f"QuickCam: Match found via hint '{name_hint}' -> '{name}' (idx {idx})")
                        break

            # Fallback to anything with "Orb" or "Sphere" or "Orbit" if hint failed
            if target_idx == -1:
                for idx, name in enumerate(devices):
                    if any(k in name.lower() for k in ["orb", "sphere", "orbit"]):
                        target_idx = idx
                        logger.debug(f"QuickCam: Match found via keyword -> '{name}' (idx {idx})")
                        break

            if target_idx == -1:
                logger.debug("QuickCam: No matching DShow device found.")
                return False

            # Get the COM Filter object
            CLSID_VideoInputDeviceCategory = GUID("{860BB310-5D01-11d0-BD3B-00A0C911CE86}")
            CLSID_SystemDeviceEnum = GUID("{62BE5D10-60EB-11d0-BD3B-00A0C911CE86}")

            devenum = CreateObject(CLSID_SystemDeviceEnum)
            # Explicitly cast to ICreateDevEnum using the imported class
            if 'ICreateDevEnum' in globals():
                devenum = devenum.QueryInterface(ICreateDevEnum)
                enum = devenum.CreateClassEnumerator(CLSID_VideoInputDeviceCategory, 0)
            else:
                # Fallback: try raw dynamic dispatch or fail
                logger.error("QuickCam: ICreateDevEnum class not available for cast.")
                return False

            if not enum:
                logger.error("QuickCam: Failed to create DShow class enumerator.")
                return False

            target_filter = None
            while True:
                mon, fetched = enum.Next(1)
                if not mon:
                    break
                # Get name from property bag
                if 'IPropertyBag' in globals():
                    # Bind to IUnknown first using GUID
                    bag_unk = mon.BindToStorage(None, None, IPropertyBag._iid_)
                    bag = bag_unk.QueryInterface(IPropertyBag)
                    # Simplified call with out parameter
                    name = bag.Read("FriendlyName", None)
                    logger.debug(f"QuickCam: Enumerated '{name}' vs Target '{devices[target_idx]}'")
                else:
                    # Fallback (Manual GUID usage would require manual definition of Read)
                    logger.error("QuickCam: IPropertyBag not available.")
                    break

                if name == devices[target_idx]:
                    logger.debug(f"QuickCam: Binding moniker for '{name}'...")
                    # Bind via GUID, then cast using MANUAL interface
                    tf_unk = mon.BindToObject(None, None, IBaseFilter._iid_)
                    target_filter = tf_unk.QueryInterface(IBaseFilter)
                    pass
                    break

            if target_filter:
                # Query for IKsControl (direct hack)
                try:
                    self.ks_control = target_filter.QueryInterface(IKsControl)
                    logger.info(f"QuickCam: Successfully queried IKsControl on Filter for '{name}'.")
                    return True
                except Exception as e:
                    logger.warning(f"QuickCam: IKsControl not on Filter ({e}).")

                    # Probe for IKsTopologyInfo and traverse nodes
                    try:
                        topo = target_filter.QueryInterface(IKsTopologyInfo)
                        logger.info("QuickCam: Filter SUPPORTS IKsTopologyInfo. Traversing nodes...")

                        # comtypes returns 'out' parameters directly
                        num_nodes_val = topo.get_NumNodes()
                        logger.info(f"QuickCam: Found {num_nodes_val} internal topology nodes.")

                        for i in range(num_nodes_val):
                            try:
                                node_guid = topo.get_NodeType(i)
                                # Only log interesting nodes or all for debug
                                logger.debug(f"  Node {i}: Type {node_guid}")

                                # Try to create instance
                                # CreateNodeInstance(dwNodeId, iid) -> ppvObject
                                node_unk = topo.CreateNodeInstance(i, IUnknown._iid_)

                                # Try query IKsControl on node
                                try:
                                    self.ks_control = node_unk.QueryInterface(IKsControl)
                                    logger.info(f"QuickCam:  -> Node {i} SUPPORTS IKsControl! (Type: {node_guid})")
                                    # We found it!
                                    return True
                                except Exception:
                                    pass

                            except Exception as node_e:
                                logger.warning(f"  Node {i} error: {node_e}")

                    except Exception as topo_e:
                        logger.info(f"QuickCam: Topology traversal failed: {topo_e}")

                    # Strategy 3: Use ICaptureGraphBuilder2.FindInterface with Full Graph
                    logger.info("QuickCam: Attempting ICaptureGraphBuilder2.FindInterface (Full Graph Setup)...")
                    try:
                        # 1. Create Filter Graph Manager
                        graph = CreateObject(CLSID_FilterGraph, interface=IGraphBuilder)

                        # 2. Add our filter to the graph
                        graph.AddFilter(target_filter, "QuickCam Target")

                        # 3. Create Capture Graph Builder
                        builder = CreateObject(CLSID_CaptureGraphBuilder2, interface=ICaptureGraphBuilder2)

                        # 4. Initialize Builder with Graph
                        builder.SetFiltergraph(graph)

                        # 5. Find Interface
                        # FindInterface(Category, Type, Filter, IID) -> ppint (automatically handled by comtypes?)
                        # WARNING: comtypes signature for FindInterface:
                        # (['in'], POINTER(GUID), 'pCategory'), (['in'], POINTER(GUID), 'pType'), (['in'], POINTER(IBaseFilter), 'pf'), (['in'], POINTER(GUID), 'riid'), (['out'], POINTER(POINTER(IUnknown)), 'ppint')
                        # We pass None for pointers to allow NULL.

                        # NOTE: manually defined COMMETHOD with ['out'] returns the value.
                        # So builder.FindInterface(None, None, target_filter, IKsControl._iid_) should return the pointer.

                        ks_control_ptr = builder.FindInterface(None, None, target_filter, IKsControl._iid_)

                        # Cast/QI to IKsControl
                        self.ks_control = ks_control_ptr.QueryInterface(IKsControl)
                        logger.info("QuickCam: ICaptureGraphBuilder2 found IKsControl!")
                        return True

                    except Exception as gb_e:
                        logger.warning(f"QuickCam: FindInterface failed: {gb_e}")
                        # import traceback
                        # logger.warning(traceback.format_exc())

                    logger.info("QuickCam: Searching Pins (fallback)...")

                    try:
                        enum_pins_ptr = target_filter.EnumPins()
                        # Cast c_void_p to IEnumPins
                        enum_pins = cast(enum_pins_ptr, POINTER(IEnumPins))
                        while True:
                            # Pass explicit pointers for Next with byref
                            pin_ptr_holder = c_void_p()
                            fetched_holder = ctypes.c_ulong(0)
                            enum_pins.Next(1, byref(pin_ptr_holder), byref(fetched_holder))

                            fetched = fetched_holder.value
                            pin_ptr = pin_ptr_holder.value

                            if not pin_ptr or fetched == 0:
                                break
                            pin = cast(pin_ptr, POINTER(IPin))

                            try:
                                self.ks_control = pin.QueryInterface(IKsControl)
                                logger.info("QuickCam: Successfully queried IKsControl on Pin.")
                                return True
                            except Exception:
                                import traceback
                                logger.error(f"QuickCam: Failed to query IKsControl on Pin: {traceback.format_exc()}")
                                continue
                    except Exception as pin_e:
                        logger.error(f"QuickCam: Failed to enumerate pins: {pin_e}")
                        import traceback
                        logger.error(traceback.format_exc())

                    pass
        except Exception as e:
            import traceback
            logger.error(f"QuickCam: Windows XU Connect error: {e}")
            logger.error(traceback.format_exc())
        return False
    def _connect_pyusb(self) -> bool:
        """Standard PyUSB discovery."""
        try:
            import usb.core
            self.device = usb.core.find(idVendor=LOGITECH_VID)
            if self.device:
                logger.debug(f"QuickCam: Found Logitech device VID:046D PID:{self.device.idProduct:04X}")
                if self.device.idProduct in QUICKCAM_ORBIT_PIDs:
                    logger.info(f"QuickCam: Connected to PID:{self.device.idProduct:04X} via PyUSB.")
                    return True
            else:
                logger.debug("QuickCam: No Logitech USB devices found.")
        except Exception as e:
            logger.debug(f"QuickCam: PyUSB error: {e}")
        return False

    def pan(self, relative: int) -> bool:
        """Relative horizontal movement."""
        relative = max(PAN_MIN, min(PAN_MAX, int(relative)))
        logger.debug(f"QuickCam: Pan request ({relative})")
        if self.mode == "WIN_XU":
            return self._win_xu_command(PAN_RELATIVE_SELECTOR, relative)
        return self._usb_command(PAN_RELATIVE_SELECTOR, relative)

    def tilt(self, relative: int) -> bool:
        """Relative vertical movement."""
        relative = max(TILT_MIN, min(TILT_MAX, int(relative)))
        logger.debug(f"QuickCam: Tilt request ({relative})")
        if self.mode == "WIN_XU":
            return self._win_xu_command(TILT_RELATIVE_SELECTOR, relative)
        return self._usb_command(TILT_RELATIVE_SELECTOR, relative)

    def reset_position(self) -> bool:
        """Sends home/center command."""
        logger.info("QuickCam: Resetting position...")
        if self.mode == "WIN_XU":
            p = self._win_xu_command(PAN_RESET_SELECTOR, 0)
            t = self._win_xu_command(TILT_RESET_SELECTOR, 0)
        else:
            p = self._usb_command(PAN_RESET_SELECTOR, 0)
            t = self._usb_command(TILT_RESET_SELECTOR, 0)
        if p and t:
            self._current_pan, self._current_tilt = 0, 0
            return True
        return False

    def get_position(self) -> tuple[int, int]:
        return (self._current_pan, self._current_tilt)

    def disconnect(self):
        with self._lock:
            logger.info("QuickCam: Disconnecting...")
            if self.device:
                try:
                    import usb.util
                    usb.util.dispose_resources(self.device)
                except Exception:
                    pass
            self.device = None
            self.ks_control = None
            self.connected = False
            self.mode = "NONE"

    def _win_xu_command(self, selector: int, value: int) -> bool:
        """Sends command via Windows IKsControl."""
        if not self.ks_control:
            return False
        try:
            prop = KSPROPERTY()
            prop.Set = GUID(LOGITECH_XU_GUID)
            prop.Id = selector
            prop.Flags = KSPROPERTY_TYPE_SET

            data = ctypes.c_short(value)
            returned = ctypes.c_ulong(0)

            hr = self.ks_control.KsProperty(
                ctypes.byref(prop), ctypes.sizeof(prop),
                ctypes.cast(ctypes.byref(data), ctypes.c_void_p), ctypes.sizeof(data),
                ctypes.byref(returned)
            )
            if hr == 0:
                logger.debug(f"QuickCam: WinXU Command {selector} value {value} SUCCESS")
                if selector == PAN_RELATIVE_SELECTOR:
                    self._current_pan += value
                if selector == TILT_RELATIVE_SELECTOR:
                    self._current_tilt += value
                return True
            else:
                logger.error(f"QuickCam: WinXU Command {selector} FAILED (HRESULT: {hex(hr)})")
        except Exception as e:
            logger.error(f"QuickCam: WinXU Command Error: {e}")
        return False

    def _usb_command(self, selector: int, value: int) -> bool:
        """Sends command via PyUSB."""
        if not self.device:
            return False
        try:
            data = struct.pack("<h", value)
            # LOGITECH_XU_UNIT_ID is 10
            self.device.ctrl_transfer(0x21, 0x01, selector << 8, (10 << 8) | 0, data)
            logger.debug(f"QuickCam: USB Command {selector} value {value} SUCCESS")
            if selector == PAN_RELATIVE_SELECTOR:
                self._current_pan += value
            if selector == TILT_RELATIVE_SELECTOR:
                self._current_tilt += value
            return True
        except Exception as e:
            logger.error(f"QuickCam: USB Command {selector} FAILED: {e}")
            return False

quickcam_driver = QuickCamOrbDriver()


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.DEBUG)

    driver = QuickCamOrbDriver()
    if driver.connect():
        print(f"Connected in mode: {driver.mode}")

        # Test movements
        print("Testing pan...")
        driver.pan(500)
        time.sleep(1)
        driver.pan(-500)
        time.sleep(1)

        print("Testing tilt...")
        driver.tilt(300)
        time.sleep(1)
        driver.tilt(-300)
        time.sleep(1)

        print("Resetting position...")
        driver.reset_position()

        driver.disconnect()
    else:
        print("No QuickCam Orbit device found")
