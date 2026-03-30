#!/usr/bin/env python3
"""
Final Root Directory Cleanup Script
Handles the remaining organizational tasks after backup consolidation
"""

import os
import shutil
from pathlib import Path

def main():
    """Execute final cleanup tasks"""
    root_dir = Path(".")
    moved_files = []
    errors = []
    
    print("🧹 ImpressionCore Final Root Directory Cleanup")
    print("=" * 50)
    
    # Files to move to docs/technical/
    technical_files = [
        "backup_manifest.md",
        "MODEL_LOADING_FIX_QUICK_REFERENCE.md",
        "SYSTEM_STATUS_FINAL.md"
    ]
    
    # Create docs/technical if it doesn't exist
    docs_technical = Path("docs/technical")
    docs_technical.mkdir(exist_ok=True)
    
    # Move technical files
    print("\n📋 Moving technical documentation files to docs/technical/...")
    for file in technical_files:
        if Path(file).exists():
            try:
                shutil.move(file, docs_technical / file)
                moved_files.append(f"{file} → docs/technical/{file}")
                print(f"✅ Moved {file}")
            except Exception as e:
                errors.append(f"Error moving {file}: {e}")
                print(f"❌ Failed to move {file}: {e}")
        else:
            print(f"⚠️  {file} not found in root")
    
    # Create .github directory if it doesn't exist
    github_dir = Path(".github")
    github_dir.mkdir(exist_ok=True)
    
    # Files to move to .github/
    github_files = [
        "COPILOT_PRIME_DIRECTIVE.md",
        "COPILOT_SACRED_COVENANT.md"
    ]
    
    print(f"\n🤖 Moving Copilot files to .github/...")
    for file in github_files:
        if Path(file).exists():
            try:
                shutil.move(file, github_dir / file)
                moved_files.append(f"{file} → .github/{file}")
                print(f"✅ Moved {file}")
            except Exception as e:
                errors.append(f"Error moving {file}: {e}")
                print(f"❌ Failed to move {file}: {e}")
        else:
            print(f"⚠️  {file} not found in root")
    
    # Check for any remaining cleanup files
    cleanup_patterns = ["*fix*.py", "*analysis*.json", "*log"]
    remaining_files = []
    
    print(f"\n🔍 Checking for remaining cleanup files...")
    for pattern in cleanup_patterns:
        for file in root_dir.glob(pattern):
            if file.is_file():
                remaining_files.append(str(file))
    
    if remaining_files:
        print(f"📋 Found {len(remaining_files)} additional files that may need cleanup:")
        for file in remaining_files:
            print(f"   - {file}")
    else:
        print("✅ No additional cleanup files found")
    
    # Remove orphaned version files and cache
    orphaned_files = ["=2.6.0", "=3.7.0", "__pycache__"]
    print(f"\n🗑️  Removing orphaned files...")
    for file in orphaned_files:
        path = Path(file)
        if path.exists():
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                moved_files.append(f"Removed {file}")
                print(f"✅ Removed {file}")
            except Exception as e:
                errors.append(f"Error removing {file}: {e}")
                print(f"❌ Failed to remove {file}: {e}")
        else:
            print(f"⚠️  {file} not found")
    
    # Generate final report
    print(f"\n📊 FINAL CLEANUP SUMMARY")
    print("=" * 30)
    print(f"✅ Successfully moved/removed: {len(moved_files)} items")
    print(f"❌ Errors encountered: {len(errors)} items")
    
    if moved_files:
        print(f"\n📋 Files moved/removed:")
        for item in moved_files:
            print(f"   - {item}")
    
    if errors:
        print(f"\n❌ Errors:")
        for error in errors:
            print(f"   - {error}")
    
    # Final root directory check
    print(f"\n📁 Current root directory contents:")
    root_contents = []
    for item in sorted(root_dir.iterdir()):
        if item.name.startswith('.'):
            continue
        root_contents.append(f"   - {item.name}{'/' if item.is_dir() else ''}")
    
    for item in root_contents:
        print(item)
    
    print(f"\n🎉 Final cleanup completed!")
    print(f"Root directory now contains {len(root_contents)} visible items")

if __name__ == "__main__":
    main()
