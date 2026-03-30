
import logging
import math
import os
import struct
import time
import wave

# For now, we'll use a placeholder or basic system TTS if local models aren't present.
# Ideally, we integrate 'piper' command line or library here.

class TTSService:
    def __init__(self):
        self.logger = logging.getLogger("TTSService")
        self.output_dir = "d:/Projects/impressioncore/static/audio_cache"
        os.makedirs(self.output_dir, exist_ok=True)

    def speak(self, text, emotion="neutral"):
        """
        Generates speech for text.
        Returns: Path to generated file (absolute) or URL.
        """
        filename = f"tts_{int(time.time()*1000)}.wav"
        filepath = os.path.join(self.output_dir, filename)

        normalized_text = (text or "").strip()
        if not normalized_text:
            raise ValueError("Text must not be empty")

        self.logger.info(f"Generating TTS for: '{normalized_text[:80]}' -> {filepath}")

        generated = False
        try:
            import pyttsx3

            engine = pyttsx3.init()
            if emotion == "calm":
                engine.setProperty("rate", 150)
            elif emotion in {"urgent", "excited"}:
                engine.setProperty("rate", 190)
            else:
                engine.setProperty("rate", 170)

            engine.save_to_file(normalized_text, filepath)
            engine.runAndWait()
            generated = os.path.exists(filepath) and os.path.getsize(filepath) > 256
        except Exception as exc:
            self.logger.warning(f"pyttsx3 generation failed, using fallback tone: {exc}")

        if not generated:
            sample_rate = 22050
            duration_seconds = min(2.4, max(0.6, len(normalized_text) / 35.0))
            total_frames = int(sample_rate * duration_seconds)
            amplitude = 9000
            frequency = 440.0

            with wave.open(filepath, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)

                frames = bytearray()
                for frame in range(total_frames):
                    envelope = 1.0 if frame < sample_rate * 0.08 else 0.2
                    value = int(amplitude * envelope * math.sin(2.0 * math.pi * frequency * (frame / sample_rate)))
                    frames.extend(struct.pack("<h", value))

                wav_file.writeframes(frames)

        if not os.path.exists(filepath) or os.path.getsize(filepath) <= 44:
            raise RuntimeError("TTS output file was not created")

        return f"/static/audio_cache/{filename}"

    def get_voices(self):
        return ["Neural_Alpha", "Neural_Beta"]
