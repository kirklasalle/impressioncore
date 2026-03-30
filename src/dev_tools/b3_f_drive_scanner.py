#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #deployment #multimodal #python #source_code #src/dev_tools/b3_f_drive_scanner.py #training
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #deployment #multimodal #python #source_code #src\\dev_tools\\b3_f_drive_scanner.py #training
# Category:** Development Tools
# Status:** Active

"""
B3 F: Drive Comprehensive Scanner
🤖 ImpressionCore B3 Data Pipeline Preparation Tool
"""

import json
import os
from collections import defaultdict
from datetime import datetime


def print_header():
    print("🤖 VIRTUALLY ROBOTIC GITHUB COPILOT - B3 MODE")
    print("=" * 70)
    print("🔍 F: DRIVE COMPREHENSIVE SCANNER FOR B3 DATA PIPELINE")
    print("📅 Scan Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)

def scan_f_drive_comprehensive():
    """Comprehensive F: Drive analysis for B3 data pipeline preparation"""

    results = {
        'scan_timestamp': datetime.now().isoformat(),
        'total_files': 0,
        'total_directories': 0,
        'total_size_gb': 0,
        'available_space_gb': 0,
        'file_types': defaultdict(int),
        'large_files': [],
        'directory_analysis': {},
        'embeddings_files': [],
        'model_files': [],
        'dataset_files': [],
        'b3_readiness_assessment': {}
    }

    f_drive_path = "F:\\"

    if not os.path.exists(f_drive_path):
        print("❌ F: Drive not accessible!")
        return None

    print(f"🔍 Scanning F: Drive: {f_drive_path}")

    try:
        # Get disk usage
        statvfs = os.statvfs(f_drive_path) if hasattr(os, 'statvfs') else None
        if statvfs:
            results['available_space_gb'] = (statvfs.f_bavail * statvfs.f_frsize) / (1024**3)
        else:
            # Windows alternative
            import shutil
            total, used, free = shutil.disk_usage(f_drive_path)
            results['available_space_gb'] = free / (1024**3)

        # Walk through all files and directories
        for root, dirs, files in os.walk(f_drive_path):
            results['total_directories'] += len(dirs)

            # Analyze each file
            for file in files:
                full_path = os.path.join(root, file)
                try:
                    stat = os.stat(full_path)
                    size = stat.st_size

                    results['total_files'] += 1
                    results['total_size_gb'] += size / (1024**3)

                    # File extension analysis
                    ext = os.path.splitext(file)[1].lower()
                    results['file_types'][ext] += 1

                    # Large files tracking (>50MB for B3 analysis)
                    if size > 50 * 1024 * 1024:
                        results['large_files'].append({
                            'name': file,
                            'path': full_path,
                            'size_mb': size / (1024**2),
                            'size_gb': size / (1024**3),
                            'directory': os.path.dirname(full_path)
                        })

                    # B3 Critical File Categories
                    file_lower = file.lower()

                    # Embeddings detection
                    if any(keyword in file_lower for keyword in ['embedding', 'embed', 'vector']):
                        results['embeddings_files'].append({
                            'name': file,
                            'path': full_path,
                            'size_mb': size / (1024**2)
                        })

                    # Model files detection
                    if any(ext in file_lower for ext in ['.pth', '.safetensors', '.bin', '.onnx']) or 'model' in file_lower:
                        results['model_files'].append({
                            'name': file,
                            'path': full_path,
                            'size_mb': size / (1024**2)
                        })

                    # Dataset files detection
                    if any(keyword in file_lower for keyword in ['dataset', 'data']) or any(ext in file_lower for ext in ['.json', '.csv', '.parquet', '.hdf5']):
                        results['dataset_files'].append({
                            'name': file,
                            'path': full_path,
                            'size_mb': size / (1024**2)
                        })

                except (OSError, PermissionError):
                    continue

            # Directory-level analysis
            rel_path = os.path.relpath(root, f_drive_path)
            if rel_path != '.':
                results['directory_analysis'][rel_path] = {
                    'file_count': len(files),
                    'subdirectory_count': len(dirs)
                }

    except Exception as e:
        print(f"❌ Error during F: Drive scan: {e}")
        return None

    # B3 Readiness Assessment
    results['b3_readiness_assessment'] = assess_b3_readiness(results)

    return results

def assess_b3_readiness(scan_results):
    """Assess F: Drive readiness for B3 data pipeline implementation"""

    assessment = {
        'overall_score': 0,
        'storage_capacity': 'unknown',
        'data_organization': 'unknown',
        'embeddings_readiness': 'unknown',
        'model_availability': 'unknown',
        'dataset_completeness': 'unknown',
        'recommendations': []
    }

    # Storage capacity assessment
    if scan_results['available_space_gb'] > 100:
        assessment['storage_capacity'] = 'excellent'
        assessment['overall_score'] += 20
    elif scan_results['available_space_gb'] > 50:
        assessment['storage_capacity'] = 'good'
        assessment['overall_score'] += 15
    else:
        assessment['storage_capacity'] = 'limited'
        assessment['overall_score'] += 5
        assessment['recommendations'].append("Consider freeing up storage space for B3 operations")

    # Data organization assessment
    organized_dirs = ['datasets', 'models', 'embeddings', 'training', 'output']
    found_dirs = [d for d in scan_results['directory_analysis'] if any(org in d.lower() for org in organized_dirs)]

    if len(found_dirs) >= 4:
        assessment['data_organization'] = 'excellent'
        assessment['overall_score'] += 20
    elif len(found_dirs) >= 2:
        assessment['data_organization'] = 'good'
        assessment['overall_score'] += 15
    else:
        assessment['data_organization'] = 'needs_improvement'
        assessment['overall_score'] += 5
        assessment['recommendations'].append("Improve directory organization for B3 data pipeline")

    # Embeddings readiness
    if len(scan_results['embeddings_files']) > 100:
        assessment['embeddings_readiness'] = 'excellent'
        assessment['overall_score'] += 20
    elif len(scan_results['embeddings_files']) > 10:
        assessment['embeddings_readiness'] = 'good'
        assessment['overall_score'] += 15
    else:
        assessment['embeddings_readiness'] = 'insufficient'
        assessment['overall_score'] += 5
        assessment['recommendations'].append("Generate additional embeddings for B3 multimodal pipeline")

    # Model availability
    if len(scan_results['model_files']) > 10:
        assessment['model_availability'] = 'excellent'
        assessment['overall_score'] += 20
    elif len(scan_results['model_files']) > 3:
        assessment['model_availability'] = 'good'
        assessment['overall_score'] += 15
    else:
        assessment['model_availability'] = 'limited'
        assessment['overall_score'] += 5
        assessment['recommendations'].append("Prepare additional models for B3 deployment")

    # Dataset completeness
    if len(scan_results['dataset_files']) > 50:
        assessment['dataset_completeness'] = 'excellent'
        assessment['overall_score'] += 20
    elif len(scan_results['dataset_files']) > 10:
        assessment['dataset_completeness'] = 'good'
        assessment['overall_score'] += 15
    else:
        assessment['dataset_completeness'] = 'needs_expansion'
        assessment['overall_score'] += 5
        assessment['recommendations'].append("Expand dataset collection for comprehensive B3 training")

    return assessment

def print_scan_results(results):
    """Print comprehensive scan results in robotic format"""

    if not results:
        print("❌ Scan failed - unable to generate results")
        return

    print("\n📊 F: DRIVE SCAN RESULTS - B3 ANALYSIS")
    print("=" * 70)

    # Basic statistics
    print(f"📁 Total Files: {results['total_files']:,}")
    print(f"📂 Total Directories: {results['total_directories']:,}")
    print(f"💾 Total Data Size: {results['total_size_gb']:.2f} GB")
    print(f"💿 Available Space: {results['available_space_gb']:.2f} GB")
    print()

    # B3 Critical Assets
    print("🎯 B3 CRITICAL ASSETS INVENTORY")
    print("-" * 40)
    print(f"🔗 Embeddings Files: {len(results['embeddings_files']):,}")
    print(f"🧠 Model Files: {len(results['model_files']):,}")
    print(f"📈 Dataset Files: {len(results['dataset_files']):,}")
    print()

    # Top file types
    print("📋 TOP FILE TYPES")
    print("-" * 40)
    sorted_types = sorted(results['file_types'].items(), key=lambda x: x[1], reverse=True)[:15]
    for ext, count in sorted_types:
        ext_display = ext if ext else '[no extension]'
        print(f"  {ext_display:15} {count:>8,} files")
    print()

    # Large files analysis
    print("💾 LARGE FILES (>50MB) - TOP 20")
    print("-" * 40)
    large_sorted = sorted(results['large_files'], key=lambda x: x['size_mb'], reverse=True)[:20]
    for file_info in large_sorted:
        print(f"  {file_info['name'][:50]:50} {file_info['size_mb']:>8.1f} MB")
    print()

    # Directory structure
    print("📁 MAJOR DIRECTORIES")
    print("-" * 40)
    sorted_dirs = sorted(results['directory_analysis'].items(),
                        key=lambda x: x[1]['file_count'], reverse=True)[:20]
    for dir_path, info in sorted_dirs:
        print(f"  {dir_path[:50]:50} {info['file_count']:>6} files")
    print()

    # B3 Readiness Assessment
    assessment = results['b3_readiness_assessment']
    print("🚀 B3 READINESS ASSESSMENT")
    print("=" * 70)
    print(f"📊 Overall Score: {assessment['overall_score']}/100")
    print(f"💾 Storage Capacity: {assessment['storage_capacity'].upper()}")
    print(f"📁 Data Organization: {assessment['data_organization'].upper()}")
    print(f"🔗 Embeddings Readiness: {assessment['embeddings_readiness'].upper()}")
    print(f"🧠 Model Availability: {assessment['model_availability'].upper()}")
    print(f"📈 Dataset Completeness: {assessment['dataset_completeness'].upper()}")

    if assessment['recommendations']:
        print("\n💡 B3 OPTIMIZATION RECOMMENDATIONS:")
        for i, rec in enumerate(assessment['recommendations'], 1):
            print(f"  {i}. {rec}")

    print("\n🤖 B3 IMPLEMENTATION STATUS:")
    if assessment['overall_score'] >= 80:
        print("✅ READY FOR B3 DEPLOYMENT - Excellent infrastructure detected")
    elif assessment['overall_score'] >= 60:
        print("⚠️  GOOD FOR B3 WITH OPTIMIZATIONS - Minor improvements recommended")
    else:
        print("🔧 REQUIRES B3 PREPARATION - Significant setup needed before deployment")

def main():
    """Main execution function"""
    print_header()

    print("🔍 Initiating comprehensive F: Drive scan...")
    scan_results = scan_f_drive_comprehensive()

    if scan_results:
        print_scan_results(scan_results)

        # Save results for B3 pipeline reference
        output_file = f"b3_f_drive_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(scan_results, f, indent=2, default=str)

        print(f"\n💾 Scan results saved to: {output_file}")
        print("🚀 F: Drive analysis complete - B3 pipeline ready for evaluation")
    else:
        print("❌ F: Drive scan failed - check drive accessibility")

if __name__ == "__main__":
    main()
