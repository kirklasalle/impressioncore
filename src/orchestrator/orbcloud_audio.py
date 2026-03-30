import io
import logging
import queue
import threading
import time
import wave

import numpy as np
import sounddevice as sd
import speech_recognition as sr

from src.orchestrator.sensory_hot_swap import hotswap_manager
from src.orchestrator.system_logger import log_event

logger = logging.getLogger(__name__)

class OrbCloudAudio:
    """
    Universal Audio Interface (OrbCloud).
    Handles microphone discovery, capture, and STT/TTS integration.
    """

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.listen_thread = None
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.device_info = {}

    def discover_microphones(self):
        """Enumerates available audio input devices and prioritizes Realtek."""
        log_event("AUDIO", "Discovering microphonic landscape...")
        try:
            devices = sd.query_devices()

            # Find Realtek HD Audio specifically as it's the most stable
            realtek_index = None
            for i, d in enumerate(devices):
                if d['max_input_channels'] > 0:
                    name = d['name'].lower()
                    if "realtek" in name and ("high definition" in name or "hd audio" in name):
                        realtek_index = i
                        log_event("AUDIO", f"Found stable Realtek hardware at index {i}: {d['name']}")
                        break

            default_device = sd.query_devices(kind='input')
            if realtek_index is not None:
                log_event("AUDIO", f"Prioritizing Realtek HD Audio over system default ({default_device['name']})")
                self.device_index = realtek_index
            else:
                log_event("AUDIO", f"Realtek not found, falling back to system default: {default_device['name']}")
                self.device_index = default_device['index']

            # Record hardware intel
            self.device_info = {
                "default": devices[self.device_index],
                "all_devices": [d for d in devices if d['max_input_channels'] > 0]
            }
            hotswap_manager.report_state("audio", "ACTIVE", self.device_info["default"])
            return self.device_info
        except Exception as e:
            log_event("AUDIO", f"Microphone discovery failed: {e}", level="ERROR")
            return {}

    def open(self, device_index=None):
        """Initializes the selected microphone."""
        try:
            # If device_index is passed, override the discovered default
            if device_index is not None:
                self.device_index = device_index

            log_event("AUDIO", f"Using sounddevice capture on index {self.device_index}")
            return True
        except Exception as e:
            log_event("AUDIO", f"Failed to open audio stream: {e}", level="CRITICAL")
            return False

    def start_listening(self, callback=None):
        """Starts a non-blocking background listening loop with VAD (Voice Activity Detection)."""
        if self.is_listening:
            return
        self.is_listening = True

        def listen_loop():
            log_event("AUDIO", "Background listening loop (VAD) active.")

            # VAD Parameters
            SILENCE_THRESHOLD = 500  # Amplitude threshold (needs tuning based on mic)
            SILENCE_DURATION = 1.5   # Seconds of silence to trigger processing
            MIN_SPEECH_DURATION = 0.5 # Minimum speech to trigger

            buffer = []
            is_speaking = False
            last_speech_time = time.time()
            speech_start_time = 0

            try:
                def audio_callback(indata, frames, time_info, status):
                    if status:
                        log_event("AUDIO", f"Stream status: {status}", level="DEBUG")

                    # Calculate RMS amplitude
                    audio_data = (indata * 32767).astype(np.int16)
                    # Simple RMS calculation
                    rms = np.sqrt(np.mean(audio_data**2))

                    nonlocal is_speaking, last_speech_time, speech_start_time, buffer

                    if rms > SILENCE_THRESHOLD:
                        if not is_speaking:
                            is_speaking = True
                            speech_start_time = time.time()
                            log_event("AUDIO", "Speech Detected...", level="DEBUG")
                        last_speech_time = time.time()
                        buffer.append(audio_data.copy())
                    else:
                        if is_speaking:
                            # We are in the silence after speech, keep recording for context
                            buffer.append(audio_data.copy())

                            # Check for silence timeout INSIDE the callback (or use a flag)
                            # Ideally we handle timeout in the main loop, but we need to know the time.
                            # We update last_speech_time only when speaking.
                            pass

                # Start stream
                with sd.InputStream(device=self.device_index, channels=1, samplerate=self.sample_rate, callback=audio_callback):
                    while self.is_listening:
                        time.sleep(0.1)
                        if is_speaking and (time.time() - last_speech_time > SILENCE_DURATION):
                            # End of speech detected
                            duration = time.time() - speech_start_time
                            if duration >= MIN_SPEECH_DURATION:
                                log_event("AUDIO", "Silence detected. Processing speech chunk...")
                                # Concatenate buffer safely
                                if buffer:
                                    full_audio = np.concatenate(buffer)
                                    buffer = [] # Clear buffer
                                    is_speaking = False

                                    # Process in a separate thread to not block the VAD?
                                    # For CLI, blocking is fine for now, or use the callback directly.
                                    self._process_audio_data(full_audio, callback)
                            else:
                                # Too short, discard
                                buffer = []
                                is_speaking = False

            except Exception as e:
                log_event("AUDIO", f"Stream Error: {e}", level="ERROR")
                self.is_listening = False

        self.listen_thread = threading.Thread(target=listen_loop, daemon=True)
        self.listen_thread.start()

    def _process_audio_data(self, audio_data, callback):
        """Helper to process raw numpy audio data with Whisper."""
        try:
             # creating wav in memory
            byte_io = io.BytesIO()
            with wave.open(byte_io, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_data.tobytes())

            byte_io.seek(0)

            with sr.AudioFile(byte_io) as source:
                recorded_audio = self.recognizer.record(source)

            # Recognize
            try:
                # Prioritize Whisper if available, else Google
                # Note: recognize_whisper might download the model on first run.
                text = self.recognizer.recognize_whisper(recorded_audio)
                log_event("AUDIO", f"Whisper Symbol: {text}", modality="audio")
                if text.strip() and callback:
                    callback(text)
            except Exception as e:
                log_event("AUDIO", f"Whisper Failed ({e}), trying Fallback...", level="WARNING")
                try:
                    text = self.recognizer.recognize_google(recorded_audio)
                    log_event("AUDIO", f"Google Symbol: {text}", modality="audio")
                    if text.strip() and callback:
                        callback(text)
                except Exception:
                    log_event("AUDIO", "Speech could not be understood.", level="DEBUG")

        except Exception as e:
            log_event("AUDIO", f"Processing Error: {e}", level="ERROR")

    def play_file(self, file_path):
        """Plays an audio file using ffplay (headless)."""
        import subprocess
        try:
            subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", file_path], check=True)
            return True
        except Exception as e:
            log_event("AUDIO", f"Playback failed: {e}", level="WARNING")
            return False

    def stop_listening(self):
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=2)
        log_event("AUDIO", "Audio capture deactivated.")

    def close(self):
        self.stop_listening()

if __name__ == "__main__":
    audio = OrbCloudAudio()
    audio.discover_microphones()
    if audio.open():
        print("Listening for 10 seconds...")
        audio.start_listening(lambda t: print(f"Heard: {t}"))
        time.sleep(10)
        audio.stop_listening()
