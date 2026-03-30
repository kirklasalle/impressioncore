"""
Detection module for Face and Motion detection.
"""
import cv2
import logging
import numpy as np
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

class Detector:
    """
    Combined Face and Motion detector using OpenCV.
    """
    
    def __init__(self, face_cascade_path: Optional[str] = None):
        """
        Initialize the detector.
        
        Args:
            face_cascade_path: Path to Haar Cascade XML for faces. 
                               If None, use default OpenCV path.
        """
        # Load Face Cascade
        if face_cascade_path is None:
            # Try to find default OpenCV cascade
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        
        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        if self.face_cascade.empty():
            logger.error(f"Failed to load face cascade from {face_cascade_path}")
            
        # Motion detection state
        self._prev_frame = None
        self.motion_threshold = 25
        self.min_area = 500

    def detect(self, frame: np.ndarray) -> Tuple[List, List]:
        faces = self.detect_faces(frame)
        motion = self.detect_motion(frame)
        return faces, motion

    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in the frame.
        
        Returns:
            List of (x, y, w, h) rectangles.
        """
        if self.face_cascade.empty():
            return []
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        return faces.tolist() if len(faces) > 0 else []

    def detect_motion(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect motion in the frame relative to the previous frame.
        
        Returns:
            List of (x, y, w, h) rectangles where motion was detected.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self._prev_frame is None:
            self._prev_frame = gray
            return []
            
        # Compute absolute difference
        frame_delta = cv2.absdiff(self._prev_frame, gray)
        thresh = cv2.threshold(frame_delta, self.motion_threshold, 255, cv2.THRESH_BINARY)[1]
        
        # Dilate thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion_boxes = []
        for c in cnts:
            if cv2.contourArea(c) < self.min_area:
                continue
            (x, y, w, h) = cv2.boundingRect(c)
            motion_boxes.append((x, y, w, h))
            
        self._prev_frame = gray
        return motion_boxes

    def draw_detections(self, frame: np.ndarray, faces: List, motion: List) -> np.ndarray:
        """
        Scale and draw detections on a copy of the frame with a sleek, enhanced aesthetic.
        """
        out = frame.copy()
        
        # Drawing motion (Green/Looking)
        for (x, y, w, h) in motion:
            color = (0, 255, 0) # Vibrant Green
            # Draw standard box
            cv2.rectangle(out, (x, y), (x+w, y+h), color, 1)
            # Add small label at bottom right
            cv2.putText(out, "SEARCHING...", (x, y+h+12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)
            
        # Drawing faces (Blue/Cyan/Grabbed) - DRAW AFTER MOTION TO BE ON TOP
        for (x, y, w, h) in faces:
            color = (255, 200, 0) # Cyan-Blue
            # Main box (thin)
            cv2.rectangle(out, (x, y), (x+w, y+h), color, 1)
            
            # Corner accents (thicker)
            d = int(min(w, h) * 0.15) # 15% of size
            thickness = 2
            # TL
            cv2.line(out, (x, y), (x+d, y), color, thickness)
            cv2.line(out, (x, y), (x, y+d), color, thickness)
            # TR
            cv2.line(out, (x+w, y), (x+w-d, y), color, thickness)
            cv2.line(out, (x+w, y), (x+w, y+d), color, thickness)
            # BL
            cv2.line(out, (x, y+h), (x+d, y+h), color, thickness)
            cv2.line(out, (x, y+h), (x, y+h-d), color, thickness)
            # BR
            cv2.line(out, (x+w, y+h), (x+w-d, y+h), color, thickness)
            cv2.line(out, (x+w, y+h), (x+w, y+h-d), color, thickness)
            
            # Label background
            cv2.rectangle(out, (x, y-18), (x+80, y), color, -1)
            cv2.putText(out, "TARGET", (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)
            
        return out
