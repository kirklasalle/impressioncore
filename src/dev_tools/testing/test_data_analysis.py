#!/usr/bin/env python3
"""
Test Data Analysis Script
Simple test to verify analyze_unified_data.py works without Unicode errors
"""

import subprocess
import sys


def test_data_analysis():
    """Test the data analysis script directly."""
    print("Testing analyze_unified_data.py...")
    print("-" * 40)

    try:
        # Run the analysis script and capture output
        result = subprocess.run([sys.executable, "analyze_unified_data.py"],
                              capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("SUCCESS: Data analysis script completed without errors")
            print("\nOutput:")
            print(result.stdout)
            return True
        else:
            print("ERROR: Data analysis script failed")
            print(f"Return code: {result.returncode}")
            print("\nStderr:")
            print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("ERROR: Data analysis script timed out (>30 seconds)")
        return False
    except Exception as e:
        print(f"ERROR: Failed to run data analysis script: {e}")
        return False

if __name__ == "__main__":
    success = test_data_analysis()
    if success:
        print("\n" + "="*50)
        print("CONCLUSION: Data analysis is working properly!")
        print("Ready to proceed with unified training.")
    else:
        print("\n" + "="*50)
        print("CONCLUSION: Data analysis needs more fixes.")
        print("Do not proceed with training until this is resolved.")

    exit(0 if success else 1)
