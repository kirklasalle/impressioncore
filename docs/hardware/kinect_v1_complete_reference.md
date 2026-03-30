# Xbox 360 Kinect v1 Complete Reference

**Device**: Microsoft Kinect for Xbox 360 (Model 1414/1473)  
**SDK**: Kinect for Windows SDK 1.8  
**Created**: January 2026  
**Status**: Active - ImpressionCore Integration

---

## Hardware Specifications

| Component | Specification | Notes |
|-----------|---------------|-------|
| **RGB Camera** | 640x480 @ 30fps, 1280x960 @ 12fps | Bayer pattern at high-res |
| **Depth Sensor** | 640x480 @ 30fps | Range: 0.8m - 4.0m |
| **IR Projector** | Class 1 Laser | Structured light pattern |
| **Microphone Array** | 4× MEMS mics | 16kHz, 16-bit, beamforming |
| **Motor Tilt** | ±27° vertical | `NuiCameraElevationSetAngle` |
| **Accelerometer** | 3-axis | For orientation detection |

---

## Stream Types

| Type | Enum Value | Resolution | Format |
|------|------------|------------|--------|
| `NUI_IMAGE_TYPE_COLOR` | 0 | 640x480 | BGRA 32-bit |
| `NUI_IMAGE_TYPE_COLOR_YUV` | 1 | 640x480 | UYVY 16-bit |
| `NUI_IMAGE_TYPE_DEPTH` | 4 | 640x480 | 16-bit (13-bit depth + 3-bit player) |
| `NUI_IMAGE_TYPE_COLOR_INFRARED` | 5 | 640x480 | 16-bit grayscale |

---

## Initialization Flags

```python
NUI_INITIALIZE_FLAG_USES_DEPTH_AND_PLAYER_INDEX = 0x01
NUI_INITIALIZE_FLAG_USES_COLOR = 0x02
NUI_INITIALIZE_FLAG_USES_SKELETON = 0x08
NUI_INITIALIZE_FLAG_USES_AUDIO = 0x10000000
NUI_INITIALIZE_FLAG_USES_DEPTH = 0x20
```

---

## Python Integration

### KinectController Usage

```python
from tools.kinect_controller_app import KinectController

# Initialize
kinect = KinectController(sensor_index=0)
kinect.open(use_color=True, use_depth=True, use_skeleton=True)

# Get frames
rgb = kinect.get_rgb_frame()
depth_vis, depth_raw = kinect.get_depth_frame()
ir = kinect.get_ir_frame()

# Motor control
kinect.set_tilt(15)  # Tilt up 15 degrees
tilt = kinect.get_tilt()

# Accelerometer
x, y, z = kinect.get_accelerometer()

# Camera settings
kinect.set_brightness(0.7)
kinect.set_contrast(1.2)
settings = kinect.get_camera_settings()

# Skeleton tracking
skeletons = kinect.get_skeleton_frame()
for skel in skeletons:
    print(f"Head position: {skel.joints[3]}")  # HEAD joint

# Cleanup
kinect.close()
```

---

## Skeleton Joints (20 Total)

| Index | Joint Name |
|-------|------------|
| 0 | HIP_CENTER |
| 1 | SPINE |
| 2 | SHOULDER_CENTER |
| 3 | HEAD |
| 4 | SHOULDER_LEFT |
| 5 | ELBOW_LEFT |
| 6 | WRIST_LEFT |
| 7 | HAND_LEFT |
| 8 | SHOULDER_RIGHT |
| 9 | ELBOW_RIGHT |
| 10 | WRIST_RIGHT |
| 11 | HAND_RIGHT |
| 12 | HIP_LEFT |
| 13 | KNEE_LEFT |
| 14 | ANKLE_LEFT |
| 15 | FOOT_LEFT |
| 16 | HIP_RIGHT |
| 17 | KNEE_RIGHT |
| 18 | ANKLE_RIGHT |
| 19 | FOOT_RIGHT |

---

## Face Tracking (via FaceTrackLib)

The C++ bridge provides face tracking with:
- **Head Pose**: Pitch, Yaw, Roll (rotation in degrees)
- **Translation**: X, Y, Z position in 3D space
- **Face Mesh**: 87 3D points for detailed facial landmarks

### Bridge Functions

```cpp
int InitFaceTracking(int width, int height, const wchar_t* modelPath);
int ProcessFace(void* colorBuffer, void* depthBuffer, float* outPose);
int GetFacePose(float* pitch, float* yaw, float* roll);
int GetFaceMesh(float* points, int maxPoints);
int LinkFaceToSkeleton(int skeletonIndex);
```

---

## Audio (4-Mic Array)

| Property | Value |
|----------|-------|
| Sample Rate | 16,000 Hz |
| Bit Depth | 16-bit signed |
| Channels | 1 (beamformed mono) |
| Beam Range | -50° to +50° |

### Audio Features
- **Beamforming**: Hardware directional audio focusing
- **Echo Cancellation**: Built-in AEC
- **Noise Suppression**: Automatic background noise reduction
- **Source Localization**: Detect speaker direction

---

## Error Codes

| HRESULT | Name | Description |
|---------|------|-------------|
| 0x83010001 | E_NUI_DEVICE_NOT_CONNECTED | Kinect not connected |
| 0x83010002 | E_NUI_DEVICE_NOT_READY | Kinect not ready |
| 0x83010004 | E_NUI_ALREADY_INITIALIZED | Already initialized |
| 0x83010008 | E_NUI_FRAME_NO_DATA | No frame data |
| 0x83010015 | E_NUI_DEVICE_IN_USE | Another app using Kinect |
| 0x80070057 | E_INVALIDARG | Invalid argument |

---

## Files in This Project

| File | Description |
|------|-------------|
| `tools/kinect_controller_app.py` | Main Python controller application |
| `tools/kinect_bridge_enhanced.cpp` | C++ bridge with audio & face tracking |
| `src/orchestrator/kinect_connector.py` | Original connector module |

---

## Troubleshooting

### "Device not connected"
- Check USB connection (must be USB 2.0+ with power)
- Verify Kinect SDK 1.8 is installed
- Check Device Manager for Kinect entries

### Green noise in RGB stream
- This indicates buffer misalignment
- Try fallback to YUV mode (automatic in controller)

### Skeleton tracking not working
- Ensure person is 1.5m - 4.0m from sensor
- Enable near mode for closer tracking
- Full body must be visible

### Audio not capturing
- Requires bridge DLL compilation
- Run as Administrator for audio access
