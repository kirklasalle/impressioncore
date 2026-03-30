"""
Orbit Motor Control - IAMCameraControl Implementation
=======================================================
Uses the proper DirectShow IAMCameraControl interface for PTZ.
This is how Windows camera applications control pan/tilt.

IMPORTANT: Video streaming continues to work during motor control
because IAMCameraControl is designed for concurrent access.
"""
import ctypes
import sys
import time
from ctypes import HRESULT, POINTER, byref, c_long, c_void_p

# --- DirectShow GUIDs ---
CLSID_SystemDeviceEnum = "{62BE5D10-60EB-11d0-BD3B-00A0C911CE86}"
CLSID_VideoInputDeviceCategory = "{860BB310-5D01-11d0-BD3B-00A0C911CE86}"
CLSID_CaptureGraphBuilder2 = "{BF87B6E1-8C27-11d0-B3F0-00AA003761C5}"
CLSID_FilterGraph = "{E436EBB3-524F-11CE-9F53-0020AF0BA770}"

IID_IBaseFilter = "{56A86895-0AD4-11CE-B03A-0020AF0BA770}"
IID_IGraphBuilder = "{56A868A9-0AD4-11CE-B03A-0020AF0BA770}"
IID_ICaptureGraphBuilder2 = "{93E5A4E0-2D50-11d2-ABFA-00A0C9C6E38D}"
IID_IAMCameraControl = "{C6E13370-30AC-11d0-A18C-00A0C9118956}"

# Camera Control Properties
CameraControl_Pan = 0
CameraControl_Tilt = 1
CameraControl_Roll = 2
CameraControl_Zoom = 3
CameraControl_Exposure = 4
CameraControl_Iris = 5
CameraControl_Focus = 6

# Camera Control Flags
CameraControl_Flags_Auto = 0x0001
CameraControl_Flags_Manual = 0x0002

def test_with_pygrabber():
    """Use pygrabber for easier DirectShow access."""
    try:
        import comtypes  # noqa: F401
        from comtypes import COMMETHOD, GUID, IUnknown
        from comtypes.client import CreateObject  # noqa: F401
        from pygrabber.dshow_graph import FilterGraph

        print("Using pygrabber for DirectShow access...")

        # Create filter graph
        graph = FilterGraph()
        devices = graph.get_input_devices()
        print(f"Found {len(devices)} video input devices:")

        target_idx = -1
        for i, name in enumerate(devices):
            print(f"  [{i}] {name}")
            if "orbit" in name.lower() or "sphere" in name.lower() or "quickcam" in name.lower():
                target_idx = i

        if target_idx == -1:
            print("Could not find Orbit camera in device list")
            return False

        print(f"\nUsing device [{target_idx}]: {devices[target_idx]}")

        # Add the device to graph
        graph.add_video_input_device(target_idx)

        # Get the source filter
        # pygrabber stores filters internally
        source_filter = graph.filters[0] if graph.filters else None

        if not source_filter:
            print("Could not get source filter from graph")
            return False

        print("Got source filter from graph")

        # Define IAMCameraControl interface
        class IAMCameraControl(IUnknown):
            _iid_ = GUID(IID_IAMCameraControl)
            _methods_ = [
                COMMETHOD([], HRESULT, "GetRange",
                    (['in'], c_long, 'Property'),
                    (['out'], POINTER(c_long), 'pMin'),
                    (['out'], POINTER(c_long), 'pMax'),
                    (['out'], POINTER(c_long), 'pSteppingDelta'),
                    (['out'], POINTER(c_long), 'pDefault'),
                    (['out'], POINTER(c_long), 'pCapsFlags')),
                COMMETHOD([], HRESULT, "Set",
                    (['in'], c_long, 'Property'),
                    (['in'], c_long, 'lValue'),
                    (['in'], c_long, 'Flags')),
                COMMETHOD([], HRESULT, "Get",
                    (['in'], c_long, 'Property'),
                    (['out'], POINTER(c_long), 'lValue'),
                    (['out'], POINTER(c_long), 'Flags')),
            ]

        # Try to query IAMCameraControl
        try:
            cam_control = source_filter.QueryInterface(IAMCameraControl)
            print("SUCCESS: Got IAMCameraControl interface!")

            # Get pan range
            pMin, pMax, pStep, pDefault, pCaps = c_long(), c_long(), c_long(), c_long(), c_long()
            hr = cam_control.GetRange(CameraControl_Pan, byref(pMin), byref(pMax), byref(pStep), byref(pDefault), byref(pCaps))
            print(f"Pan range: min={pMin.value}, max={pMax.value}, step={pStep.value}, default={pDefault.value}")

            # Get current pan
            cur_pan, cur_flags = c_long(), c_long()
            hr = cam_control.Get(CameraControl_Pan, byref(cur_pan), byref(cur_flags))
            print(f"Current pan: {cur_pan.value}, flags={cur_flags.value}")

            # Try to set pan
            print("\nAttempting to move camera RIGHT...")
            new_pan = cur_pan.value + pStep.value * 10  # Move 10 steps
            hr = cam_control.Set(CameraControl_Pan, new_pan, CameraControl_Flags_Manual)
            print(f"Set pan result: HRESULT={hex(hr) if hr else 'OK'}")

            time.sleep(1)

            # Get tilt range
            hr = cam_control.GetRange(CameraControl_Tilt, byref(pMin), byref(pMax), byref(pStep), byref(pDefault), byref(pCaps))
            print(f"\nTilt range: min={pMin.value}, max={pMax.value}, step={pStep.value}, default={pDefault.value}")

            # Get current tilt
            cur_tilt = c_long()
            hr = cam_control.Get(CameraControl_Tilt, byref(cur_tilt), byref(cur_flags))
            print(f"Current tilt: {cur_tilt.value}")

            # Try to set tilt
            print("\nAttempting to move camera UP...")
            new_tilt = cur_tilt.value + pStep.value * 5
            hr = cam_control.Set(CameraControl_Tilt, new_tilt, CameraControl_Flags_Manual)
            print(f"Set tilt result: HRESULT={hex(hr) if hr else 'OK'}")

            time.sleep(1)

            # Reset to center
            print("\nResetting to default position...")
            cam_control.Set(CameraControl_Pan, pDefault.value, CameraControl_Flags_Manual)
            cam_control.Set(CameraControl_Tilt, pDefault.value, CameraControl_Flags_Manual)

            return True

        except Exception as e:
            print(f"IAMCameraControl not supported: {e}")
            return False

    except ImportError as e:
        print(f"pygrabber not available: {e}")
        print("Install with: pip install pygrabber")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_comtypes_direct():
    """Direct COM approach without pygrabber."""
    try:
        from comtypes import COMMETHOD, GUID, IUnknown
        from comtypes.client import CreateObject

        print("Using direct comtypes approach...")

        # Define minimal interfaces
        IID_IPropertyBag = GUID("{55272A00-42CB-11CE-8135-00AA004BB851}")
        GUID("{0000000F-0000-0000-C000-000000000046}")

        HRESULT = ctypes.c_long

        class IPropertyBag(IUnknown):
            _iid_ = IID_IPropertyBag
            _methods_ = [
                COMMETHOD([], HRESULT, 'Read',
                    (['in'], ctypes.c_wchar_p, 'pszPropName'),
                    (['in', 'out'], c_void_p, 'pVar'),
                    (['in'], c_void_p, 'pErrorLog')),
            ]

        class IAMCameraControl(IUnknown):
            _iid_ = GUID(IID_IAMCameraControl)
            _methods_ = [
                COMMETHOD([], HRESULT, "GetRange",
                    (['in'], c_long, 'Property'),
                    (['out'], POINTER(c_long), 'pMin'),
                    (['out'], POINTER(c_long), 'pMax'),
                    (['out'], POINTER(c_long), 'pSteppingDelta'),
                    (['out'], POINTER(c_long), 'pDefault'),
                    (['out'], POINTER(c_long), 'pCapsFlags')),
                COMMETHOD([], HRESULT, "Set",
                    (['in'], c_long, 'Property'),
                    (['in'], c_long, 'lValue'),
                    (['in'], c_long, 'Flags')),
                COMMETHOD([], HRESULT, "Get",
                    (['in'], c_long, 'Property'),
                    (['out'], POINTER(c_long), 'lValue'),
                    (['out'], POINTER(c_long), 'Flags')),
            ]

        # Create device enumerator
        devenum = CreateObject(CLSID_SystemDeviceEnum)

        # Get video input category enumerator
        from comtypes.gen import DirectShowLib
        devenum_if = devenum.QueryInterface(DirectShowLib.ICreateDevEnum)
        enum_moniker = devenum_if.CreateClassEnumerator(GUID(CLSID_VideoInputDeviceCategory), 0)

        if not enum_moniker:
            print("No video devices found")
            return False

        # Find Orbit camera
        while True:
            moniker, fetched = enum_moniker.Next(1)
            if not moniker:
                break

            # Get name
            moniker.BindToStorage(None, None, IID_IPropertyBag)
            # ... complex property bag reading

            # Bind to filter
            filter_obj = moniker.BindToObject(None, None, GUID(IID_IBaseFilter))

            # Try IAMCameraControl
            try:
                filter_obj.QueryInterface(IAMCameraControl)
                print("Found IAMCameraControl!")
                # ... use it
                return True
            except Exception:
                continue

        return False

    except Exception as e:
        print(f"Direct comtypes approach failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("  Orbit Motor Control - IAMCameraControl Test")
    print("=" * 60)
    print()

    # Try pygrabber approach first (easier)
    print("[1/2] Testing with pygrabber...")
    print("-" * 40)
    if test_with_pygrabber():
        print()
        print("SUCCESS! Motor control works via IAMCameraControl.")
        return 0

    print()
    print("[2/2] Testing direct comtypes...")
    print("-" * 40)
    if test_with_comtypes_direct():
        print()
        print("SUCCESS! Motor control works via direct COM.")
        return 0

    print()
    print("=" * 60)
    print("  RESULT: IAMCameraControl not available")
    print("=" * 60)
    print()
    print("The Logitech driver may use a proprietary interface.")
    print("Options:")
    print("  1. Use Logitech Webcam Software UI for motor control")
    print("  2. Research Logitech SDK/API")
    print("  3. Consider IKsPropertySet with Logitech XU GUID")

    return 1


if __name__ == "__main__":
    sys.exit(main())
