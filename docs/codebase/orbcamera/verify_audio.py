
import sounddevice as sd
import numpy as np
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("verify_audio")

def verify_audio():
    logger.info("Scanning for audio devices...")
    devices = sd.query_devices()
    candidate_ids = []
    
    for i, dev in enumerate(devices):
        name = dev.get('name', 'Unknown')
        logger.info(f"Device {i}: {name} (In: {dev['max_input_channels']}, Out: {dev['max_output_channels']})")
        
        # Look for Logitech
        if 'Logitech' in name or 'Orbit' in name or 'Sphere' in name:
            if dev['max_input_channels'] > 0:
                logger.info(f"FOUND CANDIDATE: {name} at ID {i}")
                candidate_ids.append(i)

    if candidate_ids:
        for dev_id in candidate_ids:
            logger.info(f"Attempting to capture audio from Candidate ID {dev_id}...")
            try:
                # Try to grab 1 second of audio
                duration = 1.0  # seconds
                fs = 44100
                recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, device=dev_id)
                sd.wait()
                
                # Check signal level
                amplitude = np.max(np.abs(recording))
                logger.info(f"Capture successful on ID {dev_id}. Max Amplitude: {amplitude:.4f}")
                
                if amplitude > 0.001:
                    logger.info(f"SUCCESS: Audio signal detected on Device {dev_id}!")
                    return True
                else:
                    logger.warning(f"WARNING: Audio captured on Device {dev_id} but silence detected. Check gain/mute.")
                    return True # Capture worked, just silent
            except Exception as e:
                logger.error(f"Capture failed on ID {dev_id}: {e}")
                continue
        logger.error("All candidates failed to capture audio.")
        return False
    else:
        logger.warning("No Logitech audio input device found.")
        return False

if __name__ == "__main__":
    verify_audio()
