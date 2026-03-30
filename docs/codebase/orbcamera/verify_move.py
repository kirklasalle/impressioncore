
import logging
import time
import sys
import os

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("verify_move")

# Add project root to path
sys.path.append(os.path.abspath("d:/Projects/orbcamera"))

try:
    from orbcam.logitech.xu_control import XUController
except ImportError as e:
    logger.error(f"Import failed: {e}")
    sys.exit(1)

def test_movement():
    logger.info("Initializing XUController...")
    xu = XUController()
    
    if not xu._ks_control and not xu._ks_property_set:
        logger.error("FAILED to bind to any hardware interface (Simulated mode active).")
        return False
        
    interface_type = "IKsControl" if xu._ks_control else "IKsPropertySet"
    logger.info(f"SUCCESS: Bound using {interface_type}!")
    
    logger.info("Attempting Reset...")
    if xu.reset():
        logger.info("Reset command sent successfully.")
    else:
        logger.error("Reset command failed.")
        
    time.sleep(1)
    
    logger.info("Attempting Pan Left...")
    if xu.move_relative(-500, 0):
        logger.info("Pan Left command sent.")
    else:
        logger.error("Pan Left command failed.")

    time.sleep(1)
    
    logger.info("Attempting Pan Right...")
    if xu.move_relative(500, 0):
        logger.info("Pan Right command sent.")
    else:
        logger.error("Pan Right command failed.")
        
    return True

if __name__ == "__main__":
    test_movement()
