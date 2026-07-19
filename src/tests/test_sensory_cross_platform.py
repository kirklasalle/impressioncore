"""Unit tests for sensory and hardware drivers cross-platform fallbacks."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.orchestrator.diag_pnp import identify_devices
from src.orchestrator.kinect_connector import KinectConnector
from src.orchestrator.orbcloud_vision import OrbCloudVision
from src.orchestrator.quickcam_driver import QuickCamOrbDriver
from src.orchestrator.sensory_discovery import WindowsSensoryDiscovery


def test_diag_pnp_fallback():
    """Verify identify_devices degrades gracefully when WMI is unavailable."""
    with patch("src.orchestrator.diag_pnp._WMI_AVAILABLE", False):
        # Should print fallback warning and return without raising NameError or ImportError
        identify_devices()


def test_sensory_discovery_fallback():
    """Verify WindowsSensoryDiscovery degrades gracefully when WMI is unavailable."""
    with patch("src.orchestrator.sensory_discovery.WMI_AVAILABLE", False):
        discovery = WindowsSensoryDiscovery()
        assert discovery.wmi is None
        # correlate_with_pnp should return early instead of attempting WMI operations
        devices = discovery.correlate_with_pnp()
        assert isinstance(devices, list)


def test_quickcam_driver_pyusb_fallback():
    """Verify QuickCamOrbDriver falls back to PyUSB when comtypes/DShow fails."""
    driver = QuickCamOrbDriver()
    with patch("src.orchestrator.quickcam_driver._HAS_COMTYPES", False):
        with patch.object(driver, "_connect_pyusb", return_value=False) as mock_pyusb:
            res = driver.connect()
            assert res is False
            mock_pyusb.assert_called_once()


def test_kinect_connector_non_windows_importability():
    """Verify KinectConnector can be instantiated and behaves correctly when comtypes is unavailable."""
    connector = KinectConnector(index=0)
    assert connector.is_open is False
    assert connector.sensor is None


def test_orbcloud_vision_open_fallback():
    """Verify OrbCloudVision open degrades gracefully when WMI is unavailable."""
    with patch("src.orchestrator.orbcloud_vision.WMI_AVAILABLE", False):
        with patch("src.orchestrator.orbcloud_vision.COMTYPES_AVAILABLE", False):
            # In simulated mode, open should complete successfully
            vision = OrbCloudVision(simulated=True)
            assert vision.wmi is None
            res = vision.open()
            assert res is True
            vision._is_running = False
