# Vision System Architecture

**Created:** December 25, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle  
**Tags:** #docs\technical\VISION_SYSTEM_ARCHITECTURE.md #documentation  
**Category:** Technical Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

**Version:** 1.0.0  
**Author:** Kirk LaSalle  
**Status:** Production

---

## Executive Summary

The OrbCloudVision system is ImpressionCore's comprehensive vision layer, providing hardware-agnostic camera detection, multi-source frame acquisition, and real-time MJPEG streaming. It supports multiple camera backends including OpenCV (DirectShow/MSMF), PlayStation Eye (via native libusb), and Kinect sensors.

---

## 🎯 Live System Demonstration

![PS Eye Live Stream](./screenshot10.png)
*Figure 1: Live PlayStation Eye camera streaming at 640x480@60fps through the ImpressionCore Brain-Triad frontend. The Vision Layer displays real-time video captured via native libusb driver.*

---

## 🏗️ System Architecture

### Component Overview

```mermaid
flowchart TB
    subgraph Hardware["🔌 Hardware Layer"]
        PSEYE["PlayStation Eye<br/>VID:1415 PID:2000"]
        KINECT["Kinect v1<br/>VID:045E PID:02AE"]
        UVC["Generic UVC<br/>Webcams"]
    end

    subgraph Drivers["🔧 Driver Layer"]
        LIBUSB["libusb-win32<br/>(via Zadig)"]
        DSHOW["DirectShow<br/>(Windows)"]
        MSMF["Media Foundation<br/>(Windows)"]
        KINECTSDK["Kinect SDK 1.8"]
    end

    subgraph Detection["🔍 Detection Layer"]
        WMI["WMI PnP Scanner"]
        OPENCV["OpenCV Probe<br/>(Indices 0-10)"]
        PSEYEPY["pseyepy Scanner<br/>(Index 99)"]
    end

    subgraph Wrappers["📦 Wrapper Layer"]
        PSEW["PSEyeWrapper"]
        CVW["cv2.VideoCapture"]
    end

    subgraph Core["🧠 OrbCloudVision Core"]
        CAPS["caps: Dict[int, Capture]"]
        META["hardware_metadata"]
        BUFFER["visual_buffer<br/>deque(maxlen=30)"]
    end

    subgraph Output["📤 Output Layer"]
        FRAMES["Frame Generator"]
        MJPEG["MJPEG Stream"]
        API["FastAPI Endpoint"]
    end

    PSEYE --> LIBUSB --> PSEYEPY
    KINECT --> KINECTSDK
    UVC --> DSHOW --> OPENCV
    UVC --> MSMF --> OPENCV
    
    PSEYEPY --> PSEW
    OPENCV --> CVW
    
    PSEW --> CAPS
    CVW --> CAPS
    
    CAPS --> FRAMES
    META --> FRAMES
    FRAMES --> MJPEG --> API

    style PSEYE fill:#e65100,color:#fff
    style PSEYEPY fill:#e65100,color:#fff
    style PSEW fill:#e65100,color:#fff
```

---

## 📷 Camera Detection Pipeline

### Detection Sequence

```mermaid
sequenceDiagram
    autonumber
    participant V as OrbCloudVision
    participant WMI as WMI Scanner
    participant PS as pseyepy
    participant CV as OpenCV
    participant API as FastAPI

    V->>V: open()
    
    V->>WMI: run_pnp_scan()
    WMI-->>V: Device inventory (12 devices)
    
    alt PSEYE_AVAILABLE
        V->>PS: _scan_pseyepy()
        PS->>PS: Camera(0, RES_LARGE, fps=60)
        PS-->>V: PSEyeWrapper @ index 99
        Note over V: PS Eye registered
    end
    
    loop Indices 0-10
        V->>CV: VideoCapture(idx, backend)
        alt Camera Found
            CV-->>V: Active capture
            V->>V: Store in caps[idx]
        else No Camera
            CV-->>V: None
        end
    end
    
    V->>V: _record_hardware_intel()
    V->>API: Vision layer active
```

### Camera Index Mapping

| Index | Source | Backend | Priority |
|-------|--------|---------|----------|
| 99 | PlayStation Eye | libusb/pseyepy | Highest |
| 0-10 | UVC Cameras | DSHOW/MSMF/ANY | Standard |
| 100+ | Reserved | Future sensors | Low |

---

## 🎮 PlayStation Eye Integration

### Driver Requirements

```mermaid
flowchart LR
    subgraph Before["❌ Before Zadig"]
        WIN["Windows Generic<br/>USB Driver"]
        FAIL["Cannot Access<br/>via libusb"]
    end

    subgraph After["✅ After Zadig"]
        ZADIG["Zadig Tool"]
        LIBUSB["libusb-win32<br/>Driver"]
        SUCCESS["Native Access<br/>via pseyepy"]
    end

    WIN -->|"Zadig Swap"| ZADIG
    ZADIG --> LIBUSB
    LIBUSB --> SUCCESS

    style FAIL fill:#c62828,color:#fff
    style SUCCESS fill:#2e7d32,color:#fff
```

### Installation Steps

1. **Download Zadig**: https://zadig.akeo.ie/
2. **Connect PS Eye**: Verify red/blue lights
3. **Run Zadig** as Administrator
4. **Select Device**: "USB Camera-B4.04.27.1"
5. **Replace Driver**: libusb-win32
6. **Verify**: `pip install pseyepy` (anmagx fork)

### PSEyeWrapper Implementation

```python
class PSEyeWrapper:
    """
    Wraps pseyepy Camera to mimic cv2.VideoCapture interface.
    
    The pseyepy library returns (frame, timestamp) tuples from read(),
    while OpenCV returns (success, frame). This wrapper normalizes
    the interface for seamless integration.
    """
    
    def __init__(self, eye_cam):
        self.eye = eye_cam
        
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from the PS Eye camera.
        
        Returns:
            Tuple of (success: bool, frame: np.ndarray or None)
            
        Note:
            pseyepy returns RGB frames, converted to BGR for OpenCV.
        """
        try:
            result = self.eye.read()
            if result is None:
                return False, None
            
            # Unpack (frame, timestamp) tuple
            if isinstance(result, tuple) and len(result) == 2:
                frame, timestamp = result
            else:
                frame = result
            
            # Validate and convert
            if isinstance(frame, np.ndarray) and frame.size > 0:
                # Convert RGB → BGR for OpenCV compatibility
                if len(frame.shape) == 3 and frame.shape[2] == 3:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                return True, frame
            return False, None
        except Exception as e:
            print(f"DEBUG: PSEyeWrapper.read() exception: {e}")
            return False, None

    def release(self):
        """Release camera resources."""
        try:
            self.eye.close()
        except:
            pass

    def isOpened(self) -> bool:
        """Check if camera is operational."""
        return True
    
    def get(self, prop: int) -> float:
        """Get camera property (dummy implementation)."""
        if prop == cv2.CAP_PROP_FRAME_WIDTH: return 640
        if prop == cv2.CAP_PROP_FRAME_HEIGHT: return 480
        if prop == cv2.CAP_PROP_FPS: return 60
        return 0
```

---

## 📡 MJPEG Streaming Pipeline

### Stream Generator Flow

```mermaid
flowchart TB
    subgraph Generator["generate_mjpeg_stream()"]
        direction TB
        
        INIT["Initialize fallback frame"]
        LOOP["while True"]
        
        subgraph Read["Frame Acquisition"]
            CHECK99{"Index 99<br/>exists?"}
            READ99["caps[99].read()"]
            READOTHER["Iterate caps"]
            FALLBACK["Use NO SIGNAL frame"]
        end
        
        subgraph Encode["Frame Encoding"]
            JPEG["cv2.imencode('.jpg')"]
            YIELD["yield multipart frame"]
        end
        
        SLEEP["time.sleep(0.033)<br/>~30 FPS"]
    end

    INIT --> LOOP
    LOOP --> CHECK99
    CHECK99 -->|Yes| READ99
    CHECK99 -->|No| READOTHER
    READ99 -->|success| JPEG
    READ99 -->|fail| FALLBACK
    READOTHER -->|success| JPEG
    READOTHER -->|fail| FALLBACK
    FALLBACK --> JPEG
    JPEG --> YIELD
    YIELD --> SLEEP
    SLEEP --> LOOP

    style CHECK99 fill:#1976d2,color:#fff
    style FALLBACK fill:#c62828,color:#fff
```

### Stream Format

``` text
HTTP/1.1 200 OK
Content-Type: multipart/x-mixed-replace;boundary=frame

--frame
Content-Type: image/jpeg

[JPEG binary data]
--frame
Content-Type: image/jpeg

[JPEG binary data]
...
```

### Performance Characteristics

| Metric | Value |
|--------|-------|
| Source FPS | 60 (PS Eye native) |
| Stream FPS | 30 (throttled) |
| Resolution | 640x480 |
| JPEG Quality | Default (95) |
| Latency | ~50ms |

---

## 🔄 Temporal Visual Buffer

### Buffer Architecture

```mermaid
flowchart LR
    subgraph Input["Frame Input"]
        CAM[Active Camera]
    end

    subgraph Buffer["visual_buffer (deque)"]
        direction LR
        F1["Frame 1<br/>t-60s"]
        F2["Frame 2<br/>t-58s"]
        FN["...<br/>..."]
        F30["Frame 30<br/>t-0s"]
    end

    subgraph Output["Buffer Access"]
        SUMMARY["get_buffer_summary()"]
        GRID["4x4 Grid Image"]
    end

    CAM -->|"Every 2s"| Buffer
    F1 --> F2
    F2 --> FN
    FN --> F30
    
    Buffer --> SUMMARY
    SUMMARY --> GRID

    style Buffer fill:#1976d2,color:#fff
```

### Buffer Configuration

```python
visual_buffer = deque(maxlen=30)  # 30 frames max
buffer_interval = 2.0  # Capture every 2 seconds
# Total coverage: 60 seconds of visual history
```

---

## 🛠️ Hardware Metadata

### Schema

```json
{
  "99": {
    "width": 640,
    "height": 480,
    "fps": 60,
    "ptz_capabilities": {
      "pan": false,
      "tilt": false,
      "zoom": false,
      "digital": true
    },
    "backend": "LIBUSB_PSEYEPY",
    "status": "ACTIVE",
    "model": "PS Eye (Native)"
  }
}
```

### Capability Detection

| Capability | Detection Method |
|------------|------------------|
| Resolution | Camera query / defaults |
| FPS | Camera query / defaults |
| PTZ | Model-specific lookup |
| Backend | Acquisition source |

---

## 🔌 Sensory Hot-Swap

### State Transitions

```mermaid
stateDiagram-v2
    [*] --> OFFLINE
    
    OFFLINE --> SCANNING: open() called
    SCANNING --> ACTIVE: Camera(s) found
    SCANNING --> OFFLINE: No cameras
    
    ACTIVE --> DEGRADED: Camera disconnect
    ACTIVE --> OFFLINE: All cameras lost
    
    DEGRADED --> ACTIVE: Camera reconnect
    DEGRADED --> OFFLINE: Remaining cameras lost
    
    ACTIVE --> ACTIVE: Hot-swap event
    
    note right of ACTIVE
        Streaming operational
        Frames available
    end note
    
    note right of DEGRADED
        Partial functionality
        Fallback frame active
    end note
```

---

## 📊 Troubleshooting

### Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| No PS Eye detection | Index 99 missing | Run Zadig driver swap |
| NO SIGNAL frame | caps empty | Check physical connection |
| Stream breaks | ERR_INCOMPLETE | Ensure time import |
| Low FPS | Choppy video | Check USB bandwidth |

### Debug Commands

```bash
# Check USB devices
python -c "from pseyepy import cam_count; print(cam_count())"

# Test direct capture
python -c "from pseyepy import Camera; c=Camera(0); print(c.read()[0].shape)"

# WMI device scan
python src/orchestrator/diag_pnp.py
```

---

## 🔗 Related Documentation

- [API Reference](../api/TRIAD_API_REFERENCE.md)
- [Brain-Triad Design](../architecture/BRAIN_TRIAD_DESIGN.md)
- [PS Eye Integration Guide](../hardware/PS_EYE_INTEGRATION_GUIDE.md)

---

## 📜 Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-25 | Initial release with PS Eye support |
