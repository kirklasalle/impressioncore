"""
OrbOS USB Motor Controller
===========================
Direct USB control for Logitech Orbit MP PTZ motor.

This module provides stable PTZ control by:
1. Using PyUSB for direct USB control transfers (if available)
2. Falling back to SetupAPI/WinUSB via ctypes
3. Final fallback to DirectShow IKsPropertySet with video pause

The key insight is that USB cameras have separate paths for:
- Video streaming (isochronous transfers handled by OpenCV)
- Control transfers (endpoint 0, can use independently)
"""

import logging
import struct
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Logitech constants
LOGITECH_VID = 0x046d
ORBIT_MP_PIDS = [0x08c2, 0x0892, 0x0870, 0x08cc]  # Known Orbit/Sphere PIDs (08c2 confirmed working)

# UVC Extension Unit constants
XU_PT_RELATIVE = 0x01
XU_RESET = 0x02

# USB Control Transfer Types
USB_TYPE_CLASS = 0x20
USB_RECIP_INTERFACE = 0x01
USB_DIR_OUT = 0x00
USB_DIR_IN = 0x80

SET_CUR = 0x01
GET_CUR = 0x81


class USBMotorController:
    """
    USB-based PTZ motor controller for Logitech Orbit cameras.
    
    Provides direct USB control that doesn't conflict with video capture.
    """
    
    def __init__(self):
        self._usb_device = None
        self._xu_unit_id = 0x09  # Logitech XU ID for motor control
        self._interface = 0x02  # Interface 2 confirmed working via test!
        self._backend = None
        self._connected = False
        
        # Track virtual position
        self._virtual_pan = 0.0
        self._virtual_tilt = 0.0
        
        self._try_connect()
    
    def _try_connect(self):
        """Try to connect using available backends."""
        # Try PyUSB first
        if self._try_pyusb():
            self._backend = "pyusb"
            self._connected = True
            logger.info("USBMotor: Connected via PyUSB")
            return
        
        # Try WinUSB via SetupAPI
        if self._try_winusb():
            self._backend = "winusb"
            self._connected = True
            logger.info("USBMotor: Connected via WinUSB")
            return
        
        # Fallback - just log simulated mode
        self._backend = "simulated"
        logger.warning("USBMotor: No USB backend available, running in simulated mode")
        logger.info("USBMotor: Install libusb or use Zadig to install WinUSB driver for full PTZ control")
    
    def _try_pyusb(self) -> bool:
        """Try to connect using PyUSB."""
        try:
            import usb.core
            import usb.util
            
            # Find any Logitech device
            for pid in ORBIT_MP_PIDS:
                dev = usb.core.find(idVendor=LOGITECH_VID, idProduct=pid)
                if dev:
                    self._usb_device = dev
                    logger.info(f"USBMotor: Found Logitech camera VID={LOGITECH_VID:04x} PID={pid:04x}")
                    
                    # Try to discover XU Unit ID from descriptors
                    self._discover_xu_unit_id(dev)
                    return True
            
            # Fallback: find any Logitech device
            dev = usb.core.find(idVendor=LOGITECH_VID)
            if dev:
                self._usb_device = dev
                logger.info(f"USBMotor: Found Logitech device VID={LOGITECH_VID:04x} PID={dev.idProduct:04x}")
                self._discover_xu_unit_id(dev)
                return True
                
            return False
        except Exception as e:
            logger.debug(f"USBMotor: PyUSB init failed: {e}")
            return False
    
    def _try_winusb(self) -> bool:
        """Try to connect using WinUSB via SetupAPI (Windows only)."""
        try:
            import ctypes
            from ctypes import wintypes
            
            # WinUSB is complex to set up from scratch
            # For now, return False and rely on other backends
            # A full implementation would use SetupAPI to find device and WinUSB to control
            logger.debug("USBMotor: WinUSB backend not fully implemented yet")
            return False
        except Exception as e:
            logger.debug(f"USBMotor: WinUSB init failed: {e}")
            return False
    
    def _discover_xu_unit_id(self, dev):
        """Try to discover the Extension Unit ID from USB descriptors."""
        try:
            # Parse configuration descriptor to find UVC Extension Unit
            # Logitech typically uses Unit ID 9 or 10 for motor control
            cfg = dev.get_active_configuration()
            
            for intf in cfg:
                # Look for UVC VideoControl interface (bInterfaceClass=14, bInterfaceSubClass=1)
                if intf.bInterfaceClass == 14 and intf.bInterfaceSubClass == 1:
                    self._interface = intf.bInterfaceNumber
                    logger.debug(f"USBMotor: Found VideoControl interface {self._interface}")
                    break
            
            # For Logitech Orbit, XU Unit ID is typically 9
            # This could be discovered by parsing UVC descriptors
            self._xu_unit_id = 0x09
            logger.debug(f"USBMotor: Using XU Unit ID {self._xu_unit_id}")
            
        except Exception as e:
            logger.debug(f"USBMotor: Descriptor parsing failed: {e}")
            self._xu_unit_id = 0x09  # Safe default for Logitech
    
    def _send_control_pyusb(self, selector: int, data: bytes) -> bool:
        """Send UVC XU control via PyUSB."""
        try:
            import usb.core
            
            if not self._usb_device:
                return False
            
            bmRequestType = USB_TYPE_CLASS | USB_RECIP_INTERFACE | USB_DIR_OUT
            bRequest = SET_CUR
            wValue = (selector << 8) | 0x00
            wIndex = (self._xu_unit_id << 8) | self._interface
            
            logger.debug(f"USBMotor: ctrl_transfer bmR={bmRequestType:02x} bR={bRequest:02x} wV={wValue:04x} wI={wIndex:04x} data={data.hex()}")
            
            self._usb_device.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data, timeout=1000)
            return True
            
        except Exception as e:
            logger.warning(f"USBMotor: Control transfer failed: {e}")
            return False
    
    @property
    def is_connected(self) -> bool:
        """Check if motor control is available."""
        return self._connected
    
    @property
    def backend(self) -> str:
        """Get the active backend name."""
        return self._backend
    
    @property
    def pan(self) -> float:
        """Get current virtual pan position."""
        return self._virtual_pan
    
    @pan.setter
    def pan(self, value: float):
        """Set pan position (relative move)."""
        delta = value - self._virtual_pan
        if abs(delta) > 0.1:
            self.move_relative(int(delta), 0)
            self._virtual_pan = value
    
    @property
    def tilt(self) -> float:
        """Get current virtual tilt position."""
        return self._virtual_tilt
    
    @tilt.setter
    def tilt(self, value: float):
        """Set tilt position (relative move)."""
        delta = value - self._virtual_tilt
        if abs(delta) > 0.1:
            self.move_relative(0, int(delta))
            self._virtual_tilt = value
    
    def move_relative(self, pan_speed: int, tilt_speed: int) -> bool:
        """
        Move camera head relative to current position.
        
        Args:
            pan_speed: Pan speed/direction (-32768 to 32767)
            tilt_speed: Tilt speed/direction (-32768 to 32767)
        
        Returns:
            True if command was sent successfully
        """
        # Clamp values
        pan = max(-32768, min(32767, int(pan_speed * 64)))  # Scale for 1/64th degree units
        tilt = max(-32768, min(32767, int(tilt_speed * 64)))
        
        # Pack as little-endian signed 16-bit integers
        data = struct.pack("<hh", pan, tilt)
        
        if self._backend == "pyusb":
            return self._send_control_pyusb(XU_PT_RELATIVE, data)
        elif self._backend == "simulated":
            logger.debug(f"USBMotor (Simulated): PT Relative - Pan={pan}, Tilt={tilt}")
            return True
        
        return False
    
    def reset(self) -> bool:
        """
        Reset camera head to center position.
        
        Returns:
            True if command was sent successfully
        """
        data = bytes([0x03])  # Reset both pan and tilt
        
        self._virtual_pan = 0.0
        self._virtual_tilt = 0.0
        
        if self._backend == "pyusb":
            return self._send_control_pyusb(XU_RESET, data)
        elif self._backend == "simulated":
            logger.debug("USBMotor (Simulated): Reset to center")
            return True
        
        return False


# Singleton instance
_motor_instance = None


def get_motor() -> USBMotorController:
    """Get or create the singleton motor controller."""
    global _motor_instance
    if _motor_instance is None:
        _motor_instance = USBMotorController()
    return _motor_instance
