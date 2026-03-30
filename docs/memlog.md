# ImpressionCore: Memory Log (Neural Context)

**Created:** December 27, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\memlog.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

**Project Status**: High-Velocity Optimization & Audit Phase
**Current Focal Point**: Spatial Audio Intelligence & Sensor Fusion (SpatialSense v1)

### 24h Context Matrix

- **Objective**: Reduce launch time and fix hardware discovery "blind spots".
- **Key Insight**: WMI discovery was slow; caching improved speed but caused staleness when hot-swapping cameras.
- **Hardware Profile**: The system is tuned for PlayStation Eye (4-channel) and Kinect v1 (Xbox 360) sensors.
- **Constraint**: Multiple running instances lock USB interfaces, requiring a globally unique process lock.

### Critical Logic Chains

1. **Sensory Discovery**: WMI -> PnP Inventory -> Hierarchical Category Mapping -> Hardware Metadata.
2. **Audio Fusion**: 4-Channel PS Eye audio is handled by specific deduplication rules (families) to avoid "ghost" microphones.
3. **Vision Bridge**: PS Eye uses `pseyepy` (LibUSB) mapped to Virtual IDs (now standardized to 99+).

### Future Directives

- Implement true multi-camera stereoscopic depth mapping.
- Extend the "Trace Route" to include audio driver health and lattice VAD status.
- Ensure all artifacts are synced as a "Single Source of Truth" (SSoT).
