import json
import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

class CalibrationManager:
    """
    Manages hardware startup sequences, health audits, and spatial baselines.
    Ensures the 3D apparatus is correctly aligned and operational before use.
    """

    def __init__(self, config_path: str = "config/spatial_layout.json"):
        self.config_path = config_path
        self.layout = self._load_layout()
        self.startup_report = {
            "timestamp": 0,
            "status": "INITIALIZING",
            "checks": []
        }

    def _load_layout(self) -> dict[str, Any]:
        """Loads spatial baselines (mm) and FOV data for triangulation."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load spatial layout: {e}")

        # Default Layout (Assuming standard desk setup)
        return {
            "units": "cm",
            "cameras": {
                "0": {"pos": [0, 0, 0], "fov": 60, "label": "Primary"},
                "98": {"pos": [15.0, 5.0, 0], "fov": 57, "label": "Kinect"}, # 15cm right, 5cm up
                "99": {"pos": [7.5, 12.0, -2.0], "fov": 50, "label": "PS Eye"} # Center-ish
            }
        }

    def run_startup_checklist(self, vision_layer) -> dict[str, Any]:
        """
        Executes an automated battery of tests to confirm system readiness.
        """
        logger.info("--- STARTING HARDWARE STARTUP CHECKLIST ---")
        self.startup_report["timestamp"] = time.time()
        checks = []
        is_ready = True

        # 1. PnP Inventory Check
        pnp_data = vision_layer.get_hardware_intelligence()
        pnp_count = len(pnp_data.get("pnp_inventory", []))
        checks.append({
            "name": "PnP Inventory Audit",
            "status": "PASS" if pnp_count > 0 else "FAIL",
            "detail": f"Detected {pnp_count} relevant sensory devices."
        })
        if pnp_count == 0:
            is_ready = False

        # 2. Driver Conflict Check (LibUSB vs UVC)
        diag = vision_layer.diag_hardware()
        conflict_status = diag.get("status", "HEALTHY")
        checks.append({
            "name": "Driver Integrity Check",
            "status": "PASS" if conflict_status == "HEALTHY" else "WARNING",
            "detail": f"System status: {conflict_status}"
        })
        if conflict_status == "CONFLICT":
            is_ready = False

        # 3. Active Stream Signal Verification
        active_caps = len(vision_layer.caps)
        checks.append({
            "name": "Active Signal Lock",
            "status": "PASS" if active_caps > 0 else "FAIL",
            "detail": f"{active_caps} cameras successfully opened and streaming."
        })
        if active_caps == 0:
            is_ready = False

        # 4. Latency / Signal Stability (Warm-up)
        # We try to read a frame from each cap to ensure they aren't 'stuck'
        stuck_cameras = []
        stuck_cameras = []
        for idx, cap in vision_layer.caps.items():
            max_retries = 30  # Allow up to 30 retries (approx 3.0s) for slow hardware like Kinect
            success = False
            for _attempt in range(max_retries):
                try:
                    # Test read
                    ret, _ = cap.read()
                    if ret:
                        success = True
                        break
                    time.sleep(0.1)
                except Exception:
                    # Ignore exceptions during warm-up retries
                    time.sleep(0.1)

            if not success:
                stuck_cameras.append(str(idx))

        checks.append({
            "name": "Signal Warm-up",
            "status": "PASS" if not stuck_cameras else "FAIL",
            "detail": "All streams responsive." if not stuck_cameras else f"Signal loss on: {', '.join(stuck_cameras)}"
        })
        if stuck_cameras:
            is_ready = False

        self.startup_report["checks"] = checks
        self.startup_report["status"] = "READY" if is_ready else "ERROR"

        if not is_ready:
            failed_checks = [c["name"] for c in checks if c["status"] != "PASS"]
            logger.error(f"Startup Checklist FAILED. Failing checks: {failed_checks}")
            for c in checks:
                if c["status"] != "PASS":
                    logger.error(f"  - {c['name']}: {c['detail']}")

        logger.info(f"Checklist Complete. Status: {self.startup_report['status']}")
        return self.startup_report

    def get_calibration_params(self, cam_id: int) -> dict[str, Any]:
        """Returns physical coordinates and FOV for a specific camera."""
        return self.layout["cameras"].get(str(cam_id), {"pos": [0,0,0], "fov": 60})

calibration_mgr = CalibrationManager()
