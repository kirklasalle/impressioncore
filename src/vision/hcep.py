"""
HCEP - Human Conversation Eye Points
====================================
Kirk LaSalle's theory on analyzing eye/gaze position and head orientation
to infer emotional and cognitive states during human-computer interaction.

Reference: docs/codebase/HECP/HCEP_using_face_tracking_data.pdf
- Third-eye (forehead): Spiritual, conscience mind
- Right eye region: Creativity, emotion
- Left eye region: Logic, reason
- Mouth/chin: Personal connection, truth
- Upper regions: Positivity, happiness, hope
- Lower regions: Tiredness, negativity, sadness
- Far upper (looking up-left): Memories, constructing thought
- Far lower (looking down-right): Shyness, fear, deception
- Chest/heart: Caring, love, emotion (body tracking)

Integration:
- Triggered when facial recognition succeeds
- Uses face tracking data (pitch, yaw, roll) from Kinect
- Maps head pose to inferred cognitive/emotional state

Author: ImpressionCore Team
Created: January 2026
"""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto

import numpy as np

logger = logging.getLogger(__name__)


# ============================================================================
# HCEP ENUMS & DATA STRUCTURES
# ============================================================================

class GazeRegion(Enum):
    """Gaze direction regions based on HCEP model"""
    CENTER = auto()           # Direct eye contact
    UPPER = auto()            # Looking up - positivity, hope
    LOWER = auto()            # Looking down - tiredness, sadness
    LEFT = auto()             # Looking left - logic, reason (viewer's right)
    RIGHT = auto()            # Looking right - creativity, emotion (viewer's left)
    UPPER_LEFT = auto()       # Up-left - memory recall, constructed thought
    UPPER_RIGHT = auto()      # Up-right - visual imagination
    LOWER_LEFT = auto()       # Down-left - internal dialogue, feelings
    LOWER_RIGHT = auto()      # Down-right - kinesthetic, shyness, deception


class CognitiveState(Enum):
    """Inferred cognitive states from HCEP analysis"""
    ENGAGED = auto()          # Direct attention, focused
    THINKING = auto()         # Processing information
    REMEMBERING = auto()      # Accessing memories
    IMAGINING = auto()        # Creative visualization
    ANALYZING = auto()        # Logical processing
    EMOTIONAL = auto()        # Emotional response
    DECEPTIVE = auto()        # Potential deception cues
    TIRED = auto()            # Fatigue indicators
    POSITIVE = auto()         # Positive affect
    NEGATIVE = auto()         # Negative affect
    UNKNOWN = auto()          # Cannot determine


class EmotionalValence(Enum):
    """Emotional valence (positive/negative/neutral)"""
    POSITIVE = 1
    NEUTRAL = 0
    NEGATIVE = -1


@dataclass
class HCEPReading:
    """Single HCEP analysis result"""
    timestamp: float
    identity: str  # Recognized person (from facial recognition)

    # Head pose data
    pitch: float  # Nodding (positive = up, negative = down)
    yaw: float    # Turning (positive = right, negative = left)
    roll: float   # Tilting (positive = right shoulder, negative = left)

    # Derived analysis
    gaze_region: GazeRegion
    cognitive_state: CognitiveState
    emotional_valence: EmotionalValence
    confidence: float  # 0.0 to 1.0

    # Additional signals
    blink_detected: bool = False
    micro_expression: str | None = None

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "identity": self.identity,
            "pose": {"pitch": self.pitch, "yaw": self.yaw, "roll": self.roll},
            "gaze_region": self.gaze_region.name,
            "cognitive_state": self.cognitive_state.name,
            "emotional_valence": self.emotional_valence.name,
            "confidence": self.confidence
        }


@dataclass
class HCEPSession:
    """Tracks HCEP readings for a session with one identity"""
    identity: str
    start_time: float
    readings: list[HCEPReading] = field(default_factory=list)

    @property
    def duration(self) -> float:
        return time.time() - self.start_time

    @property
    def dominant_state(self) -> CognitiveState:
        """Most common cognitive state in session"""
        if not self.readings:
            return CognitiveState.UNKNOWN
        states = [r.cognitive_state for r in self.readings]
        return max(set(states), key=states.count)

    @property
    def average_valence(self) -> float:
        """Average emotional valence (-1 to +1)"""
        if not self.readings:
            return 0.0
        return np.mean([r.emotional_valence.value for r in self.readings])


# ============================================================================
# HCEP ANALYZER
# ============================================================================

class HCEPAnalyzer:
    """
    Human Communication Eye Protocol Analyzer.

    Analyzes face tracking data to infer cognitive and emotional states
    based on gaze direction and head pose.
    """

    # Thresholds for gaze region detection (degrees)
    PITCH_THRESHOLD = 10.0  # Up/down threshold
    YAW_THRESHOLD = 15.0    # Left/right threshold
    ROLL_THRESHOLD = 8.0    # Tilt threshold

    # Gaze region to cognitive state mapping
    REGION_STATE_MAP = {
        GazeRegion.CENTER: CognitiveState.ENGAGED,
        GazeRegion.UPPER: CognitiveState.POSITIVE,
        GazeRegion.LOWER: CognitiveState.TIRED,
        GazeRegion.LEFT: CognitiveState.ANALYZING,      # Logic/reason
        GazeRegion.RIGHT: CognitiveState.EMOTIONAL,     # Creativity/emotion
        GazeRegion.UPPER_LEFT: CognitiveState.REMEMBERING,  # Memory recall
        GazeRegion.UPPER_RIGHT: CognitiveState.IMAGINING,   # Visual creation
        GazeRegion.LOWER_LEFT: CognitiveState.THINKING,     # Internal dialogue
        GazeRegion.LOWER_RIGHT: CognitiveState.DECEPTIVE,   # Kinesthetic/avoidance
    }

    # Gaze region to emotional valence
    REGION_VALENCE_MAP = {
        GazeRegion.CENTER: EmotionalValence.NEUTRAL,
        GazeRegion.UPPER: EmotionalValence.POSITIVE,
        GazeRegion.LOWER: EmotionalValence.NEGATIVE,
        GazeRegion.LEFT: EmotionalValence.NEUTRAL,
        GazeRegion.RIGHT: EmotionalValence.NEUTRAL,
        GazeRegion.UPPER_LEFT: EmotionalValence.NEUTRAL,
        GazeRegion.UPPER_RIGHT: EmotionalValence.POSITIVE,
        GazeRegion.LOWER_LEFT: EmotionalValence.NEUTRAL,
        GazeRegion.LOWER_RIGHT: EmotionalValence.NEGATIVE,
    }

    def __init__(self):
        self.sessions: dict[str, HCEPSession] = {}
        self.callbacks: list[Callable[[HCEPReading], None]] = []
        self._last_reading: HCEPReading | None = None

        logger.info("HCEP Analyzer initialized")

    def analyze(self,
                identity: str,
                pitch: float,
                yaw: float,
                roll: float,
                confidence: float = 1.0) -> HCEPReading:
        """
        Analyze head pose data and produce HCEP reading.

        Args:
            identity: Recognized identity from facial recognition
            pitch: Head pitch (nod) in degrees
            yaw: Head yaw (turn) in degrees
            roll: Head roll (tilt) in degrees
            confidence: Recognition confidence (0-1)

        Returns:
            HCEPReading with analysis results
        """
        # Determine gaze region
        gaze_region = self._classify_gaze_region(pitch, yaw)

        # Map to cognitive state and valence
        cognitive_state = self.REGION_STATE_MAP.get(gaze_region, CognitiveState.UNKNOWN)
        emotional_valence = self.REGION_VALENCE_MAP.get(gaze_region, EmotionalValence.NEUTRAL)

        # Apply roll adjustment (head tilt can indicate interest or confusion)
        if abs(roll) > self.ROLL_THRESHOLD:
            if roll > 0:  # Right tilt - often curiosity
                cognitive_state = CognitiveState.THINKING
            else:  # Left tilt - often skepticism
                emotional_valence = EmotionalValence.NEGATIVE

        reading = HCEPReading(
            timestamp=time.time(),
            identity=identity,
            pitch=pitch,
            yaw=yaw,
            roll=roll,
            gaze_region=gaze_region,
            cognitive_state=cognitive_state,
            emotional_valence=emotional_valence,
            confidence=confidence
        )

        # Update session
        self._update_session(identity, reading)

        # Notify callbacks
        for callback in self.callbacks:
            try:
                callback(reading)
            except Exception as e:
                logger.error(f"HCEP callback error: {e}")

        self._last_reading = reading
        return reading

    def _classify_gaze_region(self, pitch: float, yaw: float) -> GazeRegion:
        """Classify gaze direction into a region"""
        is_up = pitch > self.PITCH_THRESHOLD
        is_down = pitch < -self.PITCH_THRESHOLD
        is_left = yaw < -self.YAW_THRESHOLD  # Negative yaw = looking left
        is_right = yaw > self.YAW_THRESHOLD  # Positive yaw = looking right

        if is_up and is_left:
            return GazeRegion.UPPER_LEFT
        elif is_up and is_right:
            return GazeRegion.UPPER_RIGHT
        elif is_down and is_left:
            return GazeRegion.LOWER_LEFT
        elif is_down and is_right:
            return GazeRegion.LOWER_RIGHT
        elif is_up:
            return GazeRegion.UPPER
        elif is_down:
            return GazeRegion.LOWER
        elif is_left:
            return GazeRegion.LEFT
        elif is_right:
            return GazeRegion.RIGHT
        else:
            return GazeRegion.CENTER

    def _update_session(self, identity: str, reading: HCEPReading):
        """Update or create session for identity"""
        if identity not in self.sessions:
            self.sessions[identity] = HCEPSession(
                identity=identity,
                start_time=time.time()
            )
        self.sessions[identity].readings.append(reading)

    def get_session(self, identity: str) -> HCEPSession | None:
        """Get session for an identity"""
        return self.sessions.get(identity)

    def get_last_reading(self) -> HCEPReading | None:
        """Get most recent reading"""
        return self._last_reading

    def add_callback(self, callback: Callable[[HCEPReading], None]):
        """Add callback to be notified on new readings"""
        self.callbacks.append(callback)

    def get_state_description(self, reading: HCEPReading) -> str:
        """Get human-readable description of current state"""
        descriptions = {
            CognitiveState.ENGAGED: "directly engaged, focused attention",
            CognitiveState.THINKING: "processing internally, considering",
            CognitiveState.REMEMBERING: "recalling memories, accessing past experience",
            CognitiveState.IMAGINING: "visualizing, creative thinking",
            CognitiveState.ANALYZING: "logical analysis, reasoning",
            CognitiveState.EMOTIONAL: "emotional response, feeling-based",
            CognitiveState.DECEPTIVE: "potential discomfort or avoidance",
            CognitiveState.TIRED: "fatigue or low energy indicators",
            CognitiveState.POSITIVE: "positive affect, optimistic",
            CognitiveState.NEGATIVE: "negative affect, pessimistic",
            CognitiveState.UNKNOWN: "state unclear",
        }

        state_desc = descriptions.get(reading.cognitive_state, "unknown state")
        valence_word = {
            EmotionalValence.POSITIVE: "positive",
            EmotionalValence.NEUTRAL: "neutral",
            EmotionalValence.NEGATIVE: "negative"
        }[reading.emotional_valence]

        return f"{reading.identity} appears {state_desc} (valence: {valence_word})"


# ============================================================================
# KINECT INTEGRATION
# ============================================================================

class KinectHCEPIntegration:
    """
    Integrates HCEP with Kinect face tracking and facial recognition.
    Automatically triggers HCEP analysis when a face is recognized.
    """

    def __init__(self, kinect_controller, face_identity_manager):
        """
        Args:
            kinect_controller: KinectController instance
            face_identity_manager: FaceIdentityManager instance
        """
        self.kinect = kinect_controller
        self.identity_manager = face_identity_manager
        self.analyzer = HCEPAnalyzer()

        self._running = False
        self._last_identity = None

        logger.info("Kinect HCEP Integration initialized")

    def process_frame(self, color_frame: np.ndarray) -> HCEPReading | None:
        """
        Process a single frame through the full pipeline:
        1. Face tracking (get head pose)
        2. Facial recognition (identify person)
        3. HCEP analysis (if recognized)

        Args:
            color_frame: BGR color frame from Kinect

        Returns:
            HCEPReading if successful, None if no face or unknown
        """
        # Step 1: Get face tracking data
        face_data = self.kinect.get_face_data(color_frame)
        if face_data is None or not face_data.is_tracked:
            return None

        # Step 2: Identify the person
        name, confidence = self.identity_manager.identify(color_frame)

        if name == "Unknown" or confidence < 0.5:
            return None

        self._last_identity = name

        # Step 3: Run HCEP analysis
        reading = self.analyzer.analyze(
            identity=name,
            pitch=face_data.pitch,
            yaw=face_data.yaw,
            roll=face_data.roll,
            confidence=confidence
        )

        return reading

    def on_recognition_success(self, callback: Callable[[HCEPReading], None]):
        """Register callback for successful recognition + HCEP reading"""
        self.analyzer.add_callback(callback)

    def get_current_state(self) -> str | None:
        """Get human-readable current state description"""
        reading = self.analyzer.get_last_reading()
        if reading:
            return self.analyzer.get_state_description(reading)
        return None


# ============================================================================
# DEMO / TEST
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print(" HCEP - Human Communication Eye Protocol")
    print("=" * 60)

    analyzer = HCEPAnalyzer()

    # Simulate some readings
    test_cases = [
        ("Alice", 0, 0, 0),         # Center - Engaged
        ("Alice", 15, 0, 0),        # Up - Positive
        ("Alice", -15, 0, 0),       # Down - Tired
        ("Alice", 0, -20, 0),       # Left - Analyzing
        ("Alice", 0, 20, 0),        # Right - Emotional
        ("Alice", 15, -20, 0),      # Up-Left - Remembering
        ("Alice", 15, 20, 0),       # Up-Right - Imagining
        ("Alice", -15, -20, 0),     # Down-Left - Thinking
        ("Alice", -15, 20, 0),      # Down-Right - Deceptive
    ]

    print("\nTest Analysis Results:")
    print("-" * 60)

    for identity, pitch, yaw, roll in test_cases:
        reading = analyzer.analyze(identity, pitch, yaw, roll)
        desc = analyzer.get_state_description(reading)
        print(f"Pose ({pitch:+3.0f}, {yaw:+3.0f}, {roll:+3.0f}) -> {desc}")

    # Session summary
    session = analyzer.get_session("Alice")
    if session:
        print(f"\nSession Summary for {session.identity}:")
        print(f"  Duration: {session.duration:.1f}s")
        print(f"  Dominant State: {session.dominant_state.name}")
        print(f"  Average Valence: {session.average_valence:+.2f}")
