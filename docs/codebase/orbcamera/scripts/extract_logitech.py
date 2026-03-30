"""
Extracts and analyzes Logitech camera control functionality from installed software.
This will help identify the necessary components for camera control.
"""
import os
import sys
import argparse
import logging
import json
from pathlib import Path

# Ensure we can import our packages
sys.path.insert(0, str(Path(__file__).parent.parent))
from orbcam.logitech.scanner import LogitechSoftwareScanner

def setup_logging(verbose=False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, 
                       format='%(levelname)s: %(message)s')

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Extract and analyze Logitech camera software')
    parser.add_argument('-p', '--path', default='G:\\',
                       help='Base path for the Logitech software (default: G:\\)')
    parser.add_argument('-o', '--output', default='logitech_analysis.json',
                       help='Output file for the analysis results (default: logitech_analysis.json)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    args = parser.parse_args()

    setup_logging(args.verbose)
    logging.info(f"Analyzing Logitech software at: {args.path}")
    
    # Create scanner and scan for files
    scanner = LogitechSoftwareScanner(args.path)
    found_files = scanner.scan_directory()
    
    # Get the best DLL for camera control
    best_dll = scanner.find_camera_control_module()
    
    # Output summary
    logging.info("\nAnalysis Summary:")
    logging.info(f"DLLs found: {len(found_files.get('dlls', []))}")
    logging.info(f"Executables found: {len(found_files.get('exe', []))}")
    logging.info(f"Configuration files found: {len(found_files.get('configs', []))}")
    
    if best_dll:
        logging.info(f"\nBest camera control DLL: {best_dll}")
        dll_info = scanner.analyze_dll(best_dll)
    else:
        logging.warning("No suitable camera control DLL found")
        dll_info = {}
    
    # Save analysis results
    analysis = {
        'scan_path': args.path,
        'files_found': {k: [str(p) for p in v] for k, v in found_files.items()},
        'best_dll': str(best_dll) if best_dll else None,
        'dll_info': dll_info
    }
    
    with open(args.output, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    logging.info(f"\nAnalysis saved to: {args.output}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
