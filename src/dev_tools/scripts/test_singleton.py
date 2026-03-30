import sys
from pathlib import Path

# Add src to path
project_root = Path(r"d:\Projects\impressioncore")
sys.path.append(str(project_root))

from src.orchestrator.orbcloud_vision import get_vision_layer


def test_singleton():
    print("Testing get_vision_layer singleton...")
    v1 = get_vision_layer()
    v2 = get_vision_layer()

    print(f"v1: {v1}")
    print(f"v2: {v2}")

    if v1 is v2:
        print("SUCCESS: get_vision_layer returns the same instance.")
    else:
        print("FAILURE: get_vision_layer returns different instances.")

if __name__ == "__main__":
    test_singleton()
