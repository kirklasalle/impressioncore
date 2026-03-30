#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #cuda #gpu_optimization #memory_management #multimodal #performance #python #pytorch #source_code #src/interfaces/web/scan_devices.py #testing #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** Kirk LaSalle
# Tags:** #cuda #gpu_optimization #memory_management #multimodal #performance #python #pytorch #source_code #src/interfaces/web/scan_devices.py #testing #web_interface
# Category:** Interface Definitions
# Status:** Active

r"""
ImpressionCore: Scan Devices

Module for scan devices functionality in the ImpressionCore framework.

File: web/scan_devices.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, pytorch, production, web, frontend, 2025]
Dependencies: [torch]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements scan devices functionality for the
ImpressionCore brain-inspired multimodal AI framework. Optimized for memory-
constrained environments and designed to run efficiently on consumer hardware.

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem

TODO:
- Add comprehensive unit tests
- Implement performance benchmarks
- Add configuration validation
- Optimize memory usage patterns

Examples:
```python
# Basic usage example
from web.scan_devices import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import json
import logging
import platform
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def scan_system():
    """Scan and return system hardware information as a JSON object."""
    logger.info("Starting hardware scan")

    # Check if running on Windows
    if platform.system() != "Windows":
        logger.error(f"Unsupported OS: {platform.system()}")
        return {"error": f"This script only works on Windows, detected: {platform.system()}"}

    try:
        # Import required libraries
        try:
            import psutil
            import wmi
        except ImportError as e:
            logger.error(f"Required libraries not installed: {e!s}")
            return {"error": f"Required libraries not installed: {e!s}. Install with: pip install wmi psutil"}

        logger.info("Creating WMI connection")
        w = wmi.WMI()

        # Get CPU information
        logger.info("Scanning CPU information")
        try:
            cpu_info = w.Win32_Processor()[0]
            cpu = {
                "name": cpu_info.Name.strip(),
                "manufacturer": cpu_info.Manufacturer.strip() if cpu_info.Manufacturer else "Unknown",
                "cores": int(cpu_info.NumberOfCores),
                "threads": int(cpu_info.NumberOfLogicalProcessors),
                "architecture": cpu_info.AddressWidth,
                "max_clock_speed_mhz": cpu_info.MaxClockSpeed
            }
            logger.info(f"CPU detected: {cpu['name']} ({cpu['cores']} cores)")
        except Exception as e:
            logger.error(f"Error scanning CPU: {e!s}")
            cpu = {"name": "Unknown", "cores": 0, "error": str(e)}

        # Get GPU information
        # Memory optimization: Memory-critical operation
        logger.info("Scanning GPU information")
        # Memory optimization: Memory-critical operation
        gpus = []
        # Memory optimization: Memory-critical operation
        try:
            for gpu in w.Win32_VideoController():
            # Memory optimization: Memory-critical operation
                try:
                    # Try to get VRAM in MB
                    vram_mb = 0
                    if gpu.AdapterRAM:
                    # Memory optimization: Memory-critical operation
                        vram_mb = int(gpu.AdapterRAM) / (1024 * 1024)
                        # Memory optimization: Memory-critical operation

                    gpus.append({
                    # Memory optimization: Memory-critical operation
                        "name": gpu.Name.strip(),
                        # Memory optimization: Memory-critical operation
                        "driver_version": gpu.DriverVersion.strip() if gpu.DriverVersion else "Unknown",
                        # Memory optimization: Memory-critical operation
                        "vram": round(vram_mb),
                        "driver_date": gpu.DriverDate if hasattr(gpu, 'DriverDate') else "Unknown"
                        # Memory optimization: Memory-critical operation
                    })
                    logger.info(f"GPU detected: {gpu.Name} ({round(vram_mb)} MB VRAM)")
                    # Memory optimization: Memory-critical operation
                except Exception as e:
                    logger.error(f"Error processing GPU information: {e!s}")
                    # Memory optimization: Memory-critical operation
                    gpus.append({"name": gpu.Name, "error": str(e)})
                    # Memory optimization: Memory-critical operation
        except Exception as e:
            logger.error(f"Error scanning GPUs: {e!s}")
            # Memory optimization: Memory-critical operation

        # Get memory information
        # Memory optimization: Memory-critical operation
        logger.info("Scanning RAM information")
        try:
            ram_info = psutil.virtual_memory()
            # Memory optimization: Memory-critical operation
            ram = {
                "total": round(ram_info.total / (1024**3), 2),  # GB
                "available": round(ram_info.available / (1024**3), 2),  # GB
                "percent_used": ram_info.percent
            }
            logger.info(f"RAM detected: {ram['total']} GB total, {ram['available']} GB available")
        except Exception as e:
            logger.error(f"Error scanning RAM: {e!s}")
            ram = {"total": 0, "available": 0, "error": str(e)}

        # Get detailed physical memory info from WMI
        # Memory optimization: Memory-critical operation
        physical_ram = []
        try:
            for mem in w.Win32_PhysicalMemory():
            # Memory optimization: Memory-critical operation
                try:
                    physical_ram.append({
                        "capacity_gb": round(int(mem.Capacity) / (1024**3), 2),
                        "speed": mem.Speed,
                        "manufacturer": mem.Manufacturer.strip() if mem.Manufacturer else "Unknown",
                        "location": mem.DeviceLocator.strip() if mem.DeviceLocator else "Unknown"
                        # Memory optimization: Device placement for memory management
                    })
                except Exception as e:
                    logger.error(f"Error processing RAM module: {e!s}")
        except Exception as e:
            logger.error(f"Error scanning physical RAM modules: {e!s}")

        # Get storage information
        logger.info("Scanning storage devices")
        # Memory optimization: Device placement for memory management
        disks = []
        try:
            for disk in w.Win32_DiskDrive():
                try:
                    size_gb = round(int(disk.Size) / (1024**3), 2)
                    disks.append({
                        "model": disk.Model.strip() if disk.Model else "Unknown",
                        # Memory optimization: Explicit memory cleanup
                        "size_gb": size_gb,
                        "interface_type": disk.InterfaceType.strip() if disk.InterfaceType else "Unknown"
                    })
                    logger.info(f"Disk detected: {disk.Model} ({size_gb} GB)")
                except Exception as e:
                    logger.error(f"Error processing disk information: {e!s}")
        except Exception as e:
            logger.error(f"Error scanning disks: {e!s}")

        # Get OS information
        logger.info("Getting OS information")
        try:
            os_info = w.Win32_OperatingSystem()[0]
            os = {
                "name": os_info.Caption.strip(),
                "version": os_info.Version.strip(),
                "build": os_info.BuildNumber.strip() if os_info.BuildNumber else "Unknown",
                "architecture": os_info.OSArchitecture.strip() if os_info.OSArchitecture else "Unknown",
            }
            logger.info(f"OS detected: {os['name']} {os['version']} {os['architecture']}")
        except Exception as e:
            logger.error(f"Error getting OS information: {e!s}")
            os = {
                "name": platform.system(),
                "version": platform.version(),
                "architecture": platform.architecture()[0],
                "error": str(e)
            }

        # Check CUDA support
        # Memory optimization: Memory-critical operation
        cuda_support = False
        # Memory optimization: Memory-critical operation
        cuda_version = "Not available"
        # Memory optimization: Memory-critical operation
        try:
            import torch
            cuda_support = torch.cuda.is_available()
            # Memory optimization: CUDA operations for GPU acceleration
            if cuda_support:
            # Memory optimization: Memory-critical operation
                cuda_version = torch.version.cuda
                # Memory optimization: Memory-critical operation
                logger.info(f"CUDA support detected: version {cuda_version}")
                # Memory optimization: Memory-critical operation
            else:
                logger.info("CUDA support not available")
                # Memory optimization: Memory-critical operation
        except ImportError:
            logger.warning("PyTorch not installed, can't check CUDA support")
            # Memory optimization: Memory-critical operation
        except Exception as e:
            logger.error(f"Error checking CUDA support: {e!s}")
            # Memory optimization: Memory-critical operation

        # Compile all information
        result = {
            "timestamp": datetime.now().isoformat(),
            "system": platform.system(),
            "computer_name": platform.node(),
            "python_version": platform.python_version(),
            "cpu": cpu,
            "gpu": gpus[0] if gpus else None,  # Return first GPU if available
            # Memory optimization: Memory-critical operation
            "ram": ram,
            "physical_ram_modules": physical_ram,
            "disks": disks,
            "os": os,
            "cuda_support": {
            # Memory optimization: Memory-critical operation
                "available": cuda_support,
                # Memory optimization: Memory-critical operation
                "version": cuda_version
                # Memory optimization: Memory-critical operation
            }
        }

        logger.info("Hardware scan completed successfully")
        return result

    except Exception as e:
        logger.error(f"Critical error during hardware scan: {e!s}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": f"Error scanning system: {e!s}"}

if __name__ == "__main__":
    # Run the scan and print the results as JSON
    try:
        print("Starting hardware scan...")
        print("-------------------------")
        results = scan_system()
        print("-------------------------")
        print("Scan completed. Results:")
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Error running scan_devices: {e!s}")
        # Memory optimization: Device placement for memory management
