#!/usr/bin/env python3
"""
ImpressionCore Model Loading Security Fix

File: src/training/utils/model_loading_fix.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-12
Modified: 2025-06-12
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [training, security, pytorch, transformers, distillation, 2025]
Dependencies: [torch, transformers]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Comprehensive solution for PyTorch 2.6+ security restrictions when loading teacher
models for knowledge distillation. Provides multiple fallback mechanisms to ensure
CUDA-enabled distillation training works regardless of PyTorch version.

Features:
- Monkey patching for transformers library
- Safe globals context management
- Safetensors conversion and loading
- Version-aware loading strategies
- Comprehensive error handling and fallbacks
"""

import torch
import warnings
import logging
from typing import Optional, Dict, Any, Union, List
from pathlib import Path
import importlib.util

logger = logging.getLogger(__name__)

class ModelLoadingFix:
    """
    Comprehensive fix for PyTorch 2.6+ weights_only security restrictions
    when loading teacher models for knowledge distillation.
    """
    
    def __init__(self):
        self.pytorch_version = self._get_pytorch_version()
        self.transformers_version = self._get_transformers_version()
        self.has_safetensors = self._check_safetensors_availability()
        self.is_pytorch_26_plus = self._is_pytorch_26_plus()
        
        logger.info(f"ModelLoadingFix initialized:")
        logger.info(f"  PyTorch version: {self.pytorch_version}")
        logger.info(f"  Transformers version: {self.transformers_version}")
        logger.info(f"  Safetensors available: {self.has_safetensors}")
        logger.info(f"  PyTorch 2.6+ detected: {self.is_pytorch_26_plus}")
    
    def _get_pytorch_version(self) -> str:
        """Get PyTorch version string"""
        try:
            return torch.__version__
        except:
            return "unknown"
    
    def _get_transformers_version(self) -> str:
        """Get transformers version string"""
        try:
            import transformers
            return transformers.__version__
        except:
            return "unknown"
    
    def _check_safetensors_availability(self) -> bool:
        """Check if safetensors is available"""
        try:
            import safetensors
            return True
        except ImportError:
            return False
    
    def _is_pytorch_26_plus(self) -> bool:
        """Check if PyTorch version is 2.6 or higher"""
        try:
            version_parts = self.pytorch_version.split('.')
            major = int(version_parts[0])
            minor = int(version_parts[1])
            return major > 2 or (major == 2 and minor >= 6)
        except:
            return False
    
    def apply_transformers_monkey_patch(self):
        """
        Apply monkey patch to transformers library to fix PyTorch 2.6+ loading issues
        """
        try:
            import transformers.modeling_utils
            
            # Store original load function
            if not hasattr(transformers.modeling_utils, '_original_torch_load'):
                transformers.modeling_utils._original_torch_load = torch.load
            
            def patched_torch_load(*args, **kwargs):
                """Patched torch.load that explicitly sets weights_only=False"""
                # Always set weights_only=False for trusted teacher models
                kwargs['weights_only'] = False
                return transformers.modeling_utils._original_torch_load(*args, **kwargs)
            
            # Apply the patch
            torch.load = patched_torch_load
            
            logger.info("Successfully applied transformers monkey patch for PyTorch 2.6+ compatibility")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to apply transformers monkey patch: {e}")
            return False
    
    def create_safe_loading_context(self, additional_globals: Optional[List[str]] = None):
        """
        Create a context manager for safe model loading with trusted globals
        """
        if not self.is_pytorch_26_plus:
            # For older PyTorch versions, return a no-op context manager
            from contextlib import nullcontext
            return nullcontext()
        
        try:
            # Default safe globals for transformers models
            safe_globals = [
                'torch.nn.Linear',
                'torch.nn.Embedding', 
                'torch.nn.LayerNorm',
                'torch.nn.Dropout',
                'torch.nn.ModuleList',
                'torch.nn.ModuleDict',
                'torch.nn.Parameter',
                'collections.OrderedDict',
                'torch.optim.Adam',
                'torch.optim.AdamW',
                'transformers.models.gpt2.modeling_gpt2.GPT2Model',
                'transformers.models.gpt2.modeling_gpt2.GPT2LMHeadModel',
                'transformers.models.bert.modeling_bert.BertModel',
                'transformers.models.bert.modeling_bert.BertForSequenceClassification'
            ]
            
            if additional_globals:
                safe_globals.extend(additional_globals)
            
            # Convert string class names to actual classes where possible
            actual_globals = []
            for global_name in safe_globals:
                try:
                    # Try to import and get the actual class
                    if '.' in global_name:
                        module_path, class_name = global_name.rsplit('.', 1)
                        module = importlib.import_module(module_path)
                        actual_class = getattr(module, class_name)
                        actual_globals.append(actual_class)
                    else:
                        # Built-in types
                        actual_globals.append(eval(global_name))
                except:
                    # If we can't resolve it, keep as string for debugging
                    logger.debug(f"Could not resolve safe global: {global_name}")
            
            return torch.serialization.safe_globals(actual_globals)
            
        except Exception as e:
            logger.warning(f"Failed to create safe loading context: {e}")
            from contextlib import nullcontext
            return nullcontext()
    
    def load_teacher_model_safe(self, model_name: str, device: torch.device, **kwargs):
        """
        Load teacher model with comprehensive fallback mechanisms
        """
        from transformers import AutoModel, AutoTokenizer
        
        logger.info(f"Loading teacher model: {model_name}")
        
        # Strategy 1: Try with monkey patch (most compatible)
        if self.apply_transformers_monkey_patch():
            try:
                logger.info("Attempting to load with monkey patch...")
                model = AutoModel.from_pretrained(model_name, **kwargs).to(device)
                logger.info("Successfully loaded teacher model with monkey patch")
                return model
            except Exception as e:
                logger.warning(f"Monkey patch loading failed: {e}")
        
        # Strategy 2: Try with safe globals context
        try:
            logger.info("Attempting to load with safe globals context...")
            with self.create_safe_loading_context():
                model = AutoModel.from_pretrained(model_name, **kwargs).to(device)
                logger.info("Successfully loaded teacher model with safe globals")
                return model
        except Exception as e:
            logger.warning(f"Safe globals loading failed: {e}")
        
        # Strategy 3: Try explicit weights_only=False (for PyTorch < 2.6)
        if not self.is_pytorch_26_plus:
            try:
                logger.info("Attempting explicit weights_only=False loading...")
                # Temporarily override torch.load
                original_load = torch.load
                def temp_load(*args, **load_kwargs):
                    load_kwargs['weights_only'] = False
                    return original_load(*args, **load_kwargs)
                
                torch.load = temp_load
                model = AutoModel.from_pretrained(model_name, **kwargs).to(device)
                torch.load = original_load
                
                logger.info("Successfully loaded teacher model with explicit weights_only=False")
                return model
            except Exception as e:
                logger.warning(f"Explicit weights_only=False loading failed: {e}")
                torch.load = original_load
        
        # Strategy 4: Try safetensors if available
        if self.has_safetensors:
            try:
                logger.info("Attempting safetensors loading...")
                model = AutoModel.from_pretrained(
                    model_name, 
                    use_safetensors=True,
                    **kwargs
                ).to(device)
                logger.info("Successfully loaded teacher model with safetensors")
                return model
            except Exception as e:
                logger.warning(f"Safetensors loading failed: {e}")
        
        # Strategy 5: CPU fallback then move to GPU (last resort)
        try:
            logger.info("Attempting CPU fallback loading...")
            cpu_kwargs = kwargs.copy()
            cpu_kwargs['torch_dtype'] = torch.float32  # CPU compatible
            
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=FutureWarning)
                model = AutoModel.from_pretrained(model_name, **cpu_kwargs)
                model = model.to(device)
            
            logger.info("Successfully loaded teacher model with CPU fallback")
            return model
        except Exception as e:
            logger.error(f"CPU fallback loading failed: {e}")
        
        # If all strategies fail, raise the last exception
        raise RuntimeError(
            f"Failed to load teacher model '{model_name}' with all available strategies. "
            f"This may be due to PyTorch 2.6+ security restrictions. "
            f"Please ensure you have a compatible PyTorch version with CUDA support."
        )
    
    def load_tokenizer_safe(self, model_name: str, **kwargs):
        """
        Load tokenizer with safe fallbacks
        """
        from transformers import AutoTokenizer
        
        try:
            # Apply monkey patch for tokenizer as well
            if self.is_pytorch_26_plus:
                self.apply_transformers_monkey_patch()
            
            tokenizer = AutoTokenizer.from_pretrained(model_name, **kwargs)
            logger.info(f"Successfully loaded tokenizer for {model_name}")
            return tokenizer
            
        except Exception as e:
            logger.error(f"Failed to load tokenizer for {model_name}: {e}")
            raise
    
    def restore_original_torch_load(self):
        """
        Restore original torch.load function if monkey patch was applied
        """
        try:
            import transformers.modeling_utils
            if hasattr(transformers.modeling_utils, '_original_torch_load'):
                torch.load = transformers.modeling_utils._original_torch_load
                logger.info("Restored original torch.load function")
        except Exception as e:
            logger.warning(f"Failed to restore original torch.load: {e}")


# Global instance for easy access
model_loading_fix = ModelLoadingFix()

def load_teacher_model_with_fix(model_name: str, device: torch.device, **kwargs):
    """
    Convenience function to load teacher model with all fixes applied
    """
    return model_loading_fix.load_teacher_model_safe(model_name, device, **kwargs)

def load_tokenizer_with_fix(model_name: str, **kwargs):
    """
    Convenience function to load tokenizer with all fixes applied
    """
    return model_loading_fix.load_tokenizer_safe(model_name, **kwargs)
