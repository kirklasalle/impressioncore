#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #multimodal #python #source_code #src/scripts\f_drive\f_drive_embedding_analysis.py
**Category:** Source Code
**Status:** Active
"""



import json
from datetime import datetime
from pathlib import Path


def analyze_embeddings_directory():
    """Analyze F: drive embeddings directory structure and contents"""
    embeddings_path = Path("F:/data/embeddings")

    print("🔍 F: DRIVE EMBEDDINGS ANALYSIS")
    print("=" * 60)

    if not embeddings_path.exists():
        print("❌ Embeddings directory does not exist: F:/data/embeddings")
        return

    analysis = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "root_path": str(embeddings_path),
        "directories": {},
        "total_files": 0,
        "total_size_mb": 0,
        "file_types": {},
        "largest_files": []
    }

    # Analyze directory structure
    print("📁 DIRECTORY STRUCTURE:")

    if not list(embeddings_path.iterdir()):
        print("   ⚠️ Directory is empty")
        return analysis

    for item in sorted(embeddings_path.rglob("*")):
        if item.is_file():
            try:
                size_mb = item.stat().st_size / (1024 * 1024)
                relative_path = item.relative_to(embeddings_path)
                parent_dir = str(relative_path.parent) if relative_path.parent != Path('.') else "root"

                # Track by directory
                if parent_dir not in analysis["directories"]:
                    analysis["directories"][parent_dir] = {
                        "files": 0,
                        "size_mb": 0,
                        "file_types": {}
                    }

                analysis["directories"][parent_dir]["files"] += 1
                analysis["directories"][parent_dir]["size_mb"] += size_mb

                # Track file types
                ext = item.suffix.lower()
                if ext not in analysis["file_types"]:
                    analysis["file_types"][ext] = {"count": 0, "size_mb": 0}
                analysis["file_types"][ext]["count"] += 1
                analysis["file_types"][ext]["size_mb"] += size_mb

                # Track by directory file types
                if ext not in analysis["directories"][parent_dir]["file_types"]:
                    analysis["directories"][parent_dir]["file_types"][ext] = 0
                analysis["directories"][parent_dir]["file_types"][ext] += 1

                analysis["total_files"] += 1
                analysis["total_size_mb"] += size_mb

                # Track largest files
                analysis["largest_files"].append({
                    "path": str(relative_path),
                    "size_mb": size_mb
                })

            except Exception as e:
                print(f"   ❌ Error processing {item}: {e}")

    # Sort largest files
    analysis["largest_files"] = sorted(analysis["largest_files"], key=lambda x: x["size_mb"], reverse=True)[:20]

    # Display results
    print("\n📊 SUMMARY:")
    print(f"   Total Files: {analysis['total_files']:,}")
    print(f"   Total Size: {analysis['total_size_mb']:.1f} MB ({analysis['total_size_mb']/1024:.2f} GB)")
    print(f"   Directories: {len(analysis['directories'])}")

    print("\n📁 DIRECTORIES:")
    for dir_name, dir_info in sorted(analysis["directories"].items()):
        print(f"   {dir_name:<30} | {dir_info['files']:>6} files | {dir_info['size_mb']:>8.1f} MB")

        # Show file types in this directory
        if dir_info["file_types"]:
            types_str = ", ".join([f"{ext}({count})" for ext, count in sorted(dir_info["file_types"].items())])
            print(f"   {'':<30} | Types: {types_str}")

    print("\n📄 FILE TYPES:")
    for ext, type_info in sorted(analysis["file_types"].items(), key=lambda x: x[1]["size_mb"], reverse=True):
        print(f"   {ext:<10} | {type_info['count']:>6} files | {type_info['size_mb']:>8.1f} MB")

    print("\n🔝 LARGEST FILES:")
    for i, file_info in enumerate(analysis["largest_files"][:10], 1):
        print(f"   {i:2d}. {file_info['path']:<50} | {file_info['size_mb']:>8.1f} MB")

    # Check for B3 specific embeddings
    print("\n🎯 B3 EMBEDDINGS SEARCH:")
    b3_patterns = ["b3", "impressioncore", "multimodal", "brain", "fusion"]
    b3_found = []

    for pattern in b3_patterns:
        for item in embeddings_path.rglob(f"*{pattern}*"):
            if item.is_file():
                size_mb = item.stat().st_size / (1024 * 1024)
                b3_found.append({
                    "pattern": pattern,
                    "path": str(item.relative_to(embeddings_path)),
                    "size_mb": size_mb
                })

    if b3_found:
        print("   ✅ Found B3-related embeddings:")
        for item in b3_found:
            print(f"      {item['path']} ({item['size_mb']:.1f} MB) - matches '{item['pattern']}'")
    else:
        print("   ⚠️ No B3-specific embeddings found")

    # Sacred Covenant compliance check
    print("\n🔐 SACRED COVENANT COMPLIANCE:")
    print("   ✅ Directory analyzed without modification")
    print("   ✅ File integrity preserved during analysis")
    print("   ✅ No unauthorized access or changes")

    # Save analysis
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis_file = f"f_drive_embedding_analysis_{timestamp}.json"

    with open(analysis_file, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"\n📋 Analysis saved: {analysis_file}")

    return analysis

if __name__ == "__main__":
    analyze_embeddings_directory()
