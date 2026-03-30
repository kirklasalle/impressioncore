"""
Face Interpreter - Semantic Facial Expression Analysis
Created: January 16, 2026

Translates facial landmarks, head pose, and emotions into semantic social cues.
"""

from typing import Any

import numpy as np


class FaceInterpreter:
    """
    Analyzes face data to determine focus, expression, and engagement.
    """

    def __init__(self):
        self.focus_threshold = 15.0 # Degrees for "Looking at you"

    def analyze(self, face_data: dict[str, Any]) -> list[str]:
        """
        Analyzes a single face and returns a list of semantic tags.
        """
        if not face_data:
            return []

        tags = []

        # 1. Attention / Focus (Head Pose)
        pose = face_data.get("head_pose")
        if pose:
            yaw = pose.get("yaw", 0)
            pitch = pose.get("pitch", 0)

            if abs(yaw) < self.focus_threshold and abs(pitch) < self.focus_threshold:
                tags.append("LOOKING_AT_YOU")
            else:
                if yaw > self.focus_threshold: tags.append("LOOKING_AWAY_RIGHT")
                elif yaw < -self.focus_threshold: tags.append("LOOKING_AWAY_LEFT")

                if pitch > self.focus_threshold: tags.append("LOOKING_UP")
                elif pitch < -self.focus_threshold: tags.append("LOOKING_DOWN")

        # 2. Emotion
        emotion = face_data.get("emotion")
        if emotion:
            dominant = emotion.get("dominant_emotion")
            conf = emotion.get("dominant_confidence", 0)
            if conf > 0.4:
                tags.append(f"APPEARS_{dominant.upper()}")

        # 3. Facial Landmark Heuristics (Smile/Mouth)
        landmarks = face_data.get("landmarks")
        if landmarks:
            # Smile Detection: mouth width vs facial width
            top_lip = landmarks.get("top_lip")
            bottom_lip = landmarks.get("bottom_lip")
            if top_lip and bottom_lip:
                # Mouth width: dist between left/right corners
                # Mouth center: (top_lip[0]...top_lip[6], bottom_lip[0]...bottom_lip[6])
                mouth_l = top_lip[0]
                mouth_r = top_lip[6]
                mouth_width = np.linalg.norm(np.array(mouth_r) - np.array(mouth_l))

                # Face width (chin points roughly 0 and 16)
                chin = landmarks.get("chin")
                if chin and len(chin) > 16:
                    face_width = np.linalg.norm(np.array(chin[16]) - np.array(chin[0]))
                    if mouth_width / face_width > 0.45:
                        tags.append("SMILING")

                # Mouth Open
                upper_center = top_lip[9] # Bottom of top lip
                lower_center = bottom_lip[9] # Top of bottom lip
                mouth_open_dist = np.linalg.norm(np.array(upper_center) - np.array(lower_center))
                if mouth_open_dist > (mouth_width * 0.15):
                    tags.append("MOUTH_OPEN")

        # 4. Liveness / Blink
        liveness = face_data.get("liveness")
        if liveness:
            checks = liveness.get("checks", {})
            if checks.get("blink", 0) > 0.8:
                tags.append("BLINKING")

        return tags

    def get_summary_string(self, tags: list[str], identity: str = "Unknown") -> str:
        """Friendly summary for the Agent."""
        if not tags: return f"I see {identity}, but cannot determine their expression."

        name = "the user" if identity == "Unknown" else identity
        return f"I see {name}. They are " + ", ".join(tags).lower().replace("_", " ") + "."
