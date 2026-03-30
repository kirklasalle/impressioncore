#!/usr/bin/env python
"""
Script to find Logitech Orbit/Sphere cameras and print their information.
This script demonstrates using the devices hardware detector to find cameras.
"""
import sys
import argparse
import logging
import json
import traceback
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

def setup_logging(verbose=False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, 
                       format='%(levelname)s: %(message)s')

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Find Logitech Orbit/Sphere cameras')
    parser.add_argument('-a', '--all', action='store_true',
                       help='Show all Logitech devices (not just cameras)')
    parser.add_argument('-j', '--json', action='store_true',
                       help='Output in JSON format')
    parser.add_argument('-o', '--output', type=str,
                       help='Save output to a file')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--fallback', action='store_true',
                       help='Use fallback detection methods only')
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    try:
        # Import here to allow setup_logging to configure loggers first
        from orbcam.logitech.devices import LogitechDeviceFinder, find_logitech_cameras
        
        finder = LogitechDeviceFinder()
        
        if args.all:
            devices = finder.find_logitech_devices()
            title = "All Logitech Devices"
        else:
            devices = find_logitech_cameras()
            title = "Logitech Cameras"
        
        # Process the devices
        if args.json:
            # Convert to serializable format
            serializable_devices = []
            for device in devices:
                device_copy = device.copy()
                # Convert any non-serializable values to strings
                if 'properties' in device_copy:
                    device_copy['properties'] = {
                        k: str(v) for k, v in device_copy['properties'].items()
                    }
                serializable_devices.append(device_copy)
            
            output = json.dumps(serializable_devices, indent=2)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
            else:
                print(output)
        else:
            # Print human-readable output
            print(f"\n{title}:")
            print("=" * len(title))
            
            if not devices:
                print("No devices found.")
            
            for i, device in enumerate(devices, 1):
                name = device.get('name', 'Unknown Device')
                category = device.get('category', 'Unknown Category')
                
                print(f"\nDevice {i}: {name}")
                print("-" * (len(f"Device {i}: ") + len(name)))
                print(f"Category: {category}")
                
                if 'properties' in device:
                    print("\nProperties:")
                    for key, value in device['properties'].items():
                        print(f"  {key}: {value}")
            
            # Specifically look for Orbit camera
            orbit = finder.find_orbit_camera()
            if orbit:
                name = orbit.get('name', 'Unknown Device')
                print("\nOrbit/Sphere camera found!")
                print(f"Name: {name}")
                print(f"Category: {orbit.get('category', 'Unknown')}")
                if 'properties' in orbit:
                    device_id = orbit['properties'].get('DeviceID', 'Unknown')
                    print(f"Device ID: {device_id}")
                    
                    # Show more device details
                    print("\nDevice Details:")
                    for key, value in orbit['properties'].items():
                        if key not in ['DeviceID', 'Name', 'Caption']:
                            print(f"  {key}: {value}")
            else:
                print("\nNo Orbit/Sphere camera detected.")
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write("Output not implemented for text mode yet.")
        
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        if args.verbose:
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
