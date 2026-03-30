
import logging
import os
import sys
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.orchestrator.kinect_connector import KinectConnector


def monitor_fps():
    logging.basicConfig(level=logging.DEBUG)
    print("--- Kinect Pro-Performance Monitor ---")

    conn = KinectConnector()
    if not conn.open():
        print("[ERROR] Could not initialize Kinect.")
        return

    print("[OK] Kinect Sensor Online. Starting Benchmark...")

    # Warm up
    time.sleep(2)

    start_time = time.time()
    frames_captured = 0
    duration = 20 # 20 seconds test for warm-up discovery

    last_print = time.time()

    ret_count = 0
    fail_count = 0
    while time.time() - start_time < duration:
        ret, pkts = conn.read()
        if ret:
            ret_count += 1
            if "color" in pkts:
                frames_captured += 1

            # Print status every 1s
            if time.time() - last_print >= 1.0:
                fps = frames_captured / (time.time() - start_time)
                print(f"  - Current Avg FPS: {fps:.2f} | Color Format: {conn.color_mode} | pkts: {list(pkts.keys())}")
                last_print = time.time()
        else:
            fail_count += 1

        # Don't spin too hard
        time.sleep(0.001)

    total_time = time.time() - start_time
    final_fps = frames_captured / total_time

    print("\n--- Final Results ---")
    print(f"Total Success Reads (ret=True): {ret_count}")
    print(f"Total Failed Reads (ret=False): {fail_count}")
    print(f"Total Frames: {frames_captured}")
    print(f"Total Time:   {total_time:.2f}s")
    print(f"Average FPS:  {final_fps:.2f}")
    print(f"Color Mode:   {conn.color_mode} (0=RGB, 1=YUV)")

    if final_fps >= 25:
        print("[SUCCESS] Fast Rate Target Achieved!")
    else:
        print("[WARNING] Frame rate below 30FPS target. Check USB bandwidth.")

    conn.release()

if __name__ == "__main__":
    monitor_fps()
