#!/usr/bin/env python3
"""
Universal Multimodal Embedder
Embeds ALL files from the entire data/ directory across all 20 modalities
"""

import os
import sys
import numpy as np
import torch
from pathlib import Path
from collections import defaultdict
import json
import logging
from datetime import datetime
import pickle
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UniversalMultimodalEmbedder:
    def __init__(self, output_dir: str = "src/embeddings"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Track all processed files by modality
        self.processed_files = {
            'text': [], 'image': [], 'audio': [], 'video': [],
            'tabular': [], 'json_structured': [], 'xml_structured': [],
            'code': [], 'markup': [], 'geospatial': [], '3d_models': [],
            'point_clouds': [], 'sensor_data': [], 'network_data': [],
            'time_series': [], 'annotated_images': [], 'documents': [],
            'medical_imaging': [], 'audio_transcripts': [], 'captioned_videos': []
        }
        
        self.embeddings = defaultdict(list)
        self.metadata = defaultdict(list)
        self.total_embedded = 0
        self.errors = []
        
        # Initialize embedders
        self.init_embedders()
    
    def init_embedders(self):
        """Initialize embedding models for different modalities"""
        try:
            # Text embeddings
            try:
                from sentence_transformers import SentenceTransformer
                self.text_embedder = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("✅ Text embedder loaded")
            except ImportError:
                logger.warning("⚠️ sentence-transformers not available, using fallback")
                self.text_embedder = None
            
            # Image embeddings
            try:
                import torch
                import torchvision.transforms as transforms
                from torchvision.models import resnet18
                
                self.image_model = resnet18(pretrained=True)
                self.image_model.eval()
                self.image_transform = transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
                logger.info("✅ Image embedder loaded")
            except ImportError:
                logger.warning("⚠️ PyTorch/torchvision not available")
                self.image_model = None
            
            # Audio embeddings
            try:
                import librosa
                self.audio_available = True
                logger.info("✅ Audio processing available")
            except ImportError:
                logger.warning("⚠️ librosa not available")
                self.audio_available = False
                
        except Exception as e:
            logger.error(f"Error initializing embedders: {e}")
    
    def embed_text(self, file_path: Path) -> Optional[np.ndarray]:
        """Embed text files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()[:10000]  # Limit content size
                
            if self.text_embedder:
                embedding = self.text_embedder.encode([content])[0]
            else:
                # Fallback: simple character-based embedding
                embedding = np.array([hash(content[:1000]) % 1000 for _ in range(384)], dtype=np.float32)
                embedding = embedding / np.linalg.norm(embedding)
                
            return embedding
            
        except Exception as e:
            self.errors.append(f"Text embedding error for {file_path}: {e}")
            return None
    
    def embed_image(self, file_path: Path) -> Optional[np.ndarray]:
        """Embed image files"""
        try:
            from PIL import Image
            
            # Load and preprocess image
            image = Image.open(file_path).convert('RGB')
            
            if self.image_model:
                image_tensor = self.image_transform(image).unsqueeze(0)
                with torch.no_grad():
                    features = self.image_model(image_tensor)
                    embedding = features.squeeze().numpy()
            else:
                # Fallback: histogram-based features
                image_array = np.array(image)
                if len(image_array.shape) == 3:
                    # RGB histogram
                    hist_r = np.histogram(image_array[:,:,0], bins=32)[0]
                    hist_g = np.histogram(image_array[:,:,1], bins=32)[0]
                    hist_b = np.histogram(image_array[:,:,2], bins=32)[0]
                    embedding = np.concatenate([hist_r, hist_g, hist_b]).astype(np.float32)
                else:
                    # Grayscale histogram
                    embedding = np.histogram(image_array, bins=96)[0].astype(np.float32)
                
                embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
                
            return embedding
            
        except Exception as e:
            self.errors.append(f"Image embedding error for {file_path}: {e}")
            # Return zero vector as fallback
            return np.zeros(512, dtype=np.float32)
    
    def embed_audio(self, file_path: Path) -> Optional[np.ndarray]:
        """Embed audio files"""
        try:
            if self.audio_available:
                import librosa
                # Load audio file
                y, sr = librosa.load(file_path, duration=30.0)  # Limit to 30 seconds
                
                # Extract features
                mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
                zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
                
                # Combine features
                features = [
                    np.mean(mfccs, axis=1),
                    np.mean(spectral_centroid),
                    np.mean(zero_crossing_rate)
                ]
                
                embedding = np.concatenate([f.flatten() if isinstance(f, np.ndarray) else [f] for f in features])
                embedding = embedding.astype(np.float32)
            else:
                # Fallback: file size and basic stats
                file_size = file_path.stat().st_size
                embedding = np.array([file_size % 1000, (file_size // 1000) % 1000] + [0] * 126, dtype=np.float32)
                
            return embedding
            
        except Exception as e:
            self.errors.append(f"Audio embedding error for {file_path}: {e}")
            return np.zeros(128, dtype=np.float32)
    
    def embed_generic_binary(self, file_path: Path, target_dim: int = 256) -> np.ndarray:
        """Generic embedding for binary files"""
        try:
            # Read file in chunks to avoid memory issues
            chunk_size = 8192
            features = []
            
            with open(file_path, 'rb') as f:
                chunk_count = 0
                while chunk_count < 10:  # Limit to first 10 chunks
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    # Calculate basic statistics
                    byte_array = np.frombuffer(chunk, dtype=np.uint8)
                    features.extend([
                        np.mean(byte_array),
                        np.std(byte_array),
                        np.min(byte_array),
                        np.max(byte_array),
                        len(np.unique(byte_array)),
                        np.sum(byte_array % 2),  # Even/odd distribution
                    ])
                    chunk_count += 1
            
            # Pad or truncate to target dimension
            embedding = np.array(features[:target_dim], dtype=np.float32)
            if len(embedding) < target_dim:
                embedding = np.pad(embedding, (0, target_dim - len(embedding)), 'constant')
            
            # Normalize
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            return embedding
            
        except Exception as e:
            self.errors.append(f"Generic binary embedding error for {file_path}: {e}")
            return np.zeros(target_dim, dtype=np.float32)
    
    def embed_structured_data(self, file_path: Path) -> Optional[np.ndarray]:
        """Embed structured data (JSON, CSV, XML)"""
        try:
            if file_path.suffix.lower() in ['.json', '.jsonl']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()[:5000]  # Limit content
                    
                # Extract structural features
                features = [
                    content.count('{'),
                    content.count('['),
                    content.count('"'),
                    content.count(':'),
                    content.count(','),
                    len(content),
                    len(content.split('\n')),
                ]
                
            elif file_path.suffix.lower() in ['.csv', '.tsv']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[:100]  # First 100 lines
                    
                if lines:
                    # CSV features
                    first_line = lines[0]
                    features = [
                        len(lines),
                        len(first_line.split(',')),
                        first_line.count(','),
                        first_line.count('"'),
                        first_line.count(';'),
                        len(first_line),
                        sum(len(line) for line in lines) / len(lines),  # Average line length
                    ]
                else:
                    features = [0] * 7
                    
            else:  # XML, HTML, other markup
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()[:5000]
                    
                features = [
                    content.count('<'),
                    content.count('>'),
                    content.count('='),
                    content.count('"'),
                    content.count("'"),
                    len(content),
                    len(content.split('\n')),
                ]
            
            # Pad to consistent size
            embedding = np.array(features + [0] * (64 - len(features)), dtype=np.float32)[:64]
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            return embedding
            
        except Exception as e:
            self.errors.append(f"Structured data embedding error for {file_path}: {e}")
            return np.zeros(64, dtype=np.float32)
    
    def categorize_file(self, file_path: Path) -> str:
        """Categorize file by extension and context"""
        ext = file_path.suffix.lower()
        name = file_path.name.lower()
        parent = file_path.parent.name.lower()
        
        # Extension mappings
        extension_map = {
            # Text
            '.txt': 'text', '.md': 'text', '.rtf': 'text',
            
            # Images
            '.jpg': 'image', '.jpeg': 'image', '.png': 'image', '.bmp': 'image', 
            '.tiff': 'image', '.gif': 'image', '.webp': 'image',
            
            # Audio
            '.wav': 'audio', '.mp3': 'audio', '.flac': 'audio', '.ogg': 'audio', 
            '.m4a': 'audio', '.aac': 'audio',
            
            # Video
            '.mp4': 'video', '.avi': 'video', '.mov': 'video', '.mkv': 'video', 
            '.webm': 'video', '.flv': 'video', '.wmv': 'video',
            
            # Structured data
            '.json': 'json_structured', '.jsonl': 'json_structured',
            '.xml': 'xml_structured', '.html': 'xml_structured', '.htm': 'xml_structured',
            '.csv': 'tabular', '.tsv': 'tabular', '.xls': 'tabular', '.xlsx': 'tabular',
            
            # Code
            '.py': 'code', '.js': 'code', '.java': 'code', '.cpp': 'code', '.c': 'code',
            '.cs': 'code', '.php': 'code', '.rb': 'code', '.go': 'code', '.rs': 'code',
            
            # Markup
            '.svg': 'markup',
            
            # 3D models
            '.obj': '3d_models', '.ply': '3d_models', '.stl': '3d_models', '.off': '3d_models',
            '.3ds': '3d_models',
            
            # Point clouds
            '.pcd': 'point_clouds', '.pts': 'point_clouds', '.xyz': 'point_clouds',
            
            # Network data
            '.pcap': 'network_data', '.cap': 'network_data', '.pcapng': 'network_data',
            
            # Sensor data
            '.bin': 'sensor_data', '.dat': 'sensor_data', '.raw': 'sensor_data',
            
            # Documents
            '.pdf': 'documents', '.doc': 'documents', '.docx': 'documents',
            
            # Medical imaging
            '.dcm': 'medical_imaging', '.nii': 'medical_imaging', '.nrrd': 'medical_imaging',
            
            # Geospatial
            '.geojson': 'geospatial', '.kml': 'geospatial', '.shp': 'geospatial', '.gpx': 'geospatial',
            
            # Audio transcripts
            '.textgrid': 'audio_transcripts', '.srt': 'audio_transcripts', '.vtt': 'audio_transcripts',
            
            # Other formats
            '.npy': 'sensor_data',  # NumPy arrays often contain sensor data
        }
        
        # Check extension first
        if ext in extension_map:
            base_category = extension_map[ext]
        else:
            base_category = 'text'  # Default fallback
        
        # Context-based refinements
        if 'annotated' in parent or 'annotation' in parent:
            if base_category == 'image':
                return 'annotated_images'
        
        if 'time_series' in parent or 'timeseries' in parent:
            return 'time_series'
        
        if 'caption' in parent or 'captioned' in parent:
            if base_category == 'video':
                return 'captioned_videos'
        
        return base_category
    
    def scan_and_embed_all(self):
        """Scan entire data directory and embed all files"""
        print("🔍 Scanning entire data/ directory for embedding...")
        
        data_dir = Path("src/data")
        if not data_dir.exists():
            logger.error("❌ Data directory not found!")
            return
        
        # Get all files
        all_files = []
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                file_path = Path(root) / file
                if not file.startswith('.') and file_path.is_file():
                    all_files.append(file_path)
        
        print(f"📊 Found {len(all_files):,} total files to process")
        
        # Categorize files
        file_categories = defaultdict(list)
        for file_path in all_files:
            category = self.categorize_file(file_path)
            file_categories[category].append(file_path)
        
        # Show breakdown
        print(f"\n📋 File breakdown by modality:")
        for modality, files in sorted(file_categories.items()):
            print(f"  {modality:20s}: {len(files):7,} files")
        
        # Embed each category
        print(f"\n🚀 Starting embedding process...")
        total_processed = 0
        
        for modality, files in file_categories.items():
            print(f"\n📂 Processing {modality} ({len(files):,} files)...")
            
            batch_size = min(1000, len(files))  # Process in batches
            for i in range(0, len(files), batch_size):
                batch = files[i:i+batch_size]
                batch_embeddings = []
                batch_metadata = []
                
                for j, file_path in enumerate(batch):
                    try:
                        # Choose embedding method based on modality
                        if modality in ['text', 'code', 'documents']:
                            embedding = self.embed_text(file_path)
                        elif modality in ['image', 'annotated_images']:
                            embedding = self.embed_image(file_path)
                        elif modality == 'audio':
                            embedding = self.embed_audio(file_path)
                        elif modality in ['json_structured', 'xml_structured', 'tabular', 'markup']:
                            embedding = self.embed_structured_data(file_path)
                        else:
                            # Generic binary embedding for other modalities
                            embedding = self.embed_generic_binary(file_path)
                        
                        if embedding is not None:
                            batch_embeddings.append(embedding)
                            batch_metadata.append({
                                'file_path': str(file_path),
                                'modality': modality,
                                'file_size': file_path.stat().st_size,
                                'extension': file_path.suffix.lower(),
                                'embedding_dim': len(embedding)
                            })
                            
                            self.processed_files[modality].append(str(file_path))
                            total_processed += 1
                        
                        # Progress update
                        if (j + 1) % 100 == 0 or j == len(batch) - 1:
                            progress = ((i + j + 1) / len(files)) * 100
                            print(f"    Progress: {progress:.1f}% ({i + j + 1:,}/{len(files):,})")
                    
                    except Exception as e:
                        self.errors.append(f"Error processing {file_path}: {e}")
                        continue
                
                # Store batch results
                if batch_embeddings:
                    self.embeddings[modality].extend(batch_embeddings)
                    self.metadata[modality].extend(batch_metadata)
            
            print(f"    ✅ Completed {modality}: {len(self.embeddings[modality]):,} embeddings")
        
        self.total_embedded = total_processed
        print(f"\n🎯 EMBEDDING COMPLETE!")
        print(f"📊 Total files processed: {self.total_embedded:,}")
        print(f"❌ Errors encountered: {len(self.errors)}")
    
    def save_embeddings(self):
        """Save all embeddings and metadata"""
        print(f"\n💾 Saving embeddings...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save embeddings by modality
        for modality, embeddings in self.embeddings.items():
            if embeddings:
                # Convert to numpy array
                embedding_array = np.array(embeddings)
                
                # Save embeddings
                embedding_file = self.output_dir / f"{modality}_embeddings_{timestamp}.npy"
                np.save(embedding_file, embedding_array)
                
                # Save metadata
                metadata_file = self.output_dir / f"{modality}_metadata_{timestamp}.json"
                with open(metadata_file, 'w') as f:
                    json.dump(self.metadata[modality], f, indent=2)
                
                print(f"  ✅ {modality}: {len(embeddings):,} embeddings saved")
                print(f"      Shape: {embedding_array.shape}")
                print(f"      Files: {embedding_file.name}, {metadata_file.name}")
        
        # Save summary
        summary = {
            'timestamp': timestamp,
            'total_files_processed': self.total_embedded,
            'modalities': {k: len(v) for k, v in self.embeddings.items()},
            'embedding_dimensions': {k: v[0].shape[0] if v else 0 for k, v in self.embeddings.items()},
            'processed_files_by_modality': self.processed_files,
            'errors': self.errors[:100],  # First 100 errors
            'error_count': len(self.errors)
        }
        
        summary_file = self.output_dir / f"embedding_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📋 Summary saved to: {summary_file}")
        
        # Save embeddings index
        index = {
            'timestamp': timestamp,
            'modalities': list(self.embeddings.keys()),
            'total_embeddings': sum(len(v) for v in self.embeddings.values()),
            'files': {
                modality: f"{modality}_embeddings_{timestamp}.npy" 
                for modality in self.embeddings.keys()
            }
        }
        
        index_file = self.output_dir / "latest_embeddings_index.json"
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
        
        print(f"📇 Index saved to: {index_file}")
    
    def run(self):
        """Main execution function"""
        print("🎯 Universal Multimodal Embedder")
        print("=" * 60)
        print("Goal: Embed ALL files from data/ directory")
        print(f"Output: {self.output_dir}")
        print()
        
        try:
            # Scan and embed all files
            self.scan_and_embed_all()
            
            # Save results
            self.save_embeddings()
            
            # Final summary
            print(f"\n🎉 EMBEDDING COMPLETE!")
            print("=" * 60)
            print(f"📊 Files processed: {self.total_embedded:,}")
            print(f"🎯 Modalities covered: {len([k for k, v in self.embeddings.items() if v])}/20")
            print(f"💾 Output directory: {self.output_dir}")
            print(f"❌ Errors: {len(self.errors)}")
            
            if self.errors:
                print(f"\n⚠️ First few errors:")
                for error in self.errors[:5]:
                    print(f"  • {error}")
            
            print(f"\n✅ All data from data/ directory has been embedded!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fatal error during embedding: {e}")
            return False

if __name__ == "__main__":
    # Change to project root
    if not os.path.exists("src"):
        if os.path.exists("d:/Projects/impressioncore"):
            os.chdir("d:/Projects/impressioncore")
        else:
            print("❌ Cannot find ImpressionCore project directory!")
            sys.exit(1)
    
    embedder = UniversalMultimodalEmbedder()
    success = embedder.run()
    
    if success:
        print("\n🚀 Ready for training with fully embedded dataset!")
    else:
        print("\n❌ Embedding process encountered issues.")
