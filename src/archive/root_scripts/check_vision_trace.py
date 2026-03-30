import requests
import json

try:
    resp = requests.get("http://127.0.0.1:8000/v1/vision/trace")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Active Caps: {data.get('6_active_caps', [])}")
        print(f"Frames in Buffer: {data.get('8_frames_in_buffer', [])}")
        print(f"Kinect Metadata: {data.get('7_hardware_metadata', {}).get('98', 'NOT FOUND')}")
    else:
        print(f"Trace Failed: {resp.status_code}")
except Exception as e:
    print(f"Error connecting to API: {e}")
