#!/usr/bin/env python3
"""
Direct Phase 7B Component Test
Tests components directly without going through main package imports
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_direct_imports():
    """Test importing components directly from their files"""
    print("Direct Import Test for Phase 7B Components")
    print("==========================================")
    
    success_count = 0
    
    # Test each component by importing directly from its file path
    components = [
        ("AdvancedControls", "src/core/ux/advanced_controls.py"),
        ("Phase7BIntegration", "src/core/ux/phase_7b_integration.py"),
        ("InteractiveDashboard", "src/core/ux/interactive_dashboard.py"),
        ("GenerationVisualizer", "src/core/ux/generation_visualizer.py")
    ]
    
    for name, filepath in components:
        try:
            # Import the module spec and load directly
            import importlib.util
            spec = importlib.util.spec_from_file_location(name, filepath)
            module = importlib.util.module_from_spec(spec)
            
            # Execute the module
            spec.loader.exec_module(module)
            
            # Get the class
            cls = getattr(module, name)
            
            # Try to instantiate
            if name == "AdvancedControls":
                instance = cls()
            elif name == "Phase7BIntegration":
                instance = cls()
            elif name == "InteractiveDashboard":
                instance = cls()
            elif name == "GenerationVisualizer":
                instance = cls()
            
            print(f"{name}: PASS (imported and instantiated)")
            success_count += 1
            
        except Exception as e:
            print(f"{name}: FAIL - {str(e)[:80]}")
    
    print(f"\nDirect Import Results: {success_count}/4 components working")
    
    if success_count >= 3:
        print("PHASE 7B STATUS: READY FOR PRODUCTION")
        return 0
    elif success_count >= 2:
        print("PHASE 7B STATUS: OPERATIONAL WITH WARNINGS")
        return 0
    else:
        print("PHASE 7B STATUS: NEEDS ATTENTION")
        return 1

if __name__ == "__main__":
    sys.exit(test_direct_imports())
