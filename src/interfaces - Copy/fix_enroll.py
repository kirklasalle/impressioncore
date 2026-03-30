"""Patch enroll_face in triad_api.py to handle int/str key mismatch."""
import re

with open("triad_api.py", encoding="utf-8") as f:
    content = f.read()

# Find and replace the simple check
old_pattern = r'    if cam_id not in frames:\s*\n        raise HTTPException\(status_code=404, detail=f"No frame available from camera \{cam_id\}"\)'

new_code = '''    if cam_id not in frames:
        # Try int version
        try:
            if int(cam_id) in frames: cam_id = int(cam_id)
        except: pass
    if cam_id not in frames and str(cam_id) in frames:
        cam_id = str(cam_id)
    if cam_id not in frames:
        raise HTTPException(status_code=404, detail=f"No frame available from camera {cam_id}. Available: {list(frames.keys())}")'''

content, count = re.subn(old_pattern, new_code, content)
print(f"Replacements made: {count}")

if count > 0:
    with open("triad_api.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Patch applied successfully!")
else:
    print("Pattern not found. Manual review needed.")
