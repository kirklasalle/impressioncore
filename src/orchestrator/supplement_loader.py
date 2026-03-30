import os
import sys
from typing import Any

import requests
import torch

# Add project root to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.orchestrator.system_logger import log_event


class MiniOmniLoader:
    """
    Teacher/Supplement Loader for Mini-Omni2 (0.5B).
    Provides multimodal teacher signals to the Triad.
    """

    def __init__(self, model_name: str = "mini-omni2"):
        self.model_name = model_name
        self.is_loaded = False
        self.api_base = "http://localhost:11434/api" # Default Ollama

    def load(self):
        """Prepares the Mini-Omni2 model session."""
        log_event("SUPPLEMENT", f"Loading teacher model: {self.model_name}")
        # In a real setup, this would check Ollama or load a local GGUF/PyTorch model
        self.is_loaded = True
        return True

    def get_teacher_signal(self, prompt: str, sensory_ctx: dict[str, Any]) -> str:
        """
        Requests a high-level reasoning signal from the teacher model via Ollama.
        """
        if not self.is_loaded:
            return "(LOG \"Teacher model not loaded.\")"

        log_event("SUPPLEMENT", f"Requesting teacher signal for: {prompt[:30]}...")

        payload = {
            "model": self.model_name,
            "prompt": f"As a multimodal teacher, provide a Nexus-style command to guide a small AI triad based on this context: {prompt}. Sensory context: {sensory_ctx}",
            "stream": False
        }

        try:
            response = requests.post(f"{self.api_base}/generate", json=payload, timeout=5)
            if response.status_code == 200:
                signal = response.json().get("response", "")
                # Ensure it's wrapped in Nexus notation if not already
                if not signal.strip().startswith("("):
                    signal = f"(TEACHER-GUIDANCE \"{signal}\")"
                return signal
        except Exception as e:
            log_event("SUPPLEMENT", f"Ollama connection failed, falling back to simulation: {e}", level="WARNING")

        # Fallback simulation
        return f"(TEACHER-GUIDANCE \"Focus on the {sensory_ctx.get('modality', 'general')} patterns. Priority: Spatial Consistency (SIMULATED).\")"

    def process_sensory_supplement(self, vision_features: torch.Tensor, audio_features: torch.Tensor | None = None):
        """
        Directly processes raw sensory features for the supplement layer.
        """
        # Simulation of direct chipset frame reading / GPU acceleration
        log_event("SUPPLEMENT", "Processing high-bandwidth sensory supplement",
                  payload={"vision_dim": list(vision_features.shape)})

        return torch.randn(1, 64) # Latent supplement vector

if __name__ == "__main__":
    loader = MiniOmniLoader()
    loader.load()
    print(loader.get_teacher_signal("Hello", {"modality": "vision"}))
