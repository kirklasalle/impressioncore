import json
import os
import sys
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.orchestrator.system_logger import sys_logger


def tail_logs():
    """Tails the current system log file and prints new entries."""
    log_file = sys_logger.current_log_file
    print("[*] Starting Log Monitor...")
    print(f"[*] Monitoring: {log_file}")
    print("[*] Press Ctrl+C to stop.\n")

    if not os.path.exists(log_file):
        print("[!] Log file not found yet. Waiting...")
        while not os.path.exists(log_file):
            time.sleep(1)

    with open(log_file) as f:
        # Go to end of file
        f.seek(0, os.SEEK_END)

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue

            try:
                entry = json.loads(line)
                ts = entry.get("timestamp", "").split("T")[-1].split(".")[0]
                comp = entry.get("component", "???")
                lvl = entry.get("level", "INFO")
                msg = entry.get("message", "")

                # Simple color coding for terminal (if supported)
                color = ""
                reset = ""
                if os.name == 'nt':
                     # Basic Windows color support via colorama or similar is best,
                     # but we will stick to plain for now for robustness
                     pass
                else:
                    if lvl == "ERROR":
                        color = "\033[91m"
                    elif lvl == "WARNING":
                        color = "\033[93m"
                    elif lvl == "SUCCESS":
                        color = "\033[92m"
                    reset = "\033[0m"

                print(f"[{ts}] [{comp}] {color}{lvl}{reset}: {msg}")
            except Exception:
                # print(f"[PARSE ERROR] {e} -> {line}")
                pass

if __name__ == "__main__":
    try:
        tail_logs()
    except KeyboardInterrupt:
        print("\n[*] Monitor stopped.")
