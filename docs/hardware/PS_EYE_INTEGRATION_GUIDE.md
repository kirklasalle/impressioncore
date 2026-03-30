# PlayStation Eye Integration Guide

**Created:** December 25, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle  
**Tags:** #docs\hardware\PS_EYE_INTEGRATION_GUIDE.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

**Version:** 1.0.0  
**Author:** Kirk LaSalle  
**Status:** Production

---

## Executive Summary

This guide provides complete instructions for integrating the PlayStation Eye (PS3 Eye) camera with ImpressionCore's vision system. The PS Eye offers exceptional value with 60fps capture at 640x480 resolution for under $10 on the secondary market.

---

## 🎯 Quick Start

### Prerequisites Checklist

- [ ] PlayStation Eye camera (SLEH-00448 or equivalent)
- [ ] Windows 10/11 64-bit
- [ ] Python 3.13+
- [ ] Zadig tool (https://zadig.akeo.ie/)
- [ ] ImpressionCore codebase

### 5-Minute Setup

```bash
# 1. Install pseyepy (anmagx fork)
pip install git+https://github.com/anmagx/pseyepy.git

# 2. Install libusb dependencies  
pip install libusb libusb1

# 3. Run Zadig (see detailed steps below)

# 4. Verify installation
python -c "from pseyepy import cam_count; print(f'Cameras: {cam_count()}')"

# 5. Start ImpressionCore
python src/interfaces/triad_api.py
```

---

## 📷 Hardware Identification

### Device Specifications

| Property | Value |
|----------|-------|
| **Vendor ID** | 1415 (OmniVision) |
| **Product ID** | 2000 |
| **Resolution** | 640x480 (Large) or 320x240 (Small) |
| **Frame Rate** | Up to 60fps (Large) or 120fps (Small) |
| **Sensor** | OmniVision OV7720 |
| **Interface** | USB 2.0 |
| **Microphone** | 4-element array |

### LED Indicators

| LED | Color | Meaning |
|-----|-------|---------|
| Power | Blue | Camera has power |
| Active | Red | Camera is streaming |
| Both Off | - | No power/disconnected |
| Blue Only | Blue | Power but not acquired |

---

## 🔧 Driver Installation

### Step 1: Download Zadig

1. Navigate to https://zadig.akeo.ie/
2. Download the latest version
3. **Run as Administrator**

### Step 2: Identify the PS Eye

1. Connect the PS Eye via USB
2. In Zadig, go to **Options → List All Devices**
3. Find "**USB Camera-B4.04.27.1**" in dropdown
4. Verify VID/PID: **1415 / 2000**

### Step 3: Replace Driver

``` text
┌─────────────────────────────────────────────────────┐
│                    Zadig 2.8                        │
├─────────────────────────────────────────────────────┤
│  Device: USB Camera-B4.04.27.1                      │
│                                                     │
│  Driver:                                            │
│  ┌───────────────┐      ┌───────────────┐          │
│  │ Windows USB   │  →   │ libusb-win32  │          │
│  │ (v10.0.xxx)   │      │ (v1.2.6.0)    │          │
│  └───────────────┘      └───────────────┘          │
│                                                     │
│              [ Replace Driver ]                     │
│                                                     │
│  ⚠ This will replace the Windows driver            │
└─────────────────────────────────────────────────────┘
```

1. Set target driver to **libusb-win32**
2. Click **Replace Driver**
3. Wait for completion (~30 seconds)

### Step 4: Verify Installation

```bash
# Test pseyepy detection
python -c "
from pseyepy import Camera, cam_count
print(f'Detected cameras: {cam_count()}')
if cam_count() > 0:
    c = Camera(0)
    frame, ts = c.read()
    print(f'Frame shape: {frame.shape}')
    c.end()
"
```

Expected output:
``` text
Detected cameras: 1
Frame shape: (480, 640, 4)
```

---

## 🐍 Python Integration

### pseyepy Library (anmagx fork)

The anmagx fork provides Windows 64-bit compatibility:

```bash
pip install git+https://github.com/anmagx/pseyepy.git
```

### Basic Usage

```python
from pseyepy import Camera

# Initialize camera
cam = Camera(0, resolution=Camera.RES_LARGE, fps=60)

# Capture frame
frame, timestamp = cam.read()
print(f"Frame: {frame.shape}, Time: {timestamp}")

# Clean up
cam.end()
```

### Resolution Options

| Constant | Resolution | Max FPS |
|----------|------------|---------|
| `Camera.RES_LARGE` | 640x480 | 60 |
| `Camera.RES_SMALL` | 320x240 | 120 |

### Advanced Options

```python
cam = Camera(
    0,                          # Camera index
    resolution=Camera.RES_LARGE,
    fps=60,
    colour=True,                # RGB mode (vs grayscale)
    vflip=False,                # Vertical flip
    hflip=False,                # Horizontal flip
    gain=50,                    # Sensor gain (0-79)
    exposure=100                # Exposure (0-511)
)
```

---

## 🔌 ImpressionCore Integration

### PSEyeWrapper Class

ImpressionCore wraps the pseyepy Camera to match OpenCV's interface:

```python
# Location: src/orchestrator/orbcloud_vision.py

class PSEyeWrapper:
    """Wraps pseyepy Camera to mimic cv2.VideoCapture interface."""
    
    def __init__(self, eye_cam):
        self.eye = eye_cam
        
    def read(self):
        """Returns (success, frame) like cv2.VideoCapture."""
        result = self.eye.read()
        if result is None:
            return False, None
        frame, timestamp = result
        if isinstance(frame, np.ndarray) and frame.size > 0:
            # Convert RGB → BGR for OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            return True, frame
        return False, None
```

### Camera Detection

The PS Eye is mapped to **index 99** to avoid collision with OpenCV indices:

```python
def _scan_pseyepy(self):
    """Scan for PS Eye via native libusb."""
    eye = PSEyeCamera(0, resolution=PSEyeCamera.RES_LARGE, fps=60)
    wrapper = PSEyeWrapper(eye)
    
    # Map to special index
    self.caps[99] = wrapper
    self.hardware_metadata[99] = {
        "width": 640,
        "height": 480,
        "fps": 60,
        "backend": "LIBUSB_PSEYEPY",
        "model": "PS Eye (Native)"
    }
```

### Stream Priority

The MJPEG stream generator prioritizes PS Eye:

```python
# Priority order:
# 1. PS Eye (index 99)
# 2. First available OpenCV camera
# 3. "NO SIGNAL" fallback frame

if 99 in vision.caps:
    ret, frame = vision.caps[99].read()  # Priority
else:
    for idx, cap in vision.caps.items():
        ret, frame = cap.read()  # Fallback
```

---

## 🐛 Troubleshooting

### Issue: Camera Not Detected

**Symptoms:**

- `cam_count()` returns 0
- Index 99 not in caps

**Solutions:**

1. Verify Zadig driver swap completed
2. Check USB connection (try different port)
3. Confirm blue LED is lit
4. Restart Python process

### Issue: Driver Conflict

**Symptoms:**

- Zadig shows wrong driver
- Windows keeps reverting

**Solutions:**

1. Disable Windows Driver Signature Enforcement
2. Use Device Manager to uninstall existing driver
3. Disconnect other USB cameras during setup

### Issue: "NO SIGNAL" Despite Red LED

**Symptoms:**

- Red LED on (camera active)
- Frontend shows "NO SIGNAL"

**Solutions:**

1. Check PSEyeWrapper is correctly unpacking tuples
2. Verify RGB→BGR conversion
3. Check for exceptions in `read()` method
4. Restart backend after physical reconnection

### Issue: Low Frame Rate

**Symptoms:**

- Choppy video
- High latency

**Solutions:**

1. Check USB bandwidth (avoid hubs)
2. Reduce resolution to RES_SMALL
3. Lower JPEG quality in stream encoder
4. Close other USB 2.0 devices

---

## 📊 Performance Optimization

### USB Bandwidth

| Configuration | Bandwidth | Notes |
|---------------|-----------|-------|
| 640x480 @ 60fps | ~36 MB/s | Requires USB 2.0 |
| 320x240 @ 120fps | ~18 MB/s | Lower latency |
| 640x480 @ 30fps | ~18 MB/s | Reduced CPU |

### CPU Usage

```python
# Throttle stream to save CPU
time.sleep(0.033)  # ~30 FPS output

# Alternative: Use hardware JPEG if available
cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
```

---

## 🔗 References

- [pseyepy GitHub (anmagx fork)](https://github.com/anmagx/pseyepy)
- [Zadig USB Driver Tool](https://zadig.akeo.ie/)
- [PS3 Eye Specifications](https://en.wikipedia.org/wiki/PlayStation_Eye)
- [libusb Windows](https://libusb.info/)

---

## 📜 Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-25 | Initial guide with successful integration |
