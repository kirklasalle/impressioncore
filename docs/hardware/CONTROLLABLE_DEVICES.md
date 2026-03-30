# Controllable Devices & Camera Library

This document outlines the motorized hardware supported by ImpressionCore and their technical specifications for long-term support.

## Supported Motorized Cameras

| Device | VID/PID | Axes | Range | Driver |
| :--- | :--- | :--- | :--- | :--- |
| **Logitech QuickCam Orb/Sphere MP** | `046d_08c2` | Pan, Tilt | P: [-4480, 4480], T: [-1920, 1920] | `QuickCamOrbDriver` |
| **Logitech QuickCam Orbit** | `046d_0892` | Pan, Tilt | P: [-4480, 4480], T: [-1920, 1920] | `QuickCamOrbDriver` |
| **Logitech QuickCam Orbit/Sphere** | `046d_08cc` | Pan, Tilt | P: [-4480, 4480], T: [-1920, 1920] | `QuickCamOrbDriver` |
| **Logitech QuickCam Orbit/Sphere AF**| `046d_0994` | Pan, Tilt, Zoom | P: [-4480, 4480], T: [-1920, 1920] | `QuickCamOrbDriver` |
| **Xbox 360 Kinect** | `045e_02ae` | Tilt | [-27, 27] Degrees | `KinectConnector` |

## Technical Implementation

### Addressing Devices
Devices are addressed via a unified `vid_pid` identifier (formatted as `vendorid_productid`). The vision layer (`OrbCloudVision`) handles the mapping between these identifiers and the active hardware indices.

### PTZ Command Structure
Commands are sent via the `/v1/devices/{vid_pid}/ptz` endpoint.
- **Pan/Tilt**: Relative units or absolute depending on driver capability.
- **Reset**: Centers the motors and recalibrates position.

### Adding New Devices
To add support for a new motorized camera:
1. Update `src/orchestrator/device_profile.py` with the new VID/PID and its `PTZRanges`.
2. Implement or update the driver logic in `src/orchestrator/`.
3. Update the routing logic in `OrbCloudVision.hardware_ptz_control`.

---
*Last Updated: 2025-12-29*
