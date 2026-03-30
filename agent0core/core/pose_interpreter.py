"""
Pose Interpreter - Semantic Body Language Analysis
Created: January 16, 2026

Translates raw Kinect skeletal joint coordinates into semantic labels.
"""

import math
from typing import Any


class PoseInterpreter:
    """
    Analyzes skeleton joints to determine postures and gestures.
    """

    def __init__(self):
        self.last_pose = None
        self.confidence_threshold = 0.5

    def analyze(self, skeleton_data: dict[str, Any]) -> list[str]:
        """
        Analyzes joints and returns a list of active pose tags.

        Args:
            skeleton_data: Dict containing 'joints' as returned by KinectConnector.serialize_skeleton

        Returns:
            List of semantic labels (e.g. ["STANDING", "WAVING"])
        """
        if not skeleton_data or "joints" not in skeleton_data:
            return []

        joints = skeleton_data["joints"]
        poses = []

        # 1. Vitality check (are we tracking?)
        if not skeleton_data.get("tracked", False):
            return ["OFF_CAMERA"]

        # 2. Sitting vs Standing
        # Simple heuristic: Hip height relative to knee/ankle and verticality
        hip = joints.get("HIP_CENTER")
        knee_l = joints.get("KNEE_LEFT")
        knee_r = joints.get("KNEE_RIGHT")
        joints.get("ANKLE_LEFT")
        joints.get("ANKLE_RIGHT")
        head = joints.get("HEAD")

        if all([hip, knee_l, knee_r]):
            # Standing: Hip is significantly higher than knees
            # In Kinect meters, > 0.4m usually means standing/leaning
            # Also check if hip.y and knee.y are similar (sitting)
            hip_knee_diff = (hip["y"] - (knee_l["y"] + knee_r["y"]) / 2)

            if hip_knee_diff < 0.2: # Hips and knees are level
                poses.append("SITTING")
            elif hip_knee_diff > 0.35:
                poses.append("STANDING")
            else:
                poses.append("CROUCHING_OR_LEANING")

        # 3. Gestures: Waving
        hand_l = joints.get("HAND_LEFT")
        hand_r = joints.get("HAND_RIGHT")

        if head:
            # Prequisite joint fetch for gestures
            shoulder_l = joints.get("SHOULDER_LEFT")
            shoulder_r = joints.get("SHOULDER_RIGHT")

            # ARM_RAISED: Hand above shoulder
            if shoulder_l and hand_l and hand_l["y"] > shoulder_l["y"]:
                poses.append("ARM_RAISED_LEFT")
            if shoulder_r and hand_r and hand_r["y"] > shoulder_r["y"]:
                poses.append("ARM_RAISED_RIGHT")

            # WAVING: Hand above head OR high vitality arm raised
            if hand_l and hand_l["y"] > head["y"]:
                poses.append("WAVING_LEFT")
            if hand_r and hand_r["y"] > head["y"]:
                poses.append("WAVING_RIGHT")

        # 4. Arms Crossed
        # Heuristic: Hands/Wrists are close to opposite shoulders
        shoulder_l = joints.get("SHOULDER_LEFT")
        shoulder_r = joints.get("SHOULDER_RIGHT")
        wrist_l = joints.get("WRIST_LEFT")
        wrist_r = joints.get("WRIST_RIGHT")

        if all([shoulder_l, shoulder_r, wrist_l, wrist_r]):
            dist_l = self._dist3d(wrist_l, shoulder_r)
            dist_r = self._dist3d(wrist_r, shoulder_l)
            if dist_l < 0.25 and dist_r < 0.25:
                poses.append("ARMS_CROSSED")

        # 5. Engagement (Leaning Forward)
        # Check Z distance of spine relative to hips
        spine = joints.get("SPINE")
        if spine and hip:
            # Kinect Z is forward (usually positive away from camera)
            # If spine is significantly closer than hip, user is leaning forward
            lean_depth = hip["z"] - spine["z"]
            if lean_depth > 0.15:
                poses.append("LEANING_FORWARD_ENGAGED")
            elif lean_depth < -0.1:
                poses.append("LEANING_BACK")

        return poses

    def _dist3d(self, p1: dict[str, float], p2: dict[str, float]) -> float:
        """3D Euclidean distance."""
        return math.sqrt(
            (p1["x"] - p2["x"])**2 +
            (p1["y"] - p2["y"])**2 +
            (p1["z"] - p2["z"])**2
        )

    def get_summary_string(self, poses: list[str]) -> str:
        """Friendly string for the Agent's prompt."""
        if not poses: return "Presence detected, but posture is unclear."
        if "OFF_CAMERA" in poses: return "The user is currently out of the visual field."

        return "The user appears to be " + ", ".join(poses).lower().replace("_", " ") + "."
