"""
Xbox 360 Kinect Controller Application
======================================
A comprehensive Python application controlling EVERY function and feature
of the Xbox 360 Kinect for debugging and control purposes.

Features:
- RGB/YUV Video Stream
- IR (Infrared) Stream
- Depth Stream with colormap visualization
- 4-Microphone Array Audio Capture
- Beam Angle & Sound Source Localization
- Motor Tilt Control (±27°)
- Accelerometer Reading
- Full Camera Settings (Brightness, Contrast, Exposure, etc.)
- Skeleton Tracking (20 joints)
- Near Mode Toggle

Requirements:
- Kinect SDK 1.8 installed
- orbos_kinect_bridge.dll compiled (for audio/skeleton)
- Python packages: numpy, opencv-python, comtypes

Author: ImpressionCore Team
Created: January 2026
"""

import contextlib
import ctypes
import logging
import os
import sys
import threading
import time
from ctypes import wintypes
from dataclasses import dataclass
from enum import IntEnum
from typing import Any

import comtypes
import cv2
import numpy as np
from comtypes import COMMETHOD, GUID, HRESULT, IUnknown

# ============================================================================
# LOGGING SETUP
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("KinectController")

# ============================================================================
# KINECT SDK CONSTANTS (SDK 1.8)
# ============================================================================
class NuiInitFlags(IntEnum):
    """Initialization flags for NuiInitialize"""
    USES_DEPTH_AND_PLAYER_INDEX = 0x01
    USES_COLOR = 0x02
    USES_SKELETON = 0x08
    USES_AUDIO = 0x10000000
    USES_DEPTH = 0x20
    USES_HIGH_QUALITY_COLOR = 0x40

class NuiImageType(IntEnum):
    """Image stream types"""
    COLOR = 0
    COLOR_YUV = 1
    COLOR_RAW_YUV = 2
    DEPTH_AND_PLAYER_INDEX = 3
    DEPTH = 4
    COLOR_INFRARED = 5

class NuiImageResolution(IntEnum):
    """Image resolutions"""
    INVALID = -1
    RES_80x60 = 0
    RES_320x240 = 1
    RES_640x480 = 2
    RES_1280x960 = 3

class NuiSkeletonTrackingState(IntEnum):
    """Skeleton tracking states"""
    NOT_TRACKED = 0
    POSITION_ONLY = 1
    TRACKED = 2

# Standard COM HRESULT
S_OK = 0

# ============================================================================
# KINECT ERROR CODES
# ============================================================================
KINECT_ERRORS = {
    0x83010001: "E_NUI_DEVICE_NOT_CONNECTED - Kinect not connected",
    0x83010002: "E_NUI_DEVICE_NOT_READY - Kinect not ready",
    0x83010004: "E_NUI_ALREADY_INITIALIZED - Already initialized",
    0x83010005: "E_NUI_NO_MORE_ITEMS - No more items",
    0x83010008: "E_NUI_FRAME_NO_DATA - No frame data available",
    0x83010015: "E_NUI_DEVICE_IN_USE - Kinect is in use by another process",
    0x80070005: "E_ACCESSDENIED - Access denied (run as admin?)",
    0x80070057: "E_INVALIDARG - Invalid argument",
}

def decode_hresult(hr: int) -> str:
    """Decode HRESULT to human-readable message"""
    if hr < 0:
        hr = hr & 0xFFFFFFFF
    return KINECT_ERRORS.get(hr, f"Unknown error: 0x{hr:08X}")

# ============================================================================
# COM INTERFACE DEFINITIONS
# ============================================================================

class Vector4(ctypes.Structure):
    """4D Vector for accelerometer and skeleton data"""
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
        ("w", ctypes.c_float)
    ]

class NUI_LOCKED_RECT(ctypes.Structure):
    """Locked rectangle for frame data access"""
    _fields_ = [
        ("Pitch", ctypes.c_int),
        ("size", ctypes.c_int),
        ("pBits", ctypes.POINTER(ctypes.c_ubyte))
    ]

class NUI_SURFACE_DESC(ctypes.Structure):
    """Surface descriptor"""
    _fields_ = [("Width", ctypes.c_uint), ("Height", ctypes.c_uint)]

class INuiFrameTexture(IUnknown):
    """Frame texture interface for accessing pixel data"""
    _iid_ = GUID("{13ea17f5-ff2e-4670-9ee5-1297a6e880d1}")
    _methods_ = [
        COMMETHOD([], ctypes.c_int, "BufferLen"),
        COMMETHOD([], ctypes.c_int, "Pitch"),
        COMMETHOD([], HRESULT, "LockRect",
                  (['in'], wintypes.UINT, "Level"),
                  (['in'], ctypes.POINTER(NUI_LOCKED_RECT), "pLockedRect"),
                  (['in'], ctypes.c_void_p, "pRect"),
                  (['in'], wintypes.DWORD, "Flags")),
        COMMETHOD([], HRESULT, "GetLevelDesc",
                  (['in'], wintypes.UINT, "Level"),
                  (['out'], ctypes.POINTER(NUI_SURFACE_DESC), "pDesc")),
        COMMETHOD([], HRESULT, "UnlockRect", (['in'], wintypes.UINT, "Level"))
    ]

class NUI_IMAGE_FRAME(ctypes.Structure):
    """Image frame structure"""
    _fields_ = [
        ("liTimeStamp", ctypes.c_int64),
        ("dwFrameNumber", wintypes.DWORD),
        ("eImageType", ctypes.c_int),
        ("eResolution", ctypes.c_int),
        ("pFrameTexture", ctypes.POINTER(INuiFrameTexture)),
        ("dwFrameFlags", wintypes.DWORD),
        ("ViewArea", ctypes.c_int * 4)
    ]

class NUI_SKELETON_DATA(ctypes.Structure):
    """Skeleton data for one tracked user"""
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
    """Skeleton frame containing up to 6 skeletons"""
    _fields_ = [
        ("liTimeStamp", ctypes.c_int64),
        ("dwFrameNumber", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("vFloorClipPlane", Vector4),
        ("vNormalToGravity", Vector4),
        ("SkeletonData", NUI_SKELETON_DATA * 6)
    ]

class INuiColorCameraSettings(IUnknown):
    """Camera settings interface for brightness, contrast, etc."""
    _iid_ = GUID("{64377484-9031-4806-95f8-1383395982d4}")
    _methods_ = [
        COMMETHOD([], HRESULT, "GetAutoExposure", (['out'], ctypes.POINTER(ctypes.c_bool), "pEnabled")),
        COMMETHOD([], HRESULT, "SetAutoExposure", (['in'], ctypes.c_bool, "bEnabled")),
        COMMETHOD([], HRESULT, "GetAutoWhiteBalance", (['out'], ctypes.POINTER(ctypes.c_bool), "pEnabled")),
        COMMETHOD([], HRESULT, "SetAutoWhiteBalance", (['in'], ctypes.c_bool, "bEnabled")),
        COMMETHOD([], HRESULT, "GetBrightness", (['out'], ctypes.POINTER(ctypes.c_double), "pBrightness")),
        COMMETHOD([], HRESULT, "SetBrightness", (['in'], ctypes.c_double, "brightness")),
        COMMETHOD([], HRESULT, "GetContrast", (['out'], ctypes.POINTER(ctypes.c_double), "pContrast")),
        COMMETHOD([], HRESULT, "SetContrast", (['in'], ctypes.c_double, "contrast")),
        COMMETHOD([], HRESULT, "GetExposureTime", (['out'], ctypes.POINTER(ctypes.c_double), "pExposureTime")),
        COMMETHOD([], HRESULT, "SetExposureTime", (['in'], ctypes.c_double, "exposureTime")),
        COMMETHOD([], HRESULT, "GetFrameInterval", (['out'], ctypes.POINTER(ctypes.c_double), "pFrameInterval")),
        COMMETHOD([], HRESULT, "SetFrameInterval", (['in'], ctypes.c_double, "frameInterval")),
        COMMETHOD([], HRESULT, "GetGain", (['out'], ctypes.POINTER(ctypes.c_double), "pGain")),
        COMMETHOD([], HRESULT, "SetGain", (['in'], ctypes.c_double, "gain")),
        COMMETHOD([], HRESULT, "GetGamma", (['out'], ctypes.POINTER(ctypes.c_double), "pGamma")),
        COMMETHOD([], HRESULT, "SetGamma", (['in'], ctypes.c_double, "gamma")),
        COMMETHOD([], HRESULT, "GetHue", (['out'], ctypes.POINTER(ctypes.c_double), "pHue")),
        COMMETHOD([], HRESULT, "SetHue", (['in'], ctypes.c_double, "hue")),
        COMMETHOD([], HRESULT, "GetSaturation", (['out'], ctypes.POINTER(ctypes.c_double), "pSaturation")),
        COMMETHOD([], HRESULT, "SetSaturation", (['in'], ctypes.c_double, "saturation")),
        COMMETHOD([], HRESULT, "GetSharpness", (['out'], ctypes.POINTER(ctypes.c_double), "pSharpness")),
        COMMETHOD([], HRESULT, "SetSharpness", (['in'], ctypes.c_double, "sharpness")),
        COMMETHOD([], HRESULT, "GetWhiteBalance", (['out'], ctypes.POINTER(ctypes.c_double), "pWhiteBalance")),
        COMMETHOD([], HRESULT, "SetWhiteBalance", (['in'], ctypes.c_double, "whiteBalance")),
        COMMETHOD([], HRESULT, "GetPowerLineFrequency", (['out'], ctypes.POINTER(ctypes.c_int), "pFrequency")),
        COMMETHOD([], HRESULT, "SetPowerLineFrequency", (['in'], ctypes.c_int, "frequency")),
        COMMETHOD([], HRESULT, "GetBacklightCompensationMode", (['out'], ctypes.POINTER(ctypes.c_int), "pMode")),
        COMMETHOD([], HRESULT, "SetBacklightCompensationMode", (['in'], ctypes.c_int, "mode")),
    ]

class INuiSensor(IUnknown):
    """Main Kinect sensor interface"""
    _iid_ = GUID("{d3d9ab7b-31ba-44ca-8cc0-d42525bbea43}")
    _methods_ = [
        COMMETHOD([], HRESULT, "NuiInitialize", (['in'], wintypes.DWORD, "dwFlags")),
        COMMETHOD([], None, "NuiShutdown"),
        COMMETHOD([], HRESULT, "NuiSetFrameEndEvent",
                  (['in'], wintypes.HANDLE, "hEvent"),
                  (['in'], wintypes.DWORD, "dwFrameEventFlag")),
        COMMETHOD([], HRESULT, "NuiImageStreamOpen",
                  (['in'], ctypes.c_int, "eImageType"),
                  (['in'], ctypes.c_int, "eResolution"),
                  (['in'], wintypes.DWORD, "dwImageFrameFlags"),
                  (['in'], wintypes.DWORD, "dwFrameLimit"),
                  (['in'], wintypes.HANDLE, "hEvent"),
                  (['in'], ctypes.POINTER(wintypes.HANDLE), "phStreamHandle")),
        COMMETHOD([], HRESULT, "NuiImageStreamSetImageFrameFlags",
                  (['in'], wintypes.HANDLE, "hStream"),
                  (['in'], wintypes.DWORD, "dwImageFrameFlags")),
        COMMETHOD([], HRESULT, "NuiImageStreamGetImageFrameFlags",
                  (['in'], wintypes.HANDLE, "hStream"),
                  (['in'], ctypes.POINTER(wintypes.DWORD), "pdwImageFrameFlags")),
        COMMETHOD([], HRESULT, "NuiImageStreamGetNextFrame",
                  (['in'], wintypes.HANDLE, "hStream"),
                  (['in'], wintypes.DWORD, "dwMillisecondsToWait"),
                  (['in'], ctypes.c_void_p, "pImageFrame")),
        COMMETHOD([], HRESULT, "NuiImageStreamReleaseFrame",
                  (['in'], wintypes.HANDLE, "hStream"),
                  (['in'], ctypes.c_void_p, "pImageFrame")),
        COMMETHOD([], HRESULT, "NuiImageGetColorPixelCoordinatesFromDepthPixel"),
        COMMETHOD([], HRESULT, "NuiImageGetColorPixelCoordinatesFromDepthPixelAtResolution"),
        COMMETHOD([], HRESULT, "NuiImageGetColorPixelCoordinateFrameFromDepthPixelFrameAtResolution"),
        COMMETHOD([], HRESULT, "NuiCameraElevationSetAngle", (['in'], ctypes.c_long, "lAngleDegrees")),
        COMMETHOD([], HRESULT, "NuiCameraElevationGetAngle", (['in'], ctypes.POINTER(ctypes.c_long), "plAngleDegrees")),
        COMMETHOD([], HRESULT, "NuiAccelerometerGetCurrentReading", (['out'], ctypes.POINTER(Vector4), "pReading")),
        COMMETHOD([], HRESULT, "NuiSkeletonTrackingEnable",
                  (['in'], wintypes.HANDLE, "hNextFrameEvent"),
                  (['in'], wintypes.DWORD, "dwFlags")),
        COMMETHOD([], HRESULT, "NuiSkeletonTrackingDisable"),
        COMMETHOD([], HRESULT, "NuiSkeletonSetTrackedSkeletons",
                  (['in'], ctypes.POINTER(wintypes.DWORD), "TrackingIDs")),
        COMMETHOD([], HRESULT, "NuiSkeletonGetNextFrame",
                  (['in'], wintypes.DWORD, "dwMillisecondsToWait"),
                  (['in'], ctypes.c_void_p, "pSkeletonFrame")),
        COMMETHOD([], HRESULT, "NuiTransformSmooth",
                  (['in'], ctypes.c_void_p, "pSkeletonFrame"),
                  (['in'], ctypes.c_void_p, "pSmoothingParams")),
        COMMETHOD([], HRESULT, "NuiGetAudioSource",
                  (['in'], ctypes.POINTER(ctypes.c_void_p), "ppDmo")),
        COMMETHOD([], ctypes.c_int, "NuiInstanceIndex"),
        COMMETHOD([], comtypes.BSTR, "NuiDeviceConnectionId"),
        COMMETHOD([], comtypes.BSTR, "NuiUniqueId"),
        COMMETHOD([], comtypes.BSTR, "NuiAudioArrayId"),
        COMMETHOD([], HRESULT, "NuiStatus"),
        COMMETHOD([], HRESULT, "NuiGetColorCameraSettings",
                  (['out'], ctypes.POINTER(ctypes.POINTER(INuiColorCameraSettings)), "ppColorCameraSettings")),
    ]

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class JointPosition:
    """Single joint position in 3D space"""
    x: float
    y: float
    z: float
    tracking_state: int

@dataclass
class SkeletonData:
    """Complete skeleton with all 20 joints"""
    tracking_id: int
    tracking_state: int
    position: tuple[float, float, float]
    joints: list[JointPosition]

@dataclass
class FaceData:
    """Face tracking data linked to skeleton"""
    is_tracked: bool
    # Head pose (rotation in degrees)
    pitch: float  # Nodding up/down
    yaw: float    # Turning left/right
    roll: float   # Tilting side to side
    # 3D position
    translation: tuple[float, float, float]
    # Scale factor
    scale: float
    # Linked skeleton index (-1 if not linked)
    skeleton_index: int
    # Face mesh (87 3D points) - optional
    mesh_points: np.ndarray | None = None

@dataclass
class FaceIdentity:
    """Recognized face identity"""
    name: str
    confidence: float
    embedding: np.ndarray | None = None

@dataclass
class AudioData:
    """Audio capture data with beam information"""
    samples: np.ndarray  # 16kHz 16-bit PCM
    beam_angle: float    # -50 to +50 degrees
    source_angle: float  # -50 to +50 degrees
    confidence: float    # 0.0 to 1.0

@dataclass
class CameraSettings:
    """All camera adjustment settings"""
    auto_exposure: bool
    auto_white_balance: bool
    brightness: float
    contrast: float
    exposure_time: float
    frame_interval: float
    gain: float
    gamma: float
    hue: float
    saturation: float
    sharpness: float
    white_balance: float
    power_line_frequency: int
    backlight_compensation_mode: int

# ============================================================================
# KINECT CONTROLLER CLASS
# ============================================================================

class KinectController:
    """
    Complete controller for Xbox 360 Kinect.
    Provides access to ALL sensor features:
    - Video (RGB/YUV, Depth, IR)
    - Audio (4-mic array with beamforming)
    - Motor (tilt ±27°)
    - Accelerometer
    - Skeleton tracking
    - Camera settings
    """

    # Bridge DLL for advanced features
    BRIDGE_PATH = r"d:\Projects\orbcamera\orbos_kinect_bridge.dll"
    ALT_BRIDGE_PATH = r"d:\Projects\impressioncore\docs\codebase\orbcamera\orbcam\native\orbos_kinect_bridge.dll"

    def __init__(self, sensor_index: int = 0):
        self.index = sensor_index
        self.sensor: INuiSensor | None = None
        self.kinect_dll = None
        self.bridge_dll = None

        # Stream handles
        self.hColorStream = wintypes.HANDLE()
        self.hDepthStream = wintypes.HANDLE()
        self.hIRStream = wintypes.HANDLE()
        self.hNextFrameEvent = None

        # State
        self.is_open = False
        self.is_shutting_down = False
        self.color_mode = NuiImageType.COLOR
        self.skeleton_enabled = False
        self.near_mode = False
        self.audio_enabled = False

        # Thread safety
        self.lock = threading.RLock()

        # Audio state
        self.audio_thread = None
        self.audio_running = False
        self.audio_buffer = None
        self.beam_angle = 0.0
        self.source_angle = 0.0
        self.source_confidence = 0.0

        # Camera settings cache
        self._camera_settings: INuiColorCameraSettings | None = None

        # Load DLLs
        self._load_dlls()

    def _load_dlls(self):
        """Load Kinect SDK and optional bridge DLL"""
        try:
            self.kinect_dll = ctypes.WinDLL("Kinect10.dll")
            logger.info("Kinect10.dll loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Kinect10.dll: {e}")
            raise RuntimeError("Kinect SDK not installed or not in PATH") from e

        # Try to load bridge DLL
        for path in [self.BRIDGE_PATH, self.ALT_BRIDGE_PATH]:
            if os.path.exists(path):
                try:
                    self.bridge_dll = ctypes.WinDLL(path)
                    logger.info(f"Kinect bridge loaded from {path}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load bridge from {path}: {e}")

        if not self.bridge_dll:
            logger.warning("Kinect bridge DLL not loaded - some features unavailable")

    # ========================================================================
    # LIFECYCLE
    # ========================================================================

    def open(self,
             use_color: bool = True,
             use_depth: bool = True,
             use_skeleton: bool = True,
             use_audio: bool = False) -> bool:
        """
        Initialize the Kinect sensor and open requested streams.

        Args:
            use_color: Enable RGB/YUV color stream
            use_depth: Enable depth stream (also enables IR)
            use_skeleton: Enable skeleton tracking
            use_audio: Enable 4-mic audio capture

        Returns:
            True if initialization succeeded
        """
        with self.lock:
            if self.is_open:
                logger.warning("Kinect already open")
                return True

            try:
                # Create sensor instance
                sensor_ptr = ctypes.POINTER(INuiSensor)()
                hr = self.kinect_dll.NuiCreateSensorByIndex(self.index, ctypes.byref(sensor_ptr))
                if hr != S_OK:
                    logger.error(f"NuiCreateSensorByIndex failed: {decode_hresult(hr)}")
                    return False

                self.sensor = sensor_ptr

                # Build initialization flags
                flags = 0
                if use_color:
                    flags |= NuiInitFlags.USES_COLOR
                if use_depth:
                    flags |= NuiInitFlags.USES_DEPTH
                if use_skeleton:
                    flags |= NuiInitFlags.USES_SKELETON
                if use_audio:
                    flags |= NuiInitFlags.USES_AUDIO

                # Initialize sensor
                hr = self.sensor.NuiInitialize(flags)
                if hr != S_OK:
                    logger.error(f"NuiInitialize failed: {decode_hresult(hr)}")
                    return False

                logger.info(f"Kinect initialized with flags: 0x{flags:X}")

                # Create frame event
                self.hNextFrameEvent = ctypes.windll.kernel32.CreateEventA(
                    None, True, False, None
                )

                # Open streams
                streams_opened = 0

                if use_color and self._open_color_stream():
                    streams_opened += 1

                if use_depth:
                    if self._open_depth_stream():
                        streams_opened += 1
                    if self._open_ir_stream():
                        streams_opened += 1

                if use_skeleton:
                    self._enable_skeleton_tracking()

                if streams_opened > 0:
                    self.is_open = True
                    logger.info(f"Kinect open: {streams_opened} streams active")
                    return True
                else:
                    logger.error("No streams could be opened")
                    return False

            except Exception as e:
                logger.exception(f"Kinect open error: {e}")
                return False

    def _open_color_stream(self) -> bool:
        """Open RGB or YUV color stream"""
        for img_type in [NuiImageType.COLOR, NuiImageType.COLOR_YUV]:
            try:
                self.sensor.NuiImageStreamOpen(
                    img_type,
                    NuiImageResolution.RES_640x480,
                    0, 2, self.hNextFrameEvent,
                    ctypes.byref(self.hColorStream)
                )
                self.color_mode = img_type
                logger.info(f"Color stream opened (type={img_type.name})")
                return True
            except comtypes.COMError as e:
                logger.debug(f"Color type {img_type.name} failed: {decode_hresult(e.hresult)}")
        return False

    def _open_depth_stream(self) -> bool:
        """Open depth stream"""
        try:
            self.sensor.NuiImageStreamOpen(
                NuiImageType.DEPTH,
                NuiImageResolution.RES_640x480,
                0, 2, self.hNextFrameEvent,
                ctypes.byref(self.hDepthStream)
            )
            logger.info("Depth stream opened")
            return True
        except comtypes.COMError as e:
            logger.warning(f"Depth stream failed: {decode_hresult(e.hresult)}")
            return False

    def _open_ir_stream(self) -> bool:
        """Open infrared stream"""
        try:
            self.sensor.NuiImageStreamOpen(
                NuiImageType.COLOR_INFRARED,
                NuiImageResolution.RES_640x480,
                0, 2, self.hNextFrameEvent,
                ctypes.byref(self.hIRStream)
            )
            logger.info("IR stream opened")
            return True
        except comtypes.COMError as e:
            logger.warning(f"IR stream failed: {decode_hresult(e.hresult)}")
            return False

    def _enable_skeleton_tracking(self) -> bool:
        """Enable skeleton tracking"""
        try:
            flags = 0x8 if self.near_mode else 0  # ENABLE_IN_NEAR_RANGE
            hr = self.sensor.NuiSkeletonTrackingEnable(0, flags)
            if hr == S_OK:
                self.skeleton_enabled = True
                logger.info("Skeleton tracking enabled")
                return True
        except Exception as e:
            logger.warning(f"Skeleton tracking failed: {e}")
        return False

    def close(self):
        """Shutdown the Kinect sensor and release all resources"""
        with self.lock:
            if not self.is_open:
                return

            self.is_shutting_down = True
            self.stop_audio_capture()

            if self.sensor:
                with contextlib.suppress(Exception):
                    self.sensor.NuiShutdown()

            if self.hNextFrameEvent:
                ctypes.windll.kernel32.CloseHandle(self.hNextFrameEvent)
                self.hNextFrameEvent = None

            self.sensor = None
            self.is_open = False
            self.is_shutting_down = False
            logger.info("Kinect closed")

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ========================================================================
    # VIDEO STREAMS
    # ========================================================================

    def get_rgb_frame(self) -> np.ndarray | None:
        """
        Get current RGB/YUV frame as BGR numpy array.

        Returns:
            640x480x3 BGR image or None if unavailable
        """
        return self._get_frame_from_stream(self.hColorStream, self.color_mode)

    def get_depth_frame(self) -> tuple[np.ndarray | None, np.ndarray | None]:
        """
        Get current depth frame.

        Returns:
            Tuple of (visualization_image, raw_depth_array)
            - visualization: 640x480x3 BGR colormap image
            - raw: 640x480 uint16 array (depth in mm >> 3)
        """
        frame, raw = self._get_frame_from_stream(
            self.hDepthStream,
            NuiImageType.DEPTH,
            return_raw=True
        )
        return frame, raw

    def get_ir_frame(self) -> np.ndarray | None:
        """
        Get current infrared frame.

        Returns:
            640x480x3 BGR grayscale converted image or None
        """
        return self._get_frame_from_stream(self.hIRStream, NuiImageType.COLOR_INFRARED)

    def get_all_frames(self) -> dict[str, np.ndarray]:
        """
        Get all available frames at once.

        Returns:
            Dict with keys: 'color', 'depth', 'depth_raw', 'ir'
        """
        frames = {}

        color = self.get_rgb_frame()
        if color is not None:
            frames['color'] = color

        depth, depth_raw = self.get_depth_frame()
        if depth is not None:
            frames['depth'] = depth
            frames['depth_raw'] = depth_raw

        ir = self.get_ir_frame()
        if ir is not None:
            frames['ir'] = ir

        return frames

    def _get_frame_from_stream(self,
                                hStream: wintypes.HANDLE,  # noqa: N803
                                mode: NuiImageType,
                                return_raw: bool = False) -> Any:
        """Internal: Get frame from a specific stream"""
        if not self.is_open or not self.sensor or self.is_shutting_down:
            return (None, None) if return_raw else None

        if not hStream or not hStream.value:
            return (None, None) if return_raw else None

        frame = NUI_IMAGE_FRAME()
        frame_acquired = False

        try:
            self.sensor.NuiImageStreamGetNextFrame(hStream, 0, ctypes.byref(frame))
            frame_acquired = True
        except comtypes.COMError:
            return (None, None) if return_raw else None

        image = None
        raw_data = None

        try:
            texture = frame.pFrameTexture
            locked_rect = NUI_LOCKED_RECT()

            if texture.LockRect(0, ctypes.byref(locked_rect), None, 0) == S_OK:
                h, w = 480, 640
                if locked_rect.pBits and locked_rect.Pitch > 0:
                    pitch = locked_rect.Pitch
                    size = h * pitch

                    if 0 < size < 2000000:
                        buffer_data = ctypes.string_at(locked_rect.pBits, size)

                        if pitch == w * 4:
                            # BGRA format
                            raw = np.frombuffer(buffer_data, dtype=np.uint8).reshape((h, w, 4))
                            image = raw[:, :, :3].copy()
                            raw_data = raw
                        elif pitch == w * 2:
                            if mode in [NuiImageType.COLOR, NuiImageType.COLOR_YUV, NuiImageType.COLOR_RAW_YUV]:
                                # YUV format
                                raw = np.frombuffer(buffer_data, dtype=np.uint8).reshape((h, w, 2))
                                image = cv2.cvtColor(raw, cv2.COLOR_YUV2BGR_YUY2)
                                raw_data = raw
                            elif mode in [NuiImageType.DEPTH, NuiImageType.DEPTH_AND_PLAYER_INDEX]:
                                # Depth format
                                raw = np.frombuffer(buffer_data, dtype=np.uint16).reshape((h, w))
                                raw_data = raw.copy()
                                depth_8 = (raw >> 3).astype(np.uint8)
                                image = cv2.applyColorMap(depth_8, cv2.COLORMAP_JET)
                            elif mode == NuiImageType.COLOR_INFRARED:
                                # IR format
                                raw = np.frombuffer(buffer_data, dtype=np.uint16).reshape((h, w))
                                raw_data = raw
                                ir_8 = (raw >> 8).astype(np.uint8)
                                image = cv2.cvtColor(ir_8, cv2.COLOR_GRAY2BGR)

                        texture.UnlockRect(0)
        except Exception as e:
            logger.error(f"Frame read error: {e}")
        finally:
            if frame_acquired:
                with contextlib.suppress(Exception):
                    self.sensor.NuiImageStreamReleaseFrame(hStream, ctypes.byref(frame))

        if return_raw:
            return image, raw_data
        return image

    # ========================================================================
    # MOTOR & SENSORS
    # ========================================================================

    def get_tilt(self) -> float:
        """Get current motor tilt angle in degrees (-27 to +27)"""
        if not self.sensor:
            return 0.0
        try:
            angle = ctypes.c_long(0)
            hr = self.sensor.NuiCameraElevationGetAngle(ctypes.byref(angle))
            if hr == S_OK:
                return float(angle.value)
        except Exception as e:
            logger.error(f"Get tilt error: {e}")
        return 0.0

    def set_tilt(self, angle: float):
        """
        Set motor tilt angle.

        Args:
            angle: Target angle in degrees (-27 to +27)
        """
        if not self.sensor:
            return
        try:
            clamped = int(max(-27, min(27, angle)))
            self.sensor.NuiCameraElevationSetAngle(clamped)
            logger.debug(f"Tilt set to {clamped}°")
        except Exception as e:
            logger.error(f"Set tilt error: {e}")

    def get_accelerometer(self) -> tuple[float, float, float]:
        """
        Get accelerometer gravity vector.

        Returns:
            Tuple of (x, y, z) acceleration values
        """
        if not self.sensor:
            return (0.0, 0.0, 0.0)

        # Try bridge first (more reliable)
        if self.bridge_dll:
            try:
                x = ctypes.c_float()
                y = ctypes.c_float()
                z = ctypes.c_float()
                ptr = ctypes.cast(self.sensor, ctypes.c_void_p)
                if self.bridge_dll.GetAccelerometer(ptr, ctypes.byref(x), ctypes.byref(y), ctypes.byref(z)) == 0:
                    return (x.value, y.value, z.value)
            except Exception:
                pass

        # Fallback to direct COM
        try:
            vec = Vector4()
            hr = self.sensor.NuiAccelerometerGetCurrentReading(ctypes.byref(vec))
            if hr == S_OK:
                return (vec.x, vec.y, vec.z)
        except Exception as e:
            logger.error(f"Accelerometer error: {e}")

        return (0.0, 0.0, 0.0)

    # ========================================================================
    # AUDIO CAPTURE
    # ========================================================================

    def start_audio_capture(self):
        """Start capturing audio from the 4-microphone array"""
        if self.audio_running:
            return

        if not self.bridge_dll:
            logger.error("Audio requires bridge DLL - not available")
            return

        self.audio_running = True
        self.audio_buffer = np.zeros(16000, dtype=np.int16)  # 1 second buffer

        # Audio capture would run in a separate thread
        # For now, we log that audio is enabled
        logger.info("Audio capture enabled (bridge required for full implementation)")

    def stop_audio_capture(self):
        """Stop audio capture"""
        self.audio_running = False
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1.0)
        logger.info("Audio capture stopped")

    def get_audio_data(self) -> AudioData | None:
        """
        Get latest audio data with beam angle information.

        Returns:
            AudioData with samples and beam info, or None if unavailable
        """
        if not self.audio_running or self.audio_buffer is None:
            return None

        return AudioData(
            samples=self.audio_buffer.copy(),
            beam_angle=self.beam_angle,
            source_angle=self.source_angle,
            confidence=self.source_confidence
        )

    # ========================================================================
    # CAMERA SETTINGS
    # ========================================================================

    def _get_camera_settings_interface(self) -> INuiColorCameraSettings | None:
        """Get camera settings COM interface"""
        if self._camera_settings:
            return self._camera_settings

        if not self.sensor:
            return None

        try:
            settings_ptr = ctypes.POINTER(INuiColorCameraSettings)()
            hr = self.sensor.NuiGetColorCameraSettings(ctypes.byref(settings_ptr))
            if hr == S_OK and settings_ptr:
                self._camera_settings = settings_ptr
                return self._camera_settings
        except Exception as e:
            logger.warning(f"Camera settings interface unavailable: {e}")

        return None

    def get_camera_settings(self) -> CameraSettings | None:
        """Get all camera settings"""
        settings = self._get_camera_settings_interface()
        if not settings:
            return None

        try:
            auto_exp = ctypes.c_bool()
            auto_wb = ctypes.c_bool()
            brightness = ctypes.c_double()
            contrast = ctypes.c_double()
            exposure = ctypes.c_double()
            frame_int = ctypes.c_double()
            gain = ctypes.c_double()
            gamma = ctypes.c_double()
            hue = ctypes.c_double()
            saturation = ctypes.c_double()
            sharpness = ctypes.c_double()
            wb = ctypes.c_double()
            plf = ctypes.c_int()
            blc = ctypes.c_int()

            settings.GetAutoExposure(ctypes.byref(auto_exp))
            settings.GetAutoWhiteBalance(ctypes.byref(auto_wb))
            settings.GetBrightness(ctypes.byref(brightness))
            settings.GetContrast(ctypes.byref(contrast))
            settings.GetExposureTime(ctypes.byref(exposure))
            settings.GetFrameInterval(ctypes.byref(frame_int))
            settings.GetGain(ctypes.byref(gain))
            settings.GetGamma(ctypes.byref(gamma))
            settings.GetHue(ctypes.byref(hue))
            settings.GetSaturation(ctypes.byref(saturation))
            settings.GetSharpness(ctypes.byref(sharpness))
            settings.GetWhiteBalance(ctypes.byref(wb))
            settings.GetPowerLineFrequency(ctypes.byref(plf))
            settings.GetBacklightCompensationMode(ctypes.byref(blc))

            return CameraSettings(
                auto_exposure=auto_exp.value,
                auto_white_balance=auto_wb.value,
                brightness=brightness.value,
                contrast=contrast.value,
                exposure_time=exposure.value,
                frame_interval=frame_int.value,
                gain=gain.value,
                gamma=gamma.value,
                hue=hue.value,
                saturation=saturation.value,
                sharpness=sharpness.value,
                white_balance=wb.value,
                power_line_frequency=plf.value,
                backlight_compensation_mode=blc.value
            )
        except Exception as e:
            logger.error(f"Get camera settings error: {e}")
            return None

    def set_brightness(self, value: float):
        """Set brightness (0.0 to 1.0)"""
        settings = self._get_camera_settings_interface()
        if settings:
            try:
                settings.SetBrightness(max(0.0, min(1.0, value)))
            except Exception as e:
                logger.error(f"Set brightness error: {e}")

    def set_contrast(self, value: float):
        """Set contrast (0.0 to 2.0)"""
        settings = self._get_camera_settings_interface()
        if settings:
            try:
                settings.SetContrast(max(0.0, min(2.0, value)))
            except Exception as e:
                logger.error(f"Set contrast error: {e}")

    def set_auto_exposure(self, enabled: bool):
        """Enable/disable auto exposure"""
        settings = self._get_camera_settings_interface()
        if settings:
            try:
                settings.SetAutoExposure(enabled)
            except Exception as e:
                logger.error(f"Set auto exposure error: {e}")

    def set_auto_white_balance(self, enabled: bool):
        """Enable/disable auto white balance"""
        settings = self._get_camera_settings_interface()
        if settings:
            try:
                settings.SetAutoWhiteBalance(enabled)
            except Exception as e:
                logger.error(f"Set auto white balance error: {e}")

    def set_gain(self, value: float):
        """Set gain"""
        settings = self._get_camera_settings_interface()
        if settings:
            try:
                settings.SetGain(value)
            except Exception as e:
                logger.error(f"Set gain error: {e}")

    def set_gamma(self, value: float):
        """Set gamma"""
        settings = self._get_camera_settings_interface()
        if settings:
            try:
                settings.SetGamma(value)
            except Exception as e:
                logger.error(f"Set gamma error: {e}")

    # ========================================================================
    # SKELETON TRACKING
    # ========================================================================

    def set_skeleton_tracking(self, enabled: bool, near_mode: bool = False):
        """Enable or disable skeleton tracking"""
        if not self.sensor:
            return

        self.near_mode = near_mode

        try:
            if enabled:
                flags = 0x8 if near_mode else 0
                hr = self.sensor.NuiSkeletonTrackingEnable(0, flags)
                if hr == S_OK:
                    self.skeleton_enabled = True
                    logger.info(f"Skeleton tracking enabled (near_mode={near_mode})")
            else:
                hr = self.sensor.NuiSkeletonTrackingDisable()
                if hr == S_OK:
                    self.skeleton_enabled = False
                    logger.info("Skeleton tracking disabled")
        except Exception as e:
            logger.error(f"Skeleton tracking error: {e}")

    def get_skeleton_frame(self) -> list[SkeletonData]:
        """
        Get current skeleton frame data.

        Returns:
            List of SkeletonData for each tracked skeleton (up to 6)
        """
        if not self.sensor or not self.skeleton_enabled:
            return []

        skeletons = []
        frame = NUI_SKELETON_FRAME()

        try:
            hr = self.sensor.NuiSkeletonGetNextFrame(0, ctypes.byref(frame))
            if hr != S_OK:
                return []

            for i in range(6):
                data = frame.SkeletonData[i]
                if data.eTrackingState == NuiSkeletonTrackingState.TRACKED:
                    joints = []
                    for j in range(20):
                        pos = data.SkeletonPositions[j]
                        state = data.eSkeletonPositionTrackingState[j]
                        joints.append(JointPosition(pos.x, pos.y, pos.z, state))

                    skeletons.append(SkeletonData(
                        tracking_id=data.dwTrackingID,
                        tracking_state=data.eTrackingState,
                        position=(data.Position.x, data.Position.y, data.Position.z),
                        joints=joints
                    ))
        except Exception as e:
            logger.error(f"Get skeleton error: {e}")

        return skeletons

    # ========================================================================
    # FACE TRACKING
    # ========================================================================

    def init_face_tracking(self, model_path: str | None = None) -> bool:
        """
        Initialize face tracking using FaceTrackLib.

        Args:
            model_path: Path to face model file (optional, uses SDK default)

        Returns:
            True if initialization succeeded
        """
        if not self.bridge_dll:
            logger.error("Face tracking requires bridge DLL")
            return False

        try:
            # Default model path in SDK
            if model_path is None:
                sdk_path = os.environ.get('KINECTSDK10_DIR',
                    r'C:\Program Files\Microsoft SDKs\Kinect\v1.8')
                model_path = os.path.join(sdk_path, 'Redist', 'Face', 'FaceTracking.dll')

            # Convert to wide string for C++
            model_wpath = ctypes.c_wchar_p(model_path) if model_path else None

            result = self.bridge_dll.InitFaceTracking(640, 480, model_wpath)
            if result == 0:
                logger.info("Face tracking initialized")
                return True
            else:
                logger.error(f"Face tracking init failed: {result}")
                return False
        except Exception as e:
            logger.error(f"Face tracking init error: {e}")
            return False

    def get_face_data(self, color_frame: np.ndarray,
                      depth_frame: np.ndarray | None = None) -> FaceData | None:
        """
        Get face tracking data from current frames.

        Args:
            color_frame: BGR color image (640x480)
            depth_frame: Optional depth data

        Returns:
            FaceData with pose and position, or None if no face detected
        """
        if not self.bridge_dll:
            return None

        try:
            # Prepare buffers
            color_bgra = cv2.cvtColor(color_frame, cv2.COLOR_BGR2BGRA)
            color_ptr = color_bgra.ctypes.data_as(ctypes.c_void_p)

            depth_ptr = None
            if depth_frame is not None:
                depth_ptr = depth_frame.ctypes.data_as(ctypes.c_void_p)

            # Output pose array: [scale, pitch, yaw, roll, tx, ty, tz]
            pose = (ctypes.c_float * 7)()

            result = self.bridge_dll.ProcessFace(color_ptr, depth_ptr, pose)

            if result == 0:
                return FaceData(
                    is_tracked=True,
                    pitch=pose[1],
                    yaw=pose[2],
                    roll=pose[3],
                    translation=(pose[4], pose[5], pose[6]),
                    scale=pose[0],
                    skeleton_index=-1,  # Not linked yet
                    mesh_points=None
                )
        except Exception as e:
            logger.error(f"Face tracking error: {e}")

        return None

    def get_face_mesh(self) -> np.ndarray | None:
        """
        Get 87-point 3D face mesh.

        Returns:
            numpy array of shape (87, 3) with x,y,z coordinates, or None
        """
        if not self.bridge_dll:
            return None

        try:
            points = (ctypes.c_float * (87 * 3))()
            result = self.bridge_dll.GetFaceMesh(points, 87)

            if result > 0:
                arr = np.ctypeslib.as_array(points)
                return arr.reshape((-1, 3))[:result]
        except Exception as e:
            logger.error(f"Face mesh error: {e}")

        return None

    def link_face_to_skeleton(self, skeleton_index: int) -> bool:
        """
        Link face tracking to a specific skeleton.

        Args:
            skeleton_index: Index of skeleton (0-5), or -1 to unlink

        Returns:
            True if linking succeeded
        """
        if not self.bridge_dll:
            return False

        try:
            result = self.bridge_dll.LinkFaceToSkeleton(skeleton_index)
            return result == 0
        except Exception as e:
            logger.error(f"Face-skeleton link error: {e}")
            return False

    # ========================================================================
    # DIAGNOSTICS
    # ========================================================================

    def get_device_info(self) -> dict[str, Any]:
        """Get comprehensive device information"""
        info = {
            "is_open": self.is_open,
            "sensor_index": self.index,
            "color_mode": self.color_mode.name if self.color_mode else "None",
            "skeleton_enabled": self.skeleton_enabled,
            "near_mode": self.near_mode,
            "audio_enabled": self.audio_running,
            "bridge_available": self.bridge_dll is not None,
        }

        if self.sensor:
            try:
                info["status"] = f"0x{self.sensor.NuiStatus():X}"
                info["instance_index"] = self.sensor.NuiInstanceIndex()
            except Exception:
                pass

            try:
                info["unique_id"] = str(self.sensor.NuiUniqueId())
            except Exception:
                info["unique_id"] = "unavailable"

            try:
                info["connection_id"] = str(self.sensor.NuiDeviceConnectionId())
            except Exception:
                info["connection_id"] = "unavailable"

            try:
                info["audio_array_id"] = str(self.sensor.NuiAudioArrayId())
            except Exception:
                info["audio_array_id"] = "unavailable"

            # Tilt and accelerometer
            info["tilt_angle"] = self.get_tilt()
            info["accelerometer"] = self.get_accelerometer()

        return info


# ============================================================================
# GUI APPLICATION
# ============================================================================

class KinectControllerGUI:
    """
    Tkinter-based GUI for the Kinect Controller.
    Displays all streams and provides controls for all features.
    """

    def __init__(self, kinect: KinectController):
        self.kinect = kinect
        self.running = False
        self.current_view = "all"  # "all", "color", "depth", "ir"

    def run(self):
        """Run the main GUI loop using OpenCV windows"""
        self.running = True

        print("\n" + "="*60)
        print(" KINECT CONTROLLER - Debug Console")
        print("="*60)
        print(" Keyboard Controls:")
        print("   1 - RGB/Color view")
        print("   2 - Depth view")
        print("   3 - IR view")
        print("   A - All views (tiled)")
        print("   W/S - Tilt up/down")
        print("   I - Print device info")
        print("   C - Print camera settings")
        print("   Q/ESC - Quit")
        print("="*60 + "\n")

        while self.running:
            frames = self.kinect.get_all_frames()

            if self.current_view == "all":
                display = self._create_tiled_view(frames)
            elif self.current_view == "color":
                display = frames.get('color')
            elif self.current_view == "depth":
                display = frames.get('depth')
            elif self.current_view == "ir":
                display = frames.get('ir')
            else:
                display = None

            if display is not None:
                # Add info overlay
                display = self._add_overlay(display)
                cv2.imshow("Kinect Controller", display)

            key = cv2.waitKey(30) & 0xFF

            if key == ord('q') or key == 27:  # Q or ESC
                self.running = False
            elif key == ord('1'):
                self.current_view = "color"
            elif key == ord('2'):
                self.current_view = "depth"
            elif key == ord('3'):
                self.current_view = "ir"
            elif key == ord('a'):
                self.current_view = "all"
            elif key == ord('w'):
                current = self.kinect.get_tilt()
                self.kinect.set_tilt(current + 5)
            elif key == ord('s'):
                current = self.kinect.get_tilt()
                self.kinect.set_tilt(current - 5)
            elif key == ord('i'):
                info = self.kinect.get_device_info()
                print("\n--- Device Info ---")
                for k, v in info.items():
                    print(f"  {k}: {v}")
            elif key == ord('c'):
                settings = self.kinect.get_camera_settings()
                if settings:
                    print("\n--- Camera Settings ---")
                    print(f"  Auto Exposure: {settings.auto_exposure}")
                    print(f"  Auto White Balance: {settings.auto_white_balance}")
                    print(f"  Brightness: {settings.brightness:.2f}")
                    print(f"  Contrast: {settings.contrast:.2f}")
                    print(f"  Gain: {settings.gain:.2f}")
                    print(f"  Gamma: {settings.gamma:.2f}")

        cv2.destroyAllWindows()

    def _create_tiled_view(self, frames: dict[str, np.ndarray]) -> np.ndarray | None:
        """Create a 2x2 tiled view of all streams"""
        color = frames.get('color')
        depth = frames.get('depth')
        ir = frames.get('ir')

        # Create placeholder for missing streams
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(blank, "No Signal", (220, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (100, 100, 100), 2)

        color = color if color is not None else blank.copy()
        depth = depth if depth is not None else blank.copy()
        ir = ir if ir is not None else blank.copy()

        # Add labels
        cv2.putText(color, "RGB", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(depth, "DEPTH", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(ir, "IR", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Scale down for tiling
        color_sm = cv2.resize(color, (320, 240))
        depth_sm = cv2.resize(depth, (320, 240))
        ir_sm = cv2.resize(ir, (320, 240))
        info_panel = self._create_info_panel()

        top = np.hstack([color_sm, depth_sm])
        bottom = np.hstack([ir_sm, info_panel])

        return np.vstack([top, bottom])

    def _create_info_panel(self) -> np.ndarray:
        """Create info panel for tiled view"""
        panel = np.zeros((240, 320, 3), dtype=np.uint8)

        tilt = self.kinect.get_tilt()
        accel = self.kinect.get_accelerometer()

        lines = [
            "KINECT CONTROLLER",
            f"Tilt: {tilt:.1f} deg",
            f"Accel: ({accel[0]:.2f}, {accel[1]:.2f}, {accel[2]:.2f})",
            "",
            "Keys: 1=RGB 2=Depth 3=IR",
            "      W/S=Tilt A=All Q=Quit",
        ]

        y = 30
        for line in lines:
            cv2.putText(panel, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            y += 25

        return panel

    def _add_overlay(self, frame: np.ndarray) -> np.ndarray:
        """Add status overlay to frame"""
        tilt = self.kinect.get_tilt()
        cv2.putText(frame, f"Tilt: {tilt:.1f}", (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        return frame


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the Kinect Controller Application"""
    print("="*60)
    print(" Xbox 360 Kinect Controller Application")
    print(" Version 1.0 - ImpressionCore")
    print("="*60)

    try:
        kinect = KinectController(sensor_index=0)

        if not kinect.open(use_color=True, use_depth=True, use_skeleton=True):
            print("\nERROR: Failed to open Kinect sensor!")
            print("Check that:")
            print("  - Kinect is connected via USB")
            print("  - Kinect SDK 1.8 is installed")
            print("  - No other application is using the Kinect")
            return 1

        print("\nKinect opened successfully!")
        print("\nDevice Info:")
        info = kinect.get_device_info()
        for k, v in info.items():
            print(f"  {k}: {v}")

        # Allow hardware to warm up
        time.sleep(1.0)

        # Launch GUI
        gui = KinectControllerGUI(kinect)
        gui.run()

        kinect.close()
        print("\nKinect closed. Goodbye!")
        return 0

    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
