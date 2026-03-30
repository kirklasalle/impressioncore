
import logging
import os
import sys
import time

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestrator.quickcam_driver import QuickCamOrbDriver

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("QuickCamTest")

def test_motor():
    print("--- INITIALIZING QUICKCAM DRIVER TEST ---")
    driver = QuickCamOrbDriver()

    print("\n[1] CONNECTING to QuickCam (046d:08c2)...")
    if driver.connect("046d_08c2"):
        print(">> CONNECTION SUCCESS")
    else:
        print(">> CONNECTION FAILED")
        return

    try:
        # TEST 1: RESET (Center)
        # The user says this usually triggers a pan-right/tilt-down dance on native driver load.
        print("\n[2] ATTEMPTING CENTER / RESET...")
        driver.reset_position()
        print(">> Reset command sent. Waiting 3s for movement...")
        time.sleep(3)

        # TEST 2: PAN RIGHT
        print("\n[3] ATTEMPTING PAN RIGHT (+15 deg)...")
        driver.pan(15)
        print(">> Pan Right sent. Waiting 2s...")
        time.sleep(2)

        # TEST 3: PAN LEFT
        print("\n[4] ATTEMPTING PAN LEFT (-30 deg)...")
        driver.pan(-30)
        print(">> Pan Left sent. Waiting 2s...")
        time.sleep(2)

        # TEST 4: TILT UP
        print("\n[5] ATTEMPTING TILT UP (+20 deg)...")
        driver.tilt(20)
        print(">> Tilt Up sent. Waiting 2s...")
        time.sleep(2)

    except Exception as e:
        print(f"\nCRITICAL ERROR DURING TEST: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\n[6] DISCONNECTING...")
        driver.disconnect()
        print(">> TEST COMPLETE")

if __name__ == "__main__":
    test_motor()
