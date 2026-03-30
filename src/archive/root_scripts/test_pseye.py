
try:
    from pseyepy import Camera
    import numpy as np

    def test_pseye_multi():
        print("--- Testing PSEye Multi-Detection ---")
        # pseyepy doesn't have a direct 'list' function, but we can try opening indices
        found = []
        for i in range(5):
            try:
                cam = Camera(i)
                print(f"Index {i}: [SUCCESS] {cam}")
                found.append(i)
                cam.close()
            except Exception as e:
                print(f"Index {i}: [FAILED] {e}")

        print(f"\nSummary: Found {len(found)} PS Eye camera(s) at indices {found}")

    if __name__ == "__main__":
        test_pseye_multi()
except ImportError:
    print("pseyepy not installed")
