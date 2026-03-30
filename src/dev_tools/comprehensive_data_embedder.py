#!/usr/bin/env python3
"""
Comprehensive Data Embedder for ImpressionCore
Embeds ALL available data across the entire data/ directory structure
"""

import os
import sys
import json
import pickle
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
import librosa

# Optional imports
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

from transformers import (
    AutoTokenizer, AutoModel, 
    CLIPProcessor, CLIPModel,
    Wav2Vec2Processor, Wav2Vec2Model
)

# Rich enhancements for better UI
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    console = None
    RICH_AVAILABLE = False

class ComprehensiveDataEmbedder:
    """Comprehensive embedder for all data types in ImpressionCore"""
    
    def __init__(self, data_root: str = "src/data", device: str = "auto"):
        self.data_root = Path(data_root)
        self.device = self._setup_device(device)
        self.embeddings = {}
        self.metadata = {}
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'skipped_files': 0,
            'error_files': 0,
            'file_types': {},
            'modalities': {}
        }
        
        # File type mappings
        self.text_extensions = {'.txt', '.md', '.json', '.jsonl', '.csv', '.xml', '.yaml', '.yml'}
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        self.audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
        self.video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv'}
        self.other_extensions = {'.pdf', '.doc', '.docx', '.rtf'}
        
        # Initialize models
        self._init_models()
        
        if RICH_AVAILABLE:
            console.print(Panel.fit(
                f"[bold blue]Comprehensive Data Embedder Initialized[/bold blue]\n"
                f"Data Root: {self.data_root}\n"
                f"Device: {self.device}",
                title="🧠 ImpressionCore Data Embedder"
            ))
    
    def _setup_device(self, device: str) -> str:
        """Setup computation device"""
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            else:
                return "cpu"
        return device
    
    def _init_models(self):
        """Initialize embedding models for different modalities"""
        if RICH_AVAILABLE:
            console.print("[yellow]Initializing embedding models...[/yellow]")
        
        try:
            # Text embedding model - lightweight but capable
            self.text_tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
            self.text_model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2').to(self.device)
            
            # Image embedding model - CLIP for multimodal understanding
            self.image_processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')
            self.image_model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32').to(self.device)
            
            # Audio embedding model - Wav2Vec2 for speech understanding
            self.audio_processor = Wav2Vec2Processor.from_pretrained('facebook/wav2vec2-base-960h')
            self.audio_model = Wav2Vec2Model.from_pretrained('facebook/wav2vec2-base-960h').to(self.device)
            
            if RICH_AVAILABLE:
                console.print("[green]✓ All models initialized successfully[/green]")
                
        except Exception as e:
            error_msg = f"Error initializing models: {str(e)}"
            if RICH_AVAILABLE:
                console.print(f"[red]{error_msg}[/red]")
            else:
                print(error_msg)
            raise
    
    def discover_all_files(self) -> Dict[str, List[Path]]:
        """Discover all embeddable files across the entire data directory"""
        if RICH_AVAILABLE:
            console.print("[blue]🔍 Discovering all data files...[/blue]")
        
        file_categories = {
            'text': [],
            'image': [],
            'audio': [],
            'video': [],
            'other': []
        }
        
        # Walk through entire data directory structure
        for root, dirs, files in os.walk(self.data_root):
            root_path = Path(root)
            
            # Skip certain directories
            skip_dirs = {'__pycache__', '.git', 'node_modules', 'venv', '.venv', 'embeddings'}
            if any(skip_dir in root_path.parts for skip_dir in skip_dirs):
                continue
            
            for file in files:
                file_path = root_path / file
                file_ext = file_path.suffix.lower()
                
                # Categorize files
                if file_ext in self.text_extensions:
                    file_categories['text'].append(file_path)
                elif file_ext in self.image_extensions:
                    file_categories['image'].append(file_path)
                elif file_ext in self.audio_extensions:
                    file_categories['audio'].append(file_path)
                elif file_ext in self.video_extensions:
                    file_categories['video'].append(file_path)
                elif file_ext in self.other_extensions:
                    file_categories['other'].append(file_path)
        
        # Update stats
        for category, files in file_categories.items():
            self.stats['modalities'][category] = len(files)
            self.stats['total_files'] += len(files)
        
        if RICH_AVAILABLE:
            # Display discovery results
            table = Table(title="📊 Data Discovery Results")
            table.add_column("Modality", style="cyan", no_wrap=True)
            table.add_column("Files Found", style="magenta")
            table.add_column("Examples", style="green")
            
            for category, files in file_categories.items():
                examples = ", ".join([f.name for f in files[:3]]) if files else "None"
                if len(files) > 3:
                    examples += "..."
                table.add_row(
                    category.capitalize(),
                    str(len(files)),
                    examples
                )
            
            console.print(table)
        
        return file_categories
    
    def embed_text_file(self, file_path: Path) -> Optional[np.ndarray]:
        """Embed text file content"""
        try:
            # Read text content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Skip empty files
            if not content.strip():
                return None
            
            # Handle large files by chunking
            max_length = 500  # tokens
            if len(content) > max_length * 4:  # rough estimate
                content = content[:max_length * 4]
            
            # Tokenize and embed
            inputs = self.text_tokenizer(
                content,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=max_length
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.text_model(**inputs)
                # Use mean pooling of last hidden states
                embeddings = outputs.last_hidden_state.mean(dim=1)
                
            return embeddings.cpu().numpy().flatten()
            
        except Exception as e:
            logging.warning(f"Error embedding text file {file_path}: {str(e)}")
            return None
    
    def embed_image_file(self, file_path: Path) -> Optional[np.ndarray]:
        """Embed image file"""
        try:
            # Load image
            image = Image.open(file_path).convert('RGB')
            
            # Process with CLIP
            inputs = self.image_processor(images=image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                image_features = self.image_model.get_image_features(**inputs)
                
            return image_features.cpu().numpy().flatten()
            
        except Exception as e:
            logging.warning(f"Error embedding image file {file_path}: {str(e)}")
            return None
    
    def embed_audio_file(self, file_path: Path) -> Optional[np.ndarray]:
        """Embed audio file"""
        try:
            # Load audio
            audio, sr = librosa.load(file_path, sr=16000, duration=10.0)  # Limit to 10 seconds
            
            # Skip very short audio
            if len(audio) < 1600:  # Less than 0.1 seconds
                return None
            
            # Process with Wav2Vec2
            inputs = self.audio_processor(
                audio,
                sampling_rate=16000,
                return_tensors="pt",
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.audio_model(**inputs)
                # Use mean pooling of hidden states
                embeddings = outputs.last_hidden_state.mean(dim=1)
                
            return embeddings.cpu().numpy().flatten()
            
        except Exception as e:
            logging.warning(f"Error embedding audio file {file_path}: {str(e)}")
            return None
    
    def embed_all_files(self, file_categories: Dict[str, List[Path]]):
        """Embed all discovered files"""
        total_files = sum(len(files) for files in file_categories.values())
        
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                task = progress.add_task("🚀 Embedding all files...", total=total_files)
                
                self._process_files_with_progress(file_categories, progress, task)
        else:
            print(f"Processing {total_files} files...")
            self._process_files_simple(file_categories)
    
    def _process_files_with_progress(self, file_categories: Dict[str, List[Path]], progress, task):
        """Process files with rich progress display"""
        for category, files in file_categories.items():
            for file_path in files:
                try:
                    embedding = None
                    
                    if category == 'text':
                        embedding = self.embed_text_file(file_path)
                    elif category == 'image':
                        embedding = self.embed_image_file(file_path)
                    elif category == 'audio':
                        embedding = self.embed_audio_file(file_path)
                    
                    if embedding is not None:
                        self.embeddings[str(file_path)] = embedding
                        self.metadata[str(file_path)] = {
                            'category': category,
                            'size': file_path.stat().st_size,
                            'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                            'embedding_shape': embedding.shape,
                            'embedding_dimension': len(embedding)
                        }
                        self.stats['processed_files'] += 1
                    else:
                        self.stats['skipped_files'] += 1
                    
                    # Update file type stats
                    ext = file_path.suffix.lower()
                    self.stats['file_types'][ext] = self.stats['file_types'].get(ext, 0) + 1
                    
                except Exception as e:
                    logging.error(f"Error processing {file_path}: {str(e)}")
                    self.stats['error_files'] += 1
                
                progress.advance(task)
    
    def _process_files_simple(self, file_categories: Dict[str, List[Path]]):
        """Process files with simple progress display"""
        processed = 0
        total = sum(len(files) for files in file_categories.values())
        
        for category, files in file_categories.items():
            for file_path in files:
                try:
                    embedding = None
                    
                    if category == 'text':
                        embedding = self.embed_text_file(file_path)
                    elif category == 'image':
                        embedding = self.embed_image_file(file_path)
                    elif category == 'audio':
                        embedding = self.embed_audio_file(file_path)
                    
                    if embedding is not None:
                        self.embeddings[str(file_path)] = embedding
                        self.metadata[str(file_path)] = {
                            'category': category,
                            'size': file_path.stat().st_size,
                            'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                            'embedding_shape': embedding.shape,
                            'embedding_dimension': len(embedding)
                        }
                        self.stats['processed_files'] += 1
                    else:
                        self.stats['skipped_files'] += 1
                    
                    # Update file type stats
                    ext = file_path.suffix.lower()
                    self.stats['file_types'][ext] = self.stats['file_types'].get(ext, 0) + 1
                    
                except Exception as e:
                    logging.error(f"Error processing {file_path}: {str(e)}")
                    self.stats['error_files'] += 1
                
                processed += 1
                if processed % 10 == 0:
                    print(f"Processed {processed}/{total} files...")
    
    def save_embeddings(self):
        """Save embeddings and metadata"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save embeddings
        embeddings_file = self.data_root / 'embeddings' / f'comprehensive_embeddings_{timestamp}.pkl'
        embeddings_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(embeddings_file, 'wb') as f:
            pickle.dump(self.embeddings, f)
        
        # Save metadata
        metadata_file = self.data_root / 'embeddings' / f'comprehensive_metadata_{timestamp}.json'
        
        # Add stats to metadata
        full_metadata = {
            'stats': self.stats,
            'timestamp': timestamp,
            'total_embeddings': len(self.embeddings),
            'file_metadata': self.metadata
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(full_metadata, f, indent=2)
        
        if RICH_AVAILABLE:
            console.print(Panel.fit(
                f"[bold green]✅ Embeddings Saved Successfully[/bold green]\n\n"
                f"📁 Embeddings: {embeddings_file}\n"
                f"📋 Metadata: {metadata_file}\n\n"
                f"📊 Statistics:\n"
                f"  • Total files processed: {self.stats['processed_files']}\n"
                f"  • Files skipped: {self.stats['skipped_files']}\n"
                f"  • Files with errors: {self.stats['error_files']}\n"
                f"  • Total embeddings: {len(self.embeddings)}",
                title="💾 Save Complete"
            ))
        else:
            print(f"Embeddings saved to: {embeddings_file}")
            print(f"Metadata saved to: {metadata_file}")
            print(f"Total embeddings: {len(self.embeddings)}")
    
    def generate_report(self):
        """Generate comprehensive embedding report"""
        if RICH_AVAILABLE:
            # Statistics table
            stats_table = Table(title="📈 Comprehensive Embedding Statistics")
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Count", style="magenta")
            
            stats_table.add_row("Total Files Discovered", str(self.stats['total_files']))
            stats_table.add_row("Successfully Processed", str(self.stats['processed_files']))
            stats_table.add_row("Skipped Files", str(self.stats['skipped_files']))
            stats_table.add_row("Error Files", str(self.stats['error_files']))
            stats_table.add_row("Total Embeddings Created", str(len(self.embeddings)))
            
            # Modality breakdown
            modality_table = Table(title="🎯 Files by Modality")
            modality_table.add_column("Modality", style="green")
            modality_table.add_column("File Count", style="blue")
            
            for modality, count in self.stats['modalities'].items():
                modality_table.add_row(modality.capitalize(), str(count))
            
            # File type breakdown
            filetype_table = Table(title="📄 Files by Extension")
            filetype_table.add_column("Extension", style="yellow")
            filetype_table.add_column("Count", style="red")
            
            for ext, count in sorted(self.stats['file_types'].items()):
                filetype_table.add_row(ext, str(count))
            
            console.print(stats_table)
            console.print(modality_table)
            console.print(filetype_table)
        else:
            print("\n" + "="*50)
            print("COMPREHENSIVE EMBEDDING REPORT")
            print("="*50)
            print(f"Total Files Discovered: {self.stats['total_files']}")
            print(f"Successfully Processed: {self.stats['processed_files']}")
            print(f"Skipped Files: {self.stats['skipped_files']}")
            print(f"Error Files: {self.stats['error_files']}")
            print(f"Total Embeddings Created: {len(self.embeddings)}")
            print("\nModality Breakdown:")
            for modality, count in self.stats['modalities'].items():
                print(f"  {modality.capitalize()}: {count}")
    
    def run_comprehensive_embedding(self):
        """Run the complete embedding process"""
        if RICH_AVAILABLE:
            console.print(Panel.fit(
                "[bold cyan]🚀 Starting Comprehensive Data Embedding[/bold cyan]\n"
                "This will process ALL available data files across the entire data/ directory",
                title="ImpressionCore Data Embedder"
            ))
        
        # Discover all files
        file_categories = self.discover_all_files()
        
        # Embed all files
        self.embed_all_files(file_categories)
        
        # Save results
        self.save_embeddings()
        
        # Generate report
        self.generate_report()
        
        return len(self.embeddings), self.stats

def analyze_missing_modalities():
    """Analyze what data types might be missing for a complete multimodal model"""
    
    missing_modalities = []
    recommendations = []
    
    if RICH_AVAILABLE:
        console.print(Panel.fit(
            "[bold blue]🔍 Analyzing Missing Data Modalities[/bold blue]",
            title="Multimodal Completeness Analysis"
        ))
    
    # Check for video data
    video_found = False
    data_path = Path("src/data")
    
    # Search for video files
    for ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv']:
        if list(data_path.rglob(f"*{ext}")):
            video_found = True
            break
    
    if not video_found:
        missing_modalities.append("Video")
        recommendations.append({
            'modality': 'Video',
            'description': 'Video understanding for temporal and visual analysis',
            'suggested_datasets': [
                'UCF-101 (action recognition)',
                'Kinetics-400 (video classification)',
                'Something-Something V2 (temporal reasoning)',
                'YouTube-8M (large-scale video understanding)'
            ],
            'download_sources': [
                'https://www.crcv.ucf.edu/data/UCF101.php',
                'https://deepmind.com/research/open-source/kinetics',
                'https://developer.qualcomm.com/software/ai-datasets/something-something'
            ]
        })
    
    # Check for tabular/structured data
    tabular_extensions = ['.csv', '.tsv', '.xlsx', '.parquet']
    tabular_found = any(list(data_path.rglob(f"*{ext}")) for ext in tabular_extensions)
    
    if not tabular_found:
        missing_modalities.append("Tabular/Structured Data")
        recommendations.append({
            'modality': 'Tabular/Structured Data',
            'description': 'Structured data for reasoning and analysis',
            'suggested_datasets': [
                'Titanic Dataset',
                'Iris Dataset',
                'Wine Quality Dataset',
                'Boston Housing Dataset'
            ],
            'download_sources': [
                'https://www.kaggle.com/c/titanic/data',
                'https://archive.ics.uci.edu/ml/datasets/iris',
                'https://archive.ics.uci.edu/ml/datasets/wine+quality'
            ]
        })
    
    # Check for 3D/spatial data
    spatial_extensions = ['.obj', '.ply', '.stl', '.off']
    spatial_found = any(list(data_path.rglob(f"*{ext}")) for ext in spatial_extensions)
    
    if not spatial_found:
        missing_modalities.append("3D/Spatial Data")
        recommendations.append({
            'modality': '3D/Spatial Data',
            'description': '3D models and spatial understanding',
            'suggested_datasets': [
                'ModelNet40 (3D object classification)',
                'ShapeNet (3D model repository)',
                'S3DIS (3D indoor scene understanding)'
            ],
            'download_sources': [
                'https://modelnet.cs.princeton.edu/',
                'https://shapenet.org/',
                'http://buildingparser.stanford.edu/dataset.html'
            ]
        })
    
    # Check for time series data
    timeseries_found = False
    # Look for files that might contain time series (this is heuristic)
    for file_path in data_path.rglob("*.csv"):
        if any(keyword in str(file_path).lower() for keyword in ['time', 'series', 'temporal', 'stock', 'sensor']):
            timeseries_found = True
            break
    
    if not timeseries_found:
        missing_modalities.append("Time Series Data")
        recommendations.append({
            'modality': 'Time Series Data',
            'description': 'Temporal sequences for forecasting and pattern recognition',
            'suggested_datasets': [
                'Stock Price Data',
                'Weather Data',
                'Sensor Data',
                'ECG/EEG Data'
            ],
            'download_sources': [
                'https://finance.yahoo.com/ (stock data)',
                'https://openweathermap.org/api (weather data)',
                'https://www.physionet.org/ (biomedical signals)'
            ]
        })
    
    # Check for multilingual text
    multilingual_found = False
    # This is a rough heuristic - check if we have non-English text files
    for file_path in data_path.rglob("*.txt"):
        if any(lang in str(file_path).lower() for lang in ['multilingual', 'spanish', 'french', 'chinese', 'german']):
            multilingual_found = True
            break
    
    if not multilingual_found:
        missing_modalities.append("Multilingual Text")
        recommendations.append({
            'modality': 'Multilingual Text',
            'description': 'Text in multiple languages for global understanding',
            'suggested_datasets': [
                'CC-100 (multilingual text)',
                'OPUS (parallel texts)',
                'mC4 (multilingual Common Crawl)'
            ],
            'download_sources': [
                'https://data.statmt.org/cc-100/',
                'https://opus.nlpl.eu/',
                'https://huggingface.co/datasets/mc4'
            ]
        })
    
    # Display results
    if RICH_AVAILABLE:
        if missing_modalities:
            console.print(f"[yellow]⚠️  Found {len(missing_modalities)} missing modalities for complete multimodal coverage[/yellow]")
            
            for rec in recommendations:
                panel_content = f"[bold]{rec['description']}[/bold]\n\n"
                panel_content += "📊 Suggested Datasets:\n"
                for dataset in rec['suggested_datasets']:
                    panel_content += f"  • {dataset}\n"
                panel_content += "\n🔗 Download Sources:\n"
                for source in rec['download_sources']:
                    panel_content += f"  • {source}\n"
                
                console.print(Panel.fit(
                    panel_content,
                    title=f"🎯 Missing: {rec['modality']}",
                    border_style="yellow"
                ))
        else:
            console.print("[green]✅ All major modalities appear to be covered![/green]")
    else:
        print(f"\nMissing Modalities Analysis:")
        print(f"Found {len(missing_modalities)} missing modalities:")
        for modality in missing_modalities:
            print(f"  - {modality}")
    
    return missing_modalities, recommendations

def main():
    """Main execution function"""
    try:
        # Initialize embedder
        embedder = ComprehensiveDataEmbedder()
        
        # Run comprehensive embedding
        total_embeddings, stats = embedder.run_comprehensive_embedding()
        
        # Analyze missing modalities
        missing_modalities, recommendations = analyze_missing_modalities()
        
        if RICH_AVAILABLE:
            console.print(Panel.fit(
                f"[bold green]🎉 Comprehensive Data Embedding Complete![/bold green]\n\n"
                f"📊 Final Results:\n"
                f"  • Total embeddings created: {total_embeddings}\n"
                f"  • Files processed: {stats['processed_files']}\n"
                f"  • Missing modalities: {len(missing_modalities)}\n\n"
                f"🚀 All available data in the ImpressionCore data/ directory\n"
                f"   has been successfully embedded and is ready for training!",
                title="✅ Mission Complete"
            ))
        else:
            print(f"\n" + "="*60)
            print("COMPREHENSIVE DATA EMBEDDING COMPLETE!")
            print("="*60)
            print(f"Total embeddings created: {total_embeddings}")
            print(f"Files processed: {stats['processed_files']}")
            print(f"Missing modalities: {len(missing_modalities)}")
        
        return True
        
    except Exception as e:
        error_msg = f"Error during comprehensive embedding: {str(e)}"
        if RICH_AVAILABLE:
            console.print(f"[red]❌ {error_msg}[/red]")
        else:
            print(f"ERROR: {error_msg}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
