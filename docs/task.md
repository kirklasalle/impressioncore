# Task: Revert to React Frontend

**Created:** December 27, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\task.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

- [x] Cancel Dear PyGui Migration <!-- id: 5 -->
- [ ] Restore Launch Scripts <!-- id: 6 -->
    - [ ] Restore Node.js checks in `orbos_ready.ps1`
    - [ ] Redirect frontend launch to `npm start` in `src/interfaces/web_client`
- [x] Verify React Client Connectivity <!-- id: 7 -->
    - [x] Debug Image Suite Controls (Deep Dive)
        - [x] Add rigorous logging to `set_controls` in `orbcloud_vision.py`
        - [x] Verify `cv2` property constants against camera drivers
    - [x] Implement Vision Hot-Swapping
        - [x] Implement `refresh_hardware` endpoint in `triad_api.py`
        - [x] **Research Audio Capabilities**
    - [x] Analyze `sensory_intelligence.py` for device counting
    - [x] Web Research (ODAS, 4-channel specs)
    - [x] **Ingest "PS Eye Bible" Google Doc** (Validated Fusion Strategy)
- [x] **Implement Audio Layer**
    - [x] Fix Microphone Count in API
    - [x] Create Audio Control Panel (Frontend)
    - [x] Implement Web Audio Visualizer
    - [x] **Backend Audio Engine** (Python)
        - [x] Verify 4-Channel Capture (WASAPI/ASIO)
        - [x] Implement VAD (Voice Activity Detection)
    - [x] **Spatial Intelligence**
        - [x] Implement GCC-PHAT for DoA
        - [x] Implement Delay-and-Sum Beamformer
        - [x] Implement VAD mechanism
    - [x] **Sensor Fusion**
        - [x] Link Vision Face X-Coord to Beamformer Angle
    - [x] Fix Default Stream Assignment (Alpha/Beta) in `App.jsx`
    - [x] Enable Explicit Hardware Assignment in GUI
- [x] **System Polish**
    - [x] Implement Graceful Shutdown (Backend & UI)
    - [x] Fix Audio Compass Layout
    - [x] Clean Console Output (Fix PyAudio warning)
- [x] **Audit & Performance Optimization**
    - [x] Optimize WMI Hardware Discovery (Caching + COM)
    - [x] Fix Audio overcount (Keyword deduplication)
    - [x] Sync API `loading_phase` with Frontend requirements
    - [x] Increase status polling frequency (2s)
    - [x] Reduce `orbos_ready.bat` timeouts
- [x] **Advanced Audit & Traceability**
    - [x] Implement Sensory Trace Route (Logic-level discovery logging)
    - [x] Implement Forced Hardware Sync (Re-probe cameras on audit)
    - [x] Add Hardware Trace to "Generate Debug Logs"
    - [x] Sync Frontend Device Lists post-audit
- [x] **Process Lifecycle & Stability**
    - [x] Implement Graceful Startup (Instance checking in `.bat`)
    - [x] Implement Graceful Shutdown (API endpoint + release hardware)
    - [x] Add Shutdown Button to Dashboard
    - [x] **24h Ledger & Documentation Audit**
        - [x] Create `change_log.md` (Ledger of all edits)
        - [x] Create `memlog.md` (Neural context & project status)
        - [x] **Media SSoT**: Consolidated walkthroughs into a continuous chronological document with persistent media links.
- [x] **Logging & Monitoring**
    - [x] Implement Comprehensive Console Redirection in `triad_api.py`
    - [x] Ensure continuous updates to `logs/triad_api_console.log`
- [x] **Sequential Startup Logic**
    - [x] Implement Health Check Polling in `orbos_ready.bat`
    - [x] Wait for Backend "READY" state before starting Frontend
    - [x] Wait for Frontend Port availability before opening Browser
- [x] **Startup Optimization & Bugfixes**
    - [x] Fix `&` parsing error in `orbos_ready.bat`
    - [x] Parallelize Frontend launch (Start Vite while Backend is loading)
    - [x] Add loading phase status to terminal polling feedback
- [x] **System Monitor Dashboard**
    - [x] Create `system_monitor.html` (Standalone status page)
    - [x] Implement live log-tailing endpoint in `triad_api.py`
    - [x] Add Orchestrator, API, and Vite status panels
    - [x] Update `orbos_ready.bat` to launch monitor immediately
    - [x] Implement 30s auto-refresh logic
- [x] **Advanced Audio Traceability**
    - [x] Implement `verify_device_health` in `audio_engine.py` (RMS Probing)
    - [x] Implement Adaptive Noise Floor & VAD logic
    - [x] Integrate Audio Probing into `SensoryIntelligence.run_discovery`
    - [x] Add "Force Sync Hardware" button to UI Audit Overlay
    - [x] Visualize `noise_floor` in `AudioPanel`
- [x] **Spatial Fusion Logic (SpatialSense v1)**
    - [x] Calculate Face -> Audio Angular Correlation in `UnifiedBrainTriad`
    - [x] Implement "Fused Target X" estimation logic
    - [x] Integrate `audio_angle` into `digital_crop` (OrbCloudVision)
    - [x] Implement "Target Lock" visualization in Acoustic Compass
- [x] **Final RAG & Documentation Sync**
    - [x] Sync all latest spatial fusion docs to `docs/` and `memlog/`
- **Change Log Entry**:
    - **Console Logging**: Implemented full console redirection for `triad_api.py` to `logs/triad_api_console.log` with unbuffered flushing for real-time monitoring, ensuring continuous updates.
    - **Sequential Startup**: Implemented intelligent PowerShell polling in `orbos_ready.bat` to synchronize Backend, Frontend, and Browser launch based on actual system health.

### 8. Intelligent Startup Synchronization

- **Deterministic Startup**: Replaced static timeouts with active health-check polling.
- **Backend Polling**: `orbos_ready.bat` now waits for `loading_phase: READY` from the API before starting the frontend.
- **Frontend Polling**: The script waits for the TCP port (3000) to be open before launching the web browser.

### 9. Parallel Startup & Batch Fixes

- **Parallel Initialization**: The Frontend dev server now spawns simultaneously with the Backend, reducing the bottleneck of serial loading.
- **Robustness**: Fixed a batch script crash where the `&` symbol in a string was being executed as a command.
- **Live Feedback**: Added PowerShell-driven phase reporting so the user can see exactly where the Neural Core is in its loading sequence.

### 10. System Monitor Dashboard

- **Standalone Health Dashboard**: Created `system_monitor.html` which launches immediately with the batch file.
- **Micro-Service Monitoring**: Tracks Backend (8000), Frontend (3000), and Orchestrator health in real-time.
- **Live Terminal Mirror**: Fetches the last 100 lines of console output via the API to show initialization progress before the main UI is ready.
- **Auto-Refresh**: Configured for 30s autorefresh as requested.

### 11. Advanced Audio Traceability & VAD

- **RMS Probing**: The system now performs a 300ms non-blocking capture on every discovered microphone during a hardware refresh to ensure the hardware is actually streaming data.
- **Adaptive noise_floor**: The `AudioEngine` now tracks environmental noise levels, allowing the VAD (Voice Activity Detection) to adapt dynamically to the room's acoustics.
- **Manual Force Sync**: A new "Force Sync Hardware" button in the Audit Overlay allows for a complete, deep-probing re-scan of the entire sensory layer.

### 12. SpatialSense Fusion v1

- **Geometric Correlation**: Correlates Face X [-1, 1] with Audio DoA [-90, 90] for precise target identification.
- **Audio-Guided Swivel**: The camera automatically swivels its digital viewport toward the source of speech if the subject moves out of the visual frame.
- **Visual Lock UI**: Real-time "Target Sync" feedback in the Acoustic Compass when audio and vision align within 12 degrees.

## Verification Results

- **Spatial Lock**: Verified correlation logic handles 75° FoV PS Eye geometry.
- **Tracking Stability**: Smooth transition between vision-dominant and audio-only tracking.
