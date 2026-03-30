"""
Digital Motor Controller
========================
Simulates a mechanical pan/tilt head by maintaining virtual coordinates
and calculating crop rectangles for high-resolution video frames.

Features:
- Physics-based smooth movement (easing)
- Full compatibility with hardware motor interface
- "Full View" toggle support
"""

import logging
import threading
import time
import math
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class DigitalMotorController:
    """
    Virtual motor controller for Digital PTZ.
    
    Coordinates are normalized from -1.0 (Left/Down) to 1.0 (Right/Up).
    0.0 is Center.
    """
    
    def __init__(self):
        # Target positions [-1.0, 1.0]
        self._target_pan = 0.0
        self._target_tilt = 0.0
        
        # Current positions (for smoothing/easing)
        self._current_pan = 0.0
        self._current_tilt = 0.0
        
        # Movement physics
        self._velocity_pan = 0.0
        self._velocity_tilt = 0.0
        self._friction = 0.85
        self._acceleration = 0.05
        self._deadzone = 0.001
        
        # State
        self._running = True
        self._thread = threading.Thread(target=self._physics_loop, daemon=True)
        self._thread.start()
        
        logger.info("DigitalMotor: Initialized virtual PTZ engine")

    def shutdown(self):
        self._running = False
        if self._thread.is_alive():
            self._thread.join(timeout=1.0)

        return True
    
    @property
    def pan(self) -> float:
        return self._current_pan * 100.0 # Scale to resemble -100..100 logic if needed? No, CLI expects raw? 
        # CLI print format is {cam.pan:4.1f}. 
        # If range is -1.0 to 1.0, it prints small numbers.
        # But motor generic interface usually implies degrees or arbitrary units?
        # Let's return raw -1.0 to 1.0 for now.
        return self._current_pan

    @pan.setter
    def pan(self, val: float):
        self._target_pan = max(-1.0, min(1.0, val))

    @property
    def tilt(self) -> float:
        return self._current_tilt

    @tilt.setter
    def tilt(self, val: float):
        self._target_tilt = max(-1.0, min(1.0, val))

    def move_relative(self, pan_delta: float, tilt_delta: float) -> bool:
        """
        Move the virtual head relative to current target.
        Input is usually raw speed values (e.g. -500 to 500).
        We scale this to reasonable normalized delta.
        """
        # Scale raw input (assume roughly -1000 to 1000 range from UI)
        # to a normalized nudge (e.g. 0.1)
        scale_factor = 0.0005 
        
        d_pan = pan_delta * scale_factor
        d_tilt = tilt_delta * scale_factor
        
        # Update target, clamped to [-1.0, 1.0]
        self._target_pan = max(-1.0, min(1.0, self._target_pan + d_pan))
        self._target_tilt = max(-1.0, min(1.0, self._target_tilt + d_tilt))
        
        return True

    def reset(self) -> bool:
        """Center the view."""
        self._target_pan = 0.0
        self._target_tilt = 0.0
        return True

    def set_target(self, pan: float, tilt: float):
        """Absolute positioning [-1.0, 1.0]."""
        self._target_pan = max(-1.0, min(1.0, pan))
        self._target_tilt = max(-1.0, min(1.0, tilt))

    def get_crop_rect(self, 
                     full_w: int, full_h: int, 
                     view_w: int, view_h: int) -> Tuple[int, int, int, int]:
        """
        Calculate the crop rectangle (x, y, w, h) based on current position.
        
        Args:
            full_w, full_h: Dimensions of the high-res sensor frame
            view_w, view_h: Dimensions of the output viewport
            
        Returns:
            (x, y, w, h) tuple defining the crop region
        """
        # Ensure viewport isn't larger than source
        vw = min(full_w, view_w)
        vh = min(full_h, view_h)
        
        # Available travel range (slack space)
        slack_w = full_w - vw
        slack_h = full_h - vh
        
        # Map [-1, 1] position to [0, slack]
        # Pan: -1 (Left) -> x=0, 1 (Right) -> x=slack_w
        # Tilt: -1 (Down) -> y=slack_h, 1 (Up) -> y=0 (Standard image coords usually y=0 is top)
        # NOTE: Tilt direction preference: usually +1 means "Look Up".
        # If "Look Up", we want the crop to move DOWN (showing upper part of image? No.)
        # If camera looks UP, it sees the ceiling.
        # In a crop, to see "higher" pixels (ceiling), the crop window must move UP (y -> 0).
        # So +1 Tilt -> y=0. -1 Tilt -> y=slack_h.
        
        # Normalize position to [0.0, 1.0]
        norm_pan = (self._current_pan + 1.0) / 2.0
        # Invert tilt logic for image coordinates: +1 (Up) means lower index (y=0)
        norm_tilt = (1.0 - self._current_tilt) / 2.0 
        
        x = int(norm_pan * slack_w)
        y = int(norm_tilt * slack_h)
        
        # Safety clamps
        x = max(0, min(slack_w, x))
        y = max(0, min(slack_h, y))
        
        return (x, y, vw, vh)

    def _physics_loop(self):
        """Update current position towards target with easing."""
        while self._running:
            # Simple proportional smoothing (Lerp)
            # Or use velocity for momentum - let's stick to simple lerp for responsiveness
            # current += (target - current) * alpha
            
            error_p = self._target_pan - self._current_pan
            error_t = self._target_tilt - self._current_tilt
            
            if abs(error_p) > self._deadzone:
                self._current_pan += error_p * 0.15
            else:
                self._current_pan = self._target_pan
                
            if abs(error_t) > self._deadzone:
                self._current_tilt += error_t * 0.15
            else:
                self._current_tilt = self._target_tilt
                
            time.sleep(0.016) # ~60Hz updates

# Singleton access
_digital_motor_instance = None
_lock = threading.Lock()

def get_digital_motor() -> DigitalMotorController:
    global _digital_motor_instance
    with _lock:
        if _digital_motor_instance is None:
            _digital_motor_instance = DigitalMotorController()
    return _digital_motor_instance
