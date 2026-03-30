#!/usr/bin/env python3
"""
ImpressionCore Data Marshal and Embedding Launcher
==================================================
Comprehensive system to marshal all data and launch full embedding process.
"""

import os
import json
import time
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import subprocess

class ImpressionCoreDataMarshal:
    def __init__(self):
        self.project_root = Path(".")
        self.data_root = self.project_root / "src" / "data"
        self.embeddings_root = self.data_root / "embeddings"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure directories exist
        self.embeddings_root.mkdir(parents=True, exist_ok=True)
        
        self.modalities = {
            '3d_models': ['.obj', '.off', '.ply', '.stl', '.3ds'],
            'annotated_images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
            'audio': ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac'],
            'audio_transcripts': ['.textgrid', '.lab', '.txt'],
            'captioned_videos': ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
            'code': ['.py', '.js', '.cpp', '.c', '.java', '.go', '.rs', '.ts'],
            'documents': ['.pdf', '.doc', '.docx', '.rtf'],
            'geospatial': ['.geojson', '.kml', '.shp', '.gpx'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
            'json_structured': ['.json', '.jsonl'],
            'markup': ['.html', '.htm', '.md', '.xml'],
            'medical_imaging': ['.dcm', '.nii', '.nifti'],
            'network_data': ['.pcap', '.cap', '.pcapng'],
            'point_clouds': ['.pcd', '.las', '.xyz'],
            'sensor_data': ['.bin', '.dat', '.raw'],
            'tabular': ['.csv', '.tsv', '.xlsx', '.xls'],
            'text': ['.txt', '.log', '.md'],
            'time_series': ['.npy', '.npz', '.h5', '.hdf5'],
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
            'xml_structured': ['.xml', '.xsd', '.xsl']
        }
        
    def marshal_all_data(self):
        """Marshal all data files and categorize by modality."""
        print("🎯 ImpressionCore Data Marshal - FULL SYSTEM")
        print("=" * 60)
        
        all_files = []
        modality_counts = defaultdict(int)
        total_size = 0
        
        # Scan all data directories
        for root, dirs, files in os.walk(self.data_root):
            # Skip embeddings directory
            if 'embeddings' in Path(root).parts:
                continue
                
            for file in files:
                file_path = Path(root) / file
                try:
                    file_size = file_path.stat().st_size
                    total_size += file_size
                    
                    # Determine modality
                    modality = self.determine_modality(file_path)
                    modality_counts[modality] += 1
                    
                    all_files.append({
                        'path': str(file_path),
                        'modality': modality,
                        'size': file_size,
                        'extension': file_path.suffix.lower()
                    })
                except Exception as e:
                    print(f"⚠️ Error processing {file_path}: {e}")
        
        # Create marshal report
        marshal_report = {
            'timestamp': self.timestamp,
            'total_files': len(all_files),
            'total_size_gb': round(total_size / (1024**3), 2),
            'modalities_found': len(modality_counts),
            'modality_breakdown': dict(modality_counts),
            'files': all_files
        }
        
        # Save marshal report
        report_path = self.embeddings_root / f"data_marshal_report_{self.timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(marshal_report, f, indent=2)
        
        # Display summary
        print(f"📊 MARSHAL SUMMARY")
        print(f"Total files: {len(all_files):,}")
        print(f"Total size: {marshal_report['total_size_gb']:.2f} GB")
        print(f"Modalities: {len(modality_counts)}/20")
        
        print("\n📋 MODALITY BREAKDOWN:")
        for modality, count in sorted(modality_counts.items()):
            print(f"  {modality}: {count:,} files")
        
        print(f"\n💾 Marshal report saved: {report_path}")
        return marshal_report
    
    def determine_modality(self, file_path):
        """Determine the modality of a file based on path and extension."""
        path_str = str(file_path).lower()
        extension = file_path.suffix.lower()
        
        # Special path-based detection
        if 'annotation' in path_str or 'label' in path_str:
            if extension in self.modalities['image']:
                return 'annotated_images'
        
        if 'caption' in path_str or 'subtitle' in path_str:
            if extension in self.modalities['video']:
                return 'captioned_videos'
        
        if 'textgrid' in path_str or 'transcript' in path_str:
            return 'audio_transcripts'
        
        # Extension-based detection
        for modality, extensions in self.modalities.items():
            if extension in extensions:
                return modality
        
        return 'unknown'
    
    def launch_full_embedding(self, marshal_report):
        """Launch the full embedding process."""
        print("\n🚀 LAUNCHING FULL EMBEDDING SYSTEM")
        print("=" * 60)
        
        # Create embedding configuration
        embedding_config = {
            'source_data': marshal_report,
            'output_directory': str(self.embeddings_root),
            'batch_size': 100,
            'parallel_workers': 4,
            'timestamp': self.timestamp
        }
        
        config_path = self.embeddings_root / f"embedding_config_{self.timestamp}.json"
        with open(config_path, 'w') as f:
            json.dump(embedding_config, f, indent=2)
        
        print(f"⚙️ Embedding config: {config_path}")
        print(f"📁 Output directory: {self.embeddings_root}")
        print(f"📊 Files to process: {marshal_report['total_files']:,}")
        print(f"💾 Data size: {marshal_report['total_size_gb']:.2f} GB")
        
        # Launch the ultimate universal embedder with optimized settings
        print("\n🎯 Starting Ultimate Universal Embedder...")
        return self.start_optimized_embedder()
    
    def start_optimized_embedder(self):
        """Start the optimized embedding process."""
        embedder_path = "src/dev_tools/embedding/ultimate_universal_embedder.py"
        
        if not os.path.exists(embedder_path):
            print(f"❌ Embedder not found: {embedder_path}")
            return False
        
        print(f"🚀 Executing: python {embedder_path}")
        try:
            # Start embedder as background process
            process = subprocess.Popen([
                'python', embedder_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            print(f"✅ Embedder started with PID: {process.pid}")
            print("📊 Monitor progress with embedding status analyzer")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start embedder: {e}")
            return False

def main():
    """Main execution function."""
    marshal = ImpressionCoreDataMarshal()
    
    # Step 1: Marshal all data
    print("🎯 STEP 1: MARSHALING ALL DATA")
    marshal_report = marshal.marshal_all_data()
    
    # Step 2: Launch full embedding
    print("\n🎯 STEP 2: LAUNCHING FULL EMBEDDING")
    success = marshal.launch_full_embedding(marshal_report)
    
    if success:
        print("\n🎉 SUCCESS! Full embedding system launched")
        print("📊 Monitor progress with:")
        print("   python src/dev_tools/validation/embedding_status_analyzer.py")
    else:
        print("\n❌ Failed to launch embedding system")
    
    print("\n" + "=" * 60)
    print("🎯 ImpressionCore Data Marshal Complete")

if __name__ == "__main__":
    main()
