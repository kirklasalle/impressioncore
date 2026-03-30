"""
Kinect Diagnostic Script
========================
Comprehensive diagnostic for Kinect device status.
"""
import ctypes
import sys

print("=" * 60)
print(" Kinect Diagnostic")
print("=" * 60)

# Load Kinect SDK
try:
    k10 = ctypes.WinDLL("Kinect10.dll")
    print("[OK] Kinect10.dll loaded")
except Exception as e:
    print(f"[FAIL] Cannot load Kinect10.dll: {e}")
    sys.exit(1)

# Get sensor count
count = ctypes.c_int()
hr = k10.NuiGetSensorCount(ctypes.byref(count))
print(f"[OK] Sensor count: {count.value}")

if count.value == 0:
    print("[FAIL] No Kinect sensors detected!")
    sys.exit(1)

# Decode HRESULT
def decode_hr(hr):
    hr = hr & 0xFFFFFFFF
    codes = {
        0x00000000: "S_OK",
        0x83010001: "E_NUI_DEVICE_NOT_CONNECTED",
        0x83010002: "E_NUI_DEVICE_NOT_READY",
        0x83010004: "E_NUI_ALREADY_INITIALIZED",
        0x83010015: "E_NUI_DEVICE_IN_USE",
        0x80070005: "E_ACCESSDENIED",
        0x80070057: "E_INVALIDARG",
    }
    return codes.get(hr, f"0x{hr:08X}")

# Try to get sensor status without opening
print("\n--- Checking sensor status ---")

# Define minimal structures
class INuiSensor_Check(ctypes.Structure):
    pass

INuiSensor_Check_Ptr = ctypes.POINTER(INuiSensor_Check)

# Create sensor
sensor_ptr = INuiSensor_Check_Ptr()
hr = k10.NuiCreateSensorByIndex(0, ctypes.byref(sensor_ptr))
print(f"NuiCreateSensorByIndex: {decode_hr(hr)}")

if hr == 0 and sensor_ptr:
    # Get status using raw vtable call
    # Status is at vtable offset for NuiStatus
    print(f"[OK] Sensor pointer obtained: {sensor_ptr}")

    # Try NuiInitialize with just color
    print("\n--- Attempting initialization ---")

    # Use CoCreateInstance approach
    try:
        import comtypes
        comtypes.CoInitializeEx(comtypes.COINIT_MULTITHREADED)
        print("[OK] COM initialized")
    except Exception:
        pass

    # Direct API call with timeout
    import threading
    result = {"hr": None, "done": False}

    def try_init():
        try:
            # Minimal flags
            hr = k10.NuiInitialize(0x02)  # Just color
            result["hr"] = hr
        except Exception as e:
            result["hr"] = -1
            print(f"Exception: {e}")
        result["done"] = True

    # Run with timeout
    thread = threading.Thread(target=try_init)
    thread.start()
    thread.join(timeout=5.0)

    if not result["done"]:
        print("[TIMEOUT] NuiInitialize hung for 5 seconds")
        print("\n*** DIAGNOSIS: The Kinect device has a stale lock ***")
        print("*** Solution: Unplug USB, wait 10 sec, replug ***")
    elif result["hr"] is not None:
        print(f"NuiInitialize: {decode_hr(result['hr'])}")
        if result["hr"] == 0:
            print("[OK] Kinect initialized successfully!")
            k10.NuiShutdown()
            print("[OK] Shutdown complete")
        elif (result["hr"] & 0xFFFFFFFF) == 0x83010015:
            print("\n*** DIAGNOSIS: E_NUI_DEVICE_IN_USE ***")
            print("Another process has exclusive access.")
            print("*** Solution: Unplug USB, wait 10 sec, replug ***")
else:
    print(f"[FAIL] Could not create sensor: {decode_hr(hr)}")

print("\n" + "=" * 60)
