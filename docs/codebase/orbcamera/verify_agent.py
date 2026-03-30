
import time
import logging
from orbcam.agent import OrbAgent

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("verify_agent")
logging.getLogger("orbcam").setLevel(logging.DEBUG)

def verify_agent():
    logger.info("Initializing AI Agent Interface...")
    try:
        agent = OrbAgent()
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        return

    # Give drivers a moment
    time.sleep(2.0)

    # Check Status
    status = agent.status()
    logger.info(f"Agent Status: {status}")

    # 1. Audio Test (Voice)
    logger.info("--- Testing Hearing (Voice) ---")
    if status.get('audio_available', False):
        logger.info("Listening for 2 seconds...")
        result = agent.listen(duration=2.0)
        if result['success']:
            logger.info(f"Hearing Result: {result['message']} (Max Amp: {result.get('max_amplitude', 0):.4f})")
            if result.get('signal_detected'):
                logger.info("SUCCESS: Signal detected.")
            else:
                logger.info("No loud signal detected (Quiet room?).")
        else:
            logger.error(f"Hearing Failed: {result['message']}")
    else:
        logger.warning("Audio not available.")

    # 2. Movement Test (Body) [Expect failure if hardware GUID issue persists]
    logger.info("--- Testing Movement (Body) ---")
    if status['can_move']:
        logger.info("Attempting: Move Left")
        res_move = agent.move("left", 300)
        logger.info(f"Move Result: {res_move}")
        
        time.sleep(1)
        
        logger.info("Attempting: Reset")
        res_reset = agent.reset()
        logger.info(f"Reset Result: {res_reset}")
    else:
        logger.warning("Hardware control not available (Simulated Mode).")

    logger.info("--- Verification Complete ---")

if __name__ == "__main__":
    verify_agent()
