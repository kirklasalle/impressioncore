
import collections
import logging
import threading
import time
from collections.abc import Callable

import numpy as np

try:
    import sounddevice as sd
    HAS_SOUNDDEVICE = True
except ImportError:
    sd = None
    HAS_SOUNDDEVICE = False
    print("WARNING: sounddevice not installed. Live microphone capture will be disabled.")

# Try importing faster_whisper, handle missing dep
try:
    from faster_whisper import WhisperModel
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False
    print("WARNING: faster_whisper not installed. STT will not function.")

class STTService:
    def __init__(self, model_size="tiny", device="cpu", compute_type="int8"):
        self.logger = logging.getLogger("STTService")
        self.model = None
        self.running = False
        self.audio_queue = collections.deque()
        self.callback: Callable[[str], None] | None = None
        self.listen_thread = None
        self.process_thread = None
        self.whisper_available = HAS_WHISPER
        self.sounddevice_available = HAS_SOUNDDEVICE
        self.model_loaded = False
        self.last_error: str | None = None

        if not HAS_SOUNDDEVICE:
            self.last_error = "sounddevice not installed"

        if HAS_WHISPER:
            try:
                self.logger.info(f"Loading Whisper model: {model_size} on {device}...")
                self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
                self.logger.info("Whisper model loaded.")
                self.model_loaded = True
            except Exception as e:
                self.last_error = str(e)
                self.logger.error(f"Failed to load Whisper: {e}")
        else:
            self.last_error = "faster_whisper not installed"

    def get_status(self) -> dict:
        """Returns STT capability and runtime status for API/UI surfaces."""
        return {
            "whisper_available": bool(self.whisper_available),
            "sounddevice_available": bool(self.sounddevice_available),
            "model_loaded": bool(self.model_loaded),
            "running": bool(self.running),
            "queue_depth": len(self.audio_queue),
            "last_error": self.last_error,
        }

    def start_listening(self, callback: Callable[[str], None], device_index=None):
        """
        Starts the microphone listener loop.
        callback: Function to call with transcribed text.
        """
        if self.running:
            return True

        if not HAS_SOUNDDEVICE or sd is None:
            self.last_error = "sounddevice dependency unavailable (install sounddevice)"
            self.logger.error("Cannot start STT: sounddevice dependency unavailable.")
            return False

        if not HAS_WHISPER:
            self.last_error = "Whisper dependency unavailable (install faster_whisper)"
            self.logger.error("Cannot start STT: Whisper dependency unavailable.")
            return False

        if not self.model:
            self.last_error = "Whisper model not loaded"
            self.logger.error("Cannot start STT: Whisper model not loaded.")
            return False

        self.callback = callback
        self.running = True
        self.last_error = None

        # Audio params
        self.sample_rate = 16000
        self.block_size = 4096

        # Threads
        self.listen_thread = threading.Thread(target=self._audio_loop, args=(device_index,), daemon=True)
        self.process_thread = threading.Thread(target=self._process_loop, daemon=True)

        self.listen_thread.start()
        self.process_thread.start()
        self.logger.info("STT Listening started...")
        return True

    def stop(self):
        self.running = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1.0)
        if self.process_thread and self.process_thread.is_alive():
            self.process_thread.join(timeout=1.0)
        self.logger.info("STT Stopping...")

    def _audio_loop(self, device_index):
        """Captures raw audio from sounddevice."""
        if sd is None:
            self.logger.error("Audio Input Error: sounddevice is unavailable")
            self.running = False
            return

        try:
            with sd.InputStream(samplerate=self.sample_rate,
                                device=device_index,
                                channels=1,
                                callback=self._sd_callback):
                while self.running:
                    sd.sleep(100)
        except Exception as e:
            self.logger.error(f"Audio Input Error: {e}")
            self.running = False

    def _sd_callback(self, indata, frames, time, status):
        """Sounddevice callback."""
        if status:
            self.logger.warning(status)
        self.audio_queue.append(indata.copy())

    def _process_loop(self):
        """Consumes audio queue, VAD, and Transcribe."""
        # Simple VAD buffer
        buffer = np.array([], dtype=np.float32)
        vad_threshold = 0.01  # Energy threshold
        silence_frames = 0
        max_silence = 10      # ~1-2 seconds depending on loop speed

        while self.running:
            if not self.audio_queue:
                time.sleep(0.05)
                continue

            chunk = self.audio_queue.popleft()
            flat = chunk.flatten()
            buffer = np.concatenate((buffer, flat))

            # Simple energy check
            energy = np.mean(np.abs(flat))

            if energy < vad_threshold:
                silence_frames += 1
            else:
                silence_frames = 0

            # If we have enough buffer and silence, transact
            if len(buffer) > self.sample_rate * 1.0 and silence_frames > max_silence:
                # Transcribe `buffer`
                self._transcribe(buffer)
                buffer = np.array([], dtype=np.float32)
                silence_frames = 0

            # Cap buffer size to avoid memory leak or huge lag
            if len(buffer) > self.sample_rate * 10: # 10 seconds max
                 self._transcribe(buffer)
                 buffer = np.array([], dtype=np.float32)

    def _transcribe(self, audio_data):
        if not self.model:
            return

        try:
            segments, info = self.model.transcribe(audio_data, beam_size=5)
            text = " ".join([segment.text for segment in segments]).strip()

            if text:
                self.logger.info(f"Heard: {text}")
                if self.callback:
                    self.callback(text)
        except Exception as e:
            self.logger.error(f"Transcription error: {e}")
