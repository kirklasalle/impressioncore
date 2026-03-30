import json
import os
from datetime import datetime

import cv2
import wmi


def log_diag(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}][DIAG] {msg}")

def run_diagnostic():
    report = {
        "timestamp": str(datetime.now()),
        "wmi": [],
        "opencv_probes": [],
        "system_status": "PENDING"
    }

    log_diag("Starting World-Class Sensory Diagnostic for 'ImpressionCore'...")

    # 1. WMI PnP Inventory
    log_diag("Scanning PnP Inventory (WMI)...")
    w = wmi.WMI()
    keywords = ["Camera", "Video", "PlayStation", "Eye", "Kinect", "Orbit", "Sphere"]
    for dev in w.Win32_PnPEntity():
        try:
            name = str(dev.Name)
            if any(k.lower() in name.lower() for k in keywords):
                log_diag(f"Found Device: {name} | Status: {dev.Status}")
                report["wmi"].append({
                    "name": name,
                    "status": dev.Status,
                    "hw_id": dev.HardwareID
                })
        except Exception:
            pass

    # 2. OpenCV Exhaustive Probe
    log_diag("Starting OpenCV Backend Probes (DirectShow, MSMF, ANY)...")
    backends = [
        (cv2.CAP_DSHOW, "DSHOW"),
        (cv2.CAP_MSMF, "MSMF"),
        (cv2.CAP_ANY, "ANY")
    ]

    for idx in range(5):
        for b_id, b_name in backends:
            log_diag(f"Probing Index {idx} | Backend: {b_name}...")
            try:
                cap = cv2.VideoCapture(idx, b_id)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        log_diag(f"[SUCCESS] Index {idx} with {b_name} is ACTIVE and GRABBING.")
                        report["opencv_probes"].append({
                            "index": idx,
                            "backend": b_name,
                            "status": "SUCCESS",
                            "width": cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                            "height": cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                        })
                    else:
                        log_diag(f"[BLOCK] Index {idx} with {b_name} OPENED but READ FAILED.")
                        report["opencv_probes"].append({
                            "index": idx,
                            "backend": b_name,
                            "status": "BLOCKED"
                        })
                    cap.release()
                else:
                    report["opencv_probes"].append({
                        "index": idx,
                        "backend": b_name,
                        "status": "FAILED_TO_OPEN"
                    })
            except Exception as e:
                log_diag(f"[CRASH] Index {idx} with {b_name} error: {e}")
                report["opencv_probes"].append({
                    "index": idx,
                    "backend": b_name,
                    "status": f"CRASH: {e}"
                })

    # Save Report
    os.makedirs("logs", exist_ok=True)
    with open("logs/sensory_diagnostic_report.json", "w") as f:
        json.dump(report, f, indent=4)

    log_diag("Diagnostic Report saved to logs/sensory_diagnostic_report.json")

    if not any(p["status"] == "SUCCESS" for p in report["opencv_probes"]):
        log_diag("CRITICAL: No cameras were successfully acquired by OpenCV.")
        log_diag("POSSIBLE CAUSE: Windows Camera Privacy Settings or exclusive driver lock.")
    else:
        log_diag("INFO: At least one camera was acquired successfully.")

if __name__ == "__main__":
    run_diagnostic()
