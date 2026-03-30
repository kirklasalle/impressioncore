# Kinect v1 (Xbox 360) Research & Implementation Plan

**Created:** December 23, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\codebase\orbcamera\orbcam\knowledge\kinect_research.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Overview

The Xbox 360 Kinect (v1) is a specialized sensor bar containing an RGB camera, a depth sensor (Infrared), a multi-microphone array, and a motorized tilt base.

The user has installed **Kinect SDK 1.8**.

## Technical Specifications (SDK 1.8)

| Component | Resolution | FPS | Notes |
|-----------|------------|-----|-------|
| RGB Camera | 640x480 / 1280x960 | 30 / 12 | 1280x960 is 12fps (Bayer) |
| Depth Sensor | 320x240 / 640x480 | 30 | `NUI_IMAGE_TYPE_DEPTH_AND_PLAYER_INDEX` |
| Motor Tilt | ±27° | - | `NuiCameraElevationSetAngle` |
| Accelerometer| 3-axis | - | `NuiAccelerometerGetCurrentReading` |
| Audio | 4-mic array | - | `NuiGetAudioSource` |

## API Investigation (Kinect10.dll)

### Core Functions

- `NuiGetSensorCount(int *pCount)`: Returns number of connected Kinects.
- `NuiCreateSensorByIndex(int index, INuiSensor **ppNuiSensor)`: Creates a sensor object.

### INuiSensor Interface (COM)

The `INuiSensor` interface provides several key methods:

- `NuiInitialize(DWORD dwFlags)`: Starts the sensor with specific features (Color, Depth, Skeleton, Audio).
- `NuiImageStreamOpen(type, res, flags, limit, event, handle)`: Opens a data stream.
- `NuiImageStreamGetNextFrame(handle, wait_ms, frame)`: Fetches the next available frame.
- `NuiCameraElevationSetAngle(LONG degrees)`: Sets the motor tilt (-27 to +27).
- `NuiCameraElevationGetAngle(LONG *pDegrees)`: Gets current tilt.
- `NuiAccelerometerGetCurrentReading(Vector4 *pReading)`: Gets gravity vector.

### Initialization Flags

- `NUI_INITIALIZE_FLAG_USES_COLOR (0x02)`
- `NUI_INITIALIZE_FLAG_USES_DEPTH (0x20)`
- `NUI_INITIALIZE_FLAG_USES_AUDIO (0x10000000)`
- `NUI_INITIALIZE_FLAG_USES_DEPTH_AND_PLAYER_INDEX (0x01)`

### Known Python Wrappers

1. **PyKinect** (Part of Python Tools for Visual Studio): Works with SDK 1.8. Wraps the managed API or uses ctypes.
2. **freenect**: libfreenect wrapper. Usually used as an alternative to the official MS SDK.
3. **OpenCV**: Can sometimes access Kinect via `CAP_OPENNI` (ASUS Xtion/Kinect v1) if drivers are correctly mapped.

## Implementation Details (Confirmed)

### 1. Audio & Camera Recognition

- **Kinect v1 Drivers**: Installed (Kinect for Windows SDK 1.8).
- **DirectShow**: Not available. Video MUST be accessed via the Kinect SDK `NuiImageStream` API.

### 2. Motor Control

- **Interface**: `INuiSensor::NuiCameraElevationSetAngle`.
- **Range**: -27 to +27 degrees.
- **Initialization**: Requires `NUI_INITIALIZE_FLAG_USES_COLOR` or `NUI_INITIALIZE_FLAG_USES_DEPTH`.

### 3. Video Access (Native)

- **Method**: `NuiImageStreamOpen` for Color/Depth.
- **Copying**: Lock the frame texture, copy bits to numpy array.

## Implementation Architecture

### `KinectCamera` (in `orbcam/logitech/kinect.py`)

- Inherits from a new `BaseCamera` interface.
- Manages `comtypes` `INuiSensor` lifecycle.
- Implements `read()` via `NuiImageStreamGetNextFrame`.
- Implements `tilt` via `NuiCameraElevationSetAngle`.
- Implements `pan` digitally (since Kinect lacks a pan motor).
