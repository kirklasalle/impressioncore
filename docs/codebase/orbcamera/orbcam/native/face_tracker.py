import ctypes
import os
import struct
import numpy as np

class FaceTracker:
    def __init__(self):
        self._dll = None
        self._is_initialized = False
        self._load_dll()

    def _load_dll(self):
        try:
            # Locate the DLL relative to this file
            base_path = os.path.dirname(os.path.abspath(__file__))
            dll_path = os.path.join(base_path, "orbos_kinect_bridge.dll")
            
            if not os.path.exists(dll_path):
                raise RuntimeError(f"Native bridge DLL not found at {dll_path}")

            # Add Kinect Redist dependencies to search path
            redist_amd64 = r"C:\Program Files\Microsoft SDKs\Kinect\Developer Toolkit v1.8.0\Redist\amd64"
            redist_x86 = r"C:\Program Files\Microsoft SDKs\Kinect\Developer Toolkit v1.8.0\Redist\x86"
            
            if hasattr(os, 'add_dll_directory'):
                if os.path.exists(redist_amd64):
                    os.add_dll_directory(redist_amd64)
                    
            self._dll = ctypes.CDLL(dll_path)
            
            # Signature: int InitFaceTracking(int width, int height, const wchar_t* pszModelPath)
            self._dll.InitFaceTracking.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_wchar_p]
            self._dll.InitFaceTracking.restype = ctypes.c_int
            
            # Signature: void ShutdownFaceTracking()
            self._dll.ShutdownFaceTracking.argtypes = []
            self._dll.ShutdownFaceTracking.restype = None
            
            # Signature: int ProcessFace(void* colorBuffer, void* depthBuffer, float* outPose)
            self._dll.ProcessFace.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_float)]
            self._dll.ProcessFace.restype = ctypes.c_int
            
        except Exception as e:
            print(f"Failed to load native face tracking: {e}")
            self._dll = None

    def initialize(self, width=640, height=480):
        if not self._dll: return False
        
        # Ensure we shut down any previous instance first
        if self._is_initialized:
            self.shutdown()
            
        # Try copying the model files locally to rule out path issues
        import shutil
        redist_src = r"C:\Program Files\Microsoft SDKs\Kinect\Developer Toolkit v1.8.0\Redist\amd64"
        files_to_copy = ["FaceTrackData.dll", "FaceTrackLib.dll"]
        
        for fname in files_to_copy:
            target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
            if not os.path.exists(target_path):
                try:
                    src = os.path.join(redist_src, fname)
                    print(f"Copying {src} to {target_path}...")
                    shutil.copy(src, target_path)
                except Exception as e:
                    print(f"Failed to copy {fname}: {e}")
                    
        # Verify model exists
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FaceTrackData.dll")
        if not os.path.exists(model_path):
             print("WARNING: FaceTrackData.dll missing in local folder!")

        # Pass "current directory" (empty string or .) or full path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Add a trailing slash just in case
        current_dir = os.path.join(current_dir, "")
        
        print(f"Initializing with model path: {current_dir}")
        
        # HACK: Change CWD to the native directory temporarily
        old_cwd = os.getcwd()
        os.chdir(current_dir)
        try:
             # Pass NULL (None) for path if we are in the dir, or pass the dir? 
             # Let's try passing the dir still.
             res = self._dll.InitFaceTracking(width, height, current_dir)
        finally:
             os.chdir(old_cwd)
        if res == 0:
            self._is_initialized = True
            return True
        print(f"FaceTracker Init Failed with HRESULT: {res} (0x{res & 0xFFFFFFFF:x})")
        return False

    def process_frame(self, frame_data):
        """
        Expects a flattened byte array of the BGR/BGRA image.
        For now, the bridge expects 640x480 RGBA/BGRA.
        """
        if not self._is_initialized: return None
        
        # Prepare output buffer for 7 floats (Scale, RotX, RotY, RotZ, TransX, TransY, TransZ)
        pose = (ctypes.c_float * 7)()
        
        # Get pointer to image data
        # If frame_data is bytes/bytearray
        if isinstance(frame_data, (bytes, bytearray)):
            buf = (ctypes.c_ubyte * len(frame_data)).from_buffer_copy(frame_data)
        # If it's a numpy array, ensure it's contiguous
        elif isinstance(frame_data, np.ndarray):
            if not frame_data.flags['C_CONTIGUOUS']:
                frame_data = np.ascontiguousarray(frame_data)
            buf = frame_data.ctypes.data_as(ctypes.c_void_p)
        else:
            return None
            
        # Call native function
        res = self._dll.ProcessFace(buf, None, pose)
        
        if res == 0:
            return {
                "scale": pose[0],
                "rotation": (pose[1], pose[2], pose[3]),
                "translation": (pose[4], pose[5], pose[6])
            }
        return None

    def shutdown(self):
        if self._dll and self._is_initialized:
            self._dll.ShutdownFaceTracking()
            self._is_initialized = False

    def __del__(self):
        self.shutdown()
