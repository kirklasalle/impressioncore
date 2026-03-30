# QuickCam Orbit/Sphere MP Technical Reference

## Device Information
- **Name**: Logitech QuickCam Orbit/Sphere MP
- **USB ID**: `046d:08c2`
- **Driver Type**: DirectShow Filter (WDM / Kernel Streaming Proxy)

## Motor Control Protocol Analysis (Windows Native)

### Objective
Establish low-level Pan/Tilt/Zoom (PTZ) control using the native Windows driver via DirectShow COM interfaces (`IKsControl`), bypassing the need for a custom USB driver (Zadig/LibUSB).

### Findings
1.  **DirectShow Filter**:
    - The device is enumerated as a standard DirectShow filter.
    - It supports standard `IBaseFilter`, `IAMStreamConfig`, `IAMVideoProcAmp` (Brightness, Contrast, etc.).
    - **Outcome**: Connection to filter successful.

2.  **Kernel Streaming Topology (`IKsTopologyInfo`)**:
    - The filter **SUPPORTS** `IKsTopologyInfo` (`{720D4AC0-7533-11D0-A5D6-28DB04C10000}`).
    - **Internal Topology**: The driver reports **8 internal nodes**.
    - **Node Types**:
        - Node 0: `{DFF229E6-F70F-11D0-B917-00A0C9223196}` (KSNODETYPE_VIDEO_PROCESSING)
        - Node 1: `{DFF229E1-F70F-11D0-B917-00A0C9223196}` (KSNODETYPE_VIDEO_CAMERA_TERMINAL)
        - Node 2: `{DFF229E5-F70F-11D0-B917-00A0C9223196}` (KSNODETYPE_VIDEO_INPUT_TERMINAL)
        - Node 3-7: `{941C7AC0-C559-11D0-8A2B-00A0C9255AC1}` (KSNODETYPE_DEV_SPECIFIC)
    - **Interpretation**: Nodes 3-7 likely represent the Extension Units (XU) for proprietary controls (Pan/Tilt, Face Tracking).

3.  **Interface Probing (`IKsControl`)**:
    - **Filter**: `QueryInterface(IKsControl)` -> **FAILED** (`E_NOINTERFACE`).
    - **Pins**: Enumerated all pins (Input/Output). `QueryInterface(IKsControl)` -> **FAILED** on all pins.
    - **Nodes**: Traversed all 8 nodes via `CreateNodeInstance`. `QueryInterface(IKsControl)` -> **FAILED** on all node instances.
    - **Graph Builder**: Used `ICaptureGraphBuilder2::FindInterface` to search upstream/downstream and on specific categories -> **FAILED**.

### Conclusion
The standard Logitech driver for Windows (verified on Windows 11) does **not** expose the `IKsControl` interface via the user-mode DirectShow proxy filter. This prevents sending raw "Extension Unit" commands (Windows Native XU Hack) to the device.

To control the motors, one of the following is required:
1.  **PyUSB / Zadig**: Replace the driver with `libusb-win32` (Zadig). This works immediately but breaks standard webcam usage in other apps (Zoom/Teams) unless using a "Filter" driver mode (experimentally supported by libusb).
2.  **Proprietary API**: Logitech likely uses a private interface or a side-channel mechanism (possibly raw `DeviceIoControl` to the driver handle) not exposed via standard COM.

## Recommended Path
Use **PyUSB** with a Zadig driver for reliable motor control in this application context. The "Windows Native" path is effectively a dead end for this specific driver version.
