#!/usr/bin/env python3
"""
ImpressionCore Embedding Status Analyzer
Comprehensive analysis of current embedding status and remaining work
"""
import os
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import traceback

# Rich enhancements
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    console = None
    RICH_AVAILABLE = False

class EmbeddingStatusAnalyzer:
    """Analyzes current embedding status and identifies remaining work"""
    
    def __init__(self):
        self.data_root = Path("src/data")
        self.embeddings_root = Path("src/data/embeddings")
        
    def print_message(self, message: str, style: str = "white"):
        """Print message with optional styling"""
        if RICH_AVAILABLE and console:
            console.print(message, style=style)
        else:
            print(message)

    def load_embedding_summary(self):
        """Load the latest embedding summary"""
        summary_file = self.embeddings_root / "embedding_summary_20250611_175210.json"
        if summary_file.exists():
            try:
                with open(summary_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.print_message(f"⚠️ Could not load embedding summary: {e}", "yellow")
        return None

    def scan_all_files(self):
        """Scan all files in data directory"""
        files_by_modality = defaultdict(list)
        total_size = 0
        
        # Modality mapping
        modality_mapping = {
            # Image modalities
            '.jpg': 'image', '.jpeg': 'image', '.png': 'image', '.gif': 'image', 
            '.bmp': 'image', '.tiff': 'image', '.tif': 'image', '.webp': 'image',
            '.svg': 'image', '.ico': 'image',
            
            # Point clouds and 3D
            '.ply': 'point_clouds', '.pcd': 'point_clouds', '.xyz': 'point_clouds',
            '.las': 'point_clouds', '.laz': 'point_clouds', '.pts': 'point_clouds',
            '.off': '3d_models',  # OFF files are 3D models
            
            # Video
            '.mp4': 'video', '.avi': 'video', '.mov': 'video', '.mkv': 'video',
            '.wmv': 'video', '.flv': 'video', '.webm': 'video', '.m4v': 'video',
            
            # Audio
            '.wav': 'audio', '.mp3': 'audio', '.flac': 'audio', '.ogg': 'audio',
            '.aac': 'audio', '.wma': 'audio', '.m4a': 'audio',
            
            # Audio transcripts  
            '.textgrid': 'audio_transcripts', '.lab': 'audio_transcripts',
            '.transcript': 'audio_transcripts',
            
            # Text
            '.txt': 'text', '.md': 'text', '.rtf': 'text',
            
            # Code
            '.py': 'code', '.js': 'code', '.html': 'markup', '.css': 'code',
            '.cpp': 'code', '.c': 'code', '.java': 'code', '.go': 'code',
            
            # Structured data
            '.json': 'json_structured', '.yaml': 'json_structured', '.yml': 'json_structured',
            '.xml': 'xml_structured', '.xsl': 'xml_structured',
            '.csv': 'tabular', '.tsv': 'tabular', '.xlsx': 'tabular',
            
            # Captions and annotations
            '.srt': 'captioned_videos', '.vtt': 'captioned_videos',
            '.ass': 'captioned_videos', '.ssa': 'captioned_videos',
            
            # Other
            '.npy': 'time_series', '.npz': 'time_series',
            '.geojson': 'geospatial', '.kml': 'geospatial', '.shp': 'geospatial',
            '.dcm': 'medical_imaging', '.nii': 'medical_imaging', '.nifti': 'medical_imaging',
            '.pcap': 'network_data', '.cap': 'network_data',
            '.bin': 'sensor_data', '.dat': 'sensor_data', '.raw': 'sensor_data',
            '.pdf': 'documents', '.doc': 'documents', '.docx': 'documents'
        }
        
        self.print_message("🔍 Scanning all files in data directory...", "cyan")
        
        for root, dirs, files in os.walk(self.data_root):
            # Skip the embeddings directory itself
            if 'embeddings' in root:
                continue
                
            for file in files:
                file_path = Path(root) / file
                file_str = str(file_path).lower()
                
                # Skip system files
                if any(skip in file_str for skip in ['.git', '__pycache__', '.DS_Store', 'Thumbs.db']):
                    continue
                
                # Get file size
                try:
                    size = file_path.stat().st_size
                    total_size += size
                except:
                    size = 0
                
                # Determine modality
                suffix = file_path.suffix.lower()
                
                # Special cases for annotated images
                if suffix == '.json' and ('annotation' in file_str or 'caption' in file_str):
                    modality = 'annotated_images'
                else:
                    modality = modality_mapping.get(suffix, 'unknown')
                
                files_by_modality[modality].append({
                    'path': file_path,
                    'size': size
                })
        
        return files_by_modality, total_size

    def analyze_embeddings(self):
        """Analyze current embeddings"""
        embedding_files = {}
        
        for file_path in self.embeddings_root.glob("*_embeddings_*.npy"):
            # Extract modality from filename
            name = file_path.stem
            modality = name.replace('_embeddings_20250611_175210', '')
            
            try:
                embeddings = np.load(file_path)
                embedding_files[modality] = {
                    'file': file_path,
                    'count': len(embeddings),
                    'shape': embeddings.shape
                }
            except Exception as e:
                self.print_message(f"⚠️ Could not load {file_path}: {e}", "yellow")
        
        return embedding_files

    def run_analysis(self):
        """Run comprehensive analysis"""
        self.print_message("🎯 ImpressionCore Embedding Status Analysis", "bold blue")
        self.print_message("=" * 60, "blue")
        
        # Load embedding summary
        summary = self.load_embedding_summary()
        
        # Scan current files
        files_by_modality, total_size = self.scan_all_files()
        
        # Analyze embeddings
        embedding_files = self.analyze_embeddings()
        
        # Calculate statistics
        total_files = sum(len(file_list) for file_list in files_by_modality.values())
        embedded_files = summary.get('total_files_processed', 0) if summary else 0
        remaining_files = total_files - embedded_files
        
        # Overall status
        self.print_message(f"📊 OVERALL STATUS", "bold yellow")
        self.print_message(f"Total files found: {total_files:,}", "green")
        self.print_message(f"Total size: {total_size / (1024**3):.2f} GB", "green")
        self.print_message(f"Files embedded: {embedded_files:,}", "cyan")
        self.print_message(f"Files remaining: {remaining_files:,}", "red" if remaining_files > 0 else "green")
        self.print_message(f"Progress: {(embedded_files/total_files)*100:.1f}%" if total_files > 0 else "0%", "green")
        
        # Modality breakdown
        if RICH_AVAILABLE:
            table = Table(title="📂 Modality Analysis")
            table.add_column("Modality", style="cyan")
            table.add_column("Total Files", justify="right", style="white")
            table.add_column("Embedded", justify="right", style="green")
            table.add_column("Remaining", justify="right", style="red")
            table.add_column("Status", style="yellow")
            
            embedded_modalities = summary.get('modalities', {}) if summary else {}
            
            for modality, file_list in sorted(files_by_modality.items()):
                total = len(file_list)
                embedded = embedded_modalities.get(modality, 0)
                remaining = total - embedded
                
                if remaining == 0:
                    status = "✅ Complete"
                elif embedded == 0:
                    status = "❌ Not started"
                else:
                    status = f"🔄 {(embedded/total)*100:.1f}%"
                
                table.add_row(
                    modality,
                    f"{total:,}",
                    f"{embedded:,}",
                    f"{remaining:,}",
                    status
                )
            
            console.print(table)
        else:
            print("\nModality breakdown:")
            embedded_modalities = summary.get('modalities', {}) if summary else {}
            
            for modality, file_list in sorted(files_by_modality.items()):
                total = len(file_list)
                embedded = embedded_modalities.get(modality, 0)
                remaining = total - embedded
                print(f"  {modality}: {total:,} total, {embedded:,} embedded, {remaining:,} remaining")
        
        # Missing modalities
        all_modalities = set(files_by_modality.keys())
        embedded_modalities_set = set(summary.get('modalities', {}).keys()) if summary else set()
        missing_modalities = all_modalities - embedded_modalities_set
        
        if missing_modalities:
            self.print_message(f"❌ Missing modalities ({len(missing_modalities)}):", "red")
            for modality in sorted(missing_modalities):
                count = len(files_by_modality[modality])
                self.print_message(f"  • {modality}: {count:,} files", "red")
        else:
            self.print_message("✅ All modalities have some embeddings", "green")
        
        # Recommendations
        self.print_message("\n🎯 RECOMMENDATIONS", "bold yellow")
        
        if remaining_files > 0:
            self.print_message(f"🔄 Run continuation embedder for {remaining_files:,} remaining files", "cyan")
        
        if missing_modalities:
            self.print_message(f"🎯 Focus on missing modalities: {', '.join(sorted(missing_modalities))}", "cyan")
        
        if remaining_files == 0:
            self.print_message("🎉 All files embedded! Ready for training!", "green")
        
        # Save analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_file = f"embedding_status_analysis_{timestamp}.json"
        
        analysis_data = {
            'timestamp': timestamp,
            'total_files': total_files,
            'total_size_gb': total_size / (1024**3),
            'embedded_files': embedded_files,
            'remaining_files': remaining_files,
            'progress_percent': (embedded_files/total_files)*100 if total_files > 0 else 0,
            'modalities': {
                modality: {
                    'total': len(file_list),
                    'embedded': embedded_modalities.get(modality, 0),
                    'remaining': len(file_list) - embedded_modalities.get(modality, 0)
                }
                for modality, file_list in files_by_modality.items()
            },
            'missing_modalities': list(missing_modalities)
        }
        
        try:
            with open(analysis_file, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            self.print_message(f"📋 Analysis saved: {analysis_file}", "cyan")
        except Exception as e:
            self.print_message(f"⚠️ Could not save analysis: {e}", "yellow")

if __name__ == "__main__":
    analyzer = EmbeddingStatusAnalyzer()
    analyzer.run_analysis()
