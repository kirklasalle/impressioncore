import logging
import time
import threading
from typing import Optional, Tuple, Union, Any, List
from abc import ABC, abstractmethod
import cv2
import numpy as np

from .logitech.devices import find_orbit_camera_index
from .detector import Detector
from .logitech.digital_motor import get_digital_motor

logger = logging.getLogger(__name__)

class CameraError(Exception):
    """Base class for camera exceptions."""
    pass

class CameraConnectionError(CameraError):
    """Raised when camera connection fails."""
    pass

class BaseCamera(ABC):
    """Abstract base class for all OrbOS cameras."""
    
    @abstractmethod
    def open(self) -> None: pass
    
    @abstractmethod
    def close(self) -> None: pass
    
    @abstractmethod
    def read(self) -> Optional[np.ndarray]: pass
    
    @abstractmethod
    def toggle_full_view(self, enabled: Optional[bool] = None): pass
    
    @property
    @abstractmethod
    def is_open(self) -> bool: pass
    
    @property
    @abstractmethod
    def pan(self) -> float: pass
    
    @pan.setter
    @abstractmethod
    def pan(self, value: float): pass
    
    @property
    @abstractmethod
    def tilt(self) -> float: pass
    
    @tilt.setter
    @abstractmethod
    def tilt(self, value: float): pass
    
    @property
    @abstractmethod
    def brightness(self) -> float: pass
    
    @brightness.setter
    @abstractmethod
    def brightness(self, value: float): pass
    
    @property
    @abstractmethod
    def contrast(self) -> float: pass
    
    @contrast.setter
    @abstractmethod
    def contrast(self, value: float): pass


class OrbCamera(BaseCamera):
    """
    Standard Logitech Orbit/Sphere implementation using OpenCV + Digital PTZ.
    """
    def __init__(self, device_index: Optional[int] = None):
        self._device_index = device_index
        self._cap: Optional[cv2.VideoCapture] = None
        self._is_open = False
        self._motor = get_digital_motor()
        self._full_view_mode = False
        self._view_w = 640
        self._view_h = 480
        
    def open(self) -> None:
        if self.is_open: return

        if self._device_index is None:
            detected_index = find_orbit_camera_index()
            time.sleep(0.5)
            self._device_index = detected_index if detected_index is not None else 0

        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        for backend in backends:
            try:
                temp_cap = cv2.VideoCapture(self._device_index, backend)
                if temp_cap.isOpened():
                    temp_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                    temp_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)
                    ret, _ = temp_cap.read()
                    if ret:
                        self._cap = temp_cap
                        self._is_open = True
                        break
                    temp_cap.release()
            except Exception: pass
            
        if not self._is_open:
            raise CameraConnectionError(f"Failed to open Orbit camera at index {self._device_index}")
        
    def close(self) -> None:
        if self._cap: self._cap.release()
        if self._motor: self._motor.shutdown()
        self._cap = None
        self._is_open = False
        
    def read(self) -> Optional[np.ndarray]:
        if not self.is_open: return None
        ret, frame = self._cap.read()
        if not ret: return None
        h, w = frame.shape[:2]
        if self._full_view_mode:
            return cv2.resize(frame, (self._view_w, self._view_h))
        x, y, cw, ch = self._motor.get_crop_rect(w, h, self._view_w, self._view_h)
        return cv2.resize(frame[y:y+ch, x:x+cw], (self._view_w, self._view_h))

    def toggle_full_view(self, enabled: Optional[bool] = None):
        if enabled is None: self._full_view_mode = not self._full_view_mode
        else: self._full_view_mode = enabled

    @property
    def is_open(self) -> bool:
        return self._is_open and self._cap is not None and self._cap.isOpened()

    @property
    def pan(self) -> float: return 0.0 # Legacy property
    @pan.setter
    def pan(self, value: float): pass

    @property
    def tilt(self) -> float: return 0.0

    @tilt.setter
    def tilt(self, value: float): pass

    @property
    def brightness(self) -> float:
        if not self.is_open: return 0.5
        return self._cap.get(cv2.CAP_PROP_BRIGHTNESS)
        
    @brightness.setter
    def brightness(self, value: float):
        if self.is_open:
            self._cap.set(cv2.CAP_PROP_BRIGHTNESS, max(0.0, min(1.0, value)))
            
    @property
    def contrast(self) -> float:
        if not self.is_open: return 0.5
        return self._cap.get(cv2.CAP_PROP_CONTRAST)
        
    @contrast.setter
    def contrast(self, value: float):
        if self.is_open:
            self._cap.set(cv2.CAP_PROP_CONTRAST, max(0.0, min(1.0, value)))


# --- Factory & Manager ---

_active_camera: Optional[BaseCamera] = None
_camera_lock = threading.Lock()

def get_active_camera(camera_type: Optional[str] = None) -> Optional[BaseCamera]:
    """Singleton-ish access to the active camera backend."""
    global _active_camera
    with _camera_lock:
        if camera_type is None:
            return _active_camera

        if _active_camera is not None:
            # Check if type matches
            current_type = "kinect" if "KinectCamera" in str(type(_active_camera)) else "orbit"
            if current_type == camera_type:
                return _active_camera
            else:
                logger.info(f"Switching camera from {current_type} to {camera_type}")
                _active_camera.close()
                _active_camera = None

        if camera_type == "kinect":
            from .logitech.kinect import KinectCamera
            _active_camera = KinectCamera()
        elif camera_type == "orbit":
            _active_camera = OrbCamera()
            
        return _active_camera
