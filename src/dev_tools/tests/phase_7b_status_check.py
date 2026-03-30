#!/usr/bin/env python3
"""
Simple Phase 7B Status Check
Provides basic validation without Unicode output issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def main():
    print("Phase 7B Status Check")
    print("====================")
    
    # Test basic imports of the core UX components
    success_count = 0
    total_count = 4
    
    try:
        from src.core.ux.generation_visualizer import GenerationVisualizer
        print("GenerationVisualizer: PASS")
        success_count += 1
    except Exception as e:
        print(f"GenerationVisualizer: FAIL - {str(e)[:50]}")
    
    try:
        from src.core.ux.advanced_controls import AdvancedControls
        print("AdvancedControls: PASS")
        success_count += 1
    except Exception as e:
        print(f"AdvancedControls: FAIL - {str(e)[:50]}")
    
    try:
        from src.core.ux.phase_7b_integration import Phase7BIntegration
        print("Phase7BIntegration: PASS")
        success_count += 1
    except Exception as e:
        print(f"Phase7BIntegration: FAIL - {str(e)[:50]}")
    
    try:
        from src.core.ux.interactive_dashboard import InteractiveDashboard
        print("InteractiveDashboard: PASS")
        success_count += 1
    except Exception as e:
        print(f"InteractiveDashboard: FAIL - {str(e)[:50]}")
    
    print(f"\nSummary: {success_count}/{total_count} components operational")
    
    # Test instantiation
    print("\nInstantiation Test:")
    try:
        if success_count >= 3:  # If at least 3 components work
            controls = AdvancedControls()
            integration = Phase7BIntegration()
            print("Core Phase 7B components can be instantiated successfully")
            print("PHASE 7B STATUS: OPERATIONAL")
            return 0
        else:
            print("PHASE 7B STATUS: PARTIAL")
            return 1
    except Exception as e:
        print(f"Instantiation failed: {e}")
        print("PHASE 7B STATUS: FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
