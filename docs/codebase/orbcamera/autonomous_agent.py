
import time
import cv2
import logging
import random

import json
import base64
from orbcam.audio_viz import AudioVisualizer
from orbcam.agent import OrbAgent
from orbcam.llm import LLMManager

def run_autonomous_mode():
    print("==========================================")
    print("      ORB AGENT: AUTONOMOUS MODE")
    print("==========================================")
    print("Initializing Agent...")
    
    agent = OrbAgent()
    status = agent.status()
    print(f"Status: {status}")
    
    if not status.get('connected'):
        print("Error: Agent failed to connect to camera.")
        return

    # Initialize Visualizer
    print("Initializing Audio Visualizer...")
    viz = AudioVisualizer()
    viz.start()
    
    # Initialize Brain
    print("Connecting to Brain...")
    brain = LLMManager()

    if not brain.active_provider:
        print("WARNING: No Active Brain configured.")
        print("Run 'python -m orbcam.cli models add ...' to configure.")


    print("Taking over control...")
    print("Function pattern: Monitor -> Scan -> Listen (Continuous)")
    
    # Access internal camera directly for frame capture
    cam = agent._cam

    # Access detector from internal camera
    detector = agent._cam._detector if agent._cam else None
    
    try:
        moves = ["left", "right", "up", "down"]
        last_move_time = time.time()
        last_face_time = time.time()
        last_think_time = 0
        current_thought = "Waiting for Brain..." if not brain.active_provider else "Initializing..."

        
        while True:
            faces = []
            
            # 1. MONITOR: Capture and save frame
            if cam and cam.is_open:
                frame = cam.read()
                if frame is not None:
                    h, w = frame.shape[:2]
                    center_x, center_y = w // 2, h // 2
                    
                    # 2. DETECT FACES & MOTION
                    if detector:
                        motion = detector.detect_motion(frame)
                        faces = detector.detect_faces(frame)
                        
                        # Use detector's fancy drawing for boxes
                        frame = detector.draw_detections(frame, faces, motion)
                        
                        if len(faces) > 0:
                            last_face_time = time.time()
                            
                            # VISUALIZE TRACKING EFFORT (Vector Line)
                            (fx, fy, fw, fh) = faces[0]
                            face_cx = fx + fw // 2
                            face_cy = fy + fh // 2
                            # Draw line from screen center to face center
                            cv2.line(frame, (center_x, center_y), (face_cx, face_cy), (0, 255, 0), 2)
                            cv2.circle(frame, (center_x, center_y), 3, (0, 0, 255), -1)
                            
                            # Use Camera's Optimize Tracker Logic
                            agent._cam.track_object(faces[0], (w, h))
                            
                            # Log tracking occasionally
                            print("Tracking: Engaged")
                    
                    # Add Overlay Text
                    
                    # Add Overlay Text
                    mode = "TRACKING" if (time.time() - last_face_time < 2.0) else "PATROL"
                    color = (0, 255, 0) if mode == "TRACKING" else (0, 255, 255)
                    
                    cv2.putText(frame, f"AGENT VIEW: {time.ctime()}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    cv2.putText(frame, f"STATUS: {mode}", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    
                    # DRAW AUDIO VIZ
                    viz_w = 400
                    viz_h = 60
                    viz_x = (w - viz_w) // 2
                    viz_y = h - viz_h - 20
                    viz.draw(frame, viz_x, viz_y, viz_w, viz_h)
                    
                    # SHOW LIVE WINDOW
                    cv2.imwrite("monitor_frame.jpg", frame)
                    cv2.imshow("OrbAgent Autonomous View", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            
            # 3. HIGH LEVEL REASONING (Slow Brain)
            if brain.active_provider and (time.time() - last_think_time > 2.0):
                # Construct minimal context
                status = "Idle"
                if len(faces) > 0: status = "Tracking Human"
                elif len(motion) > 0: status = "Motion Detected"
                
                # Prepare visual context (small resized buffer for speed/cost)
                small_f = cv2.resize(frame, (320, 240))
                _, buf = cv2.imencode('.jpg', small_f, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
                
                # Ask Brain
                decision_json = brain.think([
                    {"type": "text", "text": f"Status: {status}. Faces: {len(faces)}. Motion: {len(motion)}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(buf).decode('utf-8')}"}}
                ])
                
                try:
                    # Parse JSON
                    data = json.loads(decision_json)
                    current_thought = data.get("thought", "...")
                    action = data.get("action")
                    params = data.get("parameters", {})
                    
                    # Execute Actions
                    if action == "patrol" and len(faces) == 0:
                        d = params.get("direction", "right")
                        agent.move(d, 20)
                    elif action == "reset":
                        agent.reset()
                        
                except Exception as e:
                    print(f"Brain Error: {e}")
                    
                last_think_time = time.time()
                
            # 4. UPDATE HUD
            # Draw Thought Bubble
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, 40), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
            cv2.putText(frame, f"BRAIN: {current_thought}", (10, 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            
            # Non-blocking loop
            # time.sleep(0.01) # Handled by waitKey
            
    except KeyboardInterrupt:
        print("Agent stopping...")
    except Exception as e:
        print(f"Agent crashed: {e}")
    finally:
        # Check if agent is still defined before resetting
        if 'viz' in locals():
            viz.stop()
        if 'agent' in locals() and agent:
            print("Resetting position...")
            agent.reset()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_autonomous_mode()
