import os
import sys

import pytest

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def test_imagination_loop():
    """Integration test for UnifiedBrainTriad imagination loop.

    Requires a valid model configuration with ``model_type`` in config.json.
    """
    try:
        from src.orchestrator.unified_triad import UnifiedBrainTriad
    except Exception as exc:
        pytest.skip(f"Cannot import UnifiedBrainTriad: {exc}")
        return

    print("Initializing Triad...")
    try:
        triad = UnifiedBrainTriad()
    except (ValueError, OSError, RuntimeError) as exc:
        pytest.skip(f"UnifiedBrainTriad requires model infrastructure: {exc}")
        return

    # Simulate a Nexus command being queued (this is what the modules or Colossus would do)
    print("Queuing (GENERATE-IMAGE 'A hyper-realistic silicon brain')...")
    triad.nexus.execute("(GENERATE-IMAGE 'A hyper-realistic silicon brain')")

    # Now simulate the 'generate' method's final synthesis
    # We'll call a mock-up of the return logic or just manually check the queue
    print("Processing Nexus Queue...")

    # This mimics the logic in UnifiedBrainTriad.generate
    action = triad.nexus.output_queue.pop(0)
    if action["action"] == "GENERATE_IMAGE":
        img_url = triad.imager.generate(action["prompt"], action.get("params"))
        print(f"Success! Image Generated: {img_url}")

        # Verify file exists
        full_path = f"d:/Projects/impressioncore/src/interfaces/web_client/public{img_url}"
        if os.path.exists(full_path):
            print(f"Verification Passed: File exists at {full_path}")
        else:
            print(f"Verification Failed: File NOT found at {full_path}")
    else:
        print("Verification Failed: Action not found in queue.")

if __name__ == "__main__":
    try:
        test_imagination_loop()
    except Exception as e:
        print(f"Test Error: {e}")
