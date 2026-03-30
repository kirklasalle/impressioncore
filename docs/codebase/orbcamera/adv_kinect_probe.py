import ctypes
from ctypes import wintypes
import comtypes
from comtypes import GUID, IUnknown, COMMETHOD, HRESULT
import logging

# Standard HRESULTS
S_OK = 0

# --- Kinect Minimal Interfaces for Probing ---
class INuiSensor(IUnknown):
    _iid_ = GUID("{d3d9ab7b-31ba-44ca-8cc0-d42525bbea43}")
    _methods_ = [
        COMMETHOD([], HRESULT, "NuiInitialize", (['in'], wintypes.DWORD, "dwFlags")),
        COMMETHOD([], HRESULT, "NuiShutdown"),
        COMMETHOD([], HRESULT, "NuiSetFrameEndEvent", (['in'], wintypes.HANDLE, "hEvent"), (['in'], wintypes.DWORD, "dwFrameEventFlag")),
        COMMETHOD([], HRESULT, "NuiImageStreamOpen"), # Truncated for probing
        COMMETHOD([], HRESULT, "NuiImageStreamSetImageFrameFlags"),
        COMMETHOD([], HRESULT, "NuiImageStreamGetImageFrameFlags"),
        COMMETHOD([], HRESULT, "NuiImageStreamGetNextFrame"),
        COMMETHOD([], HRESULT, "NuiImageStreamReleaseFrame"),
        COMMETHOD([], HRESULT, "NuiImageGetColorPixelCoordinatesFromDepthPixel"),
        COMMETHOD([], HRESULT, "NuiImageGetColorPixelCoordinatesFromDepthPixelAtResolution"),
        COMMETHOD([], HRESULT, "NuiImageGetColorPixelCoordinateFrameFromDepthPixelFrameAtResolution"),
        COMMETHOD([], HRESULT, "NuiCameraElevationSetAngle", (['in'], ctypes.c_long, "lAngleDegrees")),
        COMMETHOD([], HRESULT, "NuiCameraElevationGetAngle", (['in'], ctypes.POINTER(ctypes.c_long), "plAngleDegrees")),
        COMMETHOD([], HRESULT, "NuiSkeletonTrackingEnable"),
        COMMETHOD([], HRESULT, "NuiSkeletonTrackingDisable"),
        COMMETHOD([], HRESULT, "NuiSkeletonSetTrackedSkeletons"),
        COMMETHOD([], HRESULT, "NuiSkeletonGetNextFrame"),
        COMMETHOD([], HRESULT, "NuiTransformSmooth"),
        COMMETHOD([], HRESULT, "NuiGetAudioSource"),
        COMMETHOD([], ctypes.c_int, "NuiInstanceIndex"),
        COMMETHOD([], comtypes.BSTR, "NuiDeviceConnectionId"),
        COMMETHOD([], comtypes.BSTR, "NuiUniqueId"),
        COMMETHOD([], comtypes.BSTR, "NuiAudioArrayId"),
        COMMETHOD([], HRESULT, "NuiStatus"),
    ]

# For gravity check
class Vector4(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float), ("z", ctypes.c_float), ("w", ctypes.c_float)]

def probe_sensor():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("KinectProbe")
    
    try:
        kinect_dll = ctypes.WinDLL("Kinect10.dll")
    except Exception as e:
        logger.error(f"Kinect DLL not found: {e}")
        return

    count = ctypes.c_int(0)
    kinect_dll.NuiGetSensorCount(ctypes.byref(count))
    logger.info(f"Sensors detected: {count.value}")
    
    if count.value == 0:
        return

    sensor_ptr = ctypes.POINTER(INuiSensor)()
    hr = kinect_dll.NuiCreateSensorByIndex(0, ctypes.byref(sensor_ptr))
    if hr != S_OK:
        logger.error(f"Failed to create sensor: {hr:x}")
        return
    
    sensor = sensor_ptr
    
    logger.info(f"Status: {sensor.NuiStatus():x}")
    logger.info(f"Connection ID: {sensor.NuiDeviceConnectionId()}")
    logger.info(f"Unique ID: {sensor.NuiUniqueId()}")
    logger.info(f"Instance Index: {sensor.NuiInstanceIndex()}")
    
    # Try to get accelerometer
    try:
        vec = Vector4()
        # NuiAccelerometerGetCurrentReading is a DLL export, not a COM method in INuiSensor?
        # Let's check the DLL directly
        hr = kinect_dll.NuiAccelerometerGetCurrentReading(sensor_ptr, ctypes.byref(vec))
        if hr == S_OK:
            logger.info(f"Accelerometer: X:{vec.x:.2f} Y:{vec.y:.2f} Z:{vec.z:.2f}")
    except Exception as e:
        logger.warning(f"Accelerometer check failed: {e}")

if __name__ == "__main__":
    probe_sensor()
