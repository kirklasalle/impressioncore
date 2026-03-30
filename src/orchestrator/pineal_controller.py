import sys
import time
from pathlib import Path
from typing import Any

# Fix path for script execution
if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent.parent))

from src.orchestrator.sensory_hot_swap import hotswap_manager
from src.orchestrator.system_logger import log_event
from src.orchestrator.unified_triad import UnifiedBrainTriad


class PinealController:
    """
    Pineal LLM / Pituitary System Manager.
    The "Executive" layer that orchestrates the Triad, hardware, and user interaction.
    """

    def __init__(self, config_path: str = "src/core/src/core/config/nano_triad_config.json"):
        self.triad = UnifiedBrainTriad(config_path)
        self.is_active = False
        self.session_start = time.time()

        # Subscribe to Hardware Events
        hotswap_manager.register_callback(self._on_hardware_event)

    def _on_hardware_event(self, layer: str, state: str, metadata: dict[str, Any]):
        """Injects hardware state changes into the system log/context."""
        log_event("PINEAL", f"EVENT INTERCEPT: {layer} is now {state}")
        # In a full implementation, this would push a 'System Event' to the Triad's context window.

    def start_system(self):
        """Initializes hardware and begins executive monitoring."""
        log_event("PINEAL", "Executive System Starting...")

        # 1. Run PnP Diagnostics
        self.triad.vision.run_pnp_scan()
        self.triad.vision.diag_pseye()

        # 2. Open Vision layer (Live Hardware only)
        hw_ok = self.triad.vision.open()

        # 3. Open Audio layer
        self.triad.audio.discover_microphones()
        self.triad.audio.open()

        if not hw_ok:
            log_event("PINEAL", "Vision hardware not live, proceeding in text/audio mode.", level="WARNING")

        self.is_active = True
        log_event("PINEAL", "Executive System Online (LIVE).")
        return True

    def process_user_intent(self, user_prompt: str, sensory_symbols: dict[str, Any] | None = None):
        """
        The main interaction loop.
        Sends intent to the Triad and executes returned commands.
        """
        if not self.is_active:
            return "System offline."

        log_event("PINEAL", f"Executing user intent: {user_prompt}")

        # 1. Run Triad Generation
        result = self.triad.generate(user_prompt, sensory_data=sensory_symbols)

        # 2. Executive Decision (In a full implementation, Pineal would judge 'fidelity')
        response = result["response"]

        # 3. Hardware Feedback
        pos = result["avatar_update"]["commands"][0]["data"]
        log_event("PINEAL", f"Avatar Synchronized at {pos}", level="DEBUG")

        return {
            "text": response,
            "status": "EXECUTED",
            "metadata": result
        }

    def shutdown(self):
        """Graceful shutdown of all subsystems."""
        log_event("PINEAL", "Shutting down executive system...")
        self.triad.vision.close()
        self.triad.audio.close()
        self.is_active = False

if __name__ == "__main__":
    # Final Build Integration Entry
    import argparse
    parser = argparse.ArgumentParser(description="ImpressionCore Pineal Executive Controller")
    parser.add_argument("--real-hw", action="store_true", help="Try to force real hardware use")
    args = parser.parse_args()

    pineal = PinealController()

    # We NO LONGER force simulation here.
    # System will attempt real hardware and sideline if missing.

    if pineal.start_system():
        log_event("PINEAL", "Integration Test: Running framework loop...")
        res = pineal.process_user_intent("Calibrate all sensory scaffolding.", {"moondream": "System is ready."})
        print(f"\n[FINAL RESPONSE]: {res['text']}")

        # Verify hardware awareness in output
        intel = res["metadata"].get("hardware_intelligence", {})
        if intel:
            pnp_count = len(intel.get("vision", {}).get("pnp_inventory", [])) or len(intel.get("pnp_inventory", []))
            print(f"Hardware Intelligence: {pnp_count} devices mapped.")
            vision_meta = intel.get("vision", {}).get("metadata", {})
            if -1 in vision_meta:
                print(f"Vision Status: {vision_meta[-1]['status']}")

            audio_info = intel.get("audio", {})
            if audio_info:
                print(f"Audio Status: {audio_info.get('default', {}).get('name', 'N/A')} active.")

        # Test Speech Synthesis
        print("\n[TESTING SPEECH SYNTHESIS]...")
        pineal.triad.speak("Sensory scaffolding calibrated. Audio intelligence is now integrated.")

        pineal.shutdown()
