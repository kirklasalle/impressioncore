import ctypes
from ctypes import wintypes
import comtypes
from comtypes import GUID, IUnknown, COMMETHOD, HRESULT
import cv2
import numpy as np
import logging
import time
from typing import Optional, Tuple, Dict, Any

from .digital_motor import get_digital_motor
from ..native.skeleton_tracker import SkeletonTracker

logger = logging.getLogger(__name__)

# --- Kinect Constants (SDK 1.8) ---
NUI_INITIALIZE_FLAG_USES_COLOR = 0x02
NUI_INITIALIZE_FLAG_USES_DEPTH = 0x20
NUI_INITIALIZE_FLAG_USES_SKELETON = 0x08
NUI_INITIALIZE_FLAG_USES_AUDIO = 0x10
NUI_IMAGE_TYPE_COLOR = 0
NUI_IMAGE_TYPE_COLOR_YUV = 1
NUI_IMAGE_TYPE_COLOR_INFRARED = 2
NUI_IMAGE_TYPE_DEPTH = 4
NUI_IMAGE_TYPE_DEPTH_AND_PLAYER_INDEX = 5
NUI_IMAGE_RESOLUTION_1280x960 = 3
NUI_IMAGE_RESOLUTION_640x480 = 2
NUI_IMAGE_RESOLUTION_320x240 = 1

# Standard COM HRESULT
S_OK = 0

# --- Video Settings Interface ---
class INuiColorCameraSettings(IUnknown):
    _iid_ = GUID("{64377484-9031-4806-95f8-1383395982d4}")
    _methods_ = [
        COMMETHOD([], HRESULT, "NuiGetAutoExposure", (['out'], ctypes.POINTER(ctypes.c_bool), "pEnabled")),
        COMMETHOD([], HRESULT, "NuiSetAutoExposure", (['in'], ctypes.c_bool, "bEnabled")),
        COMMETHOD([], HRESULT, "NuiGetAutoWhiteBalance", (['out'], ctypes.POINTER(ctypes.c_bool), "pEnabled")),
        COMMETHOD([], HRESULT, "NuiSetAutoWhiteBalance", (['in'], ctypes.c_bool, "bEnabled")),
        COMMETHOD([], HRESULT, "NuiGetBrightness", (['out'], ctypes.POINTER(ctypes.c_double), "pBrightness")),
        COMMETHOD([], HRESULT, "NuiSetBrightness", (['in'], ctypes.c_double, "brightness")),
        COMMETHOD([], HRESULT, "NuiGetContrast", (['out'], ctypes.POINTER(ctypes.c_double), "pContrast")),
        COMMETHOD([], HRESULT, "NuiSetContrast", (['in'], ctypes.c_double, "contrast")),
        COMMETHOD([], HRESULT, "NuiGetExposureTime", (['out'], ctypes.POINTER(ctypes.c_double), "pExposureTime")),
        COMMETHOD([], HRESULT, "NuiSetExposureTime", (['in'], ctypes.c_double, "exposureTime")),
        COMMETHOD([], HRESULT, "NuiGetFrameInterval", (['out'], ctypes.POINTER(ctypes.c_double), "pFrameInterval")),
        COMMETHOD([], HRESULT, "NuiSetFrameInterval", (['in'], ctypes.c_double, "frameInterval")),
        COMMETHOD([], HRESULT, "NuiGetGain", (['out'], ctypes.POINTER(ctypes.c_double), "pGain")),
        COMMETHOD([], HRESULT, "NuiSetGain", (['in'], ctypes.c_double, "gain")),
        COMMETHOD([], HRESULT, "NuiGetGamma", (['out'], ctypes.POINTER(ctypes.c_double), "pGamma")),
        COMMETHOD([], HRESULT, "NuiSetGamma", (['in'], ctypes.c_double, "gamma")),
        COMMETHOD([], HRESULT, "NuiGetHue", (['out'], ctypes.POINTER(ctypes.c_double), "pHue")),
        COMMETHOD([], HRESULT, "NuiSetHue", (['in'], ctypes.c_double, "hue")),
        COMMETHOD([], HRESULT, "NuiGetSaturation", (['out'], ctypes.POINTER(ctypes.c_double), "pSaturation")),
        COMMETHOD([], HRESULT, "NuiSetSaturation", (['in'], ctypes.c_double, "saturation")),
        COMMETHOD([], HRESULT, "NuiGetSharpness", (['out'], ctypes.POINTER(ctypes.c_double), "pSharpness")),
        COMMETHOD([], HRESULT, "NuiSetSharpness", (['in'], ctypes.c_double, "sharpness")),
        COMMETHOD([], HRESULT, "NuiGetWhiteBalance", (['out'], ctypes.POINTER(ctypes.c_double), "pWhiteBalance")),
        COMMETHOD([], HRESULT, "NuiSetWhiteBalance", (['in'], ctypes.c_double, "whiteBalance")),
        COMMETHOD([], HRESULT, "NuiGetPowerLineFrequency", (['out'], ctypes.POINTER(ctypes.c_int), "pFrequency")),
        COMMETHOD([], HRESULT, "NuiSetPowerLineFrequency", (['in'], ctypes.c_int, "frequency")),
        COMMETHOD([], HRESULT, "NuiGetBacklightCompensationMode", (['out'], ctypes.POINTER(ctypes.c_int), "pMode")),
        COMMETHOD([], HRESULT, "NuiSetBacklightCompensationMode", (['in'], ctypes.c_int, "mode")),
    ]

# --- Advanced Data Structures ---
class Vector4(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
        ("w", ctypes.c_float)
    ]

# Frame Structures
class NUI_LOCKED_RECT(ctypes.Structure):
    _fields_ = [
        ("Pitch", ctypes.c_int),
        ("pBits", ctypes.POINTER(ctypes.c_ubyte))
    ]

class INuiFrameTexture(IUnknown):
    _iid_ = GUID("{13ea17f5-ff2e-4670-9ee5-1297a6e880d1}")
    _methods_ = [
        COMMETHOD([], ctypes.c_int, "BufferLen"),
        COMMETHOD([], ctypes.c_int, "Pitch"),
        COMMETHOD([], HRESULT, "LockRect", 
            (['in'], wintypes.UINT, "Level"),
            (['in'], ctypes.POINTER(NUI_LOCKED_RECT), "pLockedRect"),
            (['in'], ctypes.c_void_p, "pRect"),
            (['in'], wintypes.DWORD, "Flags")),
        COMMETHOD([], HRESULT, "GetLevelDesc", (['in'], wintypes.UINT, "Level"), (['in'], ctypes.c_void_p, "pDesc")),
        COMMETHOD([], HRESULT, "UnlockRect", (['in'], wintypes.UINT, "Level"))
    ]

class NUI_SKELETON_DATA(ctypes.Structure):
    _fields_ = [
        ("eTrackingState", ctypes.c_int),
        ("dwTrackingID", wintypes.DWORD),
        ("dwEnrollmentIndex", wintypes.DWORD),
        ("dwUserIndex", wintypes.DWORD),
        ("Position", Vector4),
        ("SkeletonPositions", Vector4 * 20),
        ("eSkeletonPositionTrackingState", ctypes.c_int * 20),
        ("dwQualityFlags", wintypes.DWORD)
    ]

class NUI_SKELETON_FRAME(ctypes.Structure):
    _fields_ = [
        ("liTimeStamp", ctypes.c_int64),
        ("dwFrameNumber", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("SkeletonData", NUI_SKELETON_DATA * 6)
    ]

class NUI_IMAGE_FRAME(ctypes.Structure):
    _fields_ = [
        ("liTimeStamp", ctypes.c_int64),
        ("dwFrameNumber", wintypes.DWORD),
        ("eImageType", ctypes.c_int),
        ("eResolution", ctypes.c_int),
        ("pFrameTexture", ctypes.POINTER(INuiFrameTexture)),
        ("dwFrameFlags", wintypes.DWORD),
        ("ViewArea", ctypes.c_int * 4) # Simplified
    ]

class INuiSensor(IUnknown):
    _iid_ = GUID("{d3d9ab7b-31ba-44ca-8cc0-d42525bbea43}")
    _methods_ = [
        COMMETHOD([], HRESULT, "NuiInitialize", (['in'], wintypes.DWORD, "dwFlags")),
        COMMETHOD([], None, "NuiShutdown"),
        COMMETHOD([], HRESULT, "NuiSetFrameEndEvent", (['in'], wintypes.HANDLE, "hEvent"), (['in'], wintypes.DWORD, "dwFrameEventFlag")),
        COMMETHOD([], HRESULT, "NuiImageStreamOpen", (['in'], ctypes.c_int, "eImageType"), (['in'], ctypes.c_int, "eResolution"), (['in'], wintypes.DWORD, "dwImageFrameFlags"), (['in'], wintypes.DWORD, "dwFrameLimit"), (['in'], wintypes.HANDLE, "hEvent"), (['in'], ctypes.POINTER(wintypes.HANDLE), "phStreamHandle")),
        COMMETHOD([], HRESULT, "NuiImageStreamSetImageFrameFlags", (['in'], wintypes.HANDLE, "hStream"), (['in'], wintypes.DWORD, "dwImageFrameFlags")),
        COMMETHOD([], HRESULT, "NuiImageStreamGetImageFrameFlags", (['in'], wintypes.HANDLE, "hStream"), (['in'], ctypes.POINTER(wintypes.DWORD), "pdwImageFrameFlags")),
        COMMETHOD([], HRESULT, "NuiImageStreamGetNextFrame", (['in'], wintypes.HANDLE, "hStream"), (['in'], wintypes.DWORD, "dwMillisecondsToWait"), (['in'], ctypes.POINTER(NUI_IMAGE_FRAME), "pImageFrame")),
        COMMETHOD([], HRESULT, "NuiImageStreamReleaseFrame", (['in'], wintypes.HANDLE, "hStream"), (['in'], ctypes.POINTER(NUI_IMAGE_FRAME), "pImageFrame")),
        COMMETHOD([], HRESULT, "NuiImageGetColorPixelCoordinatesFromDepthPixel", (['in'], ctypes.c_int, "eColorResolution"), (['in'], ctypes.c_void_p, "pcViewArea"), (['in'], ctypes.c_long, "lDepthX"), (['in'], ctypes.c_long, "lDepthY"), (['in'], ctypes.c_ushort, "usDepthValue"), (['in'], ctypes.POINTER(ctypes.c_long), "plColorX"), (['in'], ctypes.POINTER(ctypes.c_long), "plColorY")),
        COMMETHOD([], HRESULT, "NuiImageGetColorPixelCoordinatesFromDepthPixelAtResolution", (['in'], ctypes.c_int, "eColorResolution"), (['in'], ctypes.c_int, "eDepthResolution"), (['in'], ctypes.c_void_p, "pcViewArea"), (['in'], ctypes.c_long, "lDepthX"), (['in'], ctypes.c_long, "lDepthY"), (['in'], ctypes.c_ushort, "usDepthValue"), (['in'], ctypes.POINTER(ctypes.c_long), "plColorX"), (['in'], ctypes.POINTER(ctypes.c_long), "plColorY")),
        COMMETHOD([], HRESULT, "NuiImageGetColorPixelCoordinateFrameFromDepthPixelFrameAtResolution", (['in'], ctypes.c_int, "eColorResolution"), (['in'], ctypes.c_int, "eDepthResolution"), (['in'], wintypes.DWORD, "cDepthValues"), (['in'], ctypes.POINTER(ctypes.c_ushort), "pDepthValues"), (['in'], wintypes.DWORD, "cColorCoordinates"), (['in'], ctypes.POINTER(ctypes.c_long), "pColorCoordinates")),
        COMMETHOD([], HRESULT, "NuiCameraElevationSetAngle", (['in'], ctypes.c_long, "lAngleDegrees")),
        COMMETHOD([], HRESULT, "NuiCameraElevationGetAngle", (['in'], ctypes.POINTER(ctypes.c_long), "plAngleDegrees")),
        COMMETHOD([], HRESULT, "NuiAccelerometerGetCurrentReading", (['out'], ctypes.POINTER(Vector4), "pReading")),
        COMMETHOD([], HRESULT, "NuiSkeletonTrackingEnable", (['in'], wintypes.HANDLE, "hNextFrameEvent"), (['in'], wintypes.DWORD, "dwFlags")),
        COMMETHOD([], HRESULT, "NuiSkeletonTrackingDisable"),
        COMMETHOD([], HRESULT, "NuiSkeletonSetTrackedSkeletons", (['in'], ctypes.POINTER(wintypes.DWORD), "TrackingIDs")),
        COMMETHOD([], HRESULT, "NuiSkeletonGetNextFrame", (['in'], wintypes.DWORD, "dwMillisecondsToWait"), (['in'], ctypes.c_void_p, "pSkeletonFrame")),
        COMMETHOD([], HRESULT, "NuiTransformSmooth", (['in'], ctypes.c_void_p, "pSkeletonFrame"), (['in'], ctypes.c_void_p, "pSmoothingParams")),
        COMMETHOD([], HRESULT, "NuiGetAudioSource", (['in'], ctypes.POINTER(ctypes.c_void_p), "ppDmo")),
        COMMETHOD([], ctypes.c_int, "NuiInstanceIndex"),
        COMMETHOD([], comtypes.BSTR, "NuiDeviceConnectionId"),
        COMMETHOD([], comtypes.BSTR, "NuiUniqueId"),
        COMMETHOD([], comtypes.BSTR, "NuiAudioArrayId"),
        COMMETHOD([], HRESULT, "NuiStatus"),
        COMMETHOD([], HRESULT, "NuiGetColorCameraSettings", (['out'], ctypes.POINTER(ctypes.POINTER(INuiColorCameraSettings)), "ppColorCameraSettings")),
    ]

# SDK Availability Check
try:
    _kinect_dll_probe = ctypes.WinDLL("Kinect10.dll")
    KINECT_SDK_AVAILABLE = True
except Exception:
    KINECT_SDK_AVAILABLE = False

from ..camera import BaseCamera

class KinectCamera(BaseCamera):
    """
    Kinect v1 implementation using the native SDK.
    """
    def __init__(self, index: int = 0):
        self._index = index
        self._sensor: Optional[INuiSensor] = None
        self._stream_handle: Optional[wintypes.HANDLE] = None
        self._is_open = False
        self._view_w = 640
        self._view_h = 480
        self._motor = get_digital_motor()
        self._full_view_mode = False
        self._skeleton_tracker: Optional[SkeletonTracker] = None
        self._last_skeleton = None
        self._skeleton_frame = NUI_SKELETON_FRAME()
        
        # Extended State
        self._skeleton_enabled = False
        self._depth_enabled = False
        self._near_mode = False
        self._depth_stream_handle = None
        self._resolution = NUI_IMAGE_RESOLUTION_640x480
        self._stream_type = NUI_IMAGE_TYPE_COLOR_YUV
        self._video_mode = "color" # "color", "ir", "depth"
        self._last_frame_time = time.time()

    def open(self) -> None:
        if not KINECT_SDK_AVAILABLE:
            raise RuntimeError("Kinect SDK not available.")
        
        # Create Sensor
        kinect_dll = ctypes.WinDLL("Kinect10.dll")
        sensor_ptr = ctypes.POINTER(INuiSensor)()
        hr = kinect_dll.NuiCreateSensorByIndex(self._index, ctypes.byref(sensor_ptr))
        if hr != S_OK:
            raise RuntimeError(f"Kinect Init failed at index {self._index} (HR: {hr:x})")
        
        self._sensor = sensor_ptr
        
        # Initialize
        # Restore full flag set (Color+Depth+Skeleton) to satisfy driver dependencies for YUV/Raw streams?
        init_combinations = [
            NUI_INITIALIZE_FLAG_USES_COLOR | NUI_INITIALIZE_FLAG_USES_DEPTH | NUI_INITIALIZE_FLAG_USES_SKELETON,
            NUI_INITIALIZE_FLAG_USES_COLOR | NUI_INITIALIZE_FLAG_USES_DEPTH,
            NUI_INITIALIZE_FLAG_USES_COLOR,
        ]
        
        last_hr = 0
        initialized = False
        for flags in init_combinations:
            hr = self._sensor.NuiInitialize(flags)
            if hr == S_OK:
                initialized = True
                logger.info(f"Kinect Init success with flags: {flags:x}")
                break
            last_hr = hr
            
        if not initialized:
            raise RuntimeError(f"Kinect Init failed (HR: {last_hr:x})")
            
        # If we initialized with SKELETON, we must enable it
        # self._sensor.NuiSkeletonTrackingEnable(None, 0)
        # We need to know which flags succeeded. The loop variable 'flags' holds the success value.
        if (flags & NUI_INITIALIZE_FLAG_USES_SKELETON):
             try:
                 # Initialize tracker but don't enable hardware yet
                 from ..native.skeleton_tracker import SkeletonTracker
                 self._skeleton_tracker = SkeletonTracker()
                 logger.info("Skeleton Tracker initialized (Hardware Disabled by default).")
             except Exception as e:
                 logger.error(f"Failed to initialize skeleton tracker: {e}")

        # Give hardware more time to stabilize for auxiliary sensors (Accel/Motor)
        time.sleep(1.0)

        # Open Color Stream
        self._stream_handle = wintypes.HANDLE()
        
        # We revert to COLOR_YUV (Type 1) as Type 0 (RGB) crashes with "Parameter Incorrect"
        for stream_type in [NUI_IMAGE_TYPE_COLOR_YUV]:
            hr = self._sensor.NuiImageStreamOpen(
                stream_type,
                self._resolution,
                0, 2, None,
                ctypes.byref(self._stream_handle)
            )
            if hr == S_OK:
                self._stream_type = stream_type
                break
        
        # Open Depth Stream (Required for Skeleton mapping internally, generally good practice to open explicitly)
        # Resolution must match or be compatible? Skeleton uses 320x240 usually for processing?
        # Use 320x240 for depth to save bandwidth. Skeleton works on 320x240 depth usually.
        
        if hr != S_OK:
            logger.warning(f"Failed to open resolution {self._resolution} (HR: {hr:x}), falling back to 640x480")
            self._resolution = NUI_IMAGE_RESOLUTION_640x480
            for stream_type in [NUI_IMAGE_TYPE_COLOR_YUV, NUI_IMAGE_TYPE_COLOR]:
                hr = self._sensor.NuiImageStreamOpen(
                    stream_type,
                    self._resolution,
                    0, 2, None,
                    ctypes.byref(self._stream_handle)
                )
                if hr == S_OK:
                    self._stream_type = stream_type
                    # SDK Sample: Smooth all skeletons
                    break

        if hr != S_OK:
            raise RuntimeError(f"Failed to open Kinect color stream (HR: {hr:x})")
            
        self._is_open = True
        logger.info(f"Kinect Camera opened at resolution index {self._resolution}")

        # Update flags state if we succeeded
        if flags & NUI_INITIALIZE_FLAG_USES_SKELETON:
            self._skeleton_enabled = True
        if flags & NUI_INITIALIZE_FLAG_USES_DEPTH:
            self._depth_enabled = True

        
    def close(self):
        if self._sensor:
            self._sensor.NuiShutdown()
        self._is_open = False
        self._sensor = None
        logger.info("Kinect Camera closed.")

    @property
    def is_open(self) -> bool:
        return self._is_open

    def read(self) -> Optional[np.ndarray]:
        if not self._is_open or not self._sensor:
            return None

        # Poll Skeleton if enabled (non-blocking attempt)
        if self._skeleton_enabled and BRIDGE_DLL:
            try:
                # Use SimpleSkeleton structure from Bridge
                skel = SimpleSkeleton()
                # comtypes client pointers can be cast directly
                ptr = ctypes.cast(self._sensor, ctypes.c_void_p)
                
                # 0ms timeout
                res = BRIDGE_DLL.GetSkeleton(ptr, ctypes.byref(skel), 0)
                if res == 0:
                    if skel.IsTracked:
                        self._last_skeleton = skel
                else:
                    # If C++ returns non-zero, it might be an error or just no frame. 
                    # Only log errors if they are persistent/fatal, otherwise debug.
                    pass
            except Exception as e:
                # CRITICAL: If bridge fails, log and DISABLE it to save the video stream
                logger.error(f"Bridge Skeleton Error (Disabling Bridge): {e}")
                global BRIDGE_DLL
                BRIDGE_DLL = None
            
        try:
            # 2. Read Color Stream
            frame = NUI_IMAGE_FRAME()
            hr = self._sensor.NuiImageStreamGetNextFrame(self._stream_handle, 50, ctypes.byref(frame))
            if hr != S_OK:
                return None
            
            try:
                texture = frame.pFrameTexture
                if not texture:
                    return None
                    
                locked_rect = NUI_LOCKED_RECT()
                hr = texture.LockRect(0, ctypes.byref(locked_rect), None, 0)
                if hr == S_OK:
                    w, h = (1280, 960) if self._resolution == NUI_IMAGE_RESOLUTION_1280x960 else (640, 480)
                    data_size = h * locked_rect.Pitch
                    data = ctypes.string_at(locked_rect.pBits, data_size)
                    
                    if self._stream_type == NUI_IMAGE_TYPE_COLOR_YUV:
                        if not hasattr(self, '_logged_green_check'):
                            sample = data[:16]
                            logger.info(f"Sample Data: {sample.hex()}")
                            self._logged_green_check = True

                        if locked_rect.Pitch == w * 4:
                             arr = np.frombuffer(data, dtype=np.uint8).reshape((h, w, 4))
                             image = arr[:, :, :3].copy()
                        else:
                             yuv = np.frombuffer(data, dtype=np.uint8).reshape((h, locked_rect.Pitch // 2, 2))
                             image = cv2.cvtColor(yuv[:, :w, :], cv2.COLOR_YUV2BGR_YUY2)
                             
                    elif self._stream_type == NUI_IMAGE_TYPE_COLOR_INFRARED:
                        # SDK Sample: IR is 16-bit, intensity is in the top 8 bits (intensity >> 8)
                        ir16 = np.frombuffer(data, dtype=np.uint16).reshape((h, w))
                        intensity = (ir16 >> 8).astype(np.uint8)
                        image = cv2.cvtColor(intensity, cv2.COLOR_GRAY2BGR)
                        
                    elif self._stream_type in [NUI_IMAGE_TYPE_DEPTH, NUI_IMAGE_TYPE_DEPTH_AND_PLAYER_INDEX]:
                        # 16-bit Depth data. Bits 3-15 are distance in mm. Bits 0-2 are player ID.
                        depth16 = np.frombuffer(data, dtype=np.uint16).reshape((h, w))
                        # Mask out player ID and scale for visualization (0-4000mm -> 0-255)
                        dist = (depth16 >> 3)
                        # Far points (>4000mm) set to 255, near points to 0.
                        depth8 = np.clip(dist / 16, 0, 255).astype(np.uint8)
                        # Apply a colormap for better "Depth perception"
                        image = cv2.applyColorMap(255 - depth8, cv2.COLORMAP_JET)
                    else:
                        # RGB decoding (4 bytes per pixel)
                        arr = np.frombuffer(data, dtype=np.uint8).reshape((h, locked_rect.Pitch // 4, 4))
                        image = arr[:, :w, :3].copy()
                    
                    texture.UnlockRect(0)
                    
                    if self._skeleton_enabled and self._last_skeleton:
                        try:
                            # Draw SimpleSkeleton (Head, Neck, Hands)
                            h, w = image.shape[:2]
                            
                            def to_xy(vec):
                                # Helper to map -1..1 to screen coords (approximate, since NUI coords are in meters)
                                # Actually, NUI is meters. 
                                # Default bridge logic might just return raw meters.
                                # To draw, we usually map -1..1 if using screen space, or project.
                                # Let's assume raw meters and do a rough projection:
                                # Center is (0,0,Z). 
                                
                                # Simple perspective projection: x_screen = (x / z) * f + cx
                                x = vec[0]
                                y = vec[1]
                                z = vec[2]
                                if z == 0: return (0,0)
                                
                                # Rough calibration for Kinect
                                focal_length_x = 580.0
                                focal_length_y = 580.0
                                center_x = w / 2
                                center_y = h / 2
                                
                                screen_x = int((x / z) * focal_length_x + center_x)
                                screen_y = int(-(y / z) * focal_length_y + center_y) # Flip Y
                                return (screen_x, screen_y)

                            head = to_xy(self._last_skeleton.Head)
                            neck = to_xy(self._last_skeleton.Neck)
                            l_hand = to_xy(self._last_skeleton.HandLeft)
                            r_hand = to_xy(self._last_skeleton.HandRight)
                            
                            # Draw Bones
                            cv2.line(image, head, neck, (0, 255, 255), 3)
                            cv2.line(image, neck, l_hand, (0, 255, 0), 3)
                            cv2.line(image, neck, r_hand, (0, 0, 255), 3)
                            
                            # Draw Joints
                            cv2.circle(image, head, 10, (255, 255, 0), -1)
                            cv2.circle(image, l_hand, 8, (0, 255, 0), -1)
                            cv2.circle(image, r_hand, 8, (0, 0, 255), -1)

                        except Exception as e:
                            logger.error(f"Draw Skeleton Error: {e}")

                    if self._full_view_mode:
                        return cv2.resize(image, (self._view_w, self._view_h))
                    else:
                        x, y, cw, ch = self._motor.get_crop_rect(w, h, self._view_w, self._view_h)
                        return cv2.resize(image[y:y+ch, x:x+cw], (self._view_w, self._view_h))
                else:
                    logger.warning(f"LockRect failed (HR: {hr:x})")
            finally:
                self._sensor.NuiImageStreamReleaseFrame(self._stream_handle, ctypes.byref(frame))
                    
        except Exception as e:
            logger.error(f"Kinect Read Error: {e}")
            
        return None

    # --- Dynamic Controls ---

    def set_skeleton_tracking(self, enabled: bool):
        """Enable or disable skeleton tracking at runtime."""
        if not self._sensor: return
        try:
            if enabled:
                # dwFlags: 0 or NUI_SKELETON_TRACKING_FLAG_ENABLE_IN_NEAR_RANGE (0x8)
                flags = 0x8 if self._near_mode else 0
                hr = self._sensor.NuiSkeletonTrackingEnable(0, flags)
                if hr == S_OK:
                    self._skeleton_enabled = True
                    logger.info("Skeleton Tracking enabled.")
            else:
                hr = self._sensor.NuiSkeletonTrackingDisable()
                if hr == S_OK:
                    self._skeleton_enabled = False
                    logger.info("Skeleton Tracking disabled.")
        except Exception as e:
            logger.error(f"Kinect Skeleton Control Error: {e}")

    def set_near_mode(self, enabled: bool):
        """Toggle Near Mode for depth and skeleton."""
        if not self._sensor: return
        self._near_mode = enabled
        # If skeleton is already enabled, we need to re-enable with new flags
        if self._skeleton_enabled:
            self.set_skeleton_tracking(True)
        
        # Also need to set near mode flag on depth stream if we had one
        # Constants: NUI_IMAGE_STREAM_FLAG_ENABLE_NEAR_MODE = 0x00020000
        if self._depth_stream_handle:
            try:
                flags = 0x00020000 if enabled else 0
                self._sensor.NuiImageStreamSetImageFrameFlags(self._depth_stream_handle, flags)
                logger.info(f"Near Mode set to {enabled} on depth stream.")
            except Exception as e:
                logger.error(f"Kinect Near Mode Error: {e}")

    def set_resolution(self, res_index: int):
        """Switch resolution (2=640x480, 3=1280x960)."""
        if not self._sensor: return
        if res_index == self._resolution: return
        
        try:
            # Stop current stream
            # The SDK actually prefers you don't 'close' just one stream.
            # We'll just re-open the stream handle.
            self._resolution = res_index
            new_handle = wintypes.HANDLE()
            hr = self._sensor.NuiImageStreamOpen(
                self._stream_type,
                self._resolution,
                0, 2, None,
                ctypes.byref(new_handle)
            )
            if hr == S_OK:
                self._stream_handle = new_handle
                logger.info(f"Resolution switched to index {res_index}")
        except Exception as e:
            logger.error(f"Kinect Resolution Switch Error: {e}")

    def set_sensor_mode(self, mode: str):
        """Switch between 'color', 'ir', and 'depth' hardware."""
        if not self._sensor: return
        if mode == self._video_mode: return
        
        try:
            # Determine target stream type and resolution
            if mode == "color":
                target_type = NUI_IMAGE_TYPE_COLOR_YUV
                target_res = NUI_IMAGE_RESOLUTION_640x480
            elif mode == "ir":
                target_type = NUI_IMAGE_TYPE_COLOR_INFRARED
                target_res = NUI_IMAGE_RESOLUTION_640x480
            elif mode == "depth":
                target_type = NUI_IMAGE_TYPE_DEPTH
                target_res = NUI_IMAGE_RESOLUTION_640x480 # or 320x240
            else:
                logger.warning(f"Unknown sensor mode: {mode}")
                return

            # Open the new stream handle
            new_handle = wintypes.HANDLE()
            hr = self._sensor.NuiImageStreamOpen(
                target_type,
                target_res,
                0, 2, None,
                ctypes.byref(new_handle)
            )
            
            if hr == S_OK:
                self._stream_handle = new_handle
                self._stream_type = target_type
                self._resolution = target_res
                self._video_mode = mode
                
                # Small delay for IR stabilization
                if mode == "ir": 
                    logger.info("Stabilizing IR sensor...")
                    time.sleep(2.0)
                
                logger.info(f"Switched sensor mode to '{mode}' (Type {target_type})")
            else:
                logger.error(f"Failed to switch sensor mode to '{mode}' (HR: {hr:x})")
                
        except Exception as e:
            logger.error(f"Kinect Sensor Mode Switch Error: {e}")

    def toggle_full_view(self, enabled: Optional[bool] = None):
        if enabled is None: self._full_view_mode = not self._full_view_mode
        else: self._full_view_mode = enabled

    @property
    def pan(self) -> float:
        return self._motor.pan if self._motor else 0.0
    
    @pan.setter
    def pan(self, value: float):
        if self._motor: self._motor.pan = value

    @property
    def tilt(self) -> float:
        if not self._sensor: return 0.0
        try:
            val = ctypes.c_long(0)
            self._sensor.NuiCameraElevationGetAngle(ctypes.byref(val))
            return float(val.value)
        except:
            return 0.0

    @tilt.setter
    def tilt(self, value: float):
        if not self._sensor: return
        try:
            val = int(max(-27, min(27, value)))
            self._sensor.NuiCameraElevationSetAngle(val)
        except Exception as e:
            logger.error(f"Kinect Tilt Error: {e}")

    @property
    def latest_skeleton(self) -> Optional[Dict]:
        """Returns the most recent skeleton data (Head, Neck, Hands)."""
        return self._last_skeleton

    # --- Diagnostic Helpers ---
    def get_hardware_info(self) -> Dict[str, Any]:
        """Returns deep hardware metadata for diagnostics."""
        try:
            # Ensure sensor is at least created
            if not self._sensor:
                try:
                    kinect_dll = ctypes.WinDLL("Kinect10.dll")
                    sensor_ptr = ctypes.POINTER(INuiSensor)()
                    hr = kinect_dll.NuiCreateSensorByIndex(self._index, ctypes.byref(sensor_ptr))
                    if hr == S_OK:
                        self._sensor = sensor_ptr
                except:
                    return {"status": "Disconnected", "message": "Could not create sensor instance"}

            if not self._sensor: return {"status": "Disconnected"}
            
            # We don't necessarily need to call NuiInitialize for IDs,
            # but we'll report what we can.
            info = {
                "status_code": self._sensor.NuiStatus(),
                "instance_index": self._sensor.NuiInstanceIndex(),
            }
            
            try:
                info["unique_id"] = self._sensor.NuiUniqueId()
            except: pass
            
            try:
                info["connection_id"] = self._sensor.NuiDeviceConnectionId()
            except: pass
            
            return info
        except Exception as e:
            return {"status": "Error", "message": str(e)}

    def get_accelerometer_reading(self) -> Optional[Tuple[float, float, float]]:
        """Returns the gravity vector (X, Y, Z) from the sensor using C++ Bridge."""
        if not self._sensor or not BRIDGE_DLL: return None
        try:
            x, y, z = ctypes.c_float(), ctypes.c_float(), ctypes.c_float()
            # comtypes pointer usually needs casting to void_p
            ptr = ctypes.cast(self._sensor, ctypes.c_void_p)
            res = BRIDGE_DLL.GetAccelerometer(ptr, ctypes.byref(x), ctypes.byref(y), ctypes.byref(z))
            if res == 0:
                return (x.value, y.value, z.value)
        except Exception as e:
            logger.error(f"Error getting accelerometer reading via bridge: {e}")
        return None
    @property
    def brightness(self) -> float:
        if not self._sensor or not BRIDGE_DLL: return 0.5
        try:
            b, c = ctypes.c_double(), ctypes.c_double()
            ptr = ctypes.cast(self._sensor, ctypes.c_void_p)
            if BRIDGE_DLL.GetColorSettings(ptr, ctypes.byref(b), ctypes.byref(c)) == 0:
                return float(b.value)
        except: pass
        return 0.5
        
    @brightness.setter
    def brightness(self, value: float):
        if not self._sensor or not BRIDGE_DLL: return
        try:
            ptr = ctypes.cast(self._sensor, ctypes.c_void_p)
            BRIDGE_DLL.SetColorSettings(ptr, float(value), -1.0) # -1 to ignore contrast
        except Exception as e:
            logger.error(f"Kinect Brightness Error: {e}")

    @property
    def contrast(self) -> float:
        if not self._sensor or not BRIDGE_DLL: return 0.5
        try:
            b, c = ctypes.c_double(), ctypes.c_double()
            ptr = ctypes.cast(self._sensor, ctypes.c_void_p)
            if BRIDGE_DLL.GetColorSettings(ptr, ctypes.byref(b), ctypes.byref(c)) == 0:
                return float(c.value)
        except: pass
        return 0.5
        
    @contrast.setter
    def contrast(self, value: float):
        if not self._sensor or not BRIDGE_DLL: return
        try:
            ptr = ctypes.cast(self._sensor, ctypes.c_void_p)
            BRIDGE_DLL.SetColorSettings(ptr, -1.0, float(value)) # -1 to ignore brightness
        except Exception as e:
            logger.error(f"Kinect Contrast Error: {e}")
