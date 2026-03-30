
import ctypes

from comtypes.client import GetModule

# Load Kinect Type Library
try:
    GetModule("C:\\Windows\\System32\\Kinect10.dll")
    from comtypes.gen.Kinect10 import INuiSensor
except Exception as e:
    print(f"Error loading Kinect10.dll: {e}")
    exit(1)

def test_rgb():
    print("Testing Kinect RGB Initialization...")

    # Get sensor
    count = ctypes.c_int(0)
    ctypes.windll.Kinect10.NuiGetSensorCount(ctypes.byref(count))
    print(f"Sensors found: {count.value}")

    if count.value == 0:
        return

    sensor_ptr = ctypes.POINTER(INuiSensor)()
    hr = ctypes.windll.Kinect10.NuiCreateSensorByIndex(0, ctypes.byref(sensor_ptr))
    if hr != 0:
        print(f"Failed to create sensor: {hex(hr & 0xFFFFFFFF)}")
        return

    sensor = sensor_ptr.contents

    # Initialize
    # NUI_INITIALIZE_FLAG_USES_COLOR = 0x00000002
    hr = sensor.NuiInitialize(0x00000002)
    if hr != 0:
        print(f"NuiInitialize fail: {hex(hr & 0xFFFFFFFF)}")
        return
    print("NuiInitialize success (Color only)")

    # Try Open RGB
    # NUI_IMAGE_TYPE_COLOR = 0
    # NUI_IMAGE_RESOLUTION_640x480 = 2
    hStream = ctypes.c_void_p(0)
    hEvent = ctypes.windll.kernel32.CreateEventW(None, False, False, None)

    try:
        hr = sensor.NuiImageStreamOpen(
            0, # NUI_IMAGE_TYPE_COLOR
            2, # NUI_IMAGE_RESOLUTION_640x480
            0, 2,
            hEvent,
            ctypes.byref(hStream)
        )
        if hr == 0:
            print("SUCCESS: RGB Stream Opened!")
        else:
            print(f"FAILED: RGB Stream Open returned {hex(hr & 0xFFFFFFFF)}")

            # Common errors:
            # E_INVALIDARG = 0x80070057
            # E_NUI_DEVICE_NOT_READY = 0x80070015
            # E_NUI_ALREADY_INITIALIZED = 0x80040201

    except Exception as e:
        print(f"Exception during Open: {e}")

    sensor.NuiShutdown()
    print("Done.")

if __name__ == "__main__":
    test_rgb()
