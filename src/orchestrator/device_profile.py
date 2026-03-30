"""
Camera Device Profile System

Manages camera device profiles with capabilities detection, calibration storage,
and RAG integration for documentation and working files.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Default paths
PROFILES_DIR = Path(__file__).parent.parent / "config" / "camera_profiles"
PROFILES_INDEX = PROFILES_DIR / "profiles.json"


@dataclass
class CameraCapabilities:
    """Hardware capabilities of a camera device."""
    pan: bool = False
    tilt: bool = False
    zoom: bool = False
    autofocus: bool = False
    face_detection: bool = False
    motor_control: bool = False
    infrared: bool = False
    depth_sensor: bool = False


@dataclass
class PTZRanges:
    """Pan/Tilt/Zoom ranges for motorized cameras."""
    pan_min: int = 0
    pan_max: int = 0
    tilt_min: int = 0
    tilt_max: int = 0
    zoom_min: int = 0
    zoom_max: int = 0


@dataclass
class CalibrationData:
    """Image calibration settings for a camera."""
    brightness: float = 128.0
    contrast: float = 128.0
    saturation: float = 128.0
    gain: float = 0.0
    exposure: float = -1.0  # Auto
    white_balance: float = -1.0  # Auto
    sharpness: float = 128.0


@dataclass
class DeviceAuditReport:
    """Results of a hardware audit for a camera device."""
    timestamp: str = ""
    device_id: str = ""  # VID_PID format (e.g., "046d_08c2")
    name: str = ""
    manufacturer: str = ""
    driver_name: str = ""
    driver_version: str = ""
    usb_path: str = ""
    capabilities: CameraCapabilities = field(default_factory=CameraCapabilities)
    ptz_ranges: PTZRanges = field(default_factory=PTZRanges)
    resolution_max: tuple[int, int] = (640, 480)
    fps_max: int = 30
    status: str = "OK"
    notes: list[str] = field(default_factory=list)


@dataclass
class CameraDeviceProfile:
    """Complete profile for a camera device, stored in RAG."""
    device_id: str  # VID_PID format
    name: str
    manufacturer: str = "Unknown"
    model: str = ""
    capabilities: CameraCapabilities = field(default_factory=CameraCapabilities)
    ptz_ranges: PTZRanges = field(default_factory=PTZRanges)
    calibration: CalibrationData = field(default_factory=CalibrationData)
    documentation_refs: list[str] = field(default_factory=list)  # RAG document IDs
    notes: str = ""
    first_seen: str = ""
    last_seen: str = ""
    audit_history: list[str] = field(default_factory=list)  # Timestamps of audits
    custom_driver: str | None = None  # Path to custom driver module if needed


class DeviceProfileManager:
    """
    Manages camera device profiles with persistence and RAG integration.
    """

    def __init__(self, profiles_dir: Path = PROFILES_DIR):
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir = self.profiles_dir / "docs"
        self.docs_dir.mkdir(exist_ok=True)
        self.index_path = self.profiles_dir / "profiles.json"
        self._profiles_cache: dict[str, CameraDeviceProfile] = {}
        self._load_index()

    def _load_index(self):
        """Loads the master profile index."""
        if self.index_path.exists():
            try:
                with open(self.index_path) as f:
                    data = json.load(f)
                    for device_id, profile_data in data.get("profiles", {}).items():
                        self._profiles_cache[device_id] = self._dict_to_profile(profile_data)
                logger.info(f"Loaded {len(self._profiles_cache)} camera profiles.")
            except Exception as e:
                logger.error(f"Failed to load profile index: {e}")

    def _save_index(self):
        """Saves the master profile index."""
        try:
            data = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "profiles": {
                    device_id: self._profile_to_dict(profile)
                    for device_id, profile in self._profiles_cache.items()
                }
            }
            with open(self.index_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save profile index: {e}")

    def _profile_to_dict(self, profile: CameraDeviceProfile) -> dict:
        """Converts a profile to a serializable dict."""
        return {
            "device_id": profile.device_id,
            "name": profile.name,
            "manufacturer": profile.manufacturer,
            "model": profile.model,
            "capabilities": asdict(profile.capabilities),
            "ptz_ranges": asdict(profile.ptz_ranges),
            "calibration": asdict(profile.calibration),
            "documentation_refs": profile.documentation_refs,
            "notes": profile.notes,
            "first_seen": profile.first_seen,
            "last_seen": profile.last_seen,
            "audit_history": profile.audit_history,
            "custom_driver": profile.custom_driver
        }

    def _dict_to_profile(self, data: dict) -> CameraDeviceProfile:
        """Converts a dict to a CameraDeviceProfile."""
        return CameraDeviceProfile(
            device_id=data.get("device_id", ""),
            name=data.get("name", "Unknown Camera"),
            manufacturer=data.get("manufacturer", "Unknown"),
            model=data.get("model", ""),
            capabilities=CameraCapabilities(**data.get("capabilities", {})),
            ptz_ranges=PTZRanges(**data.get("ptz_ranges", {})),
            calibration=CalibrationData(**data.get("calibration", {})),
            documentation_refs=data.get("documentation_refs", []),
            notes=data.get("notes", ""),
            first_seen=data.get("first_seen", ""),
            last_seen=data.get("last_seen", ""),
            audit_history=data.get("audit_history", []),
            custom_driver=data.get("custom_driver")
        )

    def get_profile(self, device_id: str) -> CameraDeviceProfile | None:
        """Gets a camera profile by device ID (VID_PID format)."""
        return self._profiles_cache.get(device_id.lower())

    def has_profile(self, device_id: str) -> bool:
        """Checks if a profile exists for the given device ID."""
        return device_id.lower() in self._profiles_cache

    def save_profile(self, profile: CameraDeviceProfile):
        """Saves a camera profile to storage."""
        profile.last_seen = datetime.now().isoformat()
        if not profile.first_seen:
            profile.first_seen = profile.last_seen

        self._profiles_cache[profile.device_id.lower()] = profile
        self._save_index()

        # Also save individual profile file for easy access
        profile_path = self.profiles_dir / f"{profile.device_id.lower()}.json"
        try:
            with open(profile_path, "w") as f:
                json.dump(self._profile_to_dict(profile), f, indent=2)
            logger.info(f"Saved profile for {profile.name} ({profile.device_id})")
        except Exception as e:
            logger.error(f"Failed to save individual profile: {e}")

    def get_all_profiles(self) -> list[CameraDeviceProfile]:
        """Returns all known camera profiles."""
        return list(self._profiles_cache.values())

    def create_profile_from_audit(self, audit: DeviceAuditReport) -> CameraDeviceProfile:
        """Creates a new profile from an audit report."""
        profile = CameraDeviceProfile(
            device_id=audit.device_id,
            name=audit.name,
            manufacturer=audit.manufacturer,
            model=audit.name,
            capabilities=audit.capabilities,
            ptz_ranges=audit.ptz_ranges,
            first_seen=datetime.now().isoformat(),
            last_seen=datetime.now().isoformat(),
            audit_history=[audit.timestamp]
        )
        return profile

    def add_document(self, device_id: str, content: str, doc_type: str = "notes") -> str:
        """
        Adds a document to a device's documentation library.
        Returns the document ID/path.
        """
        device_id = device_id.lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        doc_filename = f"{device_id}_{doc_type}_{timestamp}.txt"
        doc_path = self.docs_dir / doc_filename

        try:
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Update profile with doc reference
            if device_id in self._profiles_cache:
                self._profiles_cache[device_id].documentation_refs.append(str(doc_path))
                self._save_index()

            logger.info(f"Added document {doc_filename} for device {device_id}")
            return str(doc_path)
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return ""

    def get_documents(self, device_id: str) -> list[str]:
        """Gets all document paths for a device."""
        profile = self.get_profile(device_id)
        if profile:
            return profile.documentation_refs
        return []


# Known device profiles (pre-populated)
KNOWN_DEVICES = {
    "046d_08c2": {
        "name": "Logitech QuickCam Orb/Sphere MP",
        "manufacturer": "Logitech",
        "capabilities": CameraCapabilities(
            pan=True, tilt=True, zoom=False,
            autofocus=False, face_detection=True, motor_control=True
        ),
        "ptz_ranges": PTZRanges(
            pan_min=-4480, pan_max=4480,
            tilt_min=-1920, tilt_max=1920
        ),
        "custom_driver": "quickcam_driver"
    },
    "046d_0892": {
        "name": "Logitech QuickCam Orbit",
        "manufacturer": "Logitech",
        "capabilities": CameraCapabilities(
            pan=True, tilt=True, zoom=False,
            autofocus=False, face_detection=True, motor_control=True
        ),
        "ptz_ranges": PTZRanges(
            pan_min=-4480, pan_max=4480,
            tilt_min=-1920, tilt_max=1920
        ),
        "custom_driver": "quickcam_driver"
    },
    "046d_0870": {
        "name": "Logitech QuickCam Connect",
        "manufacturer": "Logitech",
        "capabilities": CameraCapabilities(
            pan=False, tilt=False, zoom=False,
            autofocus=False, face_detection=False, motor_control=False
        ),
        "custom_driver": None
    },
    "046d_08cc": {
        "name": "Logitech QuickCam Orbit/Sphere",
        "manufacturer": "Logitech",
        "capabilities": CameraCapabilities(
            pan=True, tilt=True, zoom=False,
            autofocus=False, face_detection=True, motor_control=True
        ),
        "ptz_ranges": PTZRanges(
            pan_min=-4480, pan_max=4480,
            tilt_min=-1920, tilt_max=1920
        ),
        "custom_driver": "quickcam_driver"
    },
    "046d_0994": {
        "name": "Logitech QuickCam Orbit/Sphere AF",
        "manufacturer": "Logitech",
        "capabilities": CameraCapabilities(
            pan=True, tilt=True, zoom=True,
            autofocus=True, face_detection=True, motor_control=True
        ),
        "ptz_ranges": PTZRanges(
            pan_min=-4480, pan_max=4480,
            tilt_min=-1920, tilt_max=1920,
            zoom_min=1, zoom_max=100
        ),
        "custom_driver": "quickcam_driver"
    },
    "1415_2000": {
        "name": "PlayStation Eye",
        "manufacturer": "Sony",
        "capabilities": CameraCapabilities(
            pan=False, tilt=False, zoom=False,
            autofocus=False, face_detection=False, motor_control=False
        ),
        "custom_driver": "pseye_driver"
    },
    "045e_02ae": {
        "name": "Xbox 360 Kinect",
        "manufacturer": "Microsoft",
        "capabilities": CameraCapabilities(
            pan=False, tilt=True, zoom=False,
            autofocus=False, face_detection=True, motor_control=True,
            infrared=True, depth_sensor=True
        ),
        "ptz_ranges": PTZRanges(
            tilt_min=-27, tilt_max=27  # Degrees
        ),
        "custom_driver": "kinect_connector"
    },
    "045e_02b0": {
        "name": "Xbox 360 Kinect (Audio Array)",
        "manufacturer": "Microsoft",
        "capabilities": CameraCapabilities(),
        "custom_driver": "kinect_audio"
    }
}

# Friendly name patterns for camera identification
# Maps lowercase substrings to device type
FRIENDLY_NAME_PATTERNS = {
    "orbit": ("ORBIT", "QuickCam Orbit/Sphere MP", True),   # (hardware_type, display_name, has_motors)
    "sphere": ("ORBIT", "QuickCam Orbit/Sphere MP", True),
    "quickcam": ("ORBIT", "QuickCam", False),  # Generic QuickCam
    "logitech usb camera (orbit": ("ORBIT", "QuickCam Orbit/Sphere MP", True),
    "logitech usb camera": ("ORBIT", "QuickCam Orbit/Sphere MP", True),  # Generic Logitech USB = likely Orbit
    "usb camera-b4": ("ORBIT", "QuickCam Orbit/Sphere MP", True),  # Known QuickCam firmware string
    "playstation": ("PSEYE", "PlayStation Eye", False),
    "ps3 eye": ("PSEYE", "PlayStation Eye", False),
    "ps eye": ("PSEYE", "PlayStation Eye", False),
    "kinect": ("KINECT", "Xbox 360 Kinect", True),  # Kinect has tilt motor
    "xbox": ("KINECT", "Xbox 360 Kinect", True),
    "nui": ("KINECT", "Xbox 360 Kinect", True),  # NUI = Natural User Interface (Kinect SDK)
}

def identify_camera_by_name(friendly_name: str) -> dict | None:
    """
    Identifies a camera by its friendly name and returns device info.
    Returns dict with 'hardware_type', 'display_name', 'has_motors' if matched.
    """
    if not friendly_name:
        return None

    name_lower = friendly_name.lower()
    for pattern, (hw_type, display_name, has_motors) in FRIENDLY_NAME_PATTERNS.items():
        if pattern in name_lower:
            return {
                "hardware_type": hw_type,
                "display_name": display_name,
                "has_motors": has_motors,
                "matched_pattern": pattern
            }
    return None



# Global instance
profile_manager = DeviceProfileManager()


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)

    # Create a test profile
    test_audit = DeviceAuditReport(
        timestamp=datetime.now().isoformat(),
        device_id="046d_08c2",
        name="Logitech QuickCam Orb/Sphere MP",
        manufacturer="Logitech",
        capabilities=CameraCapabilities(pan=True, tilt=True, motor_control=True),
        ptz_ranges=PTZRanges(pan_min=-4480, pan_max=4480, tilt_min=-1920, tilt_max=1920)
    )

    mgr = DeviceProfileManager()
    profile = mgr.create_profile_from_audit(test_audit)
    mgr.save_profile(profile)

    print(f"Created profile: {profile.name}")
    print(f"Capabilities: pan={profile.capabilities.pan}, tilt={profile.capabilities.tilt}")
