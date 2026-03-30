"""
ImpressionCore Training Checkpoint & Recovery System
===================================================

Comprehensive checkpoint and recovery system for training processes:
- Automatic checkpointing at configurable intervals
- State recovery after crashes or interruptions
- Progress tracking and metrics preservation
- Model state and optimizer state management
- Training resumption with full context

Author: ImpressionCore Development Team
Created: 2025-01-13
"""

import os
import json
import time
import shutil
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import threading
import hashlib

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class TrainingCheckpoint:
    """
    Manages training checkpoints with automatic saving and recovery
    """
    
    def __init__(self, 
                 checkpoint_dir: str = "checkpoints",
                 training_name: str = "training",
                 max_checkpoints: int = 5,
                 save_interval_minutes: float = 15.0):
        """
        Initialize checkpoint manager
        
        Args:
            checkpoint_dir: Directory to store checkpoints
            training_name: Name of the training session
            max_checkpoints: Maximum number of checkpoints to keep
            save_interval_minutes: Interval between automatic saves
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        self.training_name = training_name
        self.max_checkpoints = max_checkpoints
        self.save_interval = timedelta(minutes=save_interval_minutes)
        
        # State tracking
        self.last_save_time = None
        self.current_checkpoint = None
        self.training_state = {}
        self.metrics_history = []
        
        # Auto-save thread
        self.auto_save_thread = None
        self.auto_save_running = False
        
        print(f"Checkpoint manager initialized: {self.checkpoint_dir}")
    
    def _generate_checkpoint_id(self) -> str:
        """Generate unique checkpoint ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{self.training_name}_{timestamp}"
    
    def _get_checkpoint_path(self, checkpoint_id: str) -> Path:
        """Get path for checkpoint ID"""
        return self.checkpoint_dir / f"{checkpoint_id}.checkpoint"
    
    def save_checkpoint(self, 
                       state: Dict[str, Any],
                       metrics: Dict[str, Any] = None,
                       force: bool = False) -> str:
        """
        Save training checkpoint
        
        Args:
            state: Training state dictionary (model, optimizer, etc.)
            metrics: Current training metrics
            force: Force save even if interval hasn't passed
            
        Returns:
            str: Checkpoint ID
        """
        # Check if we should save
        if not force and self.last_save_time:
            if datetime.now() - self.last_save_time < self.save_interval:
                return None
        
        checkpoint_id = self._generate_checkpoint_id()
        checkpoint_path = self._get_checkpoint_path(checkpoint_id)
        
        try:
            # Prepare checkpoint data
            checkpoint_data = {
                'checkpoint_id': checkpoint_id,
                'timestamp': datetime.now().isoformat(),
                'training_name': self.training_name,
                'state': state,
                'metrics': metrics or {},
                'metrics_history': self.metrics_history.copy()
            }
            
            # Save checkpoint
            with open(checkpoint_path, 'wb') as f:
                pickle.dump(checkpoint_data, f)
            
            # Update current checkpoint
            self.current_checkpoint = checkpoint_id
            self.last_save_time = datetime.now()
            
            # Add to metrics history
            if metrics:
                self.metrics_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'checkpoint_id': checkpoint_id,
                    **metrics
                })
            
            print(f"Checkpoint saved: {checkpoint_id}")
            
            # Cleanup old checkpoints
            self._cleanup_old_checkpoints()
            
            return checkpoint_id
            
        except Exception as e:
            print(f"Error saving checkpoint: {e}")
            return None
    
    def load_checkpoint(self, checkpoint_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Load training checkpoint
        
        Args:
            checkpoint_id: Specific checkpoint to load (if None, loads latest)
            
        Returns:
            Dict containing checkpoint data, or None if not found
        """
        try:
            if checkpoint_id is None:
                # Find latest checkpoint
                checkpoint_id = self.get_latest_checkpoint()
                if not checkpoint_id:
                    print("No checkpoints found")
                    return None
            
            checkpoint_path = self._get_checkpoint_path(checkpoint_id)
            
            if not checkpoint_path.exists():
                print(f"Checkpoint not found: {checkpoint_id}")
                return None
            
            with open(checkpoint_path, 'rb') as f:
                checkpoint_data = pickle.load(f)
            
            # Restore state
            self.current_checkpoint = checkpoint_id
            self.metrics_history = checkpoint_data.get('metrics_history', [])
            
            print(f"Checkpoint loaded: {checkpoint_id}")
            return checkpoint_data
            
        except Exception as e:
            print(f"Error loading checkpoint: {e}")
            return None
    
    def get_latest_checkpoint(self) -> Optional[str]:
        """Get ID of the latest checkpoint"""
        checkpoints = list(self.checkpoint_dir.glob(f"{self.training_name}_*.checkpoint"))
        
        if not checkpoints:
            return None
        
        # Sort by modification time
        latest_checkpoint = max(checkpoints, key=lambda p: p.stat().st_mtime)
        return latest_checkpoint.stem
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List all available checkpoints"""
        checkpoints = []
        
        for checkpoint_file in self.checkpoint_dir.glob(f"{self.training_name}_*.checkpoint"):
            try:
                with open(checkpoint_file, 'rb') as f:
                    data = pickle.load(f)
                
                checkpoints.append({
                    'checkpoint_id': data['checkpoint_id'],
                    'timestamp': data['timestamp'],
                    'file_size_mb': checkpoint_file.stat().st_size / (1024*1024),
                    'metrics': data.get('metrics', {})
                })
            except Exception as e:
                print(f"Error reading checkpoint {checkpoint_file}: {e}")
        
        # Sort by timestamp
        checkpoints.sort(key=lambda x: x['timestamp'], reverse=True)
        return checkpoints
    
    def _cleanup_old_checkpoints(self):
        """Remove old checkpoints beyond max_checkpoints limit"""
        checkpoints = sorted(
            self.checkpoint_dir.glob(f"{self.training_name}_*.checkpoint"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        # Remove old checkpoints
        for old_checkpoint in checkpoints[self.max_checkpoints:]:
            try:
                old_checkpoint.unlink()
                print(f"Removed old checkpoint: {old_checkpoint.stem}")
            except Exception as e:
                print(f"Error removing old checkpoint: {e}")
    
    def start_auto_save(self, get_state_func, get_metrics_func=None):
        """
        Start automatic checkpoint saving
        
        Args:
            get_state_func: Function that returns current training state
            get_metrics_func: Function that returns current metrics
        """
        if self.auto_save_running:
            print("Auto-save already running")
            return
        
        self.auto_save_running = True
        
        def auto_save_loop():
            while self.auto_save_running:
                try:
                    time.sleep(60)  # Check every minute
                    
                    # Check if it's time to save
                    if self.last_save_time is None or \
                       datetime.now() - self.last_save_time >= self.save_interval:
                        
                        # Get current state and metrics
                        state = get_state_func()
                        metrics = get_metrics_func() if get_metrics_func else None
                        
                        # Save checkpoint
                        self.save_checkpoint(state, metrics)
                
                except Exception as e:
                    print(f"Auto-save error: {e}")
        
        self.auto_save_thread = threading.Thread(target=auto_save_loop, daemon=True)
        self.auto_save_thread.start()
        
        print("Auto-save started")
    
    def stop_auto_save(self):
        """Stop automatic checkpoint saving"""
        self.auto_save_running = False
        print("Auto-save stopped")
    
    def export_training_log(self, output_file: str = None) -> str:
        """
        Export complete training log
        
        Args:
            output_file: Output file path (auto-generated if None)
            
        Returns:
            str: Path to exported log file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"training_log_{self.training_name}_{timestamp}.json"
        
        output_path = Path(output_file)
        
        # Prepare export data
        export_data = {
            'training_name': self.training_name,
            'export_timestamp': datetime.now().isoformat(),
            'checkpoints': self.list_checkpoints(),
            'metrics_history': self.metrics_history,
            'current_checkpoint': self.current_checkpoint
        }
        
        # Save export
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Training log exported: {output_path}")
        return str(output_path)


class TrainingRecovery:
    """
    Handles training recovery from checkpoints
    """
    
    def __init__(self, checkpoint_manager: TrainingCheckpoint):
        """
        Initialize recovery system
        
        Args:
            checkpoint_manager: Checkpoint manager instance
        """
        self.checkpoint_manager = checkpoint_manager
    
    def can_recover(self) -> bool:
        """Check if recovery is possible"""
        return self.checkpoint_manager.get_latest_checkpoint() is not None
    
    def recover_training(self, 
                        model=None, 
                        optimizer=None, 
                        checkpoint_id: str = None) -> Dict[str, Any]:
        """
        Recover training from checkpoint
        
        Args:
            model: Model to restore state to
            optimizer: Optimizer to restore state to
            checkpoint_id: Specific checkpoint ID (if None, uses latest)
            
        Returns:
            Dict containing recovered state and metrics
        """
        # Load checkpoint
        checkpoint_data = self.checkpoint_manager.load_checkpoint(checkpoint_id)
        
        if not checkpoint_data:
            raise RuntimeError("No checkpoint available for recovery")
        
        state = checkpoint_data['state']
        
        # Restore model state
        if model is not None and 'model_state_dict' in state:
            if TORCH_AVAILABLE and hasattr(model, 'load_state_dict'):
                model.load_state_dict(state['model_state_dict'])
                print("Model state restored")
        
        # Restore optimizer state
        if optimizer is not None and 'optimizer_state_dict' in state:
            if TORCH_AVAILABLE and hasattr(optimizer, 'load_state_dict'):
                optimizer.load_state_dict(state['optimizer_state_dict'])
                print("Optimizer state restored")
        
        print(f"Training recovered from checkpoint: {checkpoint_data['checkpoint_id']}")
        
        return {
            'checkpoint_data': checkpoint_data,
            'recovered_state': state,
            'metrics': checkpoint_data.get('metrics', {}),
            'epoch': state.get('epoch', 0),
            'step': state.get('step', 0)
        }
    
    def get_recovery_options(self) -> List[Dict[str, Any]]:
        """Get available recovery options"""
        return self.checkpoint_manager.list_checkpoints()


# Convenience functions
def create_checkpoint_manager(training_name: str, 
                            checkpoint_dir: str = "checkpoints",
                            save_interval_minutes: float = 15.0) -> TrainingCheckpoint:
    """Create checkpoint manager with default settings"""
    return TrainingCheckpoint(
        checkpoint_dir=checkpoint_dir,
        training_name=training_name,
        save_interval_minutes=save_interval_minutes
    )


def quick_checkpoint_save(training_name: str, 
                         state: Dict[str, Any], 
                         metrics: Dict[str, Any] = None) -> str:
    """Quick checkpoint save without manager setup"""
    checkpoint_manager = create_checkpoint_manager(training_name)
    return checkpoint_manager.save_checkpoint(state, metrics, force=True)


def quick_checkpoint_load(training_name: str, 
                         checkpoint_id: str = None) -> Optional[Dict[str, Any]]:
    """Quick checkpoint load without manager setup"""
    checkpoint_manager = create_checkpoint_manager(training_name)
    return checkpoint_manager.load_checkpoint(checkpoint_id)


if __name__ == "__main__":
    # Example usage
    print("ImpressionCore Training Checkpoint System - Example")
    
    # Create checkpoint manager
    checkpoint_manager = create_checkpoint_manager("test_training")
    
    # Simulate some training state
    training_state = {
        'epoch': 10,
        'step': 1000,
        'model_state_dict': {'weight': 'mock_weight_data'},
        'optimizer_state_dict': {'lr': 0.001}
    }
    
    metrics = {
        'loss': 0.5,
        'accuracy': 0.85,
        'learning_rate': 0.001
    }
    
    # Save checkpoint
    checkpoint_id = checkpoint_manager.save_checkpoint(training_state, metrics, force=True)
    print(f"Saved checkpoint: {checkpoint_id}")
    
    # List checkpoints
    checkpoints = checkpoint_manager.list_checkpoints()
    print(f"Available checkpoints: {len(checkpoints)}")
    
    # Load checkpoint
    loaded_data = checkpoint_manager.load_checkpoint()
    if loaded_data:
        print(f"Loaded checkpoint: {loaded_data['checkpoint_id']}")
        print(f"Epoch: {loaded_data['state']['epoch']}")
    
    print("Checkpoint system test completed")
