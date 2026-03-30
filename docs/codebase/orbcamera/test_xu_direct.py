"""
Direct XUController Debug Test
================================
Tests the XUController with verbose logging to identify protocol issues.
"""
import logging
import time

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')
logger = logging.getLogger(__name__)

from orbcam.logitech.xu_control import XUController


def main():
    print("=" * 60)
    print("  Direct XUController Debug Test")
    print("=" * 60)
    
    xu = XUController()
    
    print(f"\nXU State:")
    print(f"  _ks_control: {xu._ks_control is not None}")
    print(f"  _ks_property_set: {xu._ks_property_set is not None}")
    print(f"  _working_guid: {xu._working_guid}")
    
    if xu._ks_control is None and xu._ks_property_set is None:
        print("\nERROR: No working interface found!")
        return 1
    
    # Test 1: Reset (simplest command)
    print("\n--- Test 1: RESET ---")
    result = xu.reset()
    print(f"Reset result: {result}")
    time.sleep(2)
    
    # Test 2: Move relative with logging
    print("\n--- Test 2: MOVE RELATIVE (Pan Right) ---")
    result = xu.move_relative(100, 0)
    print(f"Move result: {result}")
    time.sleep(1.5)
    
    # Test 3: Move relative opposite direction
    print("\n--- Test 3: MOVE RELATIVE (Pan Left) ---")
    result = xu.move_relative(-100, 0)
    print(f"Move result: {result}")
    
    print("\n" + "=" * 60)
    print("  Did you see ANY camera movement?")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
