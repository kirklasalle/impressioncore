# QuickCam Orbit/Sphere MP - Windows Native XU Driver Investigation

**Date**: 2025-12-29
**Status**: Concluded (Failed/Unsupported)
**Objective**: Enable Pan/Tilt motor control on Windows using the native Logitech driver via DirectShow/WDM interfaces (`IKsControl`) to bypass the need for Zadig/PyUSB.

## Investigation Steps & Results

1.  **Filter Analysis**:
    - The camera enumerates correctly as a DirectShow filter.
    - Standard interfaces (`IAMVideoProcAmp`) work for brightness/contrast.

2.  **`IKsControl` Search**:
    - Attempted `QueryInterface(IKsControl)` on the Filter -> Failed.
    - Enumerated all Pins (Input/Output) -> Failed.

3.  **Topology Traversal**:
    - Confirmed support for `IKsTopologyInfo`.
    - Found 8 internal nodes (3 standard UVC, 5 device-specific).
    - Attempted to instantiate each node (`CreateNodeInstance`) and query `IKsControl` -> Failed on all 8 nodes.

4.  **GraphBuilder Search**:
    - Implemented `ICaptureGraphBuilder2::FindInterface` with a full Filter Graph setup.
    - Exhaustively searched upstream/downstream and on the filter/pins for `IKsControl` -> Failed with `E_NOINTERFACE`.

## Conclusion
The Windows driver for this specific model (QuickCam Orbit/Sphere MP) does not expose the `IKsControl` interface through the user-mode DirectShow proxy. This makes the "Windows Native XU Hack" (sending raw extension unit commands) impossible via standard COM means.

## Resolution
- Validated that the native driver path is a dead end for motor control.
- Recommended switching to **PyUSB** (LibUSB-win32/Zadig) for motor control functionality.
- Code for the extensive search (Graph building, Topology traversal) has been preserved but disabled in `quickcam_driver.py`.
