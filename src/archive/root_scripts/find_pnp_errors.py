import json

def find_errors():
    with open("pnp_dump.json", "r") as f:
        data = json.load(f)

    errors = [d for d in data if d.get("status") != "OK"]
    print(f"Found {len(errors)} devices with non-OK status")
    for d in errors:
        print(f"  - {d['name']} Status: {d['status']} ID: {d['device_id']}")

    unknowns = [d for d in data if "UNKNOWN" in str(d.get("name")).upper() or d.get("name") is None]
    print(f"\nFound {len(unknowns)} unknown/unnamed devices")
    for d in unknowns:
        print(f"  - Name: {d['name']} Service: {d['service']} ID: {d['device_id']}")

if __name__ == "__main__":
    find_errors()
