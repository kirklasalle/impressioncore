import ctypes
import os

class SimpleSkeleton(ctypes.Structure):
    _fields_ = [
        ("Head", ctypes.c_float * 3),
        ("Neck", ctypes.c_float * 3),
        ("HandLeft", ctypes.c_float * 3),
        ("HandRight", ctypes.c_float * 3),
        ("IsTracked", ctypes.c_int)
    ]

class SkeletonTracker:
    def __init__(self):
        self._dll = None
        self._load_dll()

    def _load_dll(self):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            dll_path = os.path.join(base_path, "orbos_kinect_bridge.dll")
            
            if not os.path.exists(dll_path):
                raise RuntimeError(f"Native bridge DLL not found at {dll_path}")
            
            self._dll = ctypes.CDLL(dll_path)
            
            # Signature: int GetSkeleton(void* pSensorPtr, SimpleSkeleton* outSkeleton, int timeoutMs)
            self._dll.GetSkeleton.argtypes = [ctypes.c_void_p, ctypes.POINTER(SimpleSkeleton), ctypes.c_int]
            self._dll.GetSkeleton.restype = ctypes.c_int
            
        except Exception as e:
            print(f"Failed to load native skeleton tracking: {e}")
            self._dll = None

    def get_skeleton_from_frame(self, frame):
        """Extracts the first tracked skeleton from a NUI_SKELETON_FRAME."""
        for i in range(6):
            data = frame.SkeletonData[i]
            if data.eTrackingState == 2: # NUI_SKELETON_TRACKED
                # Joints index: Head=3, ShoulderCenter=2, Spine=1, HipCenter=0
                # Hands: HandLeft=7, HandRight=11
                # Position is Vector4 (x,y,z,w)
                return {
                    "head": (data.SkeletonPositions[3].x, data.SkeletonPositions[3].y, data.SkeletonPositions[3].z),
                    "neck": (data.SkeletonPositions[2].x, data.SkeletonPositions[2].y, data.SkeletonPositions[2].z),
                    "hand_left": (data.SkeletonPositions[7].x, data.SkeletonPositions[7].y, data.SkeletonPositions[7].z),
                    "hand_right": (data.SkeletonPositions[11].x, data.SkeletonPositions[11].y, data.SkeletonPositions[11].z)
                }
        return None

    def draw_skeleton(self, image, skeleton):
        """Draws basic joints onto the image."""
        import cv2
        h, w = image.shape[:2]
        
        def skeleton_to_pixel(pos):
            # Skeleton coords are -1.0 to 1.0 (float)
            # Center is 0,0. 
            # X: left is negative, right is positive
            # Y: up is positive, down is negative
            px = int((pos[0] + 1.0) * 0.5 * w)
            py = int((1.0 - pos[1]) * 0.5 * h)
            return (px, py)

        joints = ["head", "neck", "hand_left", "hand_right"]
        colors = [(0, 0, 255), (0, 255, 255), (0, 255, 0), (255, 0, 0)]
        
        for i, joint in enumerate(joints):
            pos = skeleton.get(joint)
            if pos:
                pt = skeleton_to_pixel(pos)
                cv2.circle(image, pt, 8, colors[i], -1)
                cv2.putText(image, joint.upper(), (pt[0]+10, pt[1]), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # Draw bones
        if "head" in skeleton and "neck" in skeleton:
            cv2.line(image, skeleton_to_pixel(skeleton["head"]), 
                     skeleton_to_pixel(skeleton["neck"]), (255, 255, 255), 2)
