# Kinect 360 Deep Dive & Integration Guide

## Overview
This document details the advanced integration of the Xbox 360 Kinect (V1) into ImpressionCore. The goal is to match the robust tracking capabilities of dedicated solutions like "Amethyst" (KinectToVR) by leveraging the native Microsoft Kinect SDK 1.8 through a high-performance Python `ctypes` bridge.

## Architecture

```mermaid
graph TD
    A[ImpressionCore (Python)] -->|ctypes| B[Kinect10.dll (SDK 1.8)]
    B -->|USB| C[Xbox 360 Kinect Sensor]
    
    subgraph "Kinect Connector"
        D[INuiSensor Interface]
        E[NuiSkeletonGetNextFrame]
        F[NuiTransformSmooth]
    end
    
    A --> D
    D --> E
    E -->|Raw Joints| F
    F -->|Smoothed Joints| A
```

### Why SDK 1.8?
The Xbox 360 Kinect is NOT compatible with the Kinect v2 SDK (v2.0). It requires the legacy SDK v1.8. While newer drivers like `libfreenect` exist, the official Microsoft SDK provides:
1.  **Skeletal Tracking**: Built-in, highly optimized body tracking.
2.  **Holt-Winters Smoothing**: The `NuiTransformSmooth` function applies advanced filtering (Holt Double Exponential Smoothing) to reduce jitter, which is critical for VR/Avatar usage.
3.  **Audio Beamforming**: Native support for the microphone array (future expansion).

## Implementation Details

### The Python-Native Bridge (`kinect_connector.py`)
Instead C++ wrappers, we access `Kinect10.dll` directly using `ctypes`. This reduces latency and build complexity.

#### Skeletal Smoothing
We implement the "Amethyst Standard" smoothing parameters directly in Python:
```python
# Correction: 0.5, Prediction: 0.5, JitterRadius: 0.05, MaxDeviation: 0.04
self.smooth_params = NUI_TRANSFORM_SMOOTH_PARAMETERS(0.5, 0.5, 0.05, 0.04)
# ... inside poll loop ...
k10.NuiTransformSmooth(ctypes.byref(frame), ctypes.byref(self.smooth_params))
```

### Troubleshooting

#### "Code 10" or "Code 28" in Device Manager
If the driver is not loading:
1.  Uninstall any "Kinect for Windows v2" drivers.
2.  Install **KinectSDK-v1.8-Setup.exe**.
3.  Ensure the device is plugged into a USB 2.0 port (some USB 3.0 controllers have issues with Kinect v1 isochronous transfer).

#### "Kinect Not Ready" (0x83010002)
- The sensor is detected but hasn't finished initializing.
- ImpressionCore waits 1.0s before reading. If this error persists, unplug/replug the USB.

#### Light Flickering (Green LED)
- This indicates the camera is being probed but not successfully opened.
- ImpressionCore now properly releases the sensor on error, which should stop the flickering.

## Amethyst Comparison
| Feature | ImpressionCore | Amethyst (K2VR) |
| :--- | :--- | :--- |
| **Driver** | SDK 1.8 (Direct DLL) | SDK 1.8 (C# Service) |
| **Smoothing** | Native (NuiTransformSmooth) | Native (NuiTransformSmooth) |
| **Usage** | Native Python Object | External Service (SteamVR) |
| **Audio** | WMI Detection | N/A (Focus on tracking) |
