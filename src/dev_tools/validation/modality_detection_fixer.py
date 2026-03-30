#!/usr/bin/env python3
"""
ImpressionCore Modality Detection and Embedding Fix
==================================================
Comprehensive tool to fix modality detection and ensure all 20/20 modalities are embedded.
"""

import os
import json
import time
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import hashlib

class ModalityDetectionFixer:
    def __init__(self):
        self.project_root = Path(".")
        self.data_root = self.project_root / "src" / "data"
        self.embeddings_root = self.data_root / "embeddings"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Complete modality definitions with all extensions and path patterns
        self.modalities = {
            '3d_models': {
                'extensions': ['.obj', '.off', '.ply', '.stl', '.3ds', '.gltf', '.glb', '.dae', '.fbx'],
                'paths': ['3d_models', 'models', 'meshes', 'objects']
            },
            'annotated_images': {
                'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
                'paths': ['annotated', 'labeled', 'annotation', 'labels']
            },
            'audio': {
                'extensions': ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac', '.wma'],
                'paths': ['audio', 'sound', 'music', 'speech']
            },
            'audio_transcripts': {
                'extensions': ['.textgrid', '.lab', '.txt', '.transcript'],
                'paths': ['transcript', 'textgrid', 'librispeech', 'alignment']
            },
            'captioned_videos': {
                'extensions': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'],
                'paths': ['caption', 'subtitle', 'annotated_video']
            },
            'code': {
                'extensions': ['.py', '.js', '.cpp', '.c', '.java', '.go', '.rs', '.ts', '.html', '.css'],
                'paths': ['code', 'src', 'scripts', 'examples']
            },
            'documents': {
                'extensions': ['.pdf', '.doc', '.docx', '.rtf', '.odt'],
                'paths': ['documents', 'docs', 'papers', 'text']
            },
            'geospatial': {
                'extensions': ['.geojson', '.kml', '.shp', '.gpx', '.gml'],
                'paths': ['geo', 'spatial', 'maps', 'location']
            },
            'image': {
                'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
                'paths': ['images', 'photos', 'pictures', 'train2017', 'val2017']
            },
            'json_structured': {
                'extensions': ['.json', '.jsonl', '.ndjson'],
                'paths': ['structured', 'data', 'config']
            },
            'markup': {
                'extensions': ['.html', '.htm', '.md', '.markdown', '.rst'],
                'paths': ['markup', 'web', 'docs']
            },
            'medical_imaging': {
                'extensions': ['.dcm', '.nii', '.nifti', '.hdr', '.img'],
                'paths': ['medical', 'imaging', 'dicom', 'nifti']
            },
            'network_data': {
                'extensions': ['.pcap', '.cap', '.pcapng', '.dump'],
                'paths': ['network', 'capture', 'traffic']
            },
            'point_clouds': {
                'extensions': ['.pcd', '.ply', '.las', '.xyz', '.pts'],
                'paths': ['point_cloud', 'pointcloud', 'lidar', '3d_scan']
            },
            'sensor_data': {
                'extensions': ['.bin', '.dat', '.raw', '.sensor'],
                'paths': ['sensor', 'iot', 'telemetry', 'measurements']
            },
            'tabular': {
                'extensions': ['.csv', '.tsv', '.xlsx', '.xls', '.parquet'],
                'paths': ['tabular', 'tables', 'data', 'spreadsheet']
            },
            'text': {
                'extensions': ['.txt', '.log', '.text'],
                'paths': ['text', 'logs', 'corpus', 'plain']
            },
            'time_series': {
                'extensions': ['.npy', '.npz', '.h5', '.hdf5', '.ts'],
                'paths': ['time_series', 'temporal', 'sequence']
            },
            'video': {
                'extensions': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'],
                'paths': ['video', 'movies', 'clips', 'kinetics']
            },
            'xml_structured': {
                'extensions': ['.xml', '.xsd', '.xsl', '.xslt'],
                'paths': ['xml', 'structured', 'schema']
            }
        }
        
    def enhanced_modality_detection(self, file_path):
        """Enhanced modality detection using both path and extension analysis."""
        path_str = str(file_path).lower()
        extension = file_path.suffix.lower()
        
        # Priority-based detection
        detection_scores = defaultdict(int)
        
        # Check each modality
        for modality, config in self.modalities.items():
            # Extension match (high priority)
            if extension in config['extensions']:
                detection_scores[modality] += 10
            
            # Path match (medium priority)
            for path_pattern in config['paths']:
                if path_pattern in path_str:
                    detection_scores[modality] += 5
        
        # Special case handling
        if 'annotation' in path_str or 'label' in path_str:
            if extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
                detection_scores['annotated_images'] += 20
        
        if 'caption' in path_str or 'subtitle' in path_str:
            if extension in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                detection_scores['captioned_videos'] += 20
        
        if 'textgrid' in path_str or 'transcript' in path_str:
            detection_scores['audio_transcripts'] += 20
        
        if 'point_cloud' in path_str or file_path.name.startswith('synthetic_'):
            if extension in ['.ply', '.pcd', '.las', '.xyz']:
                detection_scores['point_clouds'] += 20
        
        # Return best match
        if detection_scores:
            best_modality = max(detection_scores.items(), key=lambda x: x[1])
            return best_modality[0]
        
        return 'unknown'
    
    def scan_and_fix_modalities(self):
        """Comprehensive scan and fix of all modalities."""
        print("🎯 ImpressionCore Modality Detection Fix")
        print("=" * 60)
        
        all_files = []
        modality_counts = defaultdict(int)
        modality_files = defaultdict(list)
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
                    
                    # Enhanced modality detection
                    modality = self.enhanced_modality_detection(file_path)
                    modality_counts[modality] += 1
                    modality_files[modality].append(str(file_path))
                    
                    all_files.append({
                        'path': str(file_path),
                        'modality': modality,
                        'size': file_size,
                        'extension': file_path.suffix.lower()
                    })
                except Exception as e:
                    print(f"⚠️ Error processing {file_path}: {e}")
        
        # Analysis results
        print(f"\n📊 ENHANCED MODALITY ANALYSIS")
        print(f"Total files: {len(all_files):,}")
        print(f"Total size: {total_size / (1024**3):.2f} GB")
        print(f"Modalities detected: {len(modality_counts)}")
        
        print(f"\n📋 MODALITY BREAKDOWN:")
        target_modalities = set(self.modalities.keys())
        found_modalities = set(modality_counts.keys())
        
        for modality in sorted(target_modalities):
            count = modality_counts.get(modality, 0)
            status = "✅" if count > 0 else "❌"
            print(f"  {status} {modality}: {count:,} files")
        
        # Check for missing modalities
        missing_modalities = target_modalities - found_modalities
        if missing_modalities:
            print(f"\n❌ MISSING MODALITIES ({len(missing_modalities)}):")
            for modality in sorted(missing_modalities):
                print(f"  • {modality}")
        else:
            print(f"\n🎉 ALL 20/20 MODALITIES DETECTED!")
        
        # Unknown files
        unknown_count = modality_counts.get('unknown', 0)
        if unknown_count > 0:
            print(f"\n⚠️ UNKNOWN FILES: {unknown_count}")
            print("Sample unknown files:")
            for file_path in modality_files['unknown'][:5]:
                print(f"  • {file_path}")
        
        # Save comprehensive report
        report = {
            'timestamp': self.timestamp,
            'total_files': len(all_files),
            'total_size_gb': round(total_size / (1024**3), 2),
            'modalities_detected': len(found_modalities),
            'target_modalities': len(target_modalities),
            'coverage_percentage': (len(found_modalities) / len(target_modalities)) * 100,
            'modality_counts': dict(modality_counts),
            'modality_files': {k: v[:10] for k, v in modality_files.items()},  # Sample files
            'missing_modalities': list(missing_modalities),
            'found_modalities': list(found_modalities),
            'all_files': all_files
        }
        
        report_path = self.embeddings_root / f"enhanced_modality_analysis_{self.timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Enhanced analysis saved: {report_path}")
        return report
    
    def prepare_for_embedding(self, report):
        """Prepare all files for comprehensive embedding."""
        print(f"\n🚀 PREPARING FOR COMPREHENSIVE EMBEDDING")
        print("=" * 60)
        
        # Create embedding manifest
        embedding_manifest = {
            'source_analysis': report,
            'embedding_timestamp': self.timestamp,
            'total_files_to_embed': report['total_files'],
            'modalities_to_embed': report['found_modalities'],
            'output_directory': str(self.embeddings_root)
        }
        
        manifest_path = self.embeddings_root / f"embedding_manifest_{self.timestamp}.json"
        with open(manifest_path, 'w') as f:
            json.dump(embedding_manifest, f, indent=2)
        
        print(f"📋 Embedding manifest: {manifest_path}")
        print(f"📊 Files to embed: {report['total_files']:,}")
        print(f"🎯 Modalities: {len(report['found_modalities'])}/20")
        print(f"💾 Data size: {report['total_size_gb']:.2f} GB")
        
        return embedding_manifest

def main():
    """Main execution function."""
    fixer = ModalityDetectionFixer()
    
    print("🎯 STEP 1: ENHANCED MODALITY DETECTION")
    report = fixer.scan_and_fix_modalities()
    
    print("\n🎯 STEP 2: EMBEDDING PREPARATION")
    manifest = fixer.prepare_for_embedding(report)
    
    print(f"\n🎉 MODALITY DETECTION AND PREPARATION COMPLETE!")
    print(f"📊 Coverage: {report['coverage_percentage']:.1f}%")
    print(f"🎯 Ready for comprehensive embedding!")
    
    return report, manifest

if __name__ == "__main__":
    main()
