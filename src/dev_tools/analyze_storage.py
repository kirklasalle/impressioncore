#!/usr/bin/env python3
"""
Storage Analysis Script for ImpressionCore Training
Analyzes current storage and provides recommendations for the 500GB backup drive.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.utils.storage_manager import StorageManager
import json
from datetime import datetime

def main():
    print("🗄️  ImpressionCore Storage Analysis")
    print("=" * 60)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize storage manager with E: as backup drive
    storage = StorageManager(backup_drive="E:")
    
    print("📊 Current Drive Status:")
    print("-" * 30)
    drives = storage.get_drive_usage()
    for drive, info in drives.items():
        status = "🟢" if info['percent_used'] < 80 else "🟡" if info['percent_used'] < 90 else "🔴"
        print(f"{status} Drive {drive}: {info['free_gb']:.1f}GB free / {info['total_gb']:.1f}GB total ({info['percent_used']:.1f}% used)")
    
    print("\n🧠 Multi-Drive Analysis:")
    print("-" * 30)
    analysis = storage.analyze_multi_drive_setup()
    
    print(f"Primary Drive (D:): Available for training")
    print(f"Backup Drive (E:): 500GB capacity - {analysis['drives'].get('E', {}).get('free_gb', 'N/A')}GB free")
    print(f"Recommended Strategy: {analysis['storage_strategy']}")
    
    print("\n💡 Recommendations:")
    for rec in analysis['recommendations']:
        print(f"  {rec}")
    
    print("\n🎯 Training Feasibility Analysis:")
    print("-" * 40)
    for scenario, details in analysis['training_feasibility'].items():
        print(f"\n{scenario.replace('_', ' ').title()}:")
        print(f"  Required: {details['required_gb']}GB")
        print(f"  Primary Drive: {'✅' if details['primary_only'] else '❌'}")
        print(f"  Backup Drive: {'✅' if details['backup_only'] else '❌'}")
        print(f"  Multi-Drive: {'✅' if details['multi_drive'] else '❌'}")
        print(f"  Recommended: {details['recommended_drive']}")
    
    print("\n📋 Storage Strategy Recommendation:")
    print("-" * 40)
    strategy = storage.recommend_storage_strategy("knowledge_distillation")
    print(f"Training Type: {strategy['training_type']}")
    print(f"Required Space: {strategy['required_space_gb']}GB")
    print(f"Performance: {strategy['recommended_setup'].get('performance', 'N/A')}")
    
    print("\n📁 Recommended Data Placement:")
    for data_type, location in strategy['data_placement'].items():
        print(f"  {data_type}: {location}")
    
    if strategy['performance_notes']:
        print("\n⚠️  Performance Notes:")
        for note in strategy['performance_notes']:
            print(f"  {note}")
    
    # Setup backup drive structure if recommended
    if analysis['storage_strategy'] == 'multi_drive':
        print("\n🔧 Setting up backup drive structure...")
        directories = storage.setup_backup_drive_structure()
        print("✅ Backup drive structure created:")
        for name, path in directories.items():
            print(f"  {name}: {path}")
    
    # Save analysis report
    report_path = "src/memlog/storage_analysis_" + datetime.now().strftime('%Y%m%d_%H%M%S') + ".json"
    report_data = {
        "analysis": analysis,
        "strategy": strategy,
        "timestamp": datetime.now().isoformat()
    }
    
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)
    
    print(f"\n📄 Full analysis saved to: {report_path}")
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY FOR TRAINING SETUP:")
    print("=" * 60)
    
    # Key recommendations
    drives_info = analysis['drives']
    d_free = drives_info.get('D', {}).get('free_gb', 0)
    e_free = drives_info.get('E', {}).get('free_gb', 0)
    
    if d_free >= 108:  # Knowledge distillation requirement
        print("✅ PRIMARY RECOMMENDATION: Use D: drive for training")
        print(f"   - {d_free:.1f}GB available on D: drive")
        print("   - Optimal performance (same drive as code)")
    elif e_free >= 108:
        print("✅ PRIMARY RECOMMENDATION: Use E: drive (500GB) for training")
        print(f"   - {e_free:.1f}GB available on E: drive")
        print("   - Excellent capacity for large training runs")
    else:
        print("⚠️  WARNING: May need to manage data across both drives")
        print(f"   - Total available: {d_free + e_free:.1f}GB")
    
    print(f"\n📊 Training Space Requirements:")
    print(f"   - Knowledge Distillation: 108GB")
    print(f"   - Large Model Training: 135GB")
    print(f"   - Multimodal Dataset: 300GB")
    print(f"   - Your 500GB backup drive can handle all scenarios! 🎉")

if __name__ == "__main__":
    main()
