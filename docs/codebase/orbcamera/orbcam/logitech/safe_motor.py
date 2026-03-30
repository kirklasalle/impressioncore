"""
OrbOS Safe Motor Controller
============================
Thread-safe wrapper for DirectShow-based motor control.

The key insight is that DirectShow IKsPropertySet operations can conflict
with active video capture. This wrapper coordinates with the camera's
frame grabbing to ensure motor commands are sent during "safe" windows.

Strategy:
1. Use a threading lock to prevent concurrent DirectShow access
2. Notify the camera to briefly pause frame grabbing
3. Send the motor command
4. Resume frame grabbing
"""

import logging
import threading
import time
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class SafeMotorController:
    """
    Thread-safe motor controller that coordinates with video capture.
    
    Usage:
        motor = SafeMotorController()
        motor.set_pause_callback(camera.pause_capture)
        motor.move_relative(5, 0)  # Safe pan right
    """
    
    def __init__(self):
        self._xu = None
        self._lock = threading.RLock()
        self._pause_callback: Optional[Callable] = None
        self._resume_callback: Optional[Callable] = None
        self._connected = False
        self._virtual_pan = 0.0
        self._virtual_tilt = 0.0
        
        # Lazy initialization - don't block startup
        self._init_thread = threading.Thread(target=self._lazy_init, daemon=True)
        self._init_thread.start()
    
    def _lazy_init(self):
        """Initialize XUController in background to avoid blocking startup."""
        try:
            from .xu_control import XUController
            
            with self._lock:
                self._xu = XUController()
                # Check if XUController got a working interface
                self._connected = (self._xu._ks_control is not None or 
                                   self._xu._ks_property_set is not None)
                
            if self._connected:
                logger.info("SafeMotor: XUController connected successfully")
            else:
                logger.warning("SafeMotor: XUController created but not connected")
                
        except Exception as e:
            logger.error(f"SafeMotor: Failed to initialize XUController: {e}")
            self._connected = False
    
    def set_pause_callback(self, pause_fn: Callable, resume_fn: Callable = None):
        """
        Set callbacks for pausing/resuming video capture.
        
        Args:
            pause_fn: Function to call before motor command (should pause video)
            resume_fn: Function to call after motor command (should resume video)
        """
        self._pause_callback = pause_fn
        self._resume_callback = resume_fn
    
    @property
    def is_connected(self) -> bool:
        """Check if motor control is available."""
        return self._connected and self._xu is not None
    
    @property
    def pan(self) -> float:
        """Get current virtual pan position."""
        return self._virtual_pan
    
    @pan.setter
    def pan(self, value: float):
        """Set pan position (relative move)."""
        delta = value - self._virtual_pan
        if abs(delta) > 0.5:
            direction = 1 if delta > 0 else -1
            self.move_relative(direction, 0)
            self._virtual_pan = value
    
    @property
    def tilt(self) -> float:
        """Get current virtual tilt position."""
        return self._virtual_tilt
    
    @tilt.setter  
    def tilt(self, value: float):
        """Set tilt position (relative move)."""
        delta = value - self._virtual_tilt
        if abs(delta) > 0.5:
            direction = 1 if delta > 0 else -1
            self.move_relative(0, direction)
            self._virtual_tilt = value
    
    def move_relative(self, pan: int, tilt: int) -> bool:
        """
        Move camera head relative to current position.
        
        This is the SAFE version that coordinates with video capture.
        
        Args:
            pan: Pan direction (-1 to 1 for left/right, or larger for speed)
            tilt: Tilt direction (-1 to 1 for down/up, or larger for speed)
        
        Returns:
            True if command was sent successfully
        """
        if not self.is_connected:
            logger.warning("SafeMotor: Not connected, command ignored")
            # Still update virtual position for UI feedback
            self._virtual_pan += pan
            self._virtual_tilt += tilt
            return False
        
        with self._lock:
            try:
                # Pause video capture if callback is set
                if self._pause_callback:
                    try:
                        self._pause_callback()
                        time.sleep(0.05)  # Brief pause for DirectShow to settle
                    except Exception as e:
                        logger.debug(f"SafeMotor: Pause callback failed: {e}")
                
                # Send the motor command
                result = self._xu.move_relative(pan, tilt)
                
                # Resume video capture
                if self._resume_callback:
                    try:
                        time.sleep(0.05)  # Brief pause after command
                        self._resume_callback()
                    except Exception as e:
                        logger.debug(f"SafeMotor: Resume callback failed: {e}")
                
                if result:
                    self._virtual_pan += pan
                    self._virtual_tilt += tilt
                    logger.debug(f"SafeMotor: Moved pan={pan}, tilt={tilt}")
                
                return result
                
            except Exception as e:
                logger.error(f"SafeMotor: move_relative failed: {e}")
                return False
    
    def reset(self) -> bool:
        """
        Reset camera head to center position.
        
        Returns:
            True if command was sent successfully
        """
        if not self.is_connected:
            logger.warning("SafeMotor: Not connected, reset ignored")
            self._virtual_pan = 0.0
            self._virtual_tilt = 0.0
            return False
        
        with self._lock:
            try:
                # Pause video
                if self._pause_callback:
                    try:
                        self._pause_callback()
                        time.sleep(0.05)
                    except:
                        pass
                
                # Send reset
                result = self._xu.reset()
                
                # Resume video
                if self._resume_callback:
                    try:
                        time.sleep(0.1)  # Longer pause for reset
                        self._resume_callback()
                    except:
                        pass
                
                self._virtual_pan = 0.0
                self._virtual_tilt = 0.0
                
                logger.debug("SafeMotor: Reset to center")
                return result
                
            except Exception as e:
                logger.error(f"SafeMotor: reset failed: {e}")
                return False


# Singleton instance
_motor_instance = None
_motor_lock = threading.Lock()


def get_safe_motor() -> SafeMotorController:
    """Get or create the singleton SafeMotorController."""
    global _motor_instance
    with _motor_lock:
        if _motor_instance is None:
            _motor_instance = SafeMotorController()
    return _motor_instance
