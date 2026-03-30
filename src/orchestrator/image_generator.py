import os
import time
from datetime import datetime

from .system_logger import log_event


class ImageGenerator:
    """
    Service for generating images based on textual prompts.
    Initially supports mock generation for pipeline verification,
    designed to be extended with Stable Diffusion or similar engines.
    """

    def __init__(self, output_dir: str = "src/interfaces/web_client/public/captures"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, prompt: str, params: dict | None = None) -> str:
        """
        Generates an image and returns the relative URL.
        """
        log_event("IMAGE-GEN", f"Generating image for prompt: {prompt}")

        # Mocking generation delay
        time.sleep(0.5)

        # In a real implementation, we would use Stable Diffusion/DALL-E here.
        # For now, we'll create a "placeholder" or copy a generic asset if it exists.
        # To make it "wow", I'll create a unique filename.
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gen_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)

        # Create a simple colored placeholder for now (or use a tool to generate a real one)
        try:
            import cv2
            import numpy as np
            # Create an abstract artistic placeholder based on prompt hash?
            img = np.zeros((512, 512, 3), dtype=np.uint8)
            cv2.putText(img, "DIGITAL IMAGINATION", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(img, f"PROMPT: {prompt[:30]}...", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            cv2.putText(img, "AI SYTHESIZED ASSET", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100), 1)

            # Add some "neural" noise
            noise = np.random.randint(0, 50, (512, 512, 3), dtype=np.uint8)
            img = cv2.add(img, noise)

            cv2.imwrite(filepath, img)
            log_event("IMAGE-GEN", f"Generated mock asset at {filepath}")
            return f"/captures/{filename}"
        except Exception as e:
            log_event("IMAGE-GEN", f"Mock Generation Failed: {e}", level="ERROR")
            return None
