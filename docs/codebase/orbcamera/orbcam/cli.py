import argparse
import logging
import sys
import cv2
import time
from pathlib import Path
from typing import Optional, Union
import numpy as np
import subprocess

from .camera import get_active_camera, BaseCamera, CameraError

def setup_logging(debug: bool):
    """
    Setup centralized logging to console and a root log file.
    """
    level = logging.DEBUG if debug else logging.INFO
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    
    try:
        file_handler = logging.FileHandler('orbcam.log', mode='a', encoding='utf-8')
        file_handler.setFormatter(file_format)
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create log file 'orbcam.log': {e}")
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_format)
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)
    
    logging.info(f"Logging initialized. Level: {'DEBUG' if debug else 'INFO'}")

def list_cameras():
    print("Scanning for cameras...")
    
    # 1. Kinect Check
    try:
        from orbcam.logitech.kinect import KINECT_SDK_AVAILABLE
        import ctypes
        if KINECT_SDK_AVAILABLE:
            kinect_dll = ctypes.WinDLL("Kinect10.dll")
            count = ctypes.c_int(0)
            kinect_dll.NuiGetSensorCount(ctypes.byref(count))
            if count.value > 0:
                print(f"  - Kinect Sensors: {count.value} Detected [Native SDK]")
            else:
                print("  - Kinect Sensors: None found.")
        else:
            print("  - Kinect SDK: Not installed.")
    except Exception as e:
        print(f"  - Kinect Check Error: {e}")

    # 2. OpenCV Probe
    print("\nProbing OpenCV indices (this may take a moment)...")
    working_indices = []
    for i in range(5):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                print(f"  - Index {i}: OK ({w}x{h}) [DSHOW]")
                working_indices.append(i)
                cap.release()
                continue
            cap.release()
            
    if not working_indices:
        print("  - No working OpenCV camera indices found.")

def draw_hud(frame: np.ndarray, cam: BaseCamera, show_detect: bool, tracking: bool):
    """Draw a sleek, modern HUD overlay."""
    h, w = frame.shape[:2]
    cam_type = "KINECT (NATIVE)" if "Kinect" in str(type(cam)) else "ORBIT (UVC)"
    
    overlay = frame.copy()
    bar_height = 35
    cv2.rectangle(overlay, (0, h - bar_height), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    
    det_color = (0, 255, 0) if show_detect else (50, 50, 50)
    cv2.circle(frame, (15, h - 17), 5, det_color, -1)
    cv2.putText(frame, "DET", (25, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    
    track_color = (255, 100, 0) if tracking else (50, 50, 50)
    cv2.circle(frame, (70, h - 17), 5, track_color, -1)
    cv2.putText(frame, "TRACK", (80, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    
    stats_p = f"PAN: {cam.pan:4.1f}"
    stats_t = f"TILT: {cam.tilt:4.1f}"
    
    cv2.putText(frame, stats_p, (w - 180, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    cv2.putText(frame, stats_t, (w - 90, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    
    branding = f"OrbOS v1.1 | {cam_type}"
    cv2.putText(frame, branding, (w - 240, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)

def run_preview(camera_type: str = "orbit", index: Optional[int] = None, auto_track: bool = False):
    try:
        cam = get_active_camera(camera_type)
        if index is not None and hasattr(cam, "_device_index"):
            cam._device_index = index
            
        cam.open()
        print(f"Camera ({camera_type}) opened.")
        
        show_detect = True
        tracking_enabled = auto_track
        
        print("\nControls:")
        print("  ESC/Q : Quit")
        print("  W/S   : Tilt Up/Down")
        print("  A/D   : Pan Left/Right (Digital)")
        print("  V     : Toggle Detection")
        print("  T     : Toggle Auto-Track")
        print("  F     : Toggle Full View")
        
        window_name = f"OrbOS Preview ({camera_type.upper()})"
        cv2.namedWindow(window_name)
        
        from .detector import Detector
        detector = Detector()
        
        while True:
            frame = cam.read()
            if frame is None:
                continue
            
            # Detect
            if show_detect:
                faces, motion = detector.detect(frame)
                frame = detector.draw_detections(frame, faces, motion)
                
                if tracking_enabled and faces:
                    # Basic center tracking
                    fx, fy, fw, fh = faces[0]
                    cx, cy = fx + fw//2, fy + fh//2
                    err_x = cx - frame.shape[1]//2
                    err_y = cy - frame.shape[0]//2
                    
                    if abs(err_x) > 30:
                         if hasattr(cam, '_motor'): cam._motor.move_relative(-err_x, 0)
                    if abs(err_y) > 30:
                         cam.tilt -= (err_y / 10.0)
            
            # --- Skeleton Visualization (Kinect) ---
            if hasattr(cam, 'latest_skeleton'):
                skel = cam.latest_skeleton
                if skel:
                    # Visualization (Placeholder until projection logic)
                    cv2.putText(frame, "SKELETON ACTIVE", (w//2 - 100, h - 80), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
            draw_hud(frame, cam, show_detect, tracking_enabled)
            cv2.imshow(window_name, frame)
            
            key = cv2.waitKey(33) & 0xFF
            if key in [27, ord('q')]:
                break
            elif key == ord('v'):
                show_detect = not show_detect
            elif key == ord('t'):
                tracking_enabled = not tracking_enabled
            elif key == ord('f'):
                cam.toggle_full_view()
                
            # Manual Move
            if key == ord('w'): cam.tilt += 2
            elif key == ord('s'): cam.tilt -= 2
            elif key == ord('a'): 
                 if hasattr(cam, '_motor'): cam._motor.move_relative(100, 0)
            elif key == ord('d'):
                 if hasattr(cam, '_motor'): cam._motor.move_relative(-100, 0)

        cv2.destroyAllWindows()
        cam.close()
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def run_diagnostics():
    print("==========================================")
    print("      ORBCAM SYSTEM DIAGNOSTICS")
    print("==========================================")
    
    report = []
    def log_diag(msg):
        print(msg)
        report.append(msg)

    # 1. Driver Service Check
    log_diag("\n[1/4] Checking Logitech Driver Service (LVUVC64)...")
    try:
        res = subprocess.run(["sc", "query", "LVUVC64"], capture_output=True, text=True)
        if "RUNNING" in res.stdout:
            log_diag("  - Status: RUNNING (Good)")
        elif "STOPPED" in res.stdout:
            log_diag("  - Status: STOPPED (Driver is loaded but device not active)")
        else:
            log_diag("  - Status: NOT FOUND")
    except Exception: pass

    # 2. Kinect Native Check
    log_diag("\n[2/4] Checking Kinect Sensor Status...")
    try:
        from orbcam.logitech.kinect import KINECT_SDK_AVAILABLE, KinectCamera
        if KINECT_SDK_AVAILABLE:
            from orbcam.camera import get_active_camera
            cam = get_active_camera("kinect")
            
            # Get IDs FIRST (doesn't require full open/init)
            info = cam.get_hardware_info()
            status_val = info.get("status_code", -1)
            
            if status_val == 0:
                log_diag(f"  - Status: CONNECTED (S_OK)")
                
                # Report IDs from the info dict
                if "connection_id" in info and info["connection_id"]:
                    log_diag(f"  - Connection ID: {info['connection_id']}")
                if "unique_id" in info and info["unique_id"]:
                    log_diag(f"  - Unique ID: {info['unique_id']}")
                
                # Attempt to open for accelerometer reading
                try:
                    if not cam.is_open: cam.open()
                    accel = cam.get_accelerometer_reading()
                    if accel:
                        log_diag(f"  - Orientation (Gravity): X:{accel[0]:.2f}, Y:{accel[1]:.2f}, Z:{accel[2]:.2f}")
                except Exception as e:
                    logger.error(f"Error getting accelerometer reading: {e}")
            else:
                log_diag(f"  - Status Code: {status_val}")
        else:
            log_diag("  - Kinect SDK: Missing (Kinect10.dll not found)")
    except Exception as e:
        log_diag(f"  - Kinect Check Failed: {e}")
    log_diag("\n[3/4] Probing DirectShow Categories...")
    from orbcam.logitech.xu_control import XUController
    try:
        XUController()
        log_diag("  - DirectShow Enumeration Complete.")
    except Exception: pass

    # 4. OpenCV Probe
    log_diag("\n[4/4] Probing OpenCV Video Backends...")
    working = []
    for i in range(5):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret: working.append(i)
        cap.release()
    
    if working:
        log_diag(f"  - Working Video Indices: {working}")
    else:
        from orbcam.logitech.kinect import KINECT_SDK_AVAILABLE
        if KINECT_SDK_AVAILABLE:
            log_diag("  - TIP: No OpenCV cameras, but Kinect is available natively.")
        else:
            log_diag("  - NO WORKING VIDEO STREAMS DETECTED.")

    with open("diagnose_report.txt", "w") as f:
        f.write("\n".join(report))
    log_diag(f"\nReport saved to 'diagnose_report.txt'")
    print("==========================================\n")

def main():
    parser = argparse.ArgumentParser(description="Orb Camera Control Utility")
    parser.add_argument('--debug', action='store_true')
    subparsers = parser.add_subparsers(dest='command')
    
    subparsers.add_parser('list')
    subparsers.add_parser('diagnose')
    
    prev = subparsers.add_parser('preview')
    prev.add_argument('--type', choices=['orbit', 'kinect'], default='orbit')
    prev.add_argument('--index', type=int)
    
    chat = subparsers.add_parser('chat')
    chat.add_argument('--port', type=int, default=5000)

    args = parser.parse_args()
    setup_logging(args.debug)
    
    if args.command == 'list':
        list_cameras()
    elif args.command == 'diagnose':
        run_diagnostics()
    elif args.command == 'preview':
        # Auto-detect kinect if orbit fails and no type specified
        ctype = args.type
        if ctype == 'orbit':
             try:
                 from .logitech.devices import find_orbit_camera_index
                 if find_orbit_camera_index() is None:
                     from orbcam.logitech.kinect import KINECT_SDK_AVAILABLE
                     if KINECT_SDK_AVAILABLE:
                         import ctypes
                         kdll = ctypes.WinDLL("Kinect10.dll")
                         cnt = ctypes.c_int(0)
                         kdll.NuiGetSensorCount(ctypes.byref(cnt))
                         if cnt.value > 0:
                             print("Suggesting Kinect as Orbit was not found.")
                             ctype = 'kinect'
             except: pass
        run_preview(ctype, args.index)
    elif args.command == 'chat':
        from .ui.server import run_server
        import webbrowser
        url = f"http://127.0.0.1:{args.port}"
        print(f"Starting OrbOS Chat on {url}")
        
        # Open browser automatically
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Warning: Could not open browser: {e}")
            
        run_server(port=args.port)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
