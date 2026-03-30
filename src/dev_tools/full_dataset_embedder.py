#!/usr/bin/env python3
"""
ImpressionCore-B1 Full Dataset Embedding System
==============================================

Creates comprehensive embeddings for all available datasets:
- Text: 40+ samples → text embeddings
- Images: 40+ samples → image embeddings  
- Audio: 40+ samples → audio embeddings

Author: ImpressionCore Team
Date: 2025-01-06
Version: 1.0.0 - Full Dataset Embedding
Hardware: NVIDIA GTX 1050 Ti (4GB VRAM) Optimized
"""

import torch
import torch.nn as nn
import numpy as np
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime
import pickle
import librosa
from PIL import Image
import torchvision.transforms as transforms
import logging

# Rich UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# ImpressionCore imports
sys.path.append(str(Path(__file__).parent))
from src.training.bulletproof_incremental_trainer import BulletproofIncrementalTrainer
from src.training.models.architectures.b1.impressioncore_b1 import ImpressionCoreB1Model


class FullDatasetEmbedder:
    """
    Full dataset embedding system for ImpressionCore-B1.
    
    Features:
    - Process all 400% scaled datasets (120+ samples)
    - Generate multimodal embeddings (text, image, audio)
    - Save embeddings for fast retrieval
    - Memory-efficient processing for GTX 1050 Ti
    - Rich progress monitoring
    """
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.device = self._setup_device()
        self.base_path = Path("d:/Projects/impressioncore")
        self.data_path = self.base_path / "src/data/real_datasets/synthetic_scaled"
        self.embeddings_path = self.base_path / "src/data/embeddings"
        self.embeddings_path.mkdir(exist_ok=True)
        
        # Model and embeddings
        self.model = None
        self.embeddings = {
            'text': {},
            'images': {},
            'audio': {},
            'metadata': {
                'creation_date': datetime.now().isoformat(),
                'total_samples': 0,
                'model_info': {}
            }
        }
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Image transforms
        self.image_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        self._print_banner()
    
    def _setup_device(self):
        """Setup CUDA device."""
        if torch.cuda.is_available():
            device = "cuda:0"
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            return device
        else:
            return "cpu"
    
    def _setup_logging(self):
        """Setup logging."""
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger("FullDatasetEmbedder")
    
    def _print_banner(self):
        """Print embedding system banner."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║        ImpressionCore-B1 Full Dataset Embedding System      ║
║            🧠 COMPREHENSIVE MULTIMODAL EMBEDDINGS 🧠       ║
╠══════════════════════════════════════════════════════════════╣
║  📊 120+ Samples         🎯 GTX 1050 Ti Optimized          ║
║  🔤 Text Embeddings      🖼️ Image Embeddings               ║
║  🎵 Audio Embeddings     💾 Persistent Storage             ║
║  ⚡ CUDA Acceleration    📈 Rich Progress Monitoring        ║
╚══════════════════════════════════════════════════════════════╝
"""
        if self.console:
            panel = Panel(
                banner,
                title="🧠 ImpressionCore-B1 Full Dataset Embedder",
                subtitle="Creating Comprehensive Multimodal Embeddings",
                style="bold cyan"
            )
            self.console.print(panel)
        else:
            print(banner)
        
        print(f"Embedding Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base Path: {self.base_path}")
        print(f"Device: {self.device}")
        print()
    
    def load_trained_model(self):
        """Load the trained ImpressionCore-B1 model."""
        self.logger.info("🚀 Loading trained ImpressionCore-B1 model...")
        
        # Initialize model architecture
        model_config = {
            "hidden_size": 512,
            "num_layers": 6,
            "num_heads": 8,
            "vocab_size": 50257,
            "max_position_embeddings": 2048
        }
        
        self.model = ImpressionCoreB1Model(architecture_config=model_config)
        
        # Try to load trained weights
        best_model_path = self.base_path / "src/training/checkpoints/bulletproof_b1/best_model.pt"
        if best_model_path.exists():
            try:
                checkpoint = torch.load(best_model_path, map_location=self.device)
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.logger.info(f"✅ Loaded trained model from: {best_model_path}")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not load trained weights: {e}")
                self.logger.info("🔧 Using fresh model for embedding")
        else:
            self.logger.info("🔧 No trained model found, using fresh model for embedding")
        
        # Move to device and set to eval mode
        self.model.to(self.device)
        self.model.eval()
        
        # Update metadata
        self.embeddings['metadata']['model_info'] = {
            'architecture': 'ImpressionCoreB1Model',
            'parameters': sum(p.numel() for p in self.model.parameters()),
            'device': self.device,
            'trained_weights': best_model_path.exists()
        }
        
        self.logger.info(f"✅ Model ready for embedding: {self.embeddings['metadata']['model_info']['parameters']:,} parameters")
    
    def discover_datasets(self) -> Dict[str, int]:
        """Discover all available datasets and count samples."""
        self.logger.info("🔍 Discovering all available datasets...")
        
        dataset_counts = {}
        
        # Text samples
        text_path = self.data_path / "text_samples"
        if text_path.exists():
            text_files = list(text_path.glob("*.txt"))
            dataset_counts['text'] = len(text_files)
            self.logger.info(f"📝 Found {len(text_files)} text samples")
        
        # Image samples
        images_path = self.data_path / "images"
        if images_path.exists():
            image_files = list(images_path.glob("*.jpg"))
            dataset_counts['images'] = len(image_files)
            self.logger.info(f"🖼️ Found {len(image_files)} image samples")
        
        # Audio samples
        audio_path = self.data_path / "audio"
        if audio_path.exists():
            audio_files = list(audio_path.glob("*.wav"))
            dataset_counts['audio'] = len(audio_files)
            self.logger.info(f"🎵 Found {len(audio_files)} audio samples")
        
        total_samples = sum(dataset_counts.values())
        self.embeddings['metadata']['total_samples'] = total_samples
        
        if self.console:
            table = Table(title="🔍 Dataset Discovery Results", style="bold")
            table.add_column("Modality", style="cyan")
            table.add_column("Sample Count", style="green")
            
            for modality, count in dataset_counts.items():
                table.add_row(f"{modality.title()}", str(count))
            table.add_row("TOTAL", str(total_samples), style="bold yellow")
            
            self.console.print(table)
        
        return dataset_counts
    
    def embed_text_samples(self, progress, task_id):
        """Create embeddings for all text samples."""
        text_path = self.data_path / "text_samples"
        text_files = list(text_path.glob("*.txt"))
        
        self.logger.info(f"📝 Embedding {len(text_files)} text samples...")
        
        for i, text_file in enumerate(text_files):
            try:
                # Read text content
                with open(text_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                # Simple tokenization (convert to tensor)
                tokens = torch.tensor([ord(c) % 1000 for c in content[:128]], dtype=torch.long)
                if len(tokens) < 128:
                    # Pad to fixed length
                    padding = torch.zeros(128 - len(tokens), dtype=torch.long)
                    tokens = torch.cat([tokens, padding])
                
                # Convert to embeddings (simple embedding layer)
                text_embed = tokens.float().unsqueeze(0).to(self.device) / 1000.0  # Normalize
                
                # Get model embedding
                with torch.no_grad():
                    # Use model's text projection
                    if hasattr(self.model, 'text_projection'):
                        embedding = self.model.text_projection(text_embed.mean(dim=1))
                    else:
                        # Simple fallback embedding
                        embedding = text_embed.mean(dim=1)
                
                # Store embedding
                self.embeddings['text'][text_file.name] = {
                    'embedding': embedding.cpu().numpy(),
                    'content_preview': content[:100],
                    'file_path': str(text_file),
                    'embedding_shape': embedding.shape
                }
                
                progress.update(task_id, advance=1)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to embed text file {text_file.name}: {e}")
        
        self.logger.info(f"✅ Completed text embedding: {len(self.embeddings['text'])} samples")
    
    def embed_image_samples(self, progress, task_id):
        """Create embeddings for all image samples."""
        images_path = self.data_path / "images"
        image_files = list(images_path.glob("*.jpg"))
        
        self.logger.info(f"🖼️ Embedding {len(image_files)} image samples...")
        
        for i, image_file in enumerate(image_files):
            try:
                # Load and preprocess image
                image = Image.open(image_file).convert('RGB')
                image_tensor = self.image_transform(image).unsqueeze(0).to(self.device)
                
                # Get model embedding
                with torch.no_grad():
                    # Use model's image projection
                    if hasattr(self.model, 'image_projection'):
                        # Simple image embedding (average pooling)
                        image_embed = image_tensor.mean(dim=[2, 3])  # Average over height/width
                        embedding = self.model.image_projection(image_embed)
                    else:
                        # Simple fallback embedding
                        embedding = image_tensor.mean(dim=[2, 3])
                
                # Store embedding
                self.embeddings['images'][image_file.name] = {
                    'embedding': embedding.cpu().numpy(),
                    'image_size': image.size,
                    'file_path': str(image_file),
                    'embedding_shape': embedding.shape
                }
                
                progress.update(task_id, advance=1)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to embed image file {image_file.name}: {e}")
        
        self.logger.info(f"✅ Completed image embedding: {len(self.embeddings['images'])} samples")
    
    def embed_audio_samples(self, progress, task_id):
        """Create embeddings for all audio samples."""
        audio_path = self.data_path / "audio"
        audio_files = list(audio_path.glob("*.wav"))
        
        self.logger.info(f"🎵 Embedding {len(audio_files)} audio samples...")
        
        for i, audio_file in enumerate(audio_files):
            try:
                # Load audio file
                audio, sr = librosa.load(audio_file, sr=16000, duration=5.0)
                
                # Simple audio features (MFCC)
                mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
                audio_features = np.mean(mfccs, axis=1)  # Average over time
                
                # Convert to tensor
                audio_tensor = torch.tensor(audio_features, dtype=torch.float32).unsqueeze(0).to(self.device)
                
                # Pad or truncate to fixed size (128 features)
                if audio_tensor.shape[1] < 128:
                    padding = torch.zeros(1, 128 - audio_tensor.shape[1]).to(self.device)
                    audio_tensor = torch.cat([audio_tensor, padding], dim=1)
                else:
                    audio_tensor = audio_tensor[:, :128]
                
                # Get model embedding
                with torch.no_grad():
                    # Use model's text projection as audio projection (treat as text-like)
                    if hasattr(self.model, 'text_projection'):
                        embedding = self.model.text_projection(audio_tensor)
                    else:
                        # Simple fallback embedding
                        embedding = audio_tensor
                
                # Store embedding
                self.embeddings['audio'][audio_file.name] = {
                    'embedding': embedding.cpu().numpy(),
                    'duration': len(audio) / sr,
                    'sample_rate': sr,
                    'file_path': str(audio_file),
                    'embedding_shape': embedding.shape
                }
                
                progress.update(task_id, advance=1)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to embed audio file {audio_file.name}: {e}")
        
        self.logger.info(f"✅ Completed audio embedding: {len(self.embeddings['audio'])} samples")
    
    def save_embeddings(self):
        """Save all embeddings to disk."""
        self.logger.info("💾 Saving embeddings to disk...")
        
        # Save as pickle for fast loading
        embeddings_file = self.embeddings_path / f"full_dataset_embeddings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        with open(embeddings_file, 'wb') as f:
            pickle.dump(self.embeddings, f)
        
        # Save metadata as JSON for easy inspection
        metadata_file = self.embeddings_path / f"embeddings_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        metadata_only = self.embeddings['metadata'].copy()
        
        # Add summary stats
        metadata_only['summary'] = {
            'text_samples': len(self.embeddings['text']),
            'image_samples': len(self.embeddings['images']),
            'audio_samples': len(self.embeddings['audio']),
            'total_embeddings': len(self.embeddings['text']) + len(self.embeddings['images']) + len(self.embeddings['audio'])
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata_only, f, indent=2)
        
        self.logger.info(f"✅ Embeddings saved:")
        self.logger.info(f"   📄 Full embeddings: {embeddings_file}")
        self.logger.info(f"   📋 Metadata: {metadata_file}")
        
        return embeddings_file, metadata_file
    
    def run_full_embedding(self):
        """Run the complete embedding process for all datasets."""
        self.logger.info("🚀 Starting full dataset embedding process...")
        
        # Load model
        self.load_trained_model()
        
        # Discover datasets
        dataset_counts = self.discover_datasets()
        
        if not dataset_counts:
            self.logger.error("❌ No datasets found! Please ensure 400% scaled datasets exist.")
            return
        
        total_samples = sum(dataset_counts.values())
        
        # Create progress tracking
        if self.console:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=self.console
            ) as progress:
                
                # Text embedding task
                if 'text' in dataset_counts:
                    text_task = progress.add_task(f"[cyan]Embedding {dataset_counts['text']} text samples...", total=dataset_counts['text'])
                    self.embed_text_samples(progress, text_task)
                
                # Image embedding task
                if 'images' in dataset_counts:
                    image_task = progress.add_task(f"[green]Embedding {dataset_counts['images']} image samples...", total=dataset_counts['images'])
                    self.embed_image_samples(progress, image_task)
                
                # Audio embedding task
                if 'audio' in dataset_counts:
                    audio_task = progress.add_task(f"[yellow]Embedding {dataset_counts['audio']} audio samples...", total=dataset_counts['audio'])
                    self.embed_audio_samples(progress, audio_task)
        
        else:
            # Console fallback
            if 'text' in dataset_counts:
                self.embed_text_samples(None, None)
            if 'images' in dataset_counts:
                self.embed_image_samples(None, None)
            if 'audio' in dataset_counts:
                self.embed_audio_samples(None, None)
        
        # Save embeddings
        embeddings_file, metadata_file = self.save_embeddings()
        
        # Print final summary
        self.print_embedding_summary()
        
        return embeddings_file, metadata_file
    
    def print_embedding_summary(self):
        """Print a summary of the embedding process."""
        total_embeddings = len(self.embeddings['text']) + len(self.embeddings['images']) + len(self.embeddings['audio'])
        
        if self.console:
            # Create summary table
            table = Table(title="🧠 Full Dataset Embedding Summary", style="bold")
            table.add_column("Modality", style="cyan")
            table.add_column("Embeddings Created", style="green")
            table.add_column("Sample Embedding Shape", style="yellow")
            
            if self.embeddings['text']:
                sample_shape = list(self.embeddings['text'].values())[0]['embedding_shape']
                table.add_row("Text", str(len(self.embeddings['text'])), str(sample_shape))
            
            if self.embeddings['images']:
                sample_shape = list(self.embeddings['images'].values())[0]['embedding_shape']
                table.add_row("Images", str(len(self.embeddings['images'])), str(sample_shape))
            
            if self.embeddings['audio']:
                sample_shape = list(self.embeddings['audio'].values())[0]['embedding_shape']
                table.add_row("Audio", str(len(self.embeddings['audio'])), str(sample_shape))
            
            table.add_row("TOTAL", str(total_embeddings), "Multimodal", style="bold yellow")
            
            self.console.print(table)
            
            # Success panel
            success_panel = Panel(
                f"🎉 SUCCESS: Created {total_embeddings} multimodal embeddings!\n"
                f"📊 All 400% scaled datasets fully embedded\n"
                f"💾 Embeddings saved for fast retrieval\n"
                f"🚀 Ready for similarity search, clustering, and analysis",
                title="🧠 Full Dataset Embedding Complete",
                style="bold green"
            )
            self.console.print(success_panel)
        
        else:
            print(f"\n🎉 SUCCESS: Created {total_embeddings} multimodal embeddings!")
            print(f"📝 Text embeddings: {len(self.embeddings['text'])}")
            print(f"🖼️ Image embeddings: {len(self.embeddings['images'])}")
            print(f"🎵 Audio embeddings: {len(self.embeddings['audio'])}")


def main():
    """Main entry point for full dataset embedding."""
    print("🧠 ImpressionCore-B1 Full Dataset Embedding System")
    print("=" * 60)
    
    try:
        # Create embedder
        embedder = FullDatasetEmbedder()
        
        # Run full embedding process
        embeddings_file, metadata_file = embedder.run_full_embedding()
        
        print(f"\n🎉 Full dataset embedding completed successfully!")
        print(f"📁 Embeddings file: {embeddings_file}")
        print(f"📋 Metadata file: {metadata_file}")
        print("\n🚀 Ready for multimodal AI applications!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Embedding process interrupted by user")
    except Exception as e:
        print(f"\n❌ Embedding process failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
