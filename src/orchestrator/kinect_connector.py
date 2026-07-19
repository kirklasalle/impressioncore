import contextlib
import ctypes
import logging
import os
import threading
import time
from typing import Any

try:
    from ctypes import wintypes
except ImportError:
    class MockWinTypes:
        DWORD = ctypes.c_ulong
        HANDLE = ctypes.c_void_p
        UINT = ctypes.c_uint
    wintypes = MockWinTypes()

if not hasattr(ctypes, "WinDLL"):
    ctypes.WinDLL = lambda *args, **kwargs: None
if not hasattr(ctypes, "windll"):
    class MockWinDll:
        kernel32 = type("MockKernel32", (), {"CreateEventA": lambda *args: None})()
    ctypes.windll = MockWinDll()

import cv2
import numpy as np

try:
    from comtypes import COMMETHOD, GUID, HRESULT, IUnknown
    COMTYPES_AVAILABLE = True
except ImportError:
    COMTYPES_AVAILABLE = False
    class IUnknown:
        pass
    COMMETHOD = lambda *args, **kwargs: (lambda func: func)
    GUID = lambda *args, **kwargs: None
    class HRESULT:
        pass

logger = logging.getLogger(__name__)

# --- Kinect Constants (SDK 1.8) ---
NUI_INITIALIZE_FLAG_USES_COLOR = 0x02
NUI_INITIALIZE_FLAG_USES_DEPTH = 0x20
NUI_INITIALIZE_FLAG_USES_SKELETON = 0x08
NUI_IMAGE_RESOLUTION_80x60 = 0
NUI_IMAGE_RESOLUTION_320x240 = 1
NUI_IMAGE_RESOLUTION_640x480 = 2
NUI_IMAGE_RESOLUTION_1280x960 = 3
NUI_IMAGE_TYPE_COLOR = 0
NUI_IMAGE_TYPE_COLOR_YUV = 1
NUI_IMAGE_TYPE_COLOR_YUV_RAW = 2
NUI_IMAGE_TYPE_DEPTH_AND_PLAYER_INDEX = 3
NUI_IMAGE_TYPE_DEPTH = 4
NUI_IMAGE_TYPE_COLOR_INFRARED = 5
S_OK = 0

# --- COM Interfaces ---
class INuiSensor(IUnknown):
    _iid_ = GUID("{d3d9ab7b-31ba-44ca-8cc0-d42525bbea43}")
    _methods_ = [
        COMMETHOD([], HRESULT, "NuiInitialize", (['in'], wintypes.DWORD, "dwFlags")),
        COMMETHOD([], None, "NuiShutdown"),
        COMMETHOD([], HRESULT, "NuiSetFrameEndEvent", (['in'], wintypes.HANDLE, "hEvent"), (['in'], wintypes.DWORD, "dwFrameEventFlag")),
        COMMETHOD([], HRESULT, "NuiImageStreamOpen", (['in'], ctypes.c_int, "eImageType"), (['in'], ctypes.c_int, "eResolution"), (['in'], wintypes.DWORD, "dwImageFrameFlags"), (['in'], wintypes.DWORD, "dwFrameLimit"), (['in'], wintypes.HANDLE, "hEvent"), (['in'], ctypes.POINTER(wintypes.HANDLE), "phStreamHandle")),
        COMMETHOD([], HRESULT, "NuiImageStreamSetImageFrameFlags", (['in'], wintypes.HANDLE, "hStream"), (['in'], wintypes.DWORD, "dwImageFrameFlags")),
        COMMETHOD([], HRESULT, "NuiImageStreamGetImageFrameFlags", (['in'], wintypes.HANDLE, "hStream"), (['in'], ctypes.POINTER(wintypes.DWORD), "pdwImageFrameFlags")),
        COMMETHOD([], HRESULT, "NuiImageStreamGetNextFrame", (['in'], wintypes.HANDLE, "hStream"), (['in'], wintypes.DWORD, "dwMillisecondsToWait"), (['in'], ctypes.c_void_p, "pImageFrame")),
        COMMETHOD([], HRESULT, "NuiImageStreamReleaseFrame", (['in'], wintypes.HANDLE, "hStream"), (['in'], ctypes.c_void_p, "pImageFrame")),
        COMMETHOD([], HRESULT, "NuiImageGetColorPixelCoordinatesFromDepthPixel", (['in'], ctypes.c_int, "eColorResolution"), (['in'], ctypes.c_void_p, "pcViewArea"), (['in'], ctypes.c_long, "lDepthX"), (['in'], ctypes.c_long, "lDepthY"), (['in'], ctypes.c_ushort, "usDepthValue"), (['in'], ctypes.POINTER(ctypes.c_long), "plColorX"), (['in'], ctypes.POINTER(ctypes.c_long), "plColorY")),
        COMMETHOD([], HRESULT, "NuiImageGetColorPixelCoordinatesFromDepthPixelAtResolution", (['in'], ctypes.c_int, "eColorResolution"), (['in'], ctypes.c_int, "eDepthResolution"), (['in'], ctypes.c_void_p, "pcViewArea"), (['in'], ctypes.c_long, "lDepthX"), (['in'], ctypes.c_long, "lDepthY"), (['in'], ctypes.c_ushort, "usDepthValue"), (['in'], ctypes.POINTER(ctypes.c_long), "plColorX"), (['in'], ctypes.POINTER(ctypes.c_long), "plColorY")),
        COMMETHOD([], HRESULT, "NuiImageGetColorPixelCoordinateFrameFromDepthPixelFrameAtResolution", (['in'], ctypes.c_int, "eColorResolution"), (['in'], ctypes.c_int, "eDepthResolution"), (['in'], wintypes.DWORD, "cDepthValues"), (['in'], ctypes.POINTER(ctypes.c_ushort), "pDepthValues"), (['in'], wintypes.DWORD, "cColorCoordinates"), (['in'], ctypes.POINTER(ctypes.c_long), "pColorCoordinates")),
        COMMETHOD([], HRESULT, "NuiCameraElevationSetAngle", (['in'], ctypes.c_long, "lAngleDegrees")),
        COMMETHOD([], HRESULT, "NuiCameraElevationGetAngle", (['in'], ctypes.POINTER(ctypes.c_long), "plAngleDegrees")),
        COMMETHOD([], HRESULT, "NuiAccelerometerGetCurrentReading", (['out'], ctypes.c_void_p, "pReading")),
        COMMETHOD([], HRESULT, "NuiSkeletonTrackingEnable", (['in'], wintypes.HANDLE, "hNextFrameEvent"), (['in'], wintypes.DWORD, "dwFlags")),
        COMMETHOD([], HRESULT, "NuiSkeletonTrackingDisable"),
    ]

# Paths to the orbcamera bridge - prioritize enhanced DLL with native face tracking
ORB_BRIDGE_PATHS = [
    r"d:\Projects\impressioncore\bin\kinect_bridge_enhanced.dll",  # Enhanced with native FaceTrackLib (K2VR-style)
    r"d:\Projects\impressioncore\docs\codebase\orbcamera\orbos_kinect_bridge.dll",  # Pre-compiled fallback
    r"d:\Projects\orbcamera\orbos_kinect_bridge.dll",  # Legacy path
]
ORB_BRIDGE_PATH = next((p for p in ORB_BRIDGE_PATHS if os.path.exists(p)), None)


class NUI_LOCKED_RECT(ctypes.Structure):
    # SDK: INT Pitch, INT size, byte* pBits
    _fields_ = [
        ("Pitch", ctypes.c_int),
        ("size", ctypes.c_int),
        ("pBits", ctypes.POINTER(ctypes.c_ubyte))
    ]

class NUI_SURFACE_DESC(ctypes.Structure):
    _fields_ = [("Width", ctypes.c_uint), ("Height", ctypes.c_uint)]

class INuiFrameTexture(IUnknown):
    _iid_ = GUID("{13ea17f5-ff2e-4670-9ee5-1297a6e880d1}")
    # SDK vtable order: BufferLen, Pitch, LockRect, GetLevelDesc, UnlockRect
    _methods_ = [
        COMMETHOD([], ctypes.c_int, "BufferLen"),
        COMMETHOD([], ctypes.c_int, "Pitch"),
        COMMETHOD([], HRESULT, "LockRect", (['in'], wintypes.UINT, "Level"), (['in'], ctypes.POINTER(NUI_LOCKED_RECT), "pLockedRect"), (['in'], ctypes.c_void_p, "pRect"), (['in'], wintypes.DWORD, "Flags")),
        COMMETHOD([], HRESULT, "GetLevelDesc", (['in'], wintypes.UINT, "Level"), (['out'], ctypes.POINTER(NUI_SURFACE_DESC), "pDesc")),
        COMMETHOD([], HRESULT, "UnlockRect", (['in'], wintypes.UINT, "Level"))
    ]

class NUI_IMAGE_FRAME(ctypes.Structure):
    _fields_ = [
        ("liTimeStamp", ctypes.c_int64),
        ("dwFrameNumber", wintypes.DWORD),
        ("eImageType", ctypes.c_int),
        ("eResolution", ctypes.c_int),
        ("pFrameTexture", ctypes.POINTER(INuiFrameTexture)),
        ("dwFrameFlags", wintypes.DWORD),
        ("ViewArea", ctypes.c_int * 4)
    ]

# --- Skeleton Structures ---
class Vector4(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float), ("z", ctypes.c_float), ("w", ctypes.c_float)]

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
        ("vFloorClipPlane", Vector4),
        ("vNormalToGravity", Vector4),
        ("SkeletonData", NUI_SKELETON_DATA * 6)
    ]

class NUI_TRANSFORM_SMOOTH_PARAMETERS(ctypes.Structure):
    _fields_ = [
        ("fSmoothing", ctypes.c_float),
        ("fCorrection", ctypes.c_float),
        ("fPrediction", ctypes.c_float),
        ("fJitterRadius", ctypes.c_float),
        ("fMaxDeviationRadius", ctypes.c_float)
    ]

class KinectConnector:
    """Standalone Kinect Connector for ImpressionCore (Enhanced for Amethyst-like Tracking)."""
    def __init__(self, index: int = 0):
        self.index = index
        self.sensor: INuiSensor | None = None
        self.hColorStream = wintypes.HANDLE()
        self.hDepthStream = wintypes.HANDLE()
        self.hIRStream = wintypes.HANDLE()
        self.hNextFrameEvent = None  # Single shared event for stability

        self.is_open = False
        self.is_switching = False
        self.lock = threading.RLock()
        self.bridge = None
        self.sub_mode = NUI_IMAGE_TYPE_DEPTH
        self.last_hr = 0
        self.color_mode = NUI_IMAGE_TYPE_COLOR
        self.skeleton_enabled = False

        # Native Face Tracking (K2VR-style)
        self.face_tracking_enabled = False
        self.face_tracking_initialized = False
        self.face_tracking_failed = False
        self.face_tracking_retry_count = 0
        self._face_pose_buffer = (ctypes.c_float * 7)()  # scale, pitch, yaw, roll, tx, ty, tz

        # Skeleton Smoothing Params (Amethyst/Kinect SDK Standard)
        self.smooth_params = NUI_TRANSFORM_SMOOTH_PARAMETERS(0.5, 0.5, 0.5, 0.05, 0.04)

        # Stream Toggles
        self.enabled_streams = {
            'color': True,
            'depth': True,
            'ir': True,
            'skeleton': True,
            'face': False
        }

        try:
            if ORB_BRIDGE_PATH and os.path.exists(ORB_BRIDGE_PATH):
                # Ensure bin is in DLL search path for dependencies (FaceTrackLib, etc.)
                bin_dir = os.path.abspath(os.path.dirname(ORB_BRIDGE_PATH))
                if bin_dir not in os.environ["PATH"]:
                    os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]

                if hasattr(os, 'add_dll_directory'):
                    with contextlib.suppress(Exception):
                        os.add_dll_directory(bin_dir)

                self.bridge = ctypes.WinDLL(ORB_BRIDGE_PATH)
                logger.info(f"Kinect Bridge loaded from {ORB_BRIDGE_PATH}")
                self._setup_face_tracking_bindings()
        except Exception as e:
            logger.warning(f"Kinect Bridge failed to load: {e}")

    def _setup_face_tracking_bindings(self):
        """Setup ctypes bindings for native face tracking functions."""
        if not self.bridge:
            return
        try:
            # InitFaceTracking(int width, int height, const wchar_t* modelPath) -> int
            self.bridge.InitFaceTracking.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_wchar_p]
            self.bridge.InitFaceTracking.restype = ctypes.c_int

            # ShutdownFaceTracking() -> void
            self.bridge.ShutdownFaceTracking.argtypes = []
            self.bridge.ShutdownFaceTracking.restype = None

            # ProcessFace(void* colorBuffer, void* depthBuffer, float* outPose) -> int
            self.bridge.ProcessFace.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_float)]
            self.bridge.ProcessFace.restype = ctypes.c_int

            # GetFacePose(float* pitch, float* yaw, float* roll) -> int
            self.bridge.GetFacePose.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
            self.bridge.GetFacePose.restype = ctypes.c_int

            # GetBeamAngle(double* beamAngle) -> int
            self.bridge.GetBeamAngle.argtypes = [ctypes.POINTER(ctypes.c_double)]
            self.bridge.GetBeamAngle.restype = ctypes.c_int

            # GetSoundSourceAngle(double* sourceAngle, double* confidence) -> int
            self.bridge.GetSoundSourceAngle.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
            self.bridge.GetSoundSourceAngle.restype = ctypes.c_int

            # GetFaceMesh(float* points, int maxPoints) -> int
            self.bridge.GetFaceMesh.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_int]
            self.bridge.GetFaceMesh.restype = ctypes.c_int

            # LinkFaceToSkeleton(int skeletonIndex) -> int
            self.bridge.LinkFaceToSkeleton.argtypes = [ctypes.c_int]
            self.bridge.LinkFaceToSkeleton.restype = ctypes.c_int

            self.face_tracking_enabled = True
            logger.info("Native Face Tracking, Mesh & Audio bindings configured (K2VR-style)")
        except Exception as e:
            logger.warning(f"Face tracking bindings failed: {e}")
            self.face_tracking_enabled = False

    def init_face_tracking(self, width: int = 640, height: int = 480) -> bool:
        """Initialize native Kinect SDK face tracking."""
        if not self.bridge or not self.face_tracking_enabled:
            return False
        if self.face_tracking_initialized:
            return True
        if self.face_tracking_failed:
            return False

        self.face_tracking_retry_count += 1
        if self.face_tracking_retry_count > 3:
            self.face_tracking_failed = True
            logger.error("Native Face Tracking disabled: Failed permanently after 3 attempts.")
            return False

        try:
            # [FIX] Shutdown any previous face tracking session before re-init
            # This prevents 0x00000001 errors when hardware refresh creates new KinectConnector
            try:
                self.bridge.ShutdownFaceTracking()
                logger.debug("Face Tracking: Shutdown previous session before re-init")
            except Exception:
                pass  # May not have been initialized, that's OK

            # Use bin directory as model path (contains FaceTrackData.dll)
            # Some versions of the SDK require a trailing backslash.
            model_path = os.path.dirname(ORB_BRIDGE_PATH) if ORB_BRIDGE_PATH else None
            if model_path:
                model_path = os.path.join(model_path, "") # Ensure trailing backslash

            logger.info(f"Initializing Native Face Tracking with model path: {model_path}")
            result = self.bridge.InitFaceTracking(width, height, model_path)

            # Fallback: if initialization failed with File Not Found, try as NULL
            # Note: HRESULT 0x80070002 could be signed in Python, so we mask it.
            res_mask = result & 0xFFFFFFFF
            logger.debug(f"Face Tracking Init Raw Result: {result}, Masked: 0x{res_mask:08X}")

            if res_mask == 0x80070002 and model_path is not None:
                logger.info("Retrying Face Tracking initialization with NULL path to let SDK find models...")
                result = self.bridge.InitFaceTracking(width, height, None)

            if result == 0:
                self.face_tracking_initialized = True
                self.face_tracking_retry_count = 0  # Reset retry counter on success
                logger.info(f"Native Face Tracking initialized ({width}x{height})")
                return True
            else:
                logger.warning(f"Face Tracking init failed: 0x{result & 0xFFFFFFFF:08X}")
                return False
        except Exception as e:
            logger.error(f"Face Tracking init exception: {e}")
            return False

    def process_face(self, color_frame, depth_frame=None) -> dict:
        """
        Process a frame through native Kinect face tracking.

        Args:
            color_frame: numpy array (640x480, BGRA or BGR)
            depth_frame: optional numpy array (320x240, uint16)

        Returns:
            dict with 'success', 'scale', 'pitch', 'yaw', 'roll', 'tx', 'ty', 'tz'
            or empty dict on failure
        """
        if self.face_tracking_failed:
            return {}

        if not self.face_tracking_initialized and not self.init_face_tracking():
            return {}

        try:
            import numpy as np

            # Ensure BGRA format for Kinect Face Tracking
            if len(color_frame.shape) == 3 and color_frame.shape[2] == 3:
                # Convert BGR to BGRA
                color_frame = np.dstack([color_frame, np.full(color_frame.shape[:2], 255, dtype=np.uint8)])

            # Ensure contiguous arrays for native bridge
            color_frame = np.ascontiguousarray(color_frame)
            if depth_frame is not None:
                depth_frame = np.ascontiguousarray(depth_frame)

            color_ptr = color_frame.ctypes.data_as(ctypes.c_void_p)
            depth_ptr = depth_frame.ctypes.data_as(ctypes.c_void_p) if depth_frame is not None else None

            result = self.bridge.ProcessFace(color_ptr, depth_ptr, self._face_pose_buffer)

            if result == 0:
                return {
                    'success': True,
                    'scale': self._face_pose_buffer[0],
                    'pitch': self._face_pose_buffer[1],
                    'yaw': self._face_pose_buffer[2],
                    'roll': self._face_pose_buffer[3],
                    'tx': self._face_pose_buffer[4],
                    'ty': self._face_pose_buffer[5],
                    'tz': self._face_pose_buffer[6]
                }
            return {'success': False, 'error_code': result}
        except Exception as e:
            logger.debug(f"ProcessFace exception: {e}")
            return {'success': False, 'exception': str(e)}

    def get_face_mesh(self) -> list:
        """
        Retrieve 87-point 3D face mesh from native tracker.

        Returns:
            List of [x, y, z] points or empty list on failure.
        """
        if not self.bridge or not self.face_tracking_initialized:
            return []

        try:
            # 87 points * 3 floats (x, y, z)
            mesh_buffer = (ctypes.c_float * (87 * 3))()
            count = self.bridge.GetFaceMesh(mesh_buffer, 87)

            if count > 0:
                points = []
                for i in range(count):
                    points.append([
                        mesh_buffer[i*3 + 0],
                        mesh_buffer[i*3 + 1],
                        mesh_buffer[i*3 + 2]
                    ])
                return points
            return []
        except Exception as e:
            logger.debug(f"GetFaceMesh failed: {e}")
            return []

    def shutdown_face_tracking(self):
        """Shutdown native face tracking."""
        if self.bridge and self.face_tracking_initialized:
            try:
                self.bridge.ShutdownFaceTracking()
                self.face_tracking_initialized = False
                logger.info("Native Face Tracking shutdown")
            except Exception:
                pass

    def set_stream_state(self, stream_name: str, state: bool):
        """Enable or disable specific streams (color, depth, ir, skeleton)."""
        if stream_name in self.enabled_streams:
            self.enabled_streams[stream_name] = state
            if stream_name == 'face':
                self.face_tracking_enabled = state
            logger.info(f"Kinect Stream '{stream_name}' set to {state}")
            return True
        return False

    def open(self):
        with self.lock:
            try:
                k10 = ctypes.WinDLL("Kinect10.dll")
                # Check sensor count first
                count = ctypes.c_int(0)
                try:
                    k10.NuiGetSensorCount(ctypes.byref(count))
                    logger.info(f"Kinect SDK reports {count.value} sensor(s) available.")
                except Exception as e:
                    logger.debug(f"NuiGetSensorCount failed: {e}")

                sensor_ptr = ctypes.POINTER(INuiSensor)()
                hr = k10.NuiCreateSensorByIndex(self.index, ctypes.byref(sensor_ptr))
                if hr != S_OK:
                    masked_hr = hr & 0xFFFFFFFF
                    logger.error(f"NuiCreateSensorByIndex fail: {hex(masked_hr)}")
                    if masked_hr == 0x82AC0009:
                        logger.error("  -> E_NUI_NOTCONNECTED: Sensor found in inventory but not physically connected/powered.")
                    return False

                self.sensor = sensor_ptr

                # Try Multiple Initialization Flags (Depth is usually the most stable)
                configs = [
                    (NUI_INITIALIZE_FLAG_USES_COLOR | NUI_INITIALIZE_FLAG_USES_DEPTH | NUI_INITIALIZE_FLAG_USES_SKELETON, "Full (C+D+S)"),
                    (NUI_INITIALIZE_FLAG_USES_COLOR | NUI_INITIALIZE_FLAG_USES_DEPTH, "Basic (C+D)"),
                    (NUI_INITIALIZE_FLAG_USES_DEPTH | NUI_INITIALIZE_FLAG_USES_SKELETON, "Depth+Skel (D+S)")
                ]

                init_success = False
                for flags, name in configs:
                    try:
                        hr = self.sensor.NuiInitialize(flags)
                        if hr == S_OK:
                            logger.info(f"Kinect NuiInitialize Success: {name}")
                            init_success = True
                            break
                        else:
                            masked_hr = hr & 0xFFFFFFFF
                            logger.warning(f"Kinect NuiInitialize {name} failed with HRESULT: {hex(masked_hr)}")
                            if masked_hr == 0x82AC0009:
                                logger.error("  -> E_NUI_NOTCONNECTED: External 12V power likely missing (check circular plug).")
                    except Exception as e:
                        logger.warning(f"Kinect NuiInitialize {name} exception: {e}")

                if not init_success:
                    return False

                if not self.hNextFrameEvent:
                    self.hNextFrameEvent = ctypes.windll.kernel32.CreateEventA(None, True, False, None)

                # 1. Image Streams
                # Try 640x480 first, then 320x240
                resolutions = [
                    (NUI_IMAGE_RESOLUTION_640x480, "640x480"),
                    (NUI_IMAGE_RESOLUTION_320x240, "320x240")
                ]

                formats = [
                    (NUI_IMAGE_TYPE_COLOR, "RGB"),
                    (NUI_IMAGE_TYPE_COLOR_YUV, "YUV")
                ]

                color_locked = False
                for res, res_name in resolutions:
                    for fmt, fmt_name in formats:
                        hr = k10.NuiImageStreamOpen(fmt, res, 0, 4, None, ctypes.byref(self.hColorStream))
                        if hr == S_OK:
                            self.color_mode = fmt
                            logger.info(f"Kinect Color Locked: {fmt_name} @ {res_name} (Buffer=4)")
                            color_locked = True
                            break
                    if color_locked:
                        break

                # 2. Depth
                # [FIX] Face Tracking bridge (v1.8) hardcodes 320x240 for depth.
                # We must match this if face tracking might be used.
                depth_res = NUI_IMAGE_RESOLUTION_320x240
                k10.NuiImageStreamOpen(NUI_IMAGE_TYPE_DEPTH, depth_res, 0, 4, None, ctypes.byref(self.hDepthStream))
                logger.info("Kinect Depth Stream Opened: 320x240")

                # 3. IR Stream (Attempt - Kinect v1 Color and IR share sensor, usually mutually exclusive)
                # Only try IR if color failed, since they share the same sensor
                if not color_locked:
                    try:
                        hr = k10.NuiImageStreamOpen(NUI_IMAGE_TYPE_COLOR_INFRARED, NUI_IMAGE_RESOLUTION_640x480, 0, 4, None, ctypes.byref(self.hIRStream))
                        if hr == S_OK:
                            logger.info("Kinect IR Stream opened successfully (as fallback)")
                    except Exception as e:
                        logger.debug(f"Kinect IR Stream not available (expected if Color is active): {e}")

                # 4. Skeleton
                try:
                    hr = k10.NuiSkeletonTrackingEnable(None, 0)
                    if hr == S_OK:
                        self.skeleton_enabled = True
                        logger.info("Kinect Skeleton Tracking Enabled")
                    else:
                        logger.warning(f"Kinect Skeleton Tracking Enable failed: 0x{hr & 0xFFFFFFFF:08X}")
                except Exception as e:
                    logger.warning(f"Kinect Skeleton Tracking Enable exception: {e}")

                self.is_open = True
                return True

            except Exception as e:
                logger.error(f"Kinect Open Fatal: {e}")
                return False

    def _get_skeleton(self):
        """Fetches the next skeleton frame with native smoothing."""
        if not self.skeleton_enabled:
            return None
        try:
            frame = NUI_SKELETON_FRAME()
            k10 = ctypes.WinDLL("Kinect10.dll")

            # 0 ms wait because we sync on the shared event in `read`
            hr = k10.NuiSkeletonGetNextFrame(0, ctypes.byref(frame))
            if hr == S_OK:
                # Apply Native Smoothing (The 'Amethyst' Magic)
                k10.NuiTransformSmooth(ctypes.byref(frame), ctypes.byref(self.smooth_params))
                return frame
            return None
        except Exception:
            return None

    def diag_kinect(self) -> dict[str, Any]:
        """Provides a detailed health report of the Kinect sensor."""
        report = {
            "status": "DISCONNECTED",
            "index": self.index,
            "detected": False,
            "streams": {},
            "face_tracking": "DISABLED",
            "last_error": hex(self.last_hr & 0xFFFFFFFF) if hasattr(self, 'last_hr') else "0x0"
        }

        try:
            k10 = ctypes.WinDLL("Kinect10.dll")
            count = ctypes.c_int(0)
            k10.NuiGetSensorCount(ctypes.byref(count))
            report["sensor_count"] = count.value

            if self.sensor:
                report["status"] = "CONNECTED" if self.is_open else "INITIALIZING"
                report["detected"] = True
                report["streams"] = {k: v for k, v in self.enabled_streams.items()}
                if self.face_tracking_initialized:
                    report["face_tracking"] = "ACTIVE"
                elif self.face_tracking_failed:
                    report["face_tracking"] = "FAILED"
                else:
                    report["face_tracking"] = "READY"
        except Exception as e:
            report["diagnostic_error"] = str(e)

        return report

    def set_smoothing_parameters(self, smoothing: float, correction: float, prediction: float, jitter: float, deviation: float):
        """Updates skeletal smoothing parameters dynamically."""
        with self.lock:
            self.smooth_params = NUI_TRANSFORM_SMOOTH_PARAMETERS(
                smoothing, correction, prediction, jitter, deviation
            )
            logger.info(f"Kinect Smoothing Updated: S={smoothing}, C={correction}, P={prediction}, J={jitter}, D={deviation}")

    def _decode_kinect_error(self, hr: int) -> str:
        """Decodes common Kinect HRESULT errors to human-readable messages."""
        error_codes = {
            0x83010001: "E_NUI_DEVICE_NOT_CONNECTED - Kinect not connected",
            0x83010002: "E_NUI_DEVICE_NOT_READY - Kinect not ready",
            0x83010004: "E_NUI_ALREADY_INITIALIZED - Already initialized",
            0x83010005: "E_NUI_NO_MORE_ITEMS - No more items",
            0x83010015: "E_NUI_DEVICE_IN_USE - Kinect is in use by another process",
            0x80070005: "E_ACCESSDENIED - Access denied (run as admin?)",
        }
        if hr < 0:
            hr = hr & 0xFFFFFFFF
        return error_codes.get(hr, f"Unknown error: {hex(hr)}")

    def _get_frame_from_stream(self, hStream, mode):  # noqa: N803
        """Get a single frame from a Kinect stream. Returns (image, raw_data) or (None, None)."""
        from comtypes import COMError
        if not hStream or not hStream.value:
            return None, None

        frame = NUI_IMAGE_FRAME()
        frame_acquired = False

        try:
            self.sensor.NuiImageStreamGetNextFrame(hStream, 0, ctypes.byref(frame))
            frame_acquired = True
        except COMError:
            return None, None

        image = None
        raw_data = None
        try:
            texture = frame.pFrameTexture
            locked_rect = NUI_LOCKED_RECT()
            if texture.LockRect(0, ctypes.byref(locked_rect), None, 0) == S_OK:
                # Dynamic Resolution based on frame
                if frame.eResolution == NUI_IMAGE_RESOLUTION_640x480:
                    h, w = 480, 640
                elif frame.eResolution == NUI_IMAGE_RESOLUTION_320x240:
                    h, w = 240, 320
                elif frame.eResolution == NUI_IMAGE_RESOLUTION_80x60:
                    h, w = 60, 80
                else:
                    h, w = 480, 640 # Fallback
                if locked_rect.pBits and locked_rect.Pitch > 0:
                    pitch = locked_rect.Pitch
                    size = h * pitch

                    if 0 < size < 4000000: # Increased sanity check
                        buffer_data = ctypes.string_at(locked_rect.pBits, size)

                        if pitch == w * 4:
                            raw = np.frombuffer(buffer_data, dtype=np.uint8).reshape((h, w, 4))
                            image = raw[:, :, :3].copy()
                            raw_data = raw
                        elif pitch == w * 2:
                            if mode in [NUI_IMAGE_TYPE_COLOR, NUI_IMAGE_TYPE_COLOR_YUV, NUI_IMAGE_TYPE_COLOR_YUV_RAW]:
                                try:
                                    raw = np.frombuffer(buffer_data, dtype=np.uint8).reshape((h, w, 2))
                                    image = cv2.cvtColor(raw, cv2.COLOR_YUV2BGR_YUY2)
                                    raw_data = raw
                                except Exception as cv_e:
                                    logger.debug(f"Kinect CV Decode Fail: {cv_e}")
                            elif mode in [NUI_IMAGE_TYPE_DEPTH, NUI_IMAGE_TYPE_DEPTH_AND_PLAYER_INDEX]:
                                raw = np.frombuffer(buffer_data, dtype=np.uint16).reshape((h, w))
                                raw_data = raw.copy()
                                depth_8 = (raw >> 3).astype(np.uint8)
                                image = cv2.applyColorMap(depth_8, cv2.COLORMAP_JET)
                            elif mode == NUI_IMAGE_TYPE_COLOR_INFRARED:
                                raw = np.frombuffer(buffer_data, dtype=np.uint16).reshape((h, w))
                                raw_data = raw
                                ir_8 = (raw >> 8).astype(np.uint8)
                                image = cv2.cvtColor(ir_8, cv2.COLOR_GRAY2BGR)
                        else:
                            # Unexpected pitch
                            if getattr(self, "_last_pitch_warn", 0) != pitch:
                                logger.debug(f"Kinect Unexpected Pitch: {pitch} for mode {mode}")
                                self._last_pitch_warn = pitch

                    # [DEBUG] Optional: Remove green screen filter for now to see raw signal
                    # if image is not None and mode in [NUI_IMAGE_TYPE_COLOR, NUI_IMAGE_TYPE_COLOR_YUV, NUI_IMAGE_TYPE_COLOR_YUV_RAW]:
                    #    avg_b, avg_g, avg_r = np.mean(image, axis=(0, 1))
                    #    if avg_g > 200 and avg_r < 30 and avg_b < 30:
                    #        image = None

                    texture.UnlockRect(0)
        except Exception as e:
            logger.error(f"Kinect Frame Internal Error: {e}")
        finally:
            if frame_acquired and self.sensor:
                with contextlib.suppress(COMError):
                    self.sensor.NuiImageStreamReleaseFrame(hStream, ctypes.byref(frame))
        return image, raw_data

    def get_audio_spatial_data(self) -> dict:
        """
        Retrieves audio beamforming and sound source localization data.
        Returns: {'beam_angle': float, 'source_angle': float, 'confidence': float}
        """
        if not self.bridge:
            return {}

        beam = ctypes.c_double(0)
        source = ctypes.c_double(0)
        conf = ctypes.c_double(0)

        result_beam = self.bridge.GetBeamAngle(ctypes.byref(beam))
        result_source = self.bridge.GetSoundSourceAngle(ctypes.byref(source), ctypes.byref(conf))

        if result_beam == 0 and result_source == 0:
            return {
                'beam_angle': beam.value,
                'source_angle': source.value,
                'confidence': conf.value
            }
        return {}

    def read(self):
        """Returns a dict of available frames using Direct Polling (Fastest)."""
        if not self.is_open or not self.sensor or self.is_switching:
            return False, None

        with self.lock:
            frames = {}

            # 1. Color (Note: Color and IR share same sensor - mutually exclusive)
            if self.enabled_streams.get('color', True):
                img, _ = self._get_frame_from_stream(self.hColorStream, self.color_mode)
                if img is not None:
                    frames["color"] = img

            # 2. Depth
            if self.enabled_streams.get('depth', True):
                img, raw = self._get_frame_from_stream(self.hDepthStream, NUI_IMAGE_TYPE_DEPTH)
                if img is not None:
                    frames["sub"] = img
                    frames["depth"] = img
                    frames["raw_depth"] = raw

            # 3. IR Stream - Read from IR stream handle if available
            # Note: On Kinect v1, IR mode often uses the color stream in IR mode
            if self.enabled_streams.get('ir', True):
                # Try to read from IR stream (if opened separately)
                if self.hIRStream and self.hIRStream.value:
                    ir_img, _ = self._get_frame_from_stream(self.hIRStream, NUI_IMAGE_TYPE_COLOR_INFRARED)
                    if ir_img is not None:
                        frames["ir"] = ir_img

                # Fallback: if no dedicated IR stream, simulate IR from depth for visualization
                if "ir" not in frames and "depth" in frames:
                    # Convert depth to pseudo-IR visualization (grayscale normalized)
                    depth_vis = frames["depth"].copy()
                    if len(depth_vis.shape) == 2:
                        # Normalize to 0-255 range for IR-like visualization
                        depth_norm = cv2.normalize(depth_vis, None, 0, 255, cv2.NORM_MINMAX)
                        frames["ir"] = depth_norm.astype(np.uint8)

            # 4. Skeleton
            if self.enabled_streams.get('skeleton', True):
                skel_frame = self._get_skeleton()
                if skel_frame:
                    frames["skeleton"] = skel_frame

            return (len(frames) > 0), frames

    def get_distance_at(self, x: int, y: int, raw_depth: np.ndarray) -> float:
        """Returns distance in millimeters at (x,y). Depth is 16-bit."""
        if raw_depth is None:
            return 0.0
        val = raw_depth[y, x]
        dist = val >> 3
        return float(dist)

    def get_average_distance(self, bbox: list, raw_depth: np.ndarray) -> float:
        """Returns average distance in mm within a bounding box [x, y, w, h]."""
        if raw_depth is None or not bbox:
            return 0.0
        x, y, w, h = [int(v) for v in bbox]
        roi = raw_depth[y:y+h, x:x+w]
        if roi.size == 0:
            return 0.0
        d_vals = roi >> 3
        valid = d_vals[d_vals > 0]
        if valid.size == 0:
            return 0.0
        return float(np.median(valid))

    def switch_sub_mode(self, mode: int):
        """Switches the secondary stream using a Protected Reset (Slow but stable)."""
        if mode not in [NUI_IMAGE_TYPE_DEPTH, NUI_IMAGE_TYPE_COLOR_INFRARED]:
            return False
        if not self.sensor:
            return False

        logger.info(f"Kinect Stability: Performing Protected Reset to {mode}")
        self.is_switching = True

        with self.lock:
            try:
                self.sub_mode = mode
                self.sensor.NuiShutdown()
                self.is_open = False
                time.sleep(0.3)
                success = self.open()
                return success
            except Exception as e:
                logger.error(f"Protected Reset Failed: {e}")
                return False
            finally:
                self.is_switching = False

    def set_tilt(self, angle: float):
        if not self.sensor:
            return
        try:
            target = int(max(-27, min(27, angle)))
            self.sensor.NuiCameraElevationSetAngle(target)
        except Exception:
            pass

    def release(self):
        if self.sensor:
            self.sensor.NuiShutdown()
        self.is_open = False
        self.sensor = None

    def close(self):
        """Compatibility alias for release()."""
        self.release()

    def isOpened(self):  # noqa: N802
        return self.is_open

    def serialize_skeleton(self, skeleton_frame) -> dict[str, Any]:
        """Converts raw NUI_SKELETON_FRAME to JSON-serializable dict."""
        if not skeleton_frame:
            return None

        # Joint Index Map (SDK 1.8)
        JOINT_MAP = {
            0: "HIP_CENTER", 1: "SPINE", 2: "SHOULDER_CENTER", 3: "HEAD",
            4: "SHOULDER_LEFT", 5: "ELBOW_LEFT", 6: "WRIST_LEFT", 7: "HAND_LEFT",
            8: "SHOULDER_RIGHT", 9: "ELBOW_RIGHT", 10: "WRIST_RIGHT", 11: "HAND_RIGHT",
            12: "HIP_LEFT", 13: "KNEE_LEFT", 14: "ANKLE_LEFT", 15: "FOOT_LEFT",
            16: "HIP_RIGHT", 17: "KNEE_RIGHT", 18: "ANKLE_RIGHT", 19: "FOOT_RIGHT"
        }

        found_skeleton = None

        # Find the first tracked skeleton
        for i in range(6):
            data = skeleton_frame.SkeletonData[i]
            if data.eTrackingState == 2: # NUI_SKELETON_TRACKED
                found_skeleton = data
                break

        if not found_skeleton:
            return None

        joints = {}
        for i in range(20):
            pos = found_skeleton.SkeletonPositions[i]
            # Normalize? SDK gives meters (approx -2.0 to 2.0 range usually).
            # We keep raw meters for 3D visualization.
            joints[JOINT_MAP[i]] = {
                "x": pos.x,
                "y": pos.y,
                "z": pos.z,
                "state": found_skeleton.eSkeletonPositionTrackingState[i] # 0=Not Tracked, 1=Inferred, 2=Tracked
            }

        return {
            "tracked": True,
            "id": found_skeleton.dwTrackingID,
            "joints": joints,
            "floor_clip_plane": {
                "x": skeleton_frame.vFloorClipPlane.x,
                "y": skeleton_frame.vFloorClipPlane.y,
                "z": skeleton_frame.vFloorClipPlane.z,
                "w": skeleton_frame.vFloorClipPlane.w
            },
            "gravity": {
                "x": skeleton_frame.vNormalToGravity.x,
                "y": skeleton_frame.vNormalToGravity.y,
                "z": skeleton_frame.vNormalToGravity.z,
                "w": skeleton_frame.vNormalToGravity.w
            },
            "timestamp": time.time()
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("--- Testing Kinect Connector ---")
    conn = KinectConnector()
    if conn.open():
        print("[SUCCESS] Kinect Sensor Initialized.")
        # Allow hardware to warm up
        time.sleep(1.0)
        ret, pkts = conn.read()
        if ret:
            print(f"[SUCCESS] Captured frames: {list(pkts.keys())}")
            for name, img in pkts.items():
                if isinstance(img, np.ndarray):
                    print(f"  - {name}: {img.shape}")
                elif name == "skeleton":
                    print(f"  - {name}: {img}")
        else:
            print("[FAILED] Could not read frames (Sensor might be warming up).")
        conn.release()
    else:
        print("[FAILED] Could not initialize Kinect.")
