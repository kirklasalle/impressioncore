#!/usr/bin/env python3
"""
Modality Status Checker for ImpressionCore-B1
=============================================
Analyzes current available modalities and identifies missing ones
"""

import os
from pathlib import Path
from collections import defaultdict

def check_modality_status():
    """Check status of all modalities in the data directory"""
    data_dir = Path("src/data")
    
    # Define target modalities for complete multimodal AI
    target_modalities = {
        # Core modalities (essential)
        'text': ['.txt', '.json', '.md', '.csv'],
        'image': ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'],
        'audio': ['.wav', '.mp3', '.ogg', '.flac', '.m4a'],
        'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
        
        # Structured data
        'tabular': ['.csv', '.tsv', '.xlsx', '.parquet'],
        'json_structured': ['.json', '.jsonl'],
        'xml_structured': ['.xml', '.html'],
        
        # Scientific/Technical
        'time_series': ['.csv', '.h5', '.nc'],  # Time series data
        'geospatial': ['.geojson', '.kml', '.shp'],  # Geographic data
        'medical_imaging': ['.dcm', '.nii', '.mha'],  # Medical scans
        
        # Specialized formats
        'documents': ['.pdf', '.doc', '.docx'],
        'code': ['.py', '.js', '.cpp', '.java', '.go', '.rs'],
        'markup': ['.html', '.xml', '.svg'],
        
        # Sensor/IoT data
        'sensor_data': ['.log', '.dat', '.bin'],
        'network_data': ['.pcap', '.json'],  # Network protocols
        
        # Multimodal combinations
        'annotated_images': ['annotations.json'],  # Image + text
        'captioned_videos': ['captions.json'],    # Video + text
        'audio_transcripts': ['transcripts.json'], # Audio + text
        
        # 3D and spatial
        'point_clouds': ['.ply', '.pcd', '.obj'],
        '3d_models': ['.obj', '.fbx', '.dae', '.gltf']
    }
    
    print("🔍 Modality Status Analysis")
    print("=" * 50)
    
    found_modalities = {}
    file_counts = defaultdict(int)
    
    # Scan all files in data directory
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            file_path = Path(root) / file
            suffix = file_path.suffix.lower()
            
            # Count by extension
            file_counts[suffix] += 1
            
            # Check against modalities
            for modality, extensions in target_modalities.items():
                if suffix in extensions or file.lower() in extensions:
                    if modality not in found_modalities:
                        found_modalities[modality] = []
                    found_modalities[modality].append(str(file_path))
    
    # Report findings
    available_count = len(found_modalities)
    total_count = len(target_modalities)
    
    print(f"🎯 Available modalities: {available_count}/{total_count}")
    print()
    
    print("✅ FOUND MODALITIES:")
    for modality in sorted(found_modalities.keys()):
        count = len(found_modalities[modality])
        print(f"  • {modality}: {count} files")
    
    print()
    print("❌ MISSING MODALITIES:")
    missing = set(target_modalities.keys()) - set(found_modalities.keys())
    for modality in sorted(missing):
        extensions = ', '.join(target_modalities[modality])
        print(f"  • {modality}: {extensions}")
    
    print()
    print("📊 File Extension Summary:")
    for ext, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        if ext:  # Skip empty extensions
            print(f"  {ext}: {count} files")
    
    print()
    print("🚀 PRIORITY DOWNLOADS NEEDED:")
    critical_missing = {
        'time_series': 'Time series data for temporal analysis',
        'geospatial': 'Geographic/mapping data for spatial understanding',
        'medical_imaging': 'Medical scans for healthcare applications',
        'documents': 'PDF documents for document understanding',
        'point_clouds': '3D point cloud data for spatial reasoning',
        '3d_models': '3D model files for object understanding',
        'sensor_data': 'IoT sensor data for real-world applications',
        'network_data': 'Network protocol data for cybersecurity'
    }
    
    for modality in missing:
        if modality in critical_missing:
            print(f"  🔥 {modality}: {critical_missing[modality]}")
    
    return found_modalities, missing, file_counts

if __name__ == "__main__":
    found, missing, counts = check_modality_status()
