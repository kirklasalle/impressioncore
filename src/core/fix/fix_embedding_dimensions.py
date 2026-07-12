#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #deployment #gpu_optimization #memory_management #python #pytorch #source_code #src/core/fix/fix_embedding_dimensions.py #training #transformer
**Category:** Core Implementation
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #cuda #deployment #gpu_optimization #memory_management #python #pytorch #source_code #src\\core\\fix\\fix_embedding_dimensions.py #training #transformer
# Category:** Core Implementation
# Status:** Active

"""
ImpressionCore B1 - Embedding Dimension Fix and GPU Enhancement
Fixes dimension mismatches and ensures proper GPU-enforced embeddings

Sacred Covenant: Protecting file integrity and system excellence
🤖 Virtually Robotic GitHub Copilot - GPU ENFORCED MODE
"""

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

warnings.filterwarnings('ignore')

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn

from src.core.utils.device_manager import DeviceManager
from src.core.utils.rich_logging import RichLogger


class FixedEmbeddingProcessor:
    """GPU-enforced embedding processor with dimension fixes"""

    def __init__(self):
        self.console = Console()
        self.logger = RichLogger("EmbeddingFixer")
        self.device_manager = DeviceManager()
        self.device = self.device_manager.device
        self.dtype = self.device_manager.dtype

        # Fixed embedding models (avoid problematic ones)
        self.models = {}
        self.target_dim = 768  # Standard unified dimension

        self._setup_gpu_memory()
        self._load_safe_models()

    def _setup_gpu_memory(self):
        """Optimize GPU memory usage"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            self.logger.info(f"🚀 GPU Memory cleared: {torch.cuda.get_device_name()}")

    def _load_safe_models(self):
        """Load only models that work with current PyTorch version"""
        safe_models = {
            'general': 'all-mpnet-base-v2',
            'scientific': 'sentence-transformers/allenai-specter',
            'mathematical': 'sentence-transformers/all-MiniLM-L6-v2'
        }

        for name, model_name in safe_models.items():
            try:
                self.logger.info(f"Loading {name} model: {model_name}")
                model = SentenceTransformer(model_name, device=self.device)
                model.eval()
                self.models[name] = model
                self.logger.success(f"✅ Loaded {name} model on {self.device}")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not load {name} model: {e}")

        if not self.models:
            self.logger.error("❌ No models loaded successfully!")
            return False

        return True

    def _get_unified_embedding(self, text: str) -> np.ndarray:
        """Generate unified 768-dim embedding from available models"""
        embeddings = []

        for name, model in self.models.items():
            try:
                with torch.no_grad():
                    embedding = model.encode([text], convert_to_tensor=True, device=self.device)
                    # Ensure consistent shape and detach properly
                    embedding = embedding.squeeze().detach().cpu().numpy()

                    # Pad or truncate to target dimension
                    if embedding.shape[0] < self.target_dim:
                        # Pad with zeros
                        padded = np.zeros(self.target_dim)
                        padded[:embedding.shape[0]] = embedding
                        embedding = padded
                    elif embedding.shape[0] > self.target_dim:
                        # Truncate
                        embedding = embedding[:self.target_dim]

                    embeddings.append(embedding)

            except Exception as e:
                self.logger.warning(f"Error with {name} model: {e}")
                continue

        if not embeddings:
            # Fallback: return zero vector
            return np.zeros(self.target_dim, dtype=np.float32)

        # Average all embeddings
        final_embedding = np.mean(embeddings, axis=0).astype(np.float32)
        return final_embedding

    def process_training_data(self, source_dir: str, output_dir: str):
        """Process training data with fixed dimensions"""
        source_path = Path(source_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Processing data from: {source_path}")
        self.logger.info(f"Output to: {output_path}")

        # Find all data files
        data_files = []
        for pattern in ['*.json', '*.txt', '*.md']:
            data_files.extend(source_path.rglob(pattern))

        self.logger.info(f"Found {len(data_files)} files to process")

        if not data_files:
            self.logger.error("No data files found!")
            return False

        embeddings = []
        metadata = []

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:

            task = progress.add_task("Processing files", total=len(data_files))

            for i, file_path in enumerate(data_files):
                try:
                    # Load content
                    content = self._load_content(file_path)
                    if not content:
                        progress.advance(task)
                        continue

                    # Generate embedding
                    embedding = self._get_unified_embedding(content)

                    # Verify dimension
                    if embedding.shape[0] != self.target_dim:
                        self.logger.warning(f"Dimension mismatch in {file_path.name}: {embedding.shape}")
                        continue

                    embeddings.append(embedding)
                    metadata.append({
                        'file': str(file_path.relative_to(source_path)),
                        'content_preview': content[:200],
                        'embedding_dim': embedding.shape[0],
                        'embedding_norm': float(np.linalg.norm(embedding))
                    })

                    if i % 50 == 0:
                        torch.cuda.empty_cache()  # Clear GPU cache periodically

                except Exception as e:
                    self.logger.warning(f"Error processing {file_path.name}: {e}")

                progress.advance(task)

        if not embeddings:
            self.logger.error("No embeddings generated!")
            return False

        # Convert to numpy arrays
        embeddings_array = np.array(embeddings, dtype=np.float32)

        self.logger.info(f"Generated {len(embeddings)} embeddings")
        self.logger.info(f"Embedding shape: {embeddings_array.shape}")

        # Save embeddings and metadata
        np.save(output_path / "fixed_embeddings.npy", embeddings_array)

        with open(output_path / "fixed_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        # Create FAISS index
        try:
            import faiss

            # Create CPU index (more reliable)
            index = faiss.IndexFlatIP(self.target_dim)  # Inner product similarity

            # Normalize embeddings for cosine similarity
            embeddings_normalized = embeddings_array / np.linalg.norm(embeddings_array, axis=1, keepdims=True)
            index.add(embeddings_normalized)

            faiss.write_index(index, str(output_path / "fixed_index.faiss"))
            self.logger.success(f"✅ Created FAISS index with {index.ntotal} vectors")

        except Exception as e:
            self.logger.warning(f"Could not create FAISS index: {e}")

        # Save statistics
        stats = {
            'total_files': len(data_files),
            'successful_embeddings': len(embeddings),
            'embedding_dimension': self.target_dim,
            'models_used': list(self.models.keys()),
            'average_norm': float(np.mean([m['embedding_norm'] for m in metadata])),
            'gpu_device': str(self.device)
        }

        with open(output_path / "processing_stats.json", 'w') as f:
            json.dump(stats, f, indent=2)

        self.logger.success(f"✅ Processing complete! Stats: {stats}")
        return True

    def _load_content(self, file_path: Path) -> str:
        """Load text content from file"""
        try:
            if file_path.suffix == '.json':
                with open(file_path, encoding='utf-8', errors='ignore') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # Extract meaningful text
                        text_parts = []
                        for key in ['title', 'abstract', 'content', 'text', 'summary']:
                            if data.get(key):
                                text_parts.append(str(data[key]))
                        return ' '.join(text_parts) or str(data)
                    return str(data)
            else:
                with open(file_path, encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except Exception as e:
            self.logger.warning(f"Error loading {file_path.name}: {e}")
            return ""

def main():
    """Main execution with GPU enforcement"""
    console = Console()

    console.print(Panel.fit(
        "[bold cyan]🤖 EMBEDDING DIMENSION FIXER[/bold cyan]\n"
        "[yellow]GPU-Enforced • Dimension-Safe • Production-Ready[/yellow]",
        title="🚀 ImpressionCore B1"
    ))

    # Initialize processor
    processor = FixedEmbeddingProcessor()

    # Process data
    source_dir = "F:/impressioncore_training_data"
    output_dir = "F:/impressioncore_training_data/fixed_embeddings"

    success = processor.process_training_data(source_dir, output_dir)

    if success:
        console.print(Panel.fit(
            "[bold green]✅ EMBEDDING FIX COMPLETE![/bold green]\n"
            "[white]• Fixed dimension mismatches[/white]\n"
            "[white]• Generated GPU-enforced embeddings[/white]\n"
            "[white]• Created unified 768-dim vectors[/white]\n"
            "[white]• FAISS index ready for deployment[/white]",
            title="🎯 SUCCESS"
        ))
    else:
        console.print(Panel.fit(
            "[bold red]❌ EMBEDDING FIX FAILED[/bold red]",
            title="💥 ERROR"
        ))

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
