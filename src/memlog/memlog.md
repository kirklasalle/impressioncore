# ImpressionCore: Memory Log (Neural Context)

**Project Status**: 2025 Swarm Intelligence Advancement (Phase 1-6 Complete)
**Current Focal Point**: Synergistic MCP Orchestration & High-Density Synthesis

### 24h Context Matrix
- **Objective**: Unify the "Brain-Triad" servers (IDS, EDS, IPA, VRGC) under Goliath.
- **Key Insight**: "Synthesis-First" research methodology prevents context drift by anchoring search results in internal GraphRAG metadata.
- **Hardware Profile**: Optimized for GTX 1050 Ti (4GB VRAM) via dynamic VRAM Load Balancing and module hibernation.
- **Constraint**: VRAM ceiling requires pro-active swapping of heavy model-based servers (IPA/VRGC).

### Critical Logic Chains
1. **Sensory Discovery**: WMI -> PnP Inventory -> Hierarchical Category Mapping -> Hardware Metadata.
2. **Audio Fusion**: 4-Channel PS Eye audio is handled by specific deduplication rules (families) to avoid "ghost" microphones.
3. **Vision Bridge**: PS Eye uses `pseyepy` (LibUSB) mapped to Virtual IDs (now standardized to 99+).

### Future Directives
- Implement true multi-camera stereoscopic depth mapping.
- Extend the "Trace Route" to include audio driver health and lattice VAD status.
- Ensure all artifacts are synced as a "Single Source of Truth" (SSoT).

### Kinect v1 Controller (Jan 2026)
- **New**: `tools/kinect_controller_app.py` - Complete Kinect control app
- **New**: `tools/kinect_bridge_enhanced.cpp` - C++ bridge with audio/face
- **New**: `src/vision/hcep.py` - Human Conversation Eye Points (HCEP)
- **New**: `src/vision/face_identity.py` - Facial recognition module
- **Archived**: `docs/hardware/kinect_v1_complete_reference.md`
- **Features**: RGB/Depth/IR, Motor, Accelerometer, 20-Joint Skeleton, Camera Settings
- **HCEP**: Maps gaze direction → cognitive/emotional states
- **Pending**: Audio capture, PDF math formulas for HCEP

### STRATEGIC GOAL: Avatar Eye Tracking
- Kinect → HCEP → Frontend Avatar
- Avatar tracks user's eyes during conversation
- HCEP provides real-time gaze/cognitive state
- Critical dependency: This Kinect app must succeed

### Advanced Face Recognition Suite (Jan 14, 2026)
- **New**: `orchestrator/face_recognition_engine.py` - Core identity tracker
- **New**: `orchestrator/face_database.py` - SQLite identity storage
- **New**: `orchestrator/liveness_detector.py` - Anti-spoofing (Kinect/RGB)
- **New**: `orchestrator/emotion_analyzer.py` - Affective state analysis
- **New**: `docs/reference/face_recognition_suite.md` - Technical guide
- **UI**: Premium Face Management sidebar + rich Video Overlay in frontend
- **Agent0**: Personalized greetings and context via `vision_tool`
- **Status**: Deployment Complete. Verified high-accuracy recognition on Kinect/UVC.
