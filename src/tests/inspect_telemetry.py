
import json

import requests

API_BASE = "http://localhost:8000"

def check_telemetry():
    try:
        response = requests.get(f"{API_BASE}/v1/vision/telemetry")
        if response.status_code == 200:
            data = response.json()
            print("Telemetry keys:", data.keys())
            print("Detections keys:", data.get("detections", {}).keys())

            vision_alpha = data.get("detections", {}).get("VisionAlpha", [])
            print(f"VisionAlpha detections count: {len(vision_alpha)}")
            if vision_alpha:
                print("First detection:", json.dumps(vision_alpha[0], indent=2))
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    check_telemetry()
