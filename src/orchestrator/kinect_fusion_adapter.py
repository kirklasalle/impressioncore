import time
from dataclasses import dataclass
from typing import Any

from src.orchestrator.system_logger import log_event


@dataclass
class KinectFusionState:
    """Lightweight Kinect fusion status for runtime orchestration."""

    color_available: bool = False
    depth_available: bool = False
    ir_available: bool = False
    skeleton_available: bool = False
    fusion_ready: bool = False
    last_update_ts: float = 0.0


class KinectFusionAdapter:
    """Skeleton adapter for RGB/Depth/IR fusion readiness and telemetry-safe metadata."""

    def __init__(self):
        self.state = KinectFusionState()

    def refresh(self, vision: Any = None) -> None:
        """Refresh available Kinect streams from the current vision object."""
        if vision is None:
            self.state = KinectFusionState(last_update_ts=time.time())
            return

        color_available = False
        try:
            color_available = 98 in getattr(vision, "caps", {})
        except Exception:
            color_available = False

        depth_available = bool(getattr(vision, "depth_active", False))
        ir_available = bool(getattr(vision, "ir_active", False))
        skeleton_available = getattr(vision, "latest_skeleton", None) is not None

        self.state.color_available = color_available
        self.state.depth_available = depth_available
        self.state.ir_available = ir_available
        self.state.skeleton_available = skeleton_available
        self.state.fusion_ready = color_available and (depth_available or ir_available)
        self.state.last_update_ts = time.time()

    def get_status(self) -> dict[str, Any]:
        """Get telemetry-safe fusion status payload for API responses."""
        return {
            "color_available": self.state.color_available,
            "depth_available": self.state.depth_available,
            "ir_available": self.state.ir_available,
            "skeleton_available": self.state.skeleton_available,
            "fusion_ready": self.state.fusion_ready,
            "last_update_ts": self.state.last_update_ts,
            "fusion_mode": "rgb+depth+ir" if self.state.fusion_ready else "degraded",
        }

    def summarize(self) -> str:
        """Human-readable fusion status summary for logs."""
        summary = self.get_status()
        text = (
            "Kinect fusion status: "
            f"ready={summary['fusion_ready']}, "
            f"color={summary['color_available']}, "
            f"depth={summary['depth_available']}, "
            f"ir={summary['ir_available']}, "
            f"skeleton={summary['skeleton_available']}"
        )
        log_event("VISION", text)
        return text
