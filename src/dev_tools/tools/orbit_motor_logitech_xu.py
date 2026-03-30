"""
Orbit Motor Control - Using Official Logitech XU GUID
======================================================
Based on the official Logitech uvcdynctrl configuration.

GUID: UVC_GUID_LOGITECH_MOTOR_CONTROL_V1 = 63610682-5070-49ab-b8cc-b3855e8d2256
Selector 1: XU_MOTORCONTROL_PANTILT_RELATIVE (4 bytes: pan[0:15], tilt[16:31])
Selector 2: XU_MOTORCONTROL_PANTILT_RESET (1 byte: bit0=pan, bit1=tilt)

Units: 1/64th of a degree, resolution is 1 degree
"""
import struct
import sys
import time

# The CORRECT Logitech Motor Control GUID from logitech.xml
LOGITECH_MOTOR_GUID = "63610682-5070-49ab-b8cc-b3855e8d2256"

# Control selectors
XU_MOTORCONTROL_PANTILT_RELATIVE = 1
XU_MOTORCONTROL_PANTILT_RESET = 2


def test_with_iksproperty():
    """
    Try to send motor commands via IKsPropertySet through DirectShow.
    This is the interface the Logitech Webcam Software uses.
    """
    try:
        import ctypes
        from ctypes import POINTER, byref, c_byte, c_ulong, c_void_p

        from comtypes import COMMETHOD, GUID, HRESULT, IUnknown
        from comtypes.client import CreateObject
        from pygrabber.dshow_graph import FilterGraph

        print("=" * 60)
        print("  Orbit Motor Control - Official Logitech XU")
        print("=" * 60)
        print()
        print(f"GUID: {LOGITECH_MOTOR_GUID}")
        print()

        # Find the camera via pygrabber
        graph = FilterGraph()
        devices = graph.get_input_devices()
        print(f"Found devices: {devices}")

        if not devices:
            print("No video devices found")
            return False

        target_idx = 0
        for i, name in enumerate(devices):
            if "orbit" in name.lower() or "sphere" in name.lower():
                target_idx = i
                break

        print(f"Using: {devices[target_idx]}")

        # Get the device via DirectShow enumeration
        CLSID_SystemDeviceEnum = GUID("{62BE5D10-60EB-11d0-BD3B-00A0C911CE86}")
        CLSID_VideoInputCategory = GUID("{860BB310-5D01-11d0-BD3B-00A0C911CE86}")

        devenum = CreateObject(CLSID_SystemDeviceEnum)

        # Import the interfaces we need
        try:
            from comtypes.gen.DirectShowLib import ICreateDevEnum, IPropertyBag  # noqa: F401
            devenum_cde = devenum.QueryInterface(ICreateDevEnum)
        except ImportError:
            # Generate the type library
            from comtypes.client import GetModule
            GetModule("quartz.dll")
            from comtypes.gen.QuartzTypeLib import ICreateDevEnum
            devenum_cde = devenum.QueryInterface(ICreateDevEnum)

        enum_moniker = devenum_cde.CreateClassEnumerator(CLSID_VideoInputCategory, 0)
        if not enum_moniker:
            print("No video devices in DirectShow")
            return False

        # Find and get the filter
        IID_IBaseFilter = GUID("{56A86895-0AD4-11CE-B03A-0020AF0BA770}")

        target_filter = None
        while True:
            moniker, fetched = enum_moniker.Next(1)
            if not moniker or fetched == 0:
                break

            # Bind to filter
            try:
                target_filter = moniker.BindToObject(None, None, IID_IBaseFilter)
                print("Got IBaseFilter")
                break
            except Exception as e:
                print(f"BindToObject failed: {e}")
                continue

        if not target_filter:
            print("Could not get filter")
            return False

        # Now try IKsPropertySet
        IID_IKsPropertySet = GUID("{31EFAC30-515C-11D0-A9AA-00AA0061BE93}")

        # Define IKsPropertySet
        class IKsPropertySet(IUnknown):
            _iid_ = IID_IKsPropertySet
            _methods_ = [
                COMMETHOD([], HRESULT, "Set",
                    (['in'], POINTER(GUID), 'guidPropSet'),
                    (['in'], c_ulong, 'dwPropID'),
                    (['in'], c_void_p, 'pInstanceData'),
                    (['in'], c_ulong, 'cbInstanceData'),
                    (['in'], c_void_p, 'pPropData'),
                    (['in'], c_ulong, 'cbPropData')),
                COMMETHOD([], HRESULT, "Get",
                    (['in'], POINTER(GUID), 'guidPropSet'),
                    (['in'], c_ulong, 'dwPropID'),
                    (['in'], c_void_p, 'pInstanceData'),
                    (['in'], c_ulong, 'cbInstanceData'),
                    (['in', 'out'], c_void_p, 'pPropData'),
                    (['in'], c_ulong, 'cbPropData'),
                    (['out'], POINTER(c_ulong), 'pcbReturned')),
                COMMETHOD([], HRESULT, "QuerySupported",
                    (['in'], POINTER(GUID), 'guidPropSet'),
                    (['in'], c_ulong, 'dwPropID'),
                    (['out'], POINTER(c_ulong), 'pTypeSupport')),
            ]

        # Try to query IKsPropertySet from filter
        try:
            ksprop = target_filter.QueryInterface(IKsPropertySet)
            print("Got IKsPropertySet from filter!")
        except Exception as e:
            print(f"IKsPropertySet not on filter: {e}")

            # Try to get it from pins

            enum_pins = target_filter.EnumPins()
            while True:
                pin, fetched = enum_pins.Next(1)
                if not pin or fetched == 0:
                    break

                try:
                    ksprop = pin.QueryInterface(IKsPropertySet)
                    print("Got IKsPropertySet from pin!")
                    break
                except Exception:
                    continue
            else:
                print("IKsPropertySet not available on any pin")
                return False

        # Now send motor command!
        motor_guid = GUID(LOGITECH_MOTOR_GUID)

        # Check if motor control is supported
        type_support = c_ulong()
        try:
            hr = ksprop.QuerySupported(byref(motor_guid), XU_MOTORCONTROL_PANTILT_RELATIVE, byref(type_support))
            print(f"QuerySupported result: hr={hex(hr)}, support={type_support.value}")
        except Exception as e:
            print(f"QuerySupported failed: {e}")

        # Try to send pan/tilt command
        # Data format: pan (int16) + tilt (int16) = 4 bytes
        # Values are in 1/64th of a degree

        print()
        print("Attempting motor movement...")

        # Pan right (positive value)
        pan_value = 64 * 10  # 10 degrees right
        tilt_value = 0

        data = struct.pack("<hh", pan_value, tilt_value)
        data_array = (c_byte * len(data))(*data)

        try:
            hr = ksprop.Set(
                byref(motor_guid),
                XU_MOTORCONTROL_PANTILT_RELATIVE,
                None, 0,
                ctypes.cast(data_array, c_void_p),
                len(data)
            )
            print(f"Pan command result: hr={hex(hr) if hr else 'SUCCESS'}")

            if hr == 0:
                print("Motor should be moving RIGHT now!")
                time.sleep(1)

                # Tilt up
                pan_value = 0
                tilt_value = 64 * 5  # 5 degrees up
                data = struct.pack("<hh", pan_value, tilt_value)
                data_array = (c_byte * len(data))(*data)

                hr = ksprop.Set(
                    byref(motor_guid),
                    XU_MOTORCONTROL_PANTILT_RELATIVE,
                    None, 0,
                    ctypes.cast(data_array, c_void_p),
                    len(data)
                )
                print(f"Tilt command result: hr={hex(hr) if hr else 'SUCCESS'}")

                time.sleep(1)

                # Reset
                print("Resetting motor...")
                reset_data = (c_byte * 1)(0x03)  # Reset both pan and tilt
                hr = ksprop.Set(
                    byref(motor_guid),
                    XU_MOTORCONTROL_PANTILT_RESET,
                    None, 0,
                    ctypes.cast(reset_data, c_void_p),
                    1
                )
                print(f"Reset result: hr={hex(hr) if hr else 'SUCCESS'}")

                return True

        except Exception as e:
            print(f"Set command failed: {e}")
            import traceback
            traceback.print_exc()

        return False

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    if test_with_iksproperty():
        print()
        print("=" * 60)
        print("  SUCCESS! Motor control is working!")
        print("=" * 60)
        return 0
    else:
        print()
        print("=" * 60)
        print("  Motor control via IKsPropertySet failed")
        print("=" * 60)
        print()
        print("The Logitech driver may use a different path.")
        print("Video capture is working - this is the primary goal.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
