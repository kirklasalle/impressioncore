#!/usr/bin/env python3
"""
ImpressionCore: Real-time VRAM Monitor

A lightweight real-time VRAM monitoring utility for the GTX 1050 Ti,
designed to help optimize memory usage during training and development.

File: src/dev_tools/vram_monitor.py
Created: 2025-01-06
Modified: 2025-01-06
"""

import argparse
import json
import os
import signal
import sys
import time
import torch
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

try:
    from core.utils.rich_enhancements import create_progress, create_panel
    from core.utils.rich_logging import setup_rich_logging
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

class VRAMMonitor:
    """Real-time VRAM monitoring utility"""
    
    def __init__(self, interval: float = 1.0, log_file: Optional[str] = None):
        """Initialize VRAM monitor
        
        Args:
            interval: Monitoring interval in seconds
            log_file: Optional log file path for data recording
        """
        self.interval = interval
        self.log_file = log_file
        self.running = False
        self.data_points = []
        
        # Initialize CUDA
        self.cuda_available = torch.cuda.is_available()
        self.device_count = torch.cuda.device_count() if self.cuda_available else 0
        
        # Initialize NVIDIA ML
        self.nvml_initialized = False
        if PYNVML_AVAILABLE and self.cuda_available:
            try:
                pynvml.nvmlInit()
                self.nvml_initialized = True
            except Exception:
                pass
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down VRAM monitor...")
        self.running = False
    
    def get_memory_info(self) -> Dict:
        """Get current memory information"""
        if not self.cuda_available:
            return {"error": "CUDA not available"}
        
        info = {
            "timestamp": datetime.now().isoformat(),
            "devices": []
        }
        
        for device_id in range(self.device_count):
            torch.cuda.set_device(device_id)
            
            device_info = {
                "device_id": device_id,
                "name": torch.cuda.get_device_name(device_id),
                "allocated_mb": torch.cuda.memory_allocated(device_id) / 1e6,
                "reserved_mb": torch.cuda.memory_reserved(device_id) / 1e6,
                "max_allocated_mb": torch.cuda.max_memory_allocated(device_id) / 1e6,
                "max_reserved_mb": torch.cuda.max_memory_reserved(device_id) / 1e6,
            }
            
            # Get total memory
            props = torch.cuda.get_device_properties(device_id)
            device_info["total_mb"] = props.total_memory / 1e6
            device_info["free_mb"] = device_info["total_mb"] - device_info["allocated_mb"]
            device_info["utilization_percent"] = (device_info["allocated_mb"] / device_info["total_mb"]) * 100
            
            # Add NVIDIA ML info if available
            if self.nvml_initialized:
                try:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(device_id)
                    meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                    
                    device_info.update({
                        "nvml_used_mb": meminfo.used / 1e6,
                        "nvml_free_mb": meminfo.free / 1e6,
                        "gpu_utilization": utilization.gpu,
                        "memory_utilization": utilization.memory,
                        "temperature": temperature,
                    })
                except Exception:
                    pass
            
            info["devices"].append(device_info)
        
        return info
    
    def format_memory_display(self, info: Dict) -> str:
        """Format memory info for console display"""
        if "error" in info:
            return f"❌ {info['error']}"
        
        lines = []
        timestamp = datetime.fromisoformat(info["timestamp"]).strftime("%H:%M:%S")
        lines.append(f"⏰ {timestamp}")
        
        for device in info["devices"]:
            name = device["name"]
            allocated = device["allocated_mb"]
            total = device["total_mb"]
            utilization = device["utilization_percent"]
            
            # Create memory bar
            bar_width = 30
            filled = int((utilization / 100) * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            
            # Color coding based on utilization
            if utilization < 50:
                color = "🟢"
            elif utilization < 80:
                color = "🟡"
            else:
                color = "🔴"
            
            line = f"{color} {name}: {allocated:6.1f}/{total:6.1f}MB ({utilization:5.1f}%) [{bar}]"
            
            if "temperature" in device:
                line += f" {device['temperature']}°C"
                
            if "gpu_utilization" in device:
                line += f" GPU:{device['gpu_utilization']}%"
            
            lines.append(line)
        
        return "\n".join(lines)
    
    def log_data(self, info: Dict) -> None:
        """Log data to file if specified"""
        if not self.log_file:
            return
        
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(info) + "\n")
        except Exception as e:
            print(f"⚠️ Failed to write to log file: {e}")
    
    def monitor(self, duration: Optional[float] = None) -> None:
        """Start monitoring
        
        Args:
            duration: Optional monitoring duration in seconds
        """
        if not self.cuda_available:
            print("❌ CUDA not available - cannot monitor VRAM")
            return
        
        self.running = True
        start_time = time.time()
        
        print("🖥️ Starting VRAM monitoring...")
        print(f"📊 Monitoring {self.device_count} device(s) every {self.interval:.1f}s")
        if self.log_file:
            print(f"📝 Logging to: {self.log_file}")
        print("Press Ctrl+C to stop\n")
        
        try:
            while self.running:
                # Check duration limit
                if duration and (time.time() - start_time) >= duration:
                    break
                
                # Get memory info
                info = self.get_memory_info()
                self.data_points.append(info)
                
                # Display
                display = self.format_memory_display(info)
                
                # Clear screen and display (simple version)
                if os.name == 'nt':  # Windows
                    os.system('cls')
                else:  # Unix/Linux
                    os.system('clear')
                
                print("🔧 ImpressionCore VRAM Monitor")
                print("=" * 50)
                print(display)
                print("\n" + "=" * 50)
                print("💡 Tips:")
                print("• Green: < 50% usage (safe)")
                print("• Yellow: 50-80% usage (monitor closely)")
                print("• Red: > 80% usage (optimization needed)")
                print("\nPress Ctrl+C to stop monitoring")
                
                # Log data
                self.log_data(info)
                
                # Wait for next interval
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            pass
        
        self.running = False
        print("\n✅ Monitoring stopped")
        
        # Show summary
        self.show_summary()
    
    def show_summary(self) -> None:
        """Show monitoring summary"""
        if not self.data_points:
            return
        
        print("\n📈 Monitoring Summary:")
        print("-" * 30)
        
        for device_id in range(self.device_count):
            device_data = [dp["devices"][device_id] for dp in self.data_points if "devices" in dp]
            if not device_data:
                continue
            
            name = device_data[0]["name"]
            utilizations = [d["utilization_percent"] for d in device_data]
            allocated_mbs = [d["allocated_mb"] for d in device_data]
            
            print(f"🎮 {name}:")
            print(f"   Average utilization: {sum(utilizations)/len(utilizations):.1f}%")
            print(f"   Peak utilization: {max(utilizations):.1f}%")
            print(f"   Peak allocated: {max(allocated_mbs):.1f}MB")
            print(f"   Data points: {len(device_data)}")
            
            if any("temperature" in d for d in device_data):
                temps = [d["temperature"] for d in device_data if "temperature" in d]
                print(f"   Average temperature: {sum(temps)/len(temps):.1f}°C")
                print(f"   Peak temperature: {max(temps)}°C")
        
        if self.log_file and os.path.exists(self.log_file):
            print(f"\n📝 Data logged to: {self.log_file}")
            print(f"   File size: {os.path.getsize(self.log_file)} bytes")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ImpressionCore VRAM Monitor - Real-time GPU memory monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python vram_monitor.py                    # Monitor with default 1s interval
  python vram_monitor.py -i 0.5             # Monitor every 0.5 seconds
  python vram_monitor.py -d 300 -l vram.log # Monitor for 5 minutes, log to file
  python vram_monitor.py -i 2 -d 60         # Monitor every 2s for 1 minute
        """
    )
    
    parser.add_argument(
        "-i", "--interval",
        type=float,
        default=1.0,
        help="Monitoring interval in seconds (default: 1.0)"
    )
    
    parser.add_argument(
        "-d", "--duration",
        type=float,
        help="Monitoring duration in seconds (default: unlimited)"
    )
    
    parser.add_argument(
        "-l", "--log-file",
        type=str,
        help="Log file path for data recording"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.interval <= 0:
        print("❌ Error: Interval must be positive")
        sys.exit(1)
    
    if args.duration is not None and args.duration <= 0:
        print("❌ Error: Duration must be positive")
        sys.exit(1)
    
    # Initialize monitor
    monitor = VRAMMonitor(
        interval=args.interval,
        log_file=args.log_file
    )
    
    # Start monitoring
    monitor.monitor(duration=args.duration)

if __name__ == "__main__":
    main()
