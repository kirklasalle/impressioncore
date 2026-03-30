# PS Eye Integration Breakthrough

**Date:** December 25, 2025  
**Category:** Hardware Integration  
**Status:** SUCCESS  
**Tags:** #vision #ps-eye #libusb #pseyepy #streaming #breakthrough

---

## Summary

Successfully integrated PlayStation Eye camera into ImpressionCore's vision system via native 64-bit libusb driver, achieving live MJPEG streaming at 640x480@60fps.

---

## Technical Details

### Problem Statement
The PS Eye camera could not be accessed via standard OpenCV backends (DirectShow/MSMF) on 64-bit Python 3.13+ due to:
1. CL-Eye driver only supports 32-bit processes
2. Windows generic USB driver blocks libusb access
3. No native 64-bit driver available

### Solution Implemented
1. **Zadig Driver Swap**: Replaced Windows generic USB driver with libusb-win32
2. **pseyepy Library**: Installed anmagx fork with Windows 64-bit support
3. **PSEyeWrapper Class**: Created adapter to normalize pseyepy interface to cv2.VideoCapture
4. **Tuple Unpacking Fix**: Fixed pseyepy `read()` which returns `(frame, timestamp)` not just frame
5. **Direct Camera Read**: Updated MJPEG stream to read from `caps[99]` directly

### Key Code Changes

#### PSEyeWrapper.read() Fix
```python
# Before (broken):
frame = self.eye.read()  # Expected numpy array

# After (working):
result = self.eye.read()  # Returns (frame, timestamp)
frame, timestamp = result
frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
return True, frame
```

#### MJPEG Stream Fix
```python
# Before (broken):
if 99 in triad_instance.vision._frames:  # _frames was empty
    frame = triad_instance.vision._frames[99]

# After (working):
if 99 in vision.caps:
    ret, frame = vision.caps[99].read()  # Read directly
```

---

## Results

- **Camera Detection**: PS Eye detected at index 99
- **Frame Acquisition**: 640x480x3 BGR frames @ 60fps
- **Stream Delivery**: MJPEG to frontend at ~30fps
- **Latency**: ~50ms end-to-end
- **Stability**: No drops or disconnects

---

## Files Modified

| File | Changes |
|------|---------|
| `src/orchestrator/orbcloud_vision.py` | Added PSEyeWrapper, _scan_pseyepy, tuple unpacking |
| `src/interfaces/triad_api.py` | Fixed generate_mjpeg_stream to read from caps |
| `src/interfaces/web_client/src/App.jsx` | Vision Layer UI cleanup |

---

## Documentation Created

1. `docs/api/openapi.yaml` - Full OpenAPI 3.1 specification
2. `docs/api/TRIAD_API_REFERENCE.md` - API reference with Mermaid diagrams
3. `docs/architecture/BRAIN_TRIAD_DESIGN.md` - Brain-Triad architecture
4. `docs/technical/VISION_SYSTEM_ARCHITECTURE.md` - Vision system documentation
5. `docs/hardware/PS_EYE_INTEGRATION_GUIDE.md` - PS Eye setup guide

---

## Visual Proof

Screenshot10 captured showing live PS Eye stream in ImpressionCore frontend.
Location: `docs/assets/screenshot10.png`

---

## Lessons Learned

1. **pseyepy returns tuples**: Always check library documentation for return types
2. **Driver matters**: Zadig driver swap is essential for libusb access
3. **Direct reads beat buffers**: Reading directly from camera avoids empty buffer issues
4. **RGB→BGR conversion**: pseyepy uses RGB, OpenCV expects BGR

---

## Next Steps

- [ ] Add Kinect v1 integration using similar pattern
- [ ] Implement multi-camera streaming
- [ ] Add face detection overlay
- [ ] Create automated driver detection

---

## Attribution

- **pseyepy fork**: github.com/anmagx/pseyepy
- **Zadig tool**: zadig.akeo.ie
- **Original PS3EYEDriver**: github.com/inspirit/PS3EYEDriver
