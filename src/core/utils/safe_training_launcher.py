"""
ImpressionCore Safe Training Launcher
=====================================

Comprehensive safety wrapper for training processes with:
- Automatic monitoring and safety shutdowns
- Progress tracking and checkpointing
- Resource management
- Error recovery
- Real-time status updates

Author: ImpressionCore Development Team
Created: 2025-01-13
"""

import os
import sys
import time
import json
import subprocess
import signal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading

# Add ImpressionCore modules to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.utils.rich_logging import RichLogger
from core.utils.rich_status_animation import RichStatusAnimation


class SafeTrainingLauncher:
    """
    Safe wrapper for launching and monitoring training processes
    """
    
    def __init__(self, 
                 training_script: str,
                 training_name: str = "Training",
                 log_dir: str = "src/memlog"):
        """
        Initialize safe training launcher
        
        Args:
            training_script: Path to the training script to execute
            training_name: Name for this training session
            log_dir: Directory for log files
        """
        self.training_script = Path(training_script)
        self.training_name = training_name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # State tracking
        self.process = None
        self.is_running = False
        self.start_time = None
        self.monitoring_thread = None
        
        # Safety limits
        self.max_runtime_hours = 24
        self.max_memory_gb = 28  # Leave 4GB for system
        self.max_cpu_temp = 85  # Celsius
        self.check_interval = 30  # seconds
        
        # Initialize logging
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.logger = RichLogger(
            name=f"SafeTraining_{training_name}",
            log_file=self.log_dir / f"safe_training_{training_name}_{timestamp}.log"
        )
        
        # Initialize status animation
        self.status = RichStatusAnimation()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info(f"Safe Training Launcher initialized for {training_name}")
        self.logger.info(f"Training script: {self.training_script}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.warning(f"Received signal {signum}, initiating safe shutdown")
        self.stop_training()
    
    def _get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        try:
            import psutil
            
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')
            
            # Temperature (if available)
            temp_sensors = psutil.sensors_temperatures()
            cpu_temp = None
            if temp_sensors:
                for name, entries in temp_sensors.items():
                    if 'cpu' in name.lower() or 'core' in name.lower():
                        cpu_temp = max(entry.current for entry in entries)
                        break
            
            # GPU stats (if available)
            gpu_memory = None
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_memory = {
                        'used_gb': torch.cuda.memory_allocated() / (1024**3),
                        'total_gb': torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    }
            except Exception:
                pass
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / (1024**3),
                'memory_total_gb': memory.total / (1024**3),
                'disk_used_gb': disk.used / (1024**3),
                'disk_total_gb': disk.total / (1024**3),
                'cpu_temp': cpu_temp,
                'gpu_memory': gpu_memory,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system stats: {e}")
            return {'error': str(e)}
    
    def _check_safety_limits(self, stats: Dict[str, Any]) -> List[str]:
        """Check if system is within safety limits"""
        violations = []
        
        # Check runtime
        if self.start_time:
            runtime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
            if runtime_hours > self.max_runtime_hours:
                violations.append(f"Runtime exceeded: {runtime_hours:.1f}h > {self.max_runtime_hours}h")
        
        # Check memory
        if stats.get('memory_used_gb', 0) > self.max_memory_gb:
            violations.append(f"Memory exceeded: {stats['memory_used_gb']:.1f}GB > {self.max_memory_gb}GB")
        
        # Check CPU temperature
        if stats.get('cpu_temp') and stats['cpu_temp'] > self.max_cpu_temp:
            violations.append(f"CPU temp: {stats['cpu_temp']:.1f}°C > {self.max_cpu_temp}°C")
        
        # Check disk space (need at least 10GB free)
        if stats.get('disk_total_gb') and stats.get('disk_used_gb'):
            free_gb = stats['disk_total_gb'] - stats['disk_used_gb']
            if free_gb < 10:
                violations.append(f"Low disk space: {free_gb:.1f}GB remaining")
        
        return violations
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        self.logger.info("Starting monitoring loop")
        
        while self.is_running and self.process:
            try:
                # Check if process is still running
                if self.process.poll() is not None:
                    self.logger.info("Training process completed")
                    break
                
                # Get system stats
                stats = self._get_system_stats()
                
                # Check safety limits
                violations = self._check_safety_limits(stats)
                
                if violations:
                    violation_text = "; ".join(violations)
                    self.logger.error(f"Safety violations detected: {violation_text}")
                    
                    # Emergency shutdown
                    self._emergency_shutdown(f"Safety violations: {violation_text}")
                    break
                
                # Update status
                runtime = datetime.now() - self.start_time if self.start_time else timedelta(0)
                status_text = (f"Training {self.training_name} | "
                             f"Runtime: {str(runtime).split('.')[0]} | "
                             f"CPU: {stats.get('cpu_percent', 0):.1f}% | "
                             f"RAM: {stats.get('memory_percent', 0):.1f}%")
                
                if stats.get('gpu_memory'):
                    gpu_used = stats['gpu_memory']['used_gb']
                    status_text += f" | GPU: {gpu_used:.1f}GB"
                
                if stats.get('cpu_temp'):
                    status_text += f" | Temp: {stats['cpu_temp']:.1f}°C"
                
                self.status.update_status(status_text)
                
                # Log periodic status
                self.logger.info(f"Monitor: {status_text}")
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(5)
        
        self.logger.info("Monitoring loop ended")
    
    def _emergency_shutdown(self, reason: str):
        """Perform emergency shutdown"""
        self.logger.error(f"EMERGENCY SHUTDOWN: {reason}")
        
        if self.process:
            try:
                # Try graceful shutdown first
                self.process.terminate()
                
                # Wait a bit for graceful shutdown
                try:
                    self.process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    # Force kill if necessary
                    self.logger.warning("Graceful shutdown failed, force killing process")
                    self.process.kill()
                    self.process.wait()
                
            except Exception as e:
                self.logger.error(f"Error during emergency shutdown: {e}")
        
        self.is_running = False
    
    def start_training(self, 
                      script_args: List[str] = None,
                      env_vars: Dict[str, str] = None) -> bool:
        """
        Start the training process with monitoring
        
        Args:
            script_args: Additional arguments for the training script
            env_vars: Additional environment variables
            
        Returns:
            bool: True if training started successfully
        """
        if self.is_running:
            self.logger.warning("Training already running")
            return False
        
        try:
            # Prepare command
            cmd = ["python", str(self.training_script)]
            if script_args:
                cmd.extend(script_args)
            
            # Prepare environment
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)
            
            # Start the status animation
            self.status.start_animation(f"Starting {self.training_name}")
            
            self.logger.info(f"Starting training process: {' '.join(cmd)}")
            
            # Start the process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                env=env,
                cwd=Path.cwd()
            )
            
            self.is_running = True
            self.start_time = datetime.now()
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
            # Start output reader thread
            output_thread = threading.Thread(target=self._read_output, daemon=True)
            output_thread.start()
            
            self.logger.info(f"Training started successfully (PID: {self.process.pid})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start training: {e}")
            self.is_running = False
            self.status.stop_animation()
            return False
    
    def _read_output(self):
        """Read and log process output"""
        if not self.process:
            return
        
        try:
            for line in iter(self.process.stdout.readline, ''):
                if line.strip():
                    self.logger.info(f"Training: {line.strip()}")
        except Exception as e:
            self.logger.error(f"Error reading process output: {e}")
    
    def stop_training(self):
        """Stop the training process"""
        if not self.is_running:
            return
        
        self.logger.info("Stopping training process")
        
        if self.process:
            try:
                # Try graceful shutdown
                self.process.terminate()
                self.process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                # Force kill if needed
                self.process.kill()
                self.process.wait()
            except Exception as e:
                self.logger.error(f"Error stopping process: {e}")
        
        self.is_running = False
        self.status.stop_animation()
        
        # Calculate final stats
        if self.start_time:
            runtime = datetime.now() - self.start_time
            self.logger.info(f"Training completed. Total runtime: {str(runtime).split('.')[0]}")
    
    def wait_for_completion(self) -> int:
        """
        Wait for training to complete
        
        Returns:
            int: Process exit code
        """
        if not self.process:
            return -1
        
        try:
            return_code = self.process.wait()
            self.logger.info(f"Training process completed with code: {return_code}")
            return return_code
        except KeyboardInterrupt:
            self.logger.warning("Interrupted by user")
            self.stop_training()
            return -1
        finally:
            self.is_running = False
            self.status.stop_animation()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current training status"""
        stats = self._get_system_stats()
        
        return {
            'training_name': self.training_name,
            'is_running': self.is_running,
            'pid': self.process.pid if self.process else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'runtime_hours': (datetime.now() - self.start_time).total_seconds() / 3600 if self.start_time else 0,
            'system_stats': stats
        }


def launch_safe_training(script_path: str, 
                        training_name: str = None,
                        script_args: List[str] = None,
                        max_runtime_hours: float = 24) -> SafeTrainingLauncher:
    """
    Convenience function to launch safe training
    
    Args:
        script_path: Path to training script
        training_name: Name for the training session
        script_args: Arguments for the training script
        max_runtime_hours: Maximum runtime before auto-shutdown
        
    Returns:
        SafeTrainingLauncher: The launcher instance
    """
    if not training_name:
        training_name = Path(script_path).stem
    
    launcher = SafeTrainingLauncher(script_path, training_name)
    launcher.max_runtime_hours = max_runtime_hours
    
    if launcher.start_training(script_args):
        return launcher
    else:
        raise RuntimeError(f"Failed to start training: {script_path}")


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) < 2:
        print("Usage: python safe_training_launcher.py <training_script> [args...]")
        sys.exit(1)
    
    script_path = sys.argv[1]
    script_args = sys.argv[2:] if len(sys.argv) > 2 else None
    
    try:
        launcher = launch_safe_training(script_path, script_args=script_args)
        exit_code = launcher.wait_for_completion()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTraining interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
