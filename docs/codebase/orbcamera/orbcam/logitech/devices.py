"""
Logitech Device Discovery Utilities.

This module provides tools to identify Logitech cameras, specifically the Orbit/Sphere series,
using OpenCV probing (COM-free to avoid conflicts).
"""
import logging
import cv2
import time
from typing import Optional

logger = logging.getLogger(__name__)

def find_orbit_camera_index() -> Optional[int]:
    """
    Attempt to find the numerical index for the camera for use with OpenCV.
    
    This uses a simple brute-force probe strategies to find a working camera index.
    We avoid using WMI here to prevent COM threading model conflicts with OpenCV's DSHOW backend.
    """
    logger.info("Probing for camera devices...")
    
    # On Windows, we try DSHOW first, then MSMF (default)
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    
    for i in range(3): # Check first 3 indices
        logger.debug(f"Probing index {i}...")
        for backend in backends:
            try:
                cap = cv2.VideoCapture(i, backend)
                if cap.isOpened():
                    # Read a frame to be sure
                    ret, _ = cap.read()
                    if ret:
                        cap.release()
                        logger.info(f"Found working camera at index {i} (Backend: {backend})")
                        return i
                    cap.release()
            except Exception as e:
                logger.debug(f"Probe failed for index {i}: {e}")
            
    return None

__all__ = ['find_orbit_camera_index']
