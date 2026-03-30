"""
OrbOS Web UI Server
====================
Flask-based web interface for OrbOS chat.
"""

import os
import json
import threading
import time
from flask import Flask, render_template, request, jsonify, Response
from ..orb_service import get_orb_service
from ..agent import OrbAgent
from ..camera import get_active_camera

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Global state
_agent = None
_camera_type = None # Starts with no camera selected


def get_agent():
    """Get or create agent instance."""
    global _agent
    if _agent is None:
        _agent = OrbAgent()
    return _agent


# ===== ROUTES =====

@app.route('/')
def index():
    """Main chat page."""
    return render_template('chat.html')


@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get recent chat sessions."""
    service = get_orb_service()
    sessions = service.get_recent_sessions(20)
    return jsonify([{
        'id': s.id,
        'title': s.title,
        'started_at': s.started_at
    } for s in sessions])


@app.route('/api/sessions/new', methods=['POST'])
def new_session():
    """Create a new chat session."""
    service = get_orb_service()
    data = request.json or {}
    title = data.get('title', 'New Conversation')
    session = service.start_new_session(title)
    return jsonify({'id': session.id, 'title': session.title})


@app.route('/api/sessions/<session_id>/messages', methods=['GET'])
def get_messages(session_id):
    """Get messages for a session."""
    service = get_orb_service()
    service.load_session(session_id)
    messages = service.get_current_history()
    return jsonify(messages)


@app.route('/api/chat', methods=['POST'])
def chat():
    """Send a message and get response (synchronous)."""
    service = get_orb_service()
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Ensure we have a session
    if not service.memory.current_session_id:
        service.start_new_session()
    
    # Update camera context
    agent = get_agent()
    if agent and agent._cam:
        context = f"""
Camera Status: {'Connected' if agent._cam.is_open else 'Disconnected'}
Pan: {agent._cam.pan}, Tilt: {agent._cam.tilt}
"""
        service.set_camera_context(context)
    
    # Get response (synchronous)
    response = service.ask_orb_sync(user_message)
    
    return jsonify({
        'response': response,
        'response': response,
        'session_id': getattr(service.memory, 'current_session_id', 'default') if hasattr(service, 'memory') else 'default'
    })


@app.route('/api/status')
def status():
    """Get current system status."""
    service = get_orb_service()
    agent = get_agent()
    
    camera_status = "Disconnected"
    is_kinect = agent and agent._cam and "Kinect" in str(type(agent._cam))
    if agent and agent._cam and agent._cam.is_open:
        camera_status = "Connected"
    
    status_data = {
        'camera': camera_status,
        'camera_type': _camera_type or "none",
        'llm_active': service.llm.active_provider is not None,
        'session': getattr(service.memory, 'current_session_id', 'default') if hasattr(service, 'memory') else 'default',
        'is_thinking': service.is_thinking,
        'pan': agent._cam.pan if agent and agent._cam else 0,
        'tilt': agent._cam.tilt if agent and agent._cam else 0,
        'brightness': agent._cam.brightness if agent and agent._cam else 0.5,
        'contrast': agent._cam.contrast if agent and agent._cam else 0.5
    }

    # Add Kinect depth info if applicable
    if is_kinect and camera_status == "Connected":
        cam = agent._cam
        status_data.update({
            'kinect': {
                'skeleton_active': getattr(cam, '_skeleton_enabled', False),
                'near_mode': getattr(cam, '_near_mode', False),
                'resolution': getattr(cam, '_resolution', 2),
                'mode': getattr(cam, '_video_mode', 'color'),
                'accel': cam.get_accelerometer_reading() if hasattr(cam, 'get_accelerometer_reading') else None
            }
        })

    return jsonify(status_data)


@app.route('/api/camera/settings', methods=['POST'])
def update_camera_settings():
    """Update camera settings like brightness and contrast."""
    agent = get_agent()
    if not agent or not agent._cam: return jsonify({'error': 'No camera'}), 503
    
    data = request.json
    if 'brightness' in data:
        agent._cam.brightness = float(data['brightness'])
    if 'contrast' in data:
        agent._cam.contrast = float(data['contrast'])
        
    return jsonify({
        'status': 'ok',
        'brightness': agent._cam.brightness,
        'contrast': agent._cam.contrast
    })


@app.route('/api/camera/move', methods=['POST'])
def move_camera():
    """Move camera in specified direction."""
    agent = get_agent()
    
    if not agent or not agent._cam or not agent._cam.is_open:
        return jsonify({'error': 'Camera not connected'}), 400
    
    data = request.json
    direction = data.get('direction', '')
    
    try:
        cam = agent._cam
        # We now use the standard pan/tilt setters which are polymorphic
        if direction == 'up': cam.tilt += 5
        elif direction == 'down': cam.tilt -= 5
        elif direction == 'left': 
             # For both cameras, pan is digital in the current implementation
             if hasattr(cam, '_motor'): cam._motor.move_relative(100, 0)
        elif direction == 'right':
             if hasattr(cam, '_motor'): cam._motor.move_relative(-100, 0)
        
        return jsonify({'success': True, 'pan': cam.pan, 'tilt': cam.tilt})
    except Exception as e:
        return jsonify({'error': f'PTZ move error: {str(e)}'}), 500


@app.route('/api/camera/switch', methods=['POST'])
def switch_camera():
    """Switch active camera type."""
    global _camera_type
    data = request.json
    new_type = data.get('type', 'orbit')
    
    if new_type not in ["orbit", "kinect", "none"]:
        return jsonify({'error': 'Invalid camera type'}), 400
        
    _camera_type = new_type if new_type != "none" else None
    agent = get_agent()
    # Force agent to reload its camera handle
    agent.sync_camera(_camera_type)
    
    return jsonify({'status': 'ok', 'type': _camera_type or "none"})


@app.route('/api/camera/fullview', methods=['POST'])
def toggle_full_view():
    """Toggle Full View Mode."""
    agent = get_agent()
    if not agent or not agent._cam: return jsonify({'error': 'No camera'}), 503
    agent._cam.toggle_full_view()
    return jsonify({'status': 'ok', 'mode': 'full' if agent._cam._full_view_mode else 'ptz'})


@app.route('/api/kinect/control', methods=['POST'])
def kinect_control():
    """Kinect specific controls."""
    agent = get_agent()
    cam = agent._cam
    if not cam or "Kinect" not in str(type(cam)):
        return jsonify({'error': 'Kinect not active'}), 400
    
    data = request.json
    feature = data.get('feature')
    value = data.get('value')
    
    try:
        if feature == 'skeleton':
            cam.set_skeleton_tracking(value)
        elif feature == 'near_mode':
            cam.set_near_mode(value)
        elif feature == 'resolution':
            # value: 2 for 640, 3 for 1280
            cam.set_resolution(int(value))
        elif feature == 'mode':
            cam.set_sensor_mode(value)
        
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def generate_video_frames():
    """Generator for MJPEG video stream."""
    import cv2
    import numpy as np
    
    agent = get_agent()
    
    while True:
        try:
            frame = None
            if agent and agent._cam and agent._cam.is_open:
                frame = agent._cam.read()
            
            if frame is not None:
                h, w = frame.shape[:2]
                title = _camera_type.upper() if _camera_type else "NONE"
                cv2.putText(frame, f"OrbOS - {title}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Encode as JPEG
                ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            else:
                # Placeholder frame
                img = np.zeros((480, 640, 3), dtype=np.uint8)
                img[:] = (20, 20, 25)
                text = "No Camera Selected" if _camera_type is None else "Initializing Camera..."
                cv2.putText(img, text, (180, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 120), 2)
                ret, buffer = cv2.imencode('.jpg', img)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        except: pass
        time.sleep(0.04)


@app.route('/video_feed')
def video_feed():
    return Response(generate_video_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


def run_server(host='127.0.0.1', port=5000, debug=False):
    app.run(host=host, port=port, debug=debug, threaded=True)


def run_server_background(host='127.0.0.1', port=5000):
    """Run the server in a daemon thread."""
    thread = threading.Thread(target=run_server, args=(host, port), daemon=True)
    thread.start()
    return thread
