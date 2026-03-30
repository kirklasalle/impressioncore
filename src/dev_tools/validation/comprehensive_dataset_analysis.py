#!/usr/bin/env python3
"""
Comprehensive Dataset Analysis for ImpressionCore
Analyzes current data types and identifies missing modalities for complete multimodal AI
"""

import os
import json
from pathlib import Path
from collections import defaultdict
import time

def analyze_datasets():
    """Analyze current datasets and identify missing data types"""
    
    print("🔍 ImpressionCore Comprehensive Dataset Analysis")
    print("=" * 50)
    
    data_dir = Path("src/data")
    
    # Current data types inventory
    data_types = {
        "text": {"extensions": [".txt", ".json", ".md", ".csv", ".tsv"], "count": 0, "files": []},
        "image": {"extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"], "count": 0, "files": []},
        "audio": {"extensions": [".wav", ".mp3", ".ogg", ".flac", ".aac", ".m4a"], "count": 0, "files": []},
        "video": {"extensions": [".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv"], "count": 0, "files": []},
        "structured": {"extensions": [".json", ".csv", ".tsv", ".parquet", ".xlsx"], "count": 0, "files": []},
        "code": {"extensions": [".py", ".js", ".cpp", ".java", ".go", ".rs"], "count": 0, "files": []},
        "scientific": {"extensions": [".pdf", ".tex", ".bib"], "count": 0, "files": []},
        "3d": {"extensions": [".obj", ".stl", ".ply", ".gltf", ".fbx"], "count": 0, "files": []},
        "sensor": {"extensions": [".sensor", ".imu", ".gps", ".lidar"], "count": 0, "files": []},
        "time_series": {"extensions": [".timeseries", ".ts", ".stock"], "count": 0, "files": []},
        "medical": {"extensions": [".dicom", ".nii", ".mha"], "count": 0, "files": []},
        "geographic": {"extensions": [".shp", ".geojson", ".kml"], "count": 0, "files": []},
        "biometric": {"extensions": [".bio", ".fingerprint", ".iris"], "count": 0, "files": []},
        "speech": {"extensions": [".phoneme", ".transcript", ".alignment"], "count": 0, "files": []},
        "gesture": {"extensions": [".gesture", ".skeleton", ".pose"], "count": 0, "files": []},
        "haptic": {"extensions": [".haptic", ".force", ".tactile"], "count": 0, "files": []},
        "smell": {"extensions": [".olfactory", ".scent"], "count": 0, "files": []},
        "taste": {"extensions": [".gustatory", ".flavor"], "count": 0, "files": []},
        "emotion": {"extensions": [".emotion", ".sentiment", ".affect"], "count": 0, "files": []},
        "multimodal": {"extensions": [".multimodal", ".fusion"], "count": 0, "files": []},
    }
    
    # Scan directories
    print("\n📁 Scanning directories...")
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            file_path = Path(root) / file
            file_ext = file_path.suffix.lower()
            
            # Categorize file
            for category, info in data_types.items():
                if file_ext in info["extensions"]:
                    info["count"] += 1
                    info["files"].append(str(file_path))
                    break
    
    # Print current inventory
    print("\n📊 Current Dataset Inventory:")
    print("-" * 40)
    
    total_files = 0
    available_modalities = []
    
    for category, info in data_types.items():
        if info["count"] > 0:
            print(f"✅ {category.upper()}: {info['count']} files")
            available_modalities.append(category)
            total_files += info["count"]
        else:
            print(f"❌ {category.upper()}: 0 files")
    
    print(f"\n📈 Total files: {total_files}")
    print(f"🎯 Available modalities: {len(available_modalities)}/20")
    
    # Identify missing critical modalities for complete multimodal AI
    critical_missing = []
    missing_modalities = []
    
    for category, info in data_types.items():
        if info["count"] == 0:
            missing_modalities.append(category)
            if category in ["video", "3d", "sensor", "time_series", "medical", "speech", "gesture"]:
                critical_missing.append(category)
    
    print(f"\n⚠️  Missing modalities: {len(missing_modalities)}")
    print(f"🚨 Critical missing: {len(critical_missing)}")
    
    # ImpressionCore-specific analysis
    print("\n🧠 ImpressionCore-Specific Analysis:")
    print("-" * 40)
    
    # Check multimodal training readiness
    required_for_brain_sim = ["text", "image", "audio", "video", "structured", "time_series", "emotion"]
    brain_sim_ready = all(data_types[mod]["count"] > 0 for mod in required_for_brain_sim)
    
    print(f"🧠 Brain simulation ready: {'✅ Yes' if brain_sim_ready else '❌ No'}")
    
    # Check memory/cognitive modeling readiness
    memory_modalities = ["text", "image", "audio", "emotion", "multimodal"]
    memory_ready = all(data_types[mod]["count"] > 0 for mod in memory_modalities)
    
    print(f"🧐 Memory modeling ready: {'✅ Yes' if memory_ready else '❌ No'}")
    
    # Check lifelong learning readiness
    lifelong_modalities = ["text", "image", "audio", "video", "structured", "time_series"]
    lifelong_ready = all(data_types[mod]["count"] > 0 for mod in lifelong_modalities)
    
    print(f"📚 Lifelong learning ready: {'✅ Yes' if lifelong_ready else '❌ No'}")
    
    # Priority recommendations
    print("\n🎯 Priority Recommendations:")
    print("-" * 40)
    
    recommendations = []
    
    if data_types["video"]["count"] == 0:
        recommendations.append("🎬 VIDEO: Essential for temporal understanding and multimodal learning")
    
    if data_types["time_series"]["count"] == 0:
        recommendations.append("📈 TIME SERIES: Critical for memory formation and temporal patterns")
    
    if data_types["emotion"]["count"] == 0:
        recommendations.append("😊 EMOTION: Needed for human-centric AI and wellness focus")
    
    if data_types["speech"]["count"] == 0:
        recommendations.append("🗣️ SPEECH: Advanced audio processing beyond basic audio files")
    
    if data_types["gesture"]["count"] == 0:
        recommendations.append("👋 GESTURE: Body language and non-verbal communication")
    
    if data_types["3d"]["count"] == 0:
        recommendations.append("🎲 3D: Spatial understanding and 3D perception")
    
    if data_types["sensor"]["count"] == 0:
        recommendations.append("📡 SENSOR: IoT and environmental data integration")
    
    if data_types["medical"]["count"] == 0:
        recommendations.append("🏥 MEDICAL: Health and wellness monitoring (core directive)")
    
    for i, rec in enumerate(recommendations[:5], 1):  # Top 5 priorities
        print(f"{i}. {rec}")
    
    # Generate download recommendations
    print("\n📥 Recommended Downloads:")
    print("-" * 40)
    
    download_sources = {
        "video": [
            "Kinetics-400: https://deepmind.com/research/open-source/kinetics",
            "UCF-101: https://www.crcv.ucf.edu/data/UCF101.php",
            "YouTube-8M: https://research.google.com/youtube8m/"
        ],
        "time_series": [
            "Yahoo Finance API: Real-time stock data",
            "Weather APIs: Historical weather data",
            "IoT sensor data: Public datasets"
        ],
        "emotion": [
            "FER2013: Facial emotion recognition dataset",
            "IEMOCAP: Emotional speech dataset",
            "DEAP: Physiological emotion dataset"
        ],
        "speech": [
            "TIMIT: Phoneme recognition dataset",
            "VCTK: Voice cloning dataset",
            "LibriSpeech: Speech recognition dataset"
        ],
        "gesture": [
            "NTU RGB+D: Skeletal action recognition",
            "ChaLearn: Gesture recognition challenges",
            "JHMDB: Joint human motion database"
        ],
        "3d": [
            "ShapeNet: 3D model dataset",
            "ModelNet: 3D CAD model dataset",
            "Replica: 3D indoor scene dataset"
        ],
        "sensor": [
            "UCI ML Repository: Sensor datasets",
            "PhysioNet: Physiological signal datasets",
            "OpenML: Machine learning datasets"
        ],
        "medical": [
            "NIH Medical Imaging: Public medical images",
            "MIMIC: Medical information dataset",
            "PhysioNet: Physiological datasets"
        ]
    }
    
    for modality in critical_missing[:3]:  # Top 3 critical missing
        if modality in download_sources:
            print(f"\n🎯 {modality.upper()}:")
            for source in download_sources[modality]:
                print(f"   • {source}")
    
    # Export analysis
    analysis_result = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_files": total_files,
        "available_modalities": available_modalities,
        "missing_modalities": missing_modalities,
        "critical_missing": critical_missing,
        "brain_sim_ready": brain_sim_ready,
        "memory_ready": memory_ready,
        "lifelong_ready": lifelong_ready,
        "recommendations": recommendations,
        "data_types": {k: {"count": v["count"], "sample_files": v["files"][:5]} for k, v in data_types.items()}
    }
    
    output_file = "comprehensive_dataset_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Analysis saved to: {output_file}")
    print(f"📋 Summary: {len(available_modalities)}/20 modalities available")
    
    return analysis_result

if __name__ == "__main__":
    analyze_datasets()
