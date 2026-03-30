import json

def search_pnp():
    with open("pnp_dump.json", "r") as f:
        data = json.load(f)

    ps_eye_found = []
    kinect_found = []
    orbit_found = []

    for dev in data:
        hw_id = str(dev.get("hw_id", "")).upper()
        name = str(dev.get("name", "")).upper()

        if "1415" in hw_id or "EYE" in name:
            ps_eye_found.append(dev)
        if "045E" in hw_id or "KINECT" in name:
            kinect_found.append(dev)
        if "08C2" in hw_id or "ORBIT" in name or "SPHERE" in name:
            orbit_found.append(dev)

    print(f"PS Eye search: Found {len(ps_eye_found)} matches")
    for d in ps_eye_found:
        print(f"  - {d['name']} ({d['hw_id']}) Service: {d['service']}")

    print(f"\nKinect search: Found {len(kinect_found)} matches")
    for d in kinect_found:
        print(f"  - {d['name']} ({d['hw_id']}) Service: {d['service']}")

    print(f"\nOrbit search: Found {len(orbit_found)} matches")
    for d in orbit_found:
        print(f"  - {d['name']} ({d['hw_id']}) Service: {d['service']}")

if __name__ == "__main__":
    search_pnp()
