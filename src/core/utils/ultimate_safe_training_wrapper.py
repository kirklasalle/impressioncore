"""
ImpressionCore Safe Training Wrapper
====================================

Ultimate training wrapper combining all safety features:
- Process monitoring and resource management
- Automatic checkpointing and recovery
- Error handling and graceful shutdowns
- Progress tracking and status updates
- Real-time safety monitoring

Author: ImpressionCore Development Team
Created: 2025-01-13
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import threading

# Add ImpressionCore modules to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.utils.safe_training_launcher import SafeTrainingLauncher
from core.utils.training_checkpoint import TrainingCheckpoint, TrainingRecovery
from core.utils.rich_logging import RichLogger
from core.utils.rich_status_animation import RichStatusAnimation


class UltimateSafeTrainingWrapper:
    """
    Ultimate safe training wrapper with all safety features
    """
    
    def __init__(self, 
                 training_name: str,
                 training_script: str = None,
                 checkpoint_dir: str = "checkpoints",
                 log_dir: str = "src/memlog",
                 max_runtime_hours: float = 24.0,
                 checkpoint_interval_minutes: float = 15.0):
        """
        Initialize ultimate safe training wrapper
        
        Args:
            training_name: Name for this training session
            training_script: Path to training script (if using script mode)
            checkpoint_dir: Directory for checkpoints
            log_dir: Directory for logs
            max_runtime_hours: Maximum runtime before auto-shutdown
            checkpoint_interval_minutes: Interval between checkpoints
        """
        self.training_name = training_name
        self.training_script = training_script
        self.max_runtime_hours = max_runtime_hours
        
        # Initialize components
        self.checkpoint_manager = TrainingCheckpoint(
            checkpoint_dir=checkpoint_dir,
            training_name=training_name,
            save_interval_minutes=checkpoint_interval_minutes
        )
        
        self.recovery_manager = TrainingRecovery(self.checkpoint_manager)
        
        if training_script:
            self.launcher = SafeTrainingLauncher(
                training_script=training_script,
                training_name=training_name,
                log_dir=log_dir
            )
            self.launcher.max_runtime_hours = max_runtime_hours
        else:
            self.launcher = None
        
        # Initialize logging
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.logger = RichLogger(
            name=f"UltimateSafeTraining_{training_name}",
            log_file=self.log_dir / f"ultimate_safe_training_{training_name}_{timestamp}.log"
        )
        
        # Initialize status
        self.status = RichStatusAnimation()
        
        # State tracking
        self.start_time = None
        self.is_running = False
        self.training_metrics = {}
        self.safety_callbacks = []
        
        self.logger.info(f"Ultimate Safe Training Wrapper initialized for {training_name}")
    
    def add_safety_callback(self, callback: Callable[[str], None]):
        """Add callback to execute on safety events"""
        self.safety_callbacks.append(callback)
    
    def _execute_safety_callbacks(self, event: str):
        """Execute all safety callbacks"""
        for callback in self.safety_callbacks:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(f"Safety callback error: {e}")
    
    def can_recover_from_previous_run(self) -> bool:
        """Check if we can recover from a previous run"""
        return self.recovery_manager.can_recover()
    
    def get_recovery_options(self) -> List[Dict[str, Any]]:
        """Get available recovery options"""
        return self.recovery_manager.get_recovery_options()
    
    def start_script_training(self, 
                            script_args: List[str] = None,
                            auto_recover: bool = True) -> bool:
        """
        Start training using script mode
        
        Args:
            script_args: Arguments for the training script
            auto_recover: Whether to automatically recover from previous run
            
        Returns:
            bool: True if training started successfully
        """
        if not self.launcher:
            self.logger.error("No training script specified")
            return False
        
        # Check for recovery
        if auto_recover and self.can_recover_from_previous_run():
            recovery_options = self.get_recovery_options()
            if recovery_options:
                latest = recovery_options[0]
                self.logger.info(f"Found previous checkpoint: {latest['checkpoint_id']}")
                self.logger.info("Recovery will be handled by the training script")
        
        # Start training
        self.is_running = True
        self.start_time = datetime.now()
        
        success = self.launcher.start_training(script_args)
        
        if success:
            self.logger.info("Script training started successfully")
            self.status.start_animation(f"Running {self.training_name}")
        else:
            self.is_running = False
            self.logger.error("Failed to start script training")
        
        return success
    
    def start_direct_training(self, 
                            training_function: Callable,
                            training_args: Dict[str, Any] = None,
                            auto_recover: bool = True) -> bool:
        """
        Start training using direct function mode
        
        Args:
            training_function: Function to execute for training
            training_args: Arguments for the training function
            auto_recover: Whether to automatically recover from previous run
            
        Returns:
            bool: True if training started successfully
        """
        try:
            self.is_running = True
            self.start_time = datetime.now()
            
            # Check for recovery
            recovery_data = None
            if auto_recover and self.can_recover_from_previous_run():
                recovery_options = self.get_recovery_options()
                if recovery_options:
                    latest = recovery_options[0]
                    self.logger.info(f"Recovering from checkpoint: {latest['checkpoint_id']}")
                    recovery_data = self.checkpoint_manager.load_checkpoint()
            
            # Start status animation
            self.status.start_animation(f"Running {self.training_name}")
            
            # Start training in thread
            training_thread = threading.Thread(
                target=self._run_training_function,
                args=(training_function, training_args or {}, recovery_data),
                daemon=True
            )
            training_thread.start()
            
            self.logger.info("Direct training started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start direct training: {e}")
            self.is_running = False
            return False
    
    def _run_training_function(self, 
                              training_function: Callable,
                              training_args: Dict[str, Any],
                              recovery_data: Dict[str, Any] = None):
        """Run training function with error handling"""
        try:
            # Add recovery data to args if available
            if recovery_data:
                training_args['recovery_data'] = recovery_data
            
            # Add checkpoint callback
            training_args['checkpoint_callback'] = self._checkpoint_callback
            training_args['metrics_callback'] = self._metrics_callback
            
            # Run training
            result = training_function(**training_args)
            
            self.logger.info(f"Training completed successfully: {result}")
            
        except Exception as e:
            self.logger.error(f"Training function error: {e}")
            self._execute_safety_callbacks(f"training_error: {e}")
        
        finally:
            self.is_running = False
            self.status.stop_animation()
    
    def _checkpoint_callback(self, state: Dict[str, Any], metrics: Dict[str, Any] = None):
        """Callback for saving checkpoints"""
        try:
            checkpoint_id = self.checkpoint_manager.save_checkpoint(state, metrics)
            if checkpoint_id:
                self.logger.info(f"Checkpoint saved: {checkpoint_id}")
        except Exception as e:
            self.logger.error(f"Checkpoint save error: {e}")
    
    def _metrics_callback(self, metrics: Dict[str, Any]):
        """Callback for updating metrics"""
        self.training_metrics.update(metrics)
        
        # Update status
        if self.start_time:
            runtime = datetime.now() - self.start_time
            status_text = f"Training {self.training_name} | Runtime: {str(runtime).split('.')[0]}"
            
            if 'loss' in metrics:
                status_text += f" | Loss: {metrics['loss']:.4f}"
            if 'epoch' in metrics:
                status_text += f" | Epoch: {metrics['epoch']}"
            
            self.status.update_status(status_text)
    
    def wait_for_completion(self) -> bool:
        """
        Wait for training to complete
        
        Returns:
            bool: True if training completed successfully
        """
        if self.launcher:
            # Script mode
            exit_code = self.launcher.wait_for_completion()
            success = exit_code == 0
        else:
            # Direct mode - wait for is_running to become False
            while self.is_running:
                time.sleep(1)
            success = True
        
        # Final checkpoint
        if self.training_metrics:
            self._checkpoint_callback(
                {'final_state': True, 'training_metrics': self.training_metrics},
                self.training_metrics
            )
        
        # Calculate final stats
        if self.start_time:
            runtime = datetime.now() - self.start_time
            self.logger.info(f"Training completed. Total runtime: {str(runtime).split('.')[0]}")
        
        return success
    
    def stop_training(self):
        """Stop training gracefully"""
        self.logger.info("Stopping training")
        
        if self.launcher:
            self.launcher.stop_training()
        
        self.is_running = False
        self.status.stop_animation()
        
        # Final checkpoint
        if self.training_metrics:
            self._checkpoint_callback(
                {'stopped_state': True, 'training_metrics': self.training_metrics},
                self.training_metrics
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current training status"""
        base_status = {
            'training_name': self.training_name,
            'is_running': self.is_running,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'runtime_hours': (datetime.now() - self.start_time).total_seconds() / 3600 if self.start_time else 0,
            'training_metrics': self.training_metrics,
            'can_recover': self.can_recover_from_previous_run(),
            'checkpoints_available': len(self.get_recovery_options())
        }
        
        if self.launcher:
            launcher_status = self.launcher.get_status()
            base_status.update(launcher_status)
        
        return base_status
    
    def export_training_summary(self, output_file: str = None) -> str:
        """Export comprehensive training summary"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"training_summary_{self.training_name}_{timestamp}.json"
        
        summary = {
            'training_name': self.training_name,
            'export_timestamp': datetime.now().isoformat(),
            'status': self.get_status(),
            'recovery_options': self.get_recovery_options(),
            'training_log': self.checkpoint_manager.export_training_log()
        }
        
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"Training summary exported: {output_path}")
        return str(output_path)


# Convenience functions
def start_safe_script_training(training_name: str,
                              script_path: str,
                              script_args: List[str] = None,
                              max_runtime_hours: float = 24.0) -> UltimateSafeTrainingWrapper:
    """
    Start safe script-based training
    
    Args:
        training_name: Name for the training session
        script_path: Path to training script
        script_args: Arguments for the script
        max_runtime_hours: Maximum runtime
        
    Returns:
        UltimateSafeTrainingWrapper: Training wrapper instance
    """
    wrapper = UltimateSafeTrainingWrapper(
        training_name=training_name,
        training_script=script_path,
        max_runtime_hours=max_runtime_hours
    )
    
    if wrapper.start_script_training(script_args):
        return wrapper
    else:
        raise RuntimeError(f"Failed to start safe training: {script_path}")


def start_safe_direct_training(training_name: str,
                              training_function: Callable,
                              training_args: Dict[str, Any] = None,
                              max_runtime_hours: float = 24.0) -> UltimateSafeTrainingWrapper:
    """
    Start safe direct function training
    
    Args:
        training_name: Name for the training session
        training_function: Function to execute
        training_args: Arguments for the function
        max_runtime_hours: Maximum runtime
        
    Returns:
        UltimateSafeTrainingWrapper: Training wrapper instance
    """
    wrapper = UltimateSafeTrainingWrapper(
        training_name=training_name,
        max_runtime_hours=max_runtime_hours
    )
    
    if wrapper.start_direct_training(training_function, training_args):
        return wrapper
    else:
        raise RuntimeError(f"Failed to start safe direct training: {training_name}")


if __name__ == "__main__":
    # Example usage
    print("ImpressionCore Ultimate Safe Training Wrapper - Example")
    
    # Example training function
    def example_training_function(epochs=10, checkpoint_callback=None, metrics_callback=None, **kwargs):
        """Example training function"""
        print("Starting example training...")
        
        for epoch in range(epochs):
            # Simulate training
            time.sleep(2)
            
            # Simulate metrics
            loss = 1.0 / (epoch + 1)
            accuracy = min(0.9, 0.5 + epoch * 0.05)
            
            metrics = {
                'epoch': epoch,
                'loss': loss,
                'accuracy': accuracy
            }
            
            # Update metrics
            if metrics_callback:
                metrics_callback(metrics)
            
            # Save checkpoint every few epochs
            if checkpoint_callback and epoch % 3 == 0:
                state = {
                    'epoch': epoch,
                    'model_state': f'mock_model_state_epoch_{epoch}',
                    'optimizer_state': f'mock_optimizer_state_epoch_{epoch}'
                }
                checkpoint_callback(state, metrics)
            
            print(f"Epoch {epoch}: Loss={loss:.4f}, Accuracy={accuracy:.4f}")
        
        print("Training completed!")
        return {'status': 'completed', 'final_loss': loss, 'final_accuracy': accuracy}
    
    try:
        # Start safe direct training
        wrapper = start_safe_direct_training(
            training_name="example_training",
            training_function=example_training_function,
            training_args={'epochs': 10},
            max_runtime_hours=1.0
        )
        
        # Wait for completion
        success = wrapper.wait_for_completion()
        print(f"Training completed successfully: {success}")
        
        # Export summary
        summary_file = wrapper.export_training_summary()
        print(f"Summary exported: {summary_file}")
        
    except KeyboardInterrupt:
        print("\nTraining interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
