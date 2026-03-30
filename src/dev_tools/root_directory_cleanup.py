#!/usr/bin/env python3
"""
Root Directory Cleanup Script
Systematically organizes ImpressionCore root directory files according to project structure.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

def create_cleanup_report():
    """Create a detailed report of cleanup actions"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"root_cleanup_report_{timestamp}.json"

def ensure_directory_exists(path):
    """Ensure directory exists, create if it doesn't"""
    Path(path).mkdir(parents=True, exist_ok=True)
    return True

def move_file_safely(source, destination):
    """Move file safely with error handling"""
    try:
        if os.path.exists(source):
            ensure_directory_exists(os.path.dirname(destination))
            shutil.move(source, destination)
            return {"status": "success", "from": source, "to": destination}
        else:
            return {"status": "not_found", "from": source, "to": destination}
    except Exception as e:
        return {"status": "error", "from": source, "to": destination, "error": str(e)}

def main():
    """Main cleanup function"""
    
    # Define file movements based on our analysis
    file_movements = {
        # Development Scripts to src/dev_tools/
        "test_trainer_clip_fix.py": "src/dev_tools/tests/test_trainer_clip_fix.py",
        
        # Data Files to F: Drive
        "enhanced_high_school_training_data.json": "F:/ImpressionCore_Training/datasets/enhanced_high_school_training_data.json",
        "high_school_graduate_dataset.json": "F:/ImpressionCore_Training/datasets/high_school_graduate_dataset.json", 
        "high_school_training_data.json": "F:/ImpressionCore_Training/datasets/high_school_training_data.json",
        "world_class_high_school_dataset.json": "F:/ImpressionCore_Training/datasets/world_class_high_school_dataset.json",
        
        # Analysis Files to docs/reports/
        "embedding_status_analysis_20250611_185056.json": "docs/reports/embedding_status_analysis_20250611_185056.json",
        "embedding_status_analysis_20250611_191259.json": "docs/reports/embedding_status_analysis_20250611_191259.json",
        "embedding_status_analysis_20250612_082329.json": "docs/reports/embedding_status_analysis_20250612_082329.json",
        
        # Log Files to src/memlog/
        "ids_maintenance.log": "src/memlog/ids_maintenance.log",
        "training_10_quality.log": "src/memlog/training_10_quality.log",
    }
    
    # Files to remove (orphaned/temp files)
    files_to_remove = [
        "=2.6.0",
        "=3.7.0",
        "__pycache__"
    ]
    
    # Backup directories to consolidate (evaluate but don't auto-move)
    backup_directories = [
        "backup_enhanced_system_final_20250615_145600",
        "backup_enhanced_system_final_20250615_145606", 
        "backup_enhanced_system_final_20250615_145632",
        "backup_model_loading_fix_20250615_120018",
        "backup_runtime_fixes_20250615_144435"
    ]
    
    print("🧹 ImpressionCore Root Directory Cleanup Script")
    print("=" * 50)
    
    # Initialize report
    report = {
        "timestamp": datetime.now().isoformat(),
        "script_version": "1.0",
        "movements": [],
        "removals": [],
        "backup_analysis": [],
        "summary": {}
    }
    
    # Execute file movements
    print("\n📁 Moving files to proper locations...")
    for source, destination in file_movements.items():
        result = move_file_safely(source, destination)
        report["movements"].append(result)
        
        if result["status"] == "success":
            print(f"  ✅ {source} → {destination}")
        elif result["status"] == "not_found":
            print(f"  ⚠️  {source} (not found)")
        else:
            print(f"  ❌ {source} (error: {result.get('error', 'unknown')})")
    
    # Remove orphaned files
    print("\n🗑️  Removing orphaned files...")
    for file_to_remove in files_to_remove:
        try:
            if os.path.exists(file_to_remove):
                if os.path.isdir(file_to_remove):
                    shutil.rmtree(file_to_remove)
                else:
                    os.remove(file_to_remove)
                report["removals"].append({"file": file_to_remove, "status": "removed"})
                print(f"  ✅ Removed {file_to_remove}")
            else:
                report["removals"].append({"file": file_to_remove, "status": "not_found"})
                print(f"  ⚠️  {file_to_remove} (not found)")
        except Exception as e:
            report["removals"].append({"file": file_to_remove, "status": "error", "error": str(e)})
            print(f"  ❌ {file_to_remove} (error: {e})")
    
    # Analyze backup directories (don't auto-remove, just report)
    print("\n💾 Analyzing backup directories...")
    for backup_dir in backup_directories:
        if os.path.exists(backup_dir):
            try:
                size = sum(os.path.getsize(os.path.join(dirpath, filename))
                          for dirpath, dirnames, filenames in os.walk(backup_dir)
                          for filename in filenames)
                file_count = sum(len(filenames) 
                               for dirpath, dirnames, filenames in os.walk(backup_dir))
                
                analysis = {
                    "directory": backup_dir,
                    "exists": True,
                    "size_mb": round(size / (1024 * 1024), 2),
                    "file_count": file_count,
                    "recommendation": "evaluate_for_consolidation"
                }
                report["backup_analysis"].append(analysis)
                print(f"  📊 {backup_dir}: {file_count} files, {analysis['size_mb']} MB")
            except Exception as e:
                report["backup_analysis"].append({
                    "directory": backup_dir,
                    "exists": True,
                    "error": str(e)
                })
                print(f"  ❌ {backup_dir} (error analyzing: {e})")
        else:
            report["backup_analysis"].append({
                "directory": backup_dir,
                "exists": False
            })
            print(f"  ⚠️  {backup_dir} (not found)")
    
    # Generate summary
    successful_moves = len([m for m in report["movements"] if m["status"] == "success"])
    failed_moves = len([m for m in report["movements"] if m["status"] == "error"])
    not_found_moves = len([m for m in report["movements"] if m["status"] == "not_found"])
    
    successful_removals = len([r for r in report["removals"] if r["status"] == "removed"])
    
    report["summary"] = {
        "total_movements_attempted": len(file_movements),
        "successful_movements": successful_moves,
        "failed_movements": failed_moves,
        "not_found_movements": not_found_moves,
        "successful_removals": successful_removals,
        "backup_directories_found": len([b for b in report["backup_analysis"] if b.get("exists", False)])
    }
    
    print("\n📋 Cleanup Summary")
    print("-" * 30)
    print(f"✅ Successful moves: {successful_moves}")
    print(f"❌ Failed moves: {failed_moves}")
    print(f"⚠️  Files not found: {not_found_moves}")
    print(f"🗑️  Files removed: {successful_removals}")
    print(f"💾 Backup dirs found: {report['summary']['backup_directories_found']}")
    
    # Save detailed report
    report_file = create_cleanup_report()
    with open(f"src/memlog/{report_file}", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: src/memlog/{report_file}")
    
    # Check final root directory state
    print("\n📁 Final root directory contents:")
    try:
        root_files = [f for f in os.listdir(".") if os.path.isfile(f)]
        root_dirs = [d for d in os.listdir(".") if os.path.isdir(d) and not d.startswith('.')]
        
        print(f"  Files remaining: {len(root_files)}")
        for f in sorted(root_files):
            print(f"    📄 {f}")
            
        print(f"  Directories: {len(root_dirs)}")
        for d in sorted(root_dirs):
            print(f"    📁 {d}")
            
    except Exception as e:
        print(f"  Error listing directory: {e}")
    
    print("\n🎉 Root directory cleanup completed!")
    print("Next steps:")
    print("  1. Review the detailed report in src/memlog/")
    print("  2. Verify moved files are in correct locations")
    print("  3. Update .gitignore if needed")
    print("  4. Run IDS maintenance to update documentation index")
    print("  5. Consider consolidating backup directories")

if __name__ == "__main__":
    main()
