import os
import sys

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.orchestrator.unified_triad import UnifiedBrainTriad


def start_interactive_session():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--voice", action="store_true", help="Enable Voice Input/Output")
    parser.add_argument("--vision", action="store_true", help="Enable Vision (Camera) Input")
    args = parser.parse_args()

    # Setup
    print("\n" + "="*60)
    print("ImpressionCore B3-Triad: Interactive Inference Test")
    print("="*60)
    print("Initializing Unified Brain Triad (Qwen-Nano)...")

    try:
        triad = UnifiedBrainTriad()
        print("SUCCESS: Triad Architecture Online.")
        print(f"Device: {triad.device}")
        print(f"Loading Mode: {'SIMULTANEOUS' if triad.simultaneous_load else 'SEQUENTIAL'}")

        # Initialize Vision if requested
        if args.vision:
            print("Initializing Vision System (OrbCloud)...")
            if triad.vision and triad.vision.open():
                print("Vision System: ONLINE (Cameras Active)")
            else:
                print("Vision System: FAILED (No Cameras or Error)")
        else:
            print("Vision System: STANDBY (Use --vision to activate)")

    except Exception as e:
        print(f"\nCRITICAL ERROR: Failed to initialize Triad: {e}")
        return

    print("\nType 'quit' to exit.")
    print("-" * 60)



    # Chat Loop
    if args.voice and triad.audio:
        print("\n[VOICE MODE]: Active. Speak into the microphone...")
        triad.speak("Voice systems online. I am listening.")

        def voice_callback(text):
            if not text.strip():
                return
            print(f"\n[USER (Voice)]: {text}")
            print(f"[TRIAD PROCESSING] Broadcasting to {triad.device}...")

            try:
                # Generate
                result = triad.generate(text)

                # Monitor
                print("\n" + "-"*20 + " INTERNAL MONITORS " + "-"*20)
                print(f"[LEFT]:   {result['internal_monitors']['left_hemisphere']}")
                print(f"[RIGHT]: {result['internal_monitors']['right_hemisphere']}")
                print("-" * 60)

                # Response
                response_text = result['response']
                print(f"[COLOSSUS]: {response_text}")
                print("=" * 60)

                # Speak
                triad.speak(response_text)

                # Reset Prompt
                print("\n[USER]: ", end="", flush=True)

            except Exception as e:
                print(f"Error: {e}")

        triad.audio.start_listening(voice_callback)

    while True:
        try:
            user_input = input("\n[USER]: ")
            if user_input.lower() in ["quit", "exit"]:
                break

            print(f"\n[TRIAD PROCESSING] Broadcasting to {triad.device}...")

            # Generate Response
            result = triad.generate(user_input)

            # Display Internal States (The "Thought Process")
            print("\n" + "-"*20 + " INTERNAL MONITORS " + "-"*20)
            print(f"[LEFT HEMI (Logic)]:   {result['internal_monitors']['left_hemisphere']}")
            print(f"[RIGHT HEMI (Empathy)]: {result['internal_monitors']['right_hemisphere']}")
            print("-" * 60)

            # Display Final Colossus Output
            print(f"[COLOSSUS (Response)]: {result['response']}")
            triad.speak(result['response']) # Speak output even in text mode if audio is valid
            print("=" * 60)

        except KeyboardInterrupt:
            print("\nSession interrupted.")
            break
        except Exception as e:
            print(f"\nError during generation: {e}")

if __name__ == "__main__":
    start_interactive_session()
