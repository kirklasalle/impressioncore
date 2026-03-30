import json
import logging
import os
import time
from typing import Any

import pythoncom
import wmi

logger = logging.getLogger(__name__)

class SensoryIntelligence:
    """
    Centralized Hardware Discovery & Intelligence System.
    Mimics Windows Device Manager by categorizing PNP entities.
    """

    def __init__(self):
        self._wmi = None
        self.categories = {
            "Audio inputs and outputs": ["Microphone", "Speakers", "Audio", "Headset", "Phone"],
            "Imaging devices": ["Camera", "Video", "PlayStation", "Sony", "Logitech", "Orbit", "Sphere", "Eye"],
            "Kinect for Windows": ["Kinect"],
            "libusb-win32 devices": ["libusb"],
            "Sound, video and game controllers": ["Sound", "Controller", "Mic ("]
        }
        self.inventory = []
        self.device_tree = {}
        self.trace_log = [] # Detailed technical audit trail
        self.last_scan_time = 0
        self.cache_duration = 120 # Cache for 2 minutes
        self.suppression_file = "config/hardware_suppression.json"
        os.makedirs("config", exist_ok=True)
        self.suppressed_devices = self._load_suppression()

    def _load_suppression(self) -> list[str]:
        """Loads devices to ignore from config."""
        if os.path.exists(self.suppression_file):
            try:
                with open(self.suppression_file) as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def save_suppression(self):
        """Saves current suppression list to config."""
        try:
            with open(self.suppression_file, "w") as f:
                json.dump(self.suppressed_devices, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save suppression list: {e}")

    def suppress_device(self, name: str):
        """Adds a device to the suppression list."""
        if name not in self.suppressed_devices:
            self.suppressed_devices.append(name)
            self.save_suppression()
            self.log_trace(f"Device suppressed: {name}")

    def _get_wmi(self):
        """Lazy init WMI with COM threading support. Re-inits on failure."""
        try:
            if self._wmi is None:
                pythoncom.CoInitialize()
                self._wmi = wmi.WMI()
            else:
                # Test the connection to see if it's still alive
                self._wmi.Win32_ComputerSystem()
            return self._wmi
        except Exception as e:
            logger.warning(f"SensoryIntelligence: WMI Refreshing due to disconnect/error: {e}")
            try:
                pythoncom.CoInitialize()
                self._wmi = wmi.WMI()
                return self._wmi
            except Exception as e2:
                logger.error(f"SensoryIntelligence: Total WMI Failure: {e2}")
                return None

    def log_trace(self, message: str, level: str = "INFO"):
        """Adds a technical marker to the audit trace."""
        entry = {
            "timestamp": time.time(),
            "level": level,
            "message": message
        }
        self.trace_log.append(entry)
        logger.info("TRACE: %s", message)

    def run_discovery(self, force=False, audio_engine=None) -> dict[str, list[dict[str, Any]]]:
        """Performs a full system hardware scan and builds a hierarchical tree."""
        # Check cache
        if not force and (time.time() - self.last_scan_time < self.cache_duration) and self.device_tree:
            return self.device_tree

        self.trace_log = [] # Reset trace on fresh scan
        self.log_trace(f"Initiating Discovery Scan (Force={force}, AudioProbe={'Yes' if audio_engine else 'No'})")
        start_time = time.time()

        raw_inventory = []
        tree = {cat: [] for cat in self.categories}
        tree["Other devices"] = []

        try:
            # Direct WMI query for PnP Entities - OPTIMIZED query
            w = self._get_wmi()
            if not w:
                raise Exception("WMI service unavailable (COM initialization failed)")

            self.log_trace("WMI Connection Established. Enumerating Win32_PnPEntity...")

            pnp_entities = w.Win32_PnPEntity()
            self.log_trace(f"WMI returned {len(pnp_entities)} raw PnP entities.")

            for dev in pnp_entities:
                name = str(dev.Name) if dev.Name else "Unknown Device"
                hw_id = dev.HardwareID[0] if dev.HardwareID and len(dev.HardwareID) > 0 else "N/A"
                status = dev.Status
                service = dev.Service
                manufacturer = dev.Manufacturer

                device_info = {
                    "name": name,
                    "hw_id": hw_id,
                    "status": status,
                    "service": service,
                    "manufacturer": manufacturer
                }

                raw_inventory.append(device_info)

                # Categorization Logic
                assigned = False
                for cat, keywords in self.categories.items():
                    if any(k.lower() in name.lower() for k in keywords):
                        tree[cat].append(device_info)
                        self.log_trace(f"Matched '{name}' -> Category: {cat}")
                        assigned = True
                        break

                if not assigned and any(k.lower() in name.lower() for k in ["USB", "HID", "PCI"]):
                     tree["Other devices"].append(device_info)

            # --- Audio Health Probing ---
            if audio_engine and tree.get("Audio inputs and outputs"):
                self.log_trace("Initiating Audio Health Probing for discovered microphones...")
                # Refresh engine's device list to match current system state
                audio_engine.refresh_devices()

                for mic in tree["Audio inputs and outputs"]:
                    # Match by name to find PortAudio index
                    sd_mic = next((d for d in audio_engine.devices if d["name"] == mic["name"]), None)
                    if sd_mic:
                        self.log_trace(f"Probing {mic['name']} (Index {sd_mic['index']})...")
                        health = audio_engine.verify_device_health(sd_mic["index"])
                        mic["health"] = health
                        self.log_trace(f"Health Result: {health['status']} (RMS: {health['rms']:.6f})")
                    else:
                        mic["health"] = {"status": "PORTAUDIO_MISSING", "rms": 0}
                        self.log_trace(f"Could not find PortAudio index for {mic['name']}", level="WARNING")

        except Exception as e:
            self.log_trace(f"Sensory Discovery Fatal Error: {e}", level="ERROR")
            logger.error(f"Sensory Discovery Failed: {e}")

        self.inventory = raw_inventory
        self.device_tree = tree
        self.last_scan_time = time.time()

        scan_time = time.time() - start_time
        self.log_trace(f"Discovery Complete in {scan_time:.2f}s. Indexed {len(raw_inventory)} devices.")
        return tree

    def get_diagnostics(self) -> dict[str, Any]:
        """Provides a high-level health report of sensory hardware."""
        report = {
            "status": "HEALTHY",
            "device_count": len(self.inventory),
            "conflicts": []
        }

        for dev in self.inventory:
            # Detect LibUSB/UVC conflicts (e.g. Orbit) - Only if device is ACTIVE
            if "Orbit" in dev["name"] and "libusb" in str(dev["service"]).lower() and dev["status"] == "OK":
                report["status"] = "CONFLICT"
                report["conflicts"].append({
                    "device": dev["name"],
                    "reason": "Orbit is in LIBUSB mode (Blocks video). Restore 'USB Video Class' driver via Device Manager -> Update Driver -> Browse -> Let me pick -> USB Video Device. This restores OpenCV compatibility while keeping motor control via Native XU."
                })

            # Detect hardware errors
            if dev["status"] != "OK":
                if dev["name"] in self.suppressed_devices:
                    self.log_trace(f"Ignoring suppressed device error: {dev['name']}")
                    continue

                report["status"] = "DEGRADED"
                report["conflicts"].append({
                    "device": dev["name"],
                    "reason": f"System reported status: {dev['status']}"
                })

        return report

    def run_device_audit(self, device_name: str | None = None) -> dict[str, Any]:
        """
        Runs a comprehensive audit on a specific device or all imaging devices.
        Returns audit report with device ID, capabilities, and profile data.
        """
        from datetime import datetime

        from .device_profile import KNOWN_DEVICES, CameraCapabilities, DeviceAuditReport, PTZRanges

        self.log_trace(f"Running device audit for: {device_name or 'ALL IMAGING'}")

        # Force a fresh discovery
        tree = self.run_discovery(force=True)
        imaging_devices = tree.get("Imaging devices", [])

        audits = []

        for dev in imaging_devices:
            if device_name and device_name.lower() not in dev["name"].lower():
                continue

            # Extract VID/PID from device_id
            vid, pid = self._parse_vid_pid(dev.get("device_id", ""))
            device_id = f"{vid}_{pid}" if vid and pid else dev.get("device_id", "unknown")

            # Check if known device
            known = KNOWN_DEVICES.get(device_id.lower(), {})

            # Build capabilities
            caps = CameraCapabilities(
                pan=known.get("capabilities", CameraCapabilities()).pan if known else False,
                tilt=known.get("capabilities", CameraCapabilities()).tilt if known else False,
                zoom=known.get("capabilities", CameraCapabilities()).zoom if known else False,
                motor_control=known.get("capabilities", CameraCapabilities()).motor_control if known else False,
                face_detection="Orbit" in dev["name"] or "Sphere" in dev["name"]
            )

            # Build PTZ ranges
            ptz = known.get("ptz_ranges", PTZRanges()) if known else PTZRanges()

            audit = DeviceAuditReport(
                timestamp=datetime.now().isoformat(),
                device_id=device_id,
                name=dev["name"],
                manufacturer=dev.get("manufacturer") or ("Logitech" if "046d" in device_id else "Unknown"),
                driver_name=dev.get("service", ""),
                capabilities=caps,
                ptz_ranges=ptz,
                status=dev["status"],
                notes=["Discovered via WMI scan"] + (["Known device with pre-defined profile"] if known else [])
            )

            audits.append(audit)
            self.log_trace(f"Audit complete: {audit.name} [{audit.device_id}] - Caps: pan={caps.pan}, tilt={caps.tilt}")

        return {
            "timestamp": datetime.now().isoformat(),
            "device_count": len(audits),
            "audits": audits
        }

    def _parse_vid_pid(self, device_id: str) -> tuple:
        """Extracts VID and PID from a Windows device ID string."""
        vid = pid = None
        device_id_upper = device_id.upper()

        if "VID_" in device_id_upper:
            try:
                vid_start = device_id_upper.index("VID_") + 4
                vid = device_id_upper[vid_start:vid_start+4].lower()
            except Exception:
                pass

        if "PID_" in device_id_upper:
            try:
                pid_start = device_id_upper.index("PID_") + 4
                pid = device_id_upper[pid_start:pid_start+4].lower()
            except Exception:
                pass

        return (vid, pid)

    def build_device_profile(self, audit) -> Any:
        """
        Creates or updates a device profile from an audit report.
        Saves to profile manager and RAG.
        """
        from .device_profile import profile_manager
        from .vector_connector import VectorMemoryConnector

        # Check if profile exists
        existing = profile_manager.get_profile(audit.device_id)

        if existing:
            # Update existing profile
            existing.last_seen = audit.timestamp
            existing.audit_history.append(audit.timestamp)
            profile_manager.save_profile(existing)
            self.log_trace(f"Updated existing profile: {existing.name}")
            return existing
        else:
            # Create new profile
            profile = profile_manager.create_profile_from_audit(audit)
            profile_manager.save_profile(profile)

            # Add to RAG
            try:
                rag = VectorMemoryConnector()
                rag.add_device_profile(profile.device_id, {
                    "name": profile.name,
                    "manufacturer": profile.manufacturer,
                    "capabilities": {
                        "pan": profile.capabilities.pan,
                        "tilt": profile.capabilities.tilt,
                        "zoom": profile.capabilities.zoom,
                        "motor_control": profile.capabilities.motor_control
                    }
                })
                self.log_trace(f"Added new profile to RAG: {profile.name}")
            except Exception as e:
                self.log_trace(f"RAG ingestion failed: {e}", level="ERROR")

            return profile

    def on_device_connected(self, callback=None):
        """
        Handles a new device connection event.
        Runs audit and builds profile automatically.
        """
        self.log_trace("New device connected - Running automatic audit")

        # Run full audit
        audit_result = self.run_device_audit()

        # Build profiles for all discovered devices
        profiles = []
        for audit in audit_result.get("audits", []):
            profile = self.build_device_profile(audit)
            profiles.append(profile)

        if callback:
            callback(profiles)

        return profiles

# Global Instance
sensory_intel = SensoryIntelligence()

if __name__ == "__main__":
    # Test Output
    logging.basicConfig(level=logging.INFO)
    intel = SensoryIntelligence()
    tree = intel.run_discovery()
    for cat, devices in tree.items():
        if devices:
            print(f"\n[{cat}]")
            for d in devices:
                print(f"  |-- {d['name']} ({d['status']})")

    # Test device audit
    print("\n--- Device Audit ---")
    audit_result = intel.run_device_audit()
    for audit in audit_result.get("audits", []):
        print(f"  {audit.name} [{audit.device_id}]")
        print(f"    Pan: {audit.capabilities.pan}, Tilt: {audit.capabilities.tilt}")

