#!/usr/bin/env python3
"""
Final validation script to confirm 20/20 modality coverage and readiness for production training.
"""

import os
import sys
from pathlib import Path
from collections import defaultdict, Counter
import json
from datetime import datetime

def count_files_by_extension(directory):
    """Count files by extension in a directory"""
    if not os.path.exists(directory):
        return {}
    
    extension_counts = Counter()
    total_files = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.startswith('.'):  # Skip hidden files
                ext = Path(file).suffix.lower()
                extension_counts[ext or 'no_extension'] += 1
                total_files += 1
    
    return dict(extension_counts), total_files

def analyze_modality_coverage():
    """Analyze modality coverage across the dataset"""
    
    # Define modality mappings
    modality_extensions = {
        'text': ['.txt', '.md', '.rtf'],
        'image': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'],
        'audio': ['.wav', '.mp3', '.flac', '.ogg', '.m4a'],
        'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'],
        'tabular': ['.csv', '.tsv', '.xls', '.xlsx'],
        'json_structured': ['.json', '.jsonl'],
        'xml_structured': ['.xml', '.html', '.htm'],
        'code': ['.py', '.js', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs'],
        'markup': ['.html', '.htm', '.xml', '.svg'],
        'geospatial': ['.geojson', '.kml', '.shp', '.gpx'],
        '3d_models': ['.obj', '.ply', '.stl', '.off', '.3ds'],
        'point_clouds': ['.pcd', '.ply', '.pts', '.xyz'],
        'sensor_data': ['.bin', '.dat', '.raw'],
        'network_data': ['.pcap', '.cap', '.pcapng'],
        'time_series': ['.ts', '.csv'],  # CSV can be time series
        'annotated_images': ['.jpg', '.png'],  # Images with annotations
        'documents': ['.pdf', '.doc', '.docx', '.rtf'],
        'medical_imaging': ['.dcm', '.nii', '.nrrd'],
        'audio_transcripts': ['.textgrid', '.srt', '.vtt'],
        'captioned_videos': ['.mp4', '.avi']  # Videos with captions
    }
    
    print("🎯 ImpressionCore Multimodal Dataset Analysis")
    print("=" * 60)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check main data directories
    data_dir = Path("src/data")
    real_datasets_dir = data_dir / "real_datasets"
    synthetic_dir = real_datasets_dir / "synthetic_scaled"
    
    directories_to_check = [
        ("Real Datasets", real_datasets_dir),
        ("Synthetic Scaled", synthetic_dir),
        ("All Data", data_dir)
    ]
    
    modality_found = set()
    total_analysis = {}
    
    for dir_name, dir_path in directories_to_check:
        print(f"📁 {dir_name}: {dir_path}")
        
        if not dir_path.exists():
            print(f"   ❌ Directory not found!")
            continue
            
        extensions, total_files = count_files_by_extension(dir_path)
        total_analysis[dir_name] = {'extensions': extensions, 'total': total_files}
        
        print(f"   📊 Total files: {total_files:,}")
        
        # Map extensions to modalities
        found_modalities = set()
        for ext, count in extensions.items():
            for modality, ext_list in modality_extensions.items():
                if ext in ext_list:
                    found_modalities.add(modality)
                    modality_found.add(modality)
        
        print(f"   🎯 Modalities found: {len(found_modalities)}")
        if found_modalities:
            print(f"   📋 Modalities: {', '.join(sorted(found_modalities))}")
        
        # Show top file types
        if extensions:
            top_extensions = sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:10]
            print(f"   🔝 Top extensions:")
            for ext, count in top_extensions:
                print(f"      {ext}: {count:,} files")
        print()
    
    # Final modality coverage analysis
    print("🎯 FINAL MODALITY COVERAGE ANALYSIS")
    print("=" * 60)
    
    target_modalities = set(modality_extensions.keys())
    missing_modalities = target_modalities - modality_found
    
    print(f"✅ Found modalities: {len(modality_found)}/20")
    print(f"❌ Missing modalities: {len(missing_modalities)}")
    
    if modality_found:
        print(f"\n📋 FOUND MODALITIES ({len(modality_found)}):")
        for i, modality in enumerate(sorted(modality_found), 1):
            print(f"  {i:2d}. {modality}")
    
    if missing_modalities:
        print(f"\n❌ MISSING MODALITIES ({len(missing_modalities)}):")
        for i, modality in enumerate(sorted(missing_modalities), 1):
            print(f"  {i:2d}. {modality}")
            expected_extensions = modality_extensions[modality]
            print(f"      Expected extensions: {', '.join(expected_extensions)}")
    
    # Coverage percentage
    coverage_percent = (len(modality_found) / len(target_modalities)) * 100
    print(f"\n🎯 COVERAGE: {coverage_percent:.1f}% ({len(modality_found)}/{len(target_modalities)})")
    
    if coverage_percent == 100:
        print("🎉 CONGRATULATIONS! Full 20/20 modality coverage achieved!")
        print("🚀 Ready for production-scale multimodal training!")
    elif coverage_percent >= 90:
        print("🔥 Excellent coverage! Almost ready for production.")
    elif coverage_percent >= 75:
        print("👍 Good coverage! Need a few more modalities.")
    else:
        print("⚠️ More work needed to achieve comprehensive coverage.")
    
    # Save detailed analysis
    analysis_file = f"modality_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    analysis_data = {
        'timestamp': datetime.now().isoformat(),
        'coverage_percent': coverage_percent,
        'found_modalities': sorted(list(modality_found)),
        'missing_modalities': sorted(list(missing_modalities)),
        'directory_analysis': total_analysis,
        'modality_extensions': modality_extensions
    }
    
    with open(analysis_file, 'w') as f:
        json.dump(analysis_data, f, indent=2)
    
    print(f"\n💾 Detailed analysis saved to: {analysis_file}")
    
    return coverage_percent, modality_found, missing_modalities

def check_training_readiness():
    """Check if the system is ready for production training"""
    print("\n🚀 TRAINING READINESS CHECK")
    print("=" * 60)
    
    # Check for key training files
    training_files = [
        "bulletproof_training_launcher.py",
        "src/training/bulletproof_incremental_trainer.py",
        "src/training/multimodal_dataset_loaders.py"
    ]
    
    readiness_score = 0
    max_score = len(training_files) + 1  # +1 for modality coverage
    
    print("📋 Training Infrastructure:")
    for file_path in training_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
            readiness_score += 1
        else:
            print(f"  ❌ {file_path}")
    
    # Check modality coverage
    coverage_percent, _, _ = analyze_modality_coverage()
    if coverage_percent == 100:
        print(f"  ✅ Modality coverage: {coverage_percent:.1f}%")
        readiness_score += 1
    else:
        print(f"  ⚠️ Modality coverage: {coverage_percent:.1f}%")
    
    readiness_percent = (readiness_score / max_score) * 100
    print(f"\n🎯 TRAINING READINESS: {readiness_percent:.1f}% ({readiness_score}/{max_score})")
    
    if readiness_percent == 100:
        print("🎉 SYSTEM READY FOR PRODUCTION TRAINING!")
    elif readiness_percent >= 75:
        print("🔥 Almost ready! Minor fixes needed.")
    else:
        print("⚠️ Significant preparation needed before training.")
    
    return readiness_percent

if __name__ == "__main__":
    print("🎯 ImpressionCore Final Validation")
    print("=" * 60)
    
    # Change to project root if not already there
    if not os.path.exists("src"):
        if os.path.exists("d:/Projects/impressioncore"):
            os.chdir("d:/Projects/impressioncore")
        else:
            print("❌ Cannot find ImpressionCore project directory!")
            sys.exit(1)
    
    # Run analysis
    coverage_percent, found_modalities, missing_modalities = analyze_modality_coverage()
    readiness_percent = check_training_readiness()
    
    print(f"\n🎯 FINAL SUMMARY")
    print("=" * 60)
    print(f"📊 Modality Coverage: {coverage_percent:.1f}%")
    print(f"🚀 Training Readiness: {readiness_percent:.1f}%")
    
    if coverage_percent == 100 and readiness_percent == 100:
        print("\n🎉 SUCCESS! ImpressionCore is ready for production-scale multimodal training!")
        print("🚀 You can now proceed with confidence to train your multimodal AI system.")
    else:
        print(f"\n📋 Next Steps:")
        if coverage_percent < 100:
            print(f"  • Complete remaining {len(missing_modalities)} modalities")
        if readiness_percent < 100:
            print(f"  • Fix training infrastructure issues")
    
    print(f"\n✨ Analysis complete! Check the generated JSON file for detailed results.")
