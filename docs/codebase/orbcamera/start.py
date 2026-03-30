import logging
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from orbcam.ui.server import run_server

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("orbcam.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("OrbOS-Launcher")
    logger.info("Starting OrbOS System...")
    
    # Run the web server
    run_server(host='127.0.0.1', port=5000, debug=False)
