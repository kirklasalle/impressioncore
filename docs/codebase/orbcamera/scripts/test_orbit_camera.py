#!/usr/bin/env python
"""
Test script for the Logitech Orbit camera.
This script verifies if the camera is detected and can be accessed.
"""
import sys
import argparse
import logging
import traceback
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

def setup_logging(verbose=False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, 
                       format='%(levelname)s: %(message)s')
                       
def test_camera(verbose=False):
    """Test camera detection and connection."""
    try:
        from orbcam.logitech.devices import test_orbit_camera_connection
        
        # Test camera connectivity
        print("\nTesting Orbit camera connection...")
        results = test_orbit_camera_connection()
        
        if results['found']:
            print("✅ Orbit camera detected")
            print(f"Device ID: {results['device_id']}")
            
            if results['connection']:
                print("✅ Successfully connected to camera")
                if 'resolution' in results:
                    print(f"Resolution: {results['resolution']}")
            else:
                print("❌ Failed to connect to camera")
                if verbose and results.get('error'):
                    print(f"Error: {results['error']}")
        else:
            print("❌ Orbit camera not detected")
            if verbose and results.get('error'):
                print(f"Error: {results['error']}")
        
        return results['found'] and results['connection']
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        if verbose:
            traceback.print_exc()
        return False
    
def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Test Logitech Orbit camera')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    success = test_camera(args.verbose)
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
