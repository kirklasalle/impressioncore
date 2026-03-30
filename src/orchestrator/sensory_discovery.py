import sys
from pathlib import Path

import wmi
from comtypes import *
from comtypes.automation import VARIANT

# Add project root to PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.orchestrator.system_logger import log_event

# Minimal DirectShow definitions from OrbMP/directshow_utils.py
CLSID_SystemDeviceEnum = GUID('{62BE5D10-60EB-11D0-BD3B-00A0C911CE86}')
CLSID_VideoInputDeviceCategory = GUID('{860BB310-5D01-11D0-BD3B-00A0C911CE86}')

class IPropertyBag(IUnknown):
    _iid_ = GUID('{55272A00-42CB-11CE-8135-00AA004BB851}')
    _methods_ = [
        COMMETHOD([], HRESULT, 'Read',
                  (['in'], c_void_p, 'pszPropName'),
                  (['in', 'out'], POINTER(VARIANT), 'pVar'),
                  (['in'], c_void_p, 'pErrorLog')),
    ]

class IEnumMoniker(IUnknown):
    _iid_ = GUID('{00000102-0000-0000-C000-000000000046}')
    _methods_ = [
        COMMETHOD([], HRESULT, 'Next',
                  (['in'], c_ulong, 'celt'),
                  (['out'], POINTER(c_void_p), 'rgelt'), # Using c_void_p for flexibility
                  (['out'], POINTER(c_ulong), 'pceltFetched')),
    ]

class ICreateDevEnum(IUnknown):
    _iid_ = GUID('{29840822-5B84-11D0-BD3B-00A0C911CE86}')
    _methods_ = [
        COMMETHOD([], HRESULT, 'CreateClassEnumerator',
                  (['in'], POINTER(GUID), 'clsidDeviceClass'),
                  (['out'], POINTER(POINTER(IEnumMoniker)), 'ppEnumMoniker'),
                  (['in'], c_ulong, 'dwFlags')),
    ]

class IMoniker(IUnknown):
    _iid_ = GUID('{0000000f-0000-0000-C000-000000000046}')
    _methods_ = [
        COMMETHOD([], HRESULT, 'BindToObject',
                  (['in'], c_void_p, 'pbc'),
                  (['in'], c_void_p, 'pmkToLeft'),
                  (['in'], POINTER(GUID), 'riidResult'),
                  (['out'], POINTER(c_void_p), 'ppvResult')),
        COMMETHOD([], HRESULT, 'BindToStorage',
                  (['in'], c_void_p, 'pbc'),
                  (['in'], c_void_p, 'pmkToLeft'),
                  (['in'], POINTER(GUID), 'riid'),
                  (['out'], POINTER(POINTER(IPropertyBag)), 'ppvObj')),
    ]

class WindowsSensoryDiscovery:
    """
    Advanced Windows Device Discovery.
    Uses DirectShow, WMI, and USB probing to build a complete sensory map.
    """

    def __init__(self):
        self.wmi = wmi.WMI()
        self.devices = []

    def scan_cameras(self):
        """Enumerates Video Input Devices via DirectShow."""
        log_event("HARDWARE", "Starting DirectShow camera scan...")

        try:
            from comtypes.client import CreateObject
            sys_enum = CreateObject(CLSID_SystemDeviceEnum, interface=ICreateDevEnum)
            enum_moniker = sys_enum.CreateClassEnumerator(CLSID_VideoInputDeviceCategory, 0)
        except Exception as e:
            log_event("HARDWARE", f"DirectShow init failed: {e}", level="ERROR")
            return []

        if not enum_moniker:
            log_event("HARDWARE", "No DirectShow video devices found.")
            return []

        found = []
        index = 0
        while True:
            try:
                # Manual next call because comtypes wrapper can be tricky with output pointers
                ptr = c_void_p()
                fetched = c_ulong()
                hr = enum_moniker.Next(1, byref(ptr), byref(fetched))

                if hr != 0 or fetched.value == 0:
                    break

                moniker = cast(ptr, POINTER(IMoniker))
                prop_bag = moniker.BindToStorage(None, None, IPropertyBag._iid_)

                var = VARIANT()
                prop_bag.Read("FriendlyName", byref(var), None)
                name = var.value

                path_var = VARIANT()
                # DevicePath contains the hardware ID / Symbolic link
                try:
                    prop_bag.Read("DevicePath", byref(path_var), None)
                    path = path_var.value
                except Exception:
                    path = "UNKNOWN"

                found.append({
                    "index": index,
                    "name": name,
                    "path": path,
                    "source": "DirectShow"
                })
                index += 1
            except Exception as e:
                log_event("HARDWARE", f"Error reading camera moniker: {e}", level="WARNING")
                break

        self.devices = found
        log_event("HARDWARE", f"Discovery found {len(found)} cameras via DirectShow.")
        return found

    def correlate_with_pnp(self):
        """Matches DirectShow names with WMI PnP entities to identify hardware types."""
        pnp_entities = self.wmi.Win32_PnPEntity()

        for dev in self.devices:
            dev["hardware_type"] = "GENERIC"
            dev["status"] = "UNKNOWN"

            # Match by name or path
            for pnp in pnp_entities:
                if (dev["name"] in str(pnp.Name) or
                    (dev["path"] != "UNKNOWN" and dev["path"].lower() in str(pnp.DeviceID).lower())):
                    dev["hardware_id"] = pnp.HardwareID
                    dev["status"] = pnp.Status
                    dev["manufacturer"] = pnp.Manufacturer

                    # Identify specific hardware
                    if "08C2" in str(pnp.HardwareID):
                        dev["hardware_type"] = "LOGITECH_ORBIT"
                    if "045E" in str(pnp.HardwareID):
                        dev["hardware_type"] = "MICROSOFT_KINECT"
                    if "1415" in str(pnp.HardwareID):
                        dev["hardware_type"] = "SONY_PSEYE"
                    break

        return self.devices

    def run_full_diagnosis(self):
        self.scan_cameras()
        self.correlate_with_pnp()
        return self.devices

if __name__ == "__main__":
    discovery = WindowsSensoryDiscovery()
    results = discovery.run_full_diagnosis()
    print("\n--- FINAL SENSORY MAP ---")
    for d in results:
        print(f"[{d['index']}] {d['name']}")
        print(f"    Type: {d['hardware_type']} | Status: {d['status']} | Driver: {d.get('manufacturer')}")
        print(f"    Path: {d['path'][:100]}...")
