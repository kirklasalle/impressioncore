
import cv2
import numpy as np
import threading
import logging
import collections

# Try imports
try:
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

logger = logging.getLogger("AudioViz")

class AudioVisualizer:
    """
    Captures real-time audio and renders it as a waveform/level meter on OpenCV frames.
    """
    def __init__(self, device_index=None, history_size=400):
        self.device_index = device_index
        self.history_size = history_size
        self.lock = threading.Lock()
        
        # Buffer for raw waveform (normalized -1.0 to 1.0)
        self.waveform = collections.deque(maxlen=history_size)
        # Pre-fill with zeros
        self.waveform.extend([0.0] * history_size)
        
        self.stream = None
        self.running = False
        
        if not AUDIO_AVAILABLE:
            logger.warning("AudioVisualizer: sounddevice not found. Visuals will be flat.")

    def start(self):
        if not AUDIO_AVAILABLE:
            return

        try:
            # If no device index provided, find Logitech or use default
            if self.device_index is None:
                devices = sd.query_devices()
                for i, dev in enumerate(devices):
                    if dev['max_input_channels'] > 0 and ('Logitech' in dev['name'] or 'Orbit' in dev['name']):
                        self.device_index = i
                        break
            
            # Fallback to default input if still None
            if self.device_index is None:
                self.device_index = sd.default.device[0]

            logger.info(f"AudioViz using device index: {self.device_index}")

            # Callback for non-blocking capture
            def callback(indata, frames, time, status):
                if status:
                    logger.debug(f"Audio status: {status}")
                # indata is (frames, channels). We take channel 0.
                # Downsample if needed? No, just take the chunk.
                # We normalize and extend.
                
                # Check volume (amplitude) for simple level
                volume_norm = float(np.max(np.abs(indata)))
                
                with self.lock:
                    # Append new samples. Flatten to 1D array.
                    samples = indata[:, 0]
                    self.waveform.extend(samples)

            self.stream = sd.InputStream(
                device=self.device_index,
                channels=1,
                samplerate=44100,
                callback=callback,
                blocksize=1024 # Update chunk size
            )
            self.stream.start()
            self.running = True
            logger.info("AudioViz stream started.")

        except Exception as e:
            logger.error(f"Failed to start AudioViz stream: {e}")

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.running = False

    def draw(self, frame, x, y, w, h, color=(0, 255, 0)):
        """Draw component waveform and levels."""
        if not self.running:
            return

        # Create overlay
        overlay = frame.copy()
        
        # Background for audio area
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (20, 20, 20), -1)
        
        # Get data safely
        with self.lock:
            data = list(self.waveform)
            
        if not data:
            return

        # 1. Draw Waveform
        # Map data (-1.0 to 1.0) to y range
        center_y = y + h // 2
        amplitude_scale = h // 2 
        
        # We assume data length matches history size approx, but we scaling to width
        pts = []
        step = max(1, len(data) / w)
        
        for i in range(w):
            idx = int(i * step)
            if idx < len(data):
                val = data[idx]
                # visual boost
                val = val * 3.0 
                # clamp
                val = max(-1.0, min(1.0, val))
                
                pt_x = x + i
                pt_y = int(center_y - (val * amplitude_scale))
                pts.append((pt_x, pt_y))

        if pts:
            cv2.polylines(frame, [np.array(pts)], False, color, 1)

        # 2. Draw Volume Meter (Bar on the right)
        # Calculate RMS of recent data
        recent = data[-1024:] # Last chunk
        if recent:
            rms = np.sqrt(np.mean(np.array(recent)**2))
            # Log scale for dB-ish visual? Or linear boosted.
            level = min(1.0, rms * 5.0) 
            
            bar_w = 10
            bar_h = int(level * h)
            bar_x = x + w - bar_w - 2
            bar_y = y + h - bar_h - 2
            
            # gradient color based on intensity
            meter_color = (0, 255, 0)
            if level > 0.7: meter_color = (0, 0, 255) # Red clip
            elif level > 0.4: meter_color = (0, 255, 255) # Yellow warn
            
            cv2.rectangle(frame, (bar_x, y+2), (bar_x+bar_w, y+h-2), (50,50,50), -1) # track
            cv2.rectangle(frame, (bar_x, y + h - 2 - bar_h), (bar_x+bar_w, y+h-2), meter_color, -1) # fill

        # Blend background (transparency)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
        
        # Label
        cv2.putText(frame, "RAW AUDIO", (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

