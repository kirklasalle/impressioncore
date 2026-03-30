#!/usr/bin/env python
"""
Script to fix OpenCV installation with GUI support.
Run this script directly if the orbcam --fix-opencv command doesn't work.
"""
import sys
import subprocess
import importlib.util

def check_package_installed(package_name):
    """Check if a package is installed."""
    return importlib.util.find_spec(package_name) is not None

def main():
    """Fix OpenCV installation to ensure GUI support."""
    print("\nOpenCV Installer for orbcamera")
    print("===============================\n")
    
    # Check for existing installations
    opencv_installed = check_package_installed('cv2')
    if opencv_installed:
        try:
            import cv2
            print(f"Current OpenCV version: {cv2.__version__}")
            
            # Check for GUI support
            has_gui = hasattr(cv2, 'namedWindow')
            print(f"GUI Support Available: {'Yes' if has_gui else 'No'}")
            
            if has_gui:
                print("\nOpenCV already has GUI support. No fix needed.")
                return 0
        except ImportError:
            print("OpenCV is installed but cannot be imported.")
    else:
        print("OpenCV is not installed.")
    
    print("\nWill now install OpenCV with GUI support.")
    
    try:
        # Remove any existing OpenCV installations
        print("\nRemoving any existing OpenCV installations...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', 
                              'opencv-python', 'opencv-python-headless'])
        
        # Install the contrib version with GUI support
        print("\nInstalling opencv-contrib-python...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'opencv-contrib-python'])
        
        print("\nOpenCV installation complete!")
        print("\nPlease restart your terminal and application for changes to take effect.")
        return 0
    except Exception as e:
        print(f"\nError during installation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
