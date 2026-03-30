"""
Logitech specific camera control and hardware detection.
"""
from .devices import find_orbit_camera_index

__all__ = [
    'LogitechDeviceFinder',
    'find_orbit_camera_index'
]
