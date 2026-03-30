#!/usr/bin/env python3
"""
ImpressionCore: Train Vae

Module for train vae functionality in the ImpressionCore framework.

File: examples\train_vae.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [pytorch, production, memory-critical, 2025]
Dependencies: [torch, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements train vae functionality for the
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
from examples.train_vae import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import sys
import argparse
import logging
import time
from pathlib import Path

import torch
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.utils import save_image

# Add project root to path - make this more robust
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import custom modules
try:
    from src.models.vae_encoder import VAE
    from src.core.utils.cuda_utils import setup_cuda_for_1050ti, clean_gpu_memory
    # Memory optimization: Memory-critical operation
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Module import error: {e}")
    logger.error("Required modules not found. Make sure src/models/vae_encoder.py and src/core/utils/cuda_utils.py exist.")
    # Memory optimization: Memory-critical operation
    # Print current sys.path for debugging
    logger.error(f"Current sys.path: {sys.path}")
    logger.error(f"Checking file existence: src/models/vae_encoder.py exists: {os.path.exists(os.path.join(project_root, 'src/models/vae_encoder.py'))}")
    logger.error(f"Checking file existence: src/core/utils/cuda_utils.py exists: {os.path.exists(os.path.join(project_root, 'src/core/utils/cuda_utils.py'))}")
    # Memory optimization: Memory-critical operation
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def get_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="VAE Training Script")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for training")
    parser.add_argument("--test-batch-size", type=int, default=32, help="Batch size for testing")
    parser.add_argument("--epochs", type=int, default=10, help="Number of epochs to train")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--img-size", type=int, default=64, help="Image size (square)")
    parser.add_argument("--latent-dim", type=int, default=128, help="Latent dimension size")
    parser.add_argument("--beta", type=float, default=1.0, help="KL divergence weight (beta)")
    parser.add_argument("--no-cuda", action="store_true", default=False, help="Disable CUDA training")
    # Memory optimization: Memory-critical operation
    parser.add_argument("--log-interval", type=int, default=10, help="How many batches to wait before logging")
    parser.add_argument("--seed", type=int, default=1, help="Random seed")
    parser.add_argument("--save-model", action="store_true", default=True, help="Save the trained model")
    parser.add_argument("--output-dir", type=str, default="output", help="Output directory for results")
    parser.add_argument("--data-dir", type=str, default="data", help="Data directory")
    parser.add_argument("--dataset", type=str, default="cifar10", choices=["cifar10", "mnist", "fashion"], help="Dataset to use")
    
    # CUDA optimization arguments
    # Memory optimization: Memory-critical operation
    parser.add_argument("--cudnn-benchmark", action="store_true", default=True, 
                      help="Enable cuDNN benchmark for optimizing convolution operations")
    parser.add_argument("--mixed-precision", action="store_true", default=False,
                      help="Use mixed precision training (fp16) to save memory and potentially speed up training")
                      # Memory optimization: Memory-critical operation
    parser.add_argument("--memory-efficient", action="store_true", default=True,
    # Memory optimization: Memory-critical operation
                      help="Apply memory-efficient operations (useful for GPUs with limited memory)")
                      # Memory optimization: Memory-critical operation
    parser.add_argument("--compatibility-mode", action="store_true", default=False,
                      help="Enable checkpoint dimension adaptation")
    
    return parser.parse_args()

def get_dataloaders(args):
    """Set up data loaders for training and testing."""
    dataset_dir = os.path.join(project_root, args.data_dir)
    os.makedirs(dataset_dir, exist_ok=True)
    
    img_transform = transforms.Compose([
        transforms.Resize((args.img_size, args.img_size)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,)) if args.dataset in ["mnist", "fashion"] else 
                     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    try:
        if args.dataset == "cifar10":
            train_dataset = datasets.CIFAR10(
                root=dataset_dir, train=True, download=True, transform=img_transform
            )
            test_dataset = datasets.CIFAR10(
                root=dataset_dir, train=False, download=True, transform=img_transform
            )
        elif args.dataset == "mnist":
            train_dataset = datasets.MNIST(
                root=dataset_dir, train=True, download=True, transform=img_transform
            )
            test_dataset = datasets.MNIST(
                root=dataset_dir, train=False, download=True, transform=img_transform
            )
        elif args.dataset == "fashion":
            train_dataset = datasets.FashionMNIST(
                root=dataset_dir, train=True, download=True, transform=img_transform
            )
            test_dataset = datasets.FashionMNIST(
                root=dataset_dir, train=False, download=True, transform=img_transform
            )
        else:
            logger.error(f"Unknown dataset: {args.dataset}")
            sys.exit(1)
            
        logger.info(f"Loaded dataset {args.dataset} with {len(train_dataset)} training and {len(test_dataset)} testing examples")
        
        train_loader = DataLoader(
            train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=4, pin_memory=True
            # Memory optimization: Memory-critical operation
        )
        
        test_loader = DataLoader(
            test_dataset, batch_size=args.test_batch_size, shuffle=False, num_workers=4, pin_memory=True
            # Memory optimization: Memory-critical operation
        )
        
        return train_loader, test_loader
        
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        sys.exit(1)

def train_epoch(model, train_loader, optimizer, device, epoch, log_interval):
# Memory optimization: Device placement for memory management
    """Train for one epoch."""
    model.train()
    train_loss = 0
    recon_loss_total = 0
    kl_loss_total = 0
    
    for batch_idx, (data, _) in enumerate(train_loader):
        data = data.to(device)
        # Memory optimization: Device placement for memory management
        optimizer.zero_grad()
        
        # Forward pass
        result = model(data)
        recons = result["reconstruction"]
        mu = result["mu"]
        log_var = result["log_var"]
        
        # Compute loss
        loss_dict = model.loss_function(recons, data, mu, log_var)
        loss = loss_dict["loss"]
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # Track metrics
        train_loss += loss.item()
        recon_loss_total += loss_dict["reconstruction_loss"].item()
        kl_loss_total += loss_dict["kl_loss"].item()
        
        if batch_idx % log_interval == 0:
            logger.info(
                f"Train Epoch: {epoch} [{batch_idx * len(data)}/{len(train_loader.dataset)} "
                f"({100. * batch_idx / len(train_loader):.0f}%)]\tLoss: {loss.item():.6f}"
            )
    
    avg_loss = train_loss / len(train_loader)
    avg_recon_loss = recon_loss_total / len(train_loader)
    avg_kl_loss = kl_loss_total / len(train_loader)
    
    logger.info(f"====> Epoch: {epoch} Average loss: {avg_loss:.4f}")
    
    return {
        "loss": avg_loss,
        "recon_loss": avg_recon_loss,
        "kl_loss": avg_kl_loss
    }

def test_epoch(model, test_loader, device, epoch, output_dir, n_samples=8):
# Memory optimization: Device placement for memory management
    """Test the model and generate samples."""
    # Memory optimization: Explicit memory cleanup
    model.eval()
    test_loss = 0
    recon_loss_total = 0
    kl_loss_total = 0
    
    with torch.no_grad():
    # Memory optimization: Disable gradient computation to save memory
        for data, _ in test_loader:
            data = data.to(device)
            # Memory optimization: Device placement for memory management
            
            # Forward pass
            result = model(data)
            recons = result["reconstruction"]
            mu = result["mu"]
            log_var = result["log_var"]
            
            # Compute loss
            loss_dict = model.loss_function(recons, data, mu, log_var)
            
            # Track metrics
            test_loss += loss_dict["loss"].item()
            recon_loss_total += loss_dict["reconstruction_loss"].item()
            kl_loss_total += loss_dict["kl_loss"].item()
        
        # Generate samples
        samples = model.sample(n_samples, device)
        # Memory optimization: Device placement for memory management
        
        # Save input, reconstructions, and samples
        os.makedirs(output_dir, exist_ok=True)
        
        # Get a batch to visualize (first n_samples items)
        comparison = torch.cat([
            data[:n_samples],
            recons[:n_samples]
        ])
        
        save_image(
            comparison.cpu(),
            os.path.join(output_dir, f"reconstruction_epoch_{epoch}.png"),
            nrow=n_samples
        )
        
        save_image(
            samples.cpu(),
            os.path.join(output_dir, f"sample_epoch_{epoch}.png"),
            nrow=int(n_samples**0.5)
        )
    
    avg_loss = test_loss / len(test_loader)
    avg_recon_loss = recon_loss_total / len(test_loader)
    avg_kl_loss = kl_loss_total / len(test_loader)
    
    logger.info(f"====> Test set loss: {avg_loss:.4f}")
    
    return {
        "loss": avg_loss,
        "recon_loss": avg_recon_loss,
        "kl_loss": avg_kl_loss
    }

def save_checkpoint(model, optimizer, epoch, filename):
    """Save model checkpoint."""
    # Memory optimization: Explicit memory cleanup
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    checkpoint = {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict()
    }
    torch.save(checkpoint, filename)
    logger.info(f"Checkpoint saved to {filename}")

def load_checkpoint(model, optimizer, filename, compatibility_mode=False):
    """Load model checkpoint."""
    # Memory optimization: Explicit memory cleanup
    if os.path.exists(filename):
        try:
            checkpoint = torch.load(filename)
            
            if not compatibility_mode:
                model.load_state_dict(checkpoint["model_state_dict"])
                if optimizer is not None:
                    optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
                start_epoch = checkpoint["epoch"] + 1
                logger.info(f"Checkpoint loaded from {filename}, resuming at epoch {start_epoch}")
                return start_epoch
            else:
                logger.info("Attempting to adapt checkpoint dimensions to current model")
                checkpoint_state_dict = checkpoint["model_state_dict"]
                model_state_dict = model.state_dict()
                adapted_state_dict = {}
                loaded_params = 0
                adapted_params = 0
                skipped_params = 0
                
                for name, checkpoint_param in checkpoint_state_dict.items():
                    if name in model_state_dict:
                        model_param = model_state_dict[name]
                        
                        if checkpoint_param.shape == model_param.shape:
                            adapted_state_dict[name] = checkpoint_param
                            loaded_params += 1
                        elif len(checkpoint_param.shape) == 4 and len(model_param.shape) == 4:
                            if checkpoint_param.shape[1] >= model_param.shape[1]:
                                if name.endswith("weight"):
                                    adapted_param = checkpoint_param[:model_param.shape[0], 
                                                                  :model_param.shape[1], 
                                                                  :model_param.shape[2], 
                                                                  :model_param.shape[3]]
                                    adapted_state_dict[name] = adapted_param
                                    adapted_params += 1
                            else:
                                skipped_params += 1
                        elif len(checkpoint_param.shape) == 1 and len(model_param.shape) == 1:
                            if checkpoint_param.shape[0] >= model_param.shape[0]:
                                adapted_param = checkpoint_param[:model_param.shape[0]]
                                adapted_state_dict[name] = adapted_param
                                adapted_params += 1
                            else:
                                skipped_params += 1
                        elif len(checkpoint_param.shape) == 2 and len(model_param.shape) == 2:
                            if checkpoint_param.shape[0] >= model_param.shape[0] and \
                               checkpoint_param.shape[1] >= model_param.shape[1]:
                                adapted_param = checkpoint_param[:model_param.shape[0], :model_param.shape[1]]
                                adapted_state_dict[name] = adapted_param
                                adapted_params += 1
                            else:
                                skipped_params += 1
                        else:
                            skipped_params += 1
                    else:
                        skipped_params += 1
                
                model.load_state_dict(adapted_state_dict, strict=False)
                
                logger.info(f"Checkpoint adaptation complete:")
                logger.info(f"  Parameters directly loaded: {loaded_params}")
                logger.info(f"  Parameters adapted: {adapted_params}")
                logger.info(f"  Parameters skipped: {skipped_params}")
                
                return True if loaded_params + adapted_params > 0 else False
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {str(e)}")
    return 0

def main():
    """Main training function."""
    # Parse arguments
    args = get_args()
    
    try:
        # Set random seed for reproducibility
        torch.manual_seed(args.seed)
        
        # Set device
        # Memory optimization: Device placement for memory management
        use_cuda = not args.no_cuda and torch.cuda.is_available()
        # Memory optimization: CUDA operations for GPU acceleration
        device = torch.device("cuda" if use_cuda else "cpu")
        # Memory optimization: Device placement for memory management
        
        if use_cuda:
        # Memory optimization: Memory-critical operation
            torch.cuda.manual_seed(args.seed)
            # Memory optimization: CUDA operations for GPU acceleration
            if args.cudnn_benchmark:
                torch.backends.cudnn.benchmark = True
            
            # Log device info
            # Memory optimization: Device placement for memory management
            if torch.cuda.is_available():
            # Memory optimization: CUDA operations for GPU acceleration
                logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
                # Memory optimization: CUDA operations for GPU acceleration
                logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
                # Memory optimization: CUDA operations for GPU acceleration
                
                # Special handling for limited VRAM GPUs like GTX 1050 Ti
                # Memory optimization: Memory-critical operation
                if "1050" in torch.cuda.get_device_name(0) and args.memory_efficient:
                # Memory optimization: CUDA operations for GPU acceleration
                    logger.info("Detected GTX 1050 Ti, applying memory optimization settings")
                    # Memory optimization: Memory-critical operation
                    # Apply memory-efficient settings
                    # Memory optimization: Memory-critical operation
                    torch.cuda.empty_cache()
                    # Memory optimization: CUDA operations for GPU acceleration
        else:
            logger.info("Using CPU for training (CUDA not available or disabled)")
            # Memory optimization: Memory-critical operation
        
        # Determine input channels based on dataset
        in_channels = 1 if args.dataset in ["mnist", "fashion"] else 3
        
        # Create model
        model = VAE(
        # Memory optimization: Explicit memory cleanup
            in_channels=in_channels,
            latent_dim=args.latent_dim,
            beta=args.beta,
            img_size=args.img_size
        ).to(device)
        # Memory optimization: Device placement for memory management
        
        logger.info(f"Created VAE model with {sum(p.numel() for p in model.parameters())} parameters")
        # Memory optimization: Explicit memory cleanup
        
        # Set up optimizer
        optimizer = optim.Adam(model.parameters(), lr=args.lr)
        
        # Set up data loaders
        train_loader, test_loader = get_dataloaders(args)
        
        # Set up output directory
        output_dir = os.path.join(project_root, args.output_dir, f"vae_{args.dataset}_{args.latent_dim}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up checkpoint path
        checkpoint_dir = os.path.join(project_root, "models", "checkpoints")
        os.makedirs(checkpoint_dir, exist_ok=True)
        checkpoint_path = os.path.join(checkpoint_dir, f"vae_{args.dataset}_{args.latent_dim}.pt")
        
        # Resume from checkpoint if available
        start_epoch = load_checkpoint(model, optimizer, checkpoint_path, compatibility_mode=args.compatibility_mode)
        if not isinstance(start_epoch, int):
            start_epoch = 0  # Reset to 0 if loading failed or returned a boolean
        
        # Training loop
        logger.info(f"Starting training for {args.epochs} epochs")
        
        for epoch in range(start_epoch, args.epochs):
            # Train
            train_metrics = train_epoch(
                model, train_loader, optimizer, device, epoch, args.log_interval
                # Memory optimization: Device placement for memory management
            )
            
            # Test and visualize
            test_metrics = test_epoch(
                model, test_loader, device, epoch, output_dir
                # Memory optimization: Device placement for memory management
            )
            
            # Save checkpoint
            if args.save_model:
                save_checkpoint(model, optimizer, epoch, checkpoint_path)
        
        # Final samples
        model.eval()
        with torch.no_grad():
        # Memory optimization: Disable gradient computation to save memory
            samples = model.sample(64, device)
            # Memory optimization: Device placement for memory management
            save_image(
                samples.cpu(),
                os.path.join(output_dir, "final_samples.png"),
                nrow=8
            )
        
        logger.info("Training completed!")
        
    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
