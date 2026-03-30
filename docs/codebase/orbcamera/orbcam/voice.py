"""
OrbOS Voice Module
===================
Handles Text-to-Speech synthesis for OrbOS.

Supports:
- System TTS (pyttsx3 - offline, fast)
- OpenAI TTS API (high quality, requires API key)

Based on GuitarWizard's voice pattern.
"""

import threading
import queue
import os
import tempfile
from typing import Optional

# Optional imports
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    print("pyttsx3 not installed - offline TTS unavailable")


class OrbVoice:
    """
    Text-to-Speech engine for OrbOS.
    
    Singleton pattern with background worker thread.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OrbVoice, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def initialize(self, provider: str = "system", openai_voice: str = "onyx"):
        """
        Initialize TTS engine.
        
        Args:
            provider: 'system' for pyttsx3, 'openai' for OpenAI TTS
            openai_voice: Voice name for OpenAI (alloy, echo, fable, onyx, nova, shimmer)
        """
        if self.initialized:
            return

        self.queue = queue.Queue()
        self.is_speaking = False
        self.provider = provider
        self.openai_voice = openai_voice
        self._openai_client = None

        # Start worker thread
        self.thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.thread.start()

        self.initialized = True
        print(f"OrbOS Voice initialized (provider: {provider})")

    def speak(self, text: str):
        """Queue text to be spoken."""
        if not text or not self.initialized:
            return
        self.queue.put(text)

    def _worker_loop(self):
        """Background worker for TTS synthesis."""
        # Initialize system TTS engine
        engine = None
        if PYTTSX3_AVAILABLE:
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)  # Speed
                engine.setProperty('volume', 0.9)
                
                # Try to find a suitable voice
                voices = engine.getProperty('voices')
                for v in voices:
                    # Prefer male voices for the turret persona
                    if "David" in v.name or "Male" in v.name.lower():
                        engine.setProperty('voice', v.id)
                        break
            except Exception as e:
                print(f"pyttsx3 init error: {e}")
                engine = None

        while True:
            try:
                text = self.queue.get()
                if text is None:
                    break  # Poison pill

                self.is_speaking = True

                if self.provider == "openai":
                    self._speak_openai(text)
                elif engine:
                    engine.say(text)
                    engine.runAndWait()
                else:
                    print(f"[TTS] {text}")  # Fallback - just print

                self.is_speaking = False

            except Exception as e:
                print(f"OrbVoice error: {e}")
                self.is_speaking = False

    def _speak_openai(self, text: str):
        """Use OpenAI TTS API."""
        if self._openai_client is None:
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self._openai_client = OpenAI(api_key=api_key)
                else:
                    print("No OPENAI_API_KEY for TTS")
                    return
            except ImportError:
                print("OpenAI library not installed")
                return

        try:
            response = self._openai_client.audio.speech.create(
                model="tts-1",
                voice=self.openai_voice,
                input=text,
                response_format="mp3"
            )

            # Save and play with pygame
            try:
                import pygame
                
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)
                    temp_path = f.name

                pygame.mixer.init()
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                
                os.unlink(temp_path)
                
            except ImportError:
                print("pygame not available for audio playback")
            except Exception as e:
                print(f"Audio playback error: {e}")

        except Exception as e:
            print(f"OpenAI TTS error: {e}")

    def stop(self):
        """Stop the voice worker."""
        self.queue.put(None)


# ===== SINGLETON ACCESS =====

_voice_instance = None

def get_voice() -> OrbVoice:
    """Get or create the singleton OrbVoice instance."""
    global _voice_instance
    if _voice_instance is None:
        _voice_instance = OrbVoice()
        _voice_instance.initialize()
    return _voice_instance
