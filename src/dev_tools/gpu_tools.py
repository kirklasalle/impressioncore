#!/usr/bin/env python3
"""
ImpressionCore: GPU Tools Setup

Easy access script for GPU diagnostics and monitoring tools.

File: src/dev_tools/gpu_tools.py
Created: 2025-01-06
Modified: 2025-01-06
"""

import argparse
import subprocess
import sys
from pathlib import Path

def run_diagnostics():
    """Run GPU diagnostics"""
    script_path = Path(__file__).parent / "gpu_diagnostics.py"
    subprocess.run([sys.executable, str(script_path)])

def run_monitor(args):
    """Run VRAM monitor with arguments"""
    script_path = Path(__file__).parent / "vram_monitor.py"
    cmd = [sys.executable, str(script_path)]
    
    if args.interval:
        cmd.extend(["-i", str(args.interval)])
    if args.duration:
        cmd.extend(["-d", str(args.duration)])
    if args.log_file:
        cmd.extend(["-l", args.log_file])
    
    subprocess.run(cmd)

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ImpressionCore GPU Tools - Easy access to GPU diagnostics and monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available commands:
  diagnostics    Run comprehensive GPU diagnostics
  monitor        Run real-time VRAM monitoring

Examples:
  python gpu_tools.py diagnostics
  python gpu_tools.py monitor
  python gpu_tools.py monitor -d 60 -i 0.5
  python gpu_tools.py monitor -l gpu_usage.log
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Diagnostics command
    diag_parser = subparsers.add_parser("diagnostics", help="Run GPU diagnostics")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Run VRAM monitor")
    monitor_parser.add_argument("-i", "--interval", type=float, help="Monitoring interval in seconds")
    monitor_parser.add_argument("-d", "--duration", type=float, help="Monitoring duration in seconds")
    monitor_parser.add_argument("-l", "--log-file", type=str, help="Log file path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "diagnostics":
        run_diagnostics()
    elif args.command == "monitor":
        run_monitor(args)

if __name__ == "__main__":
    main()
