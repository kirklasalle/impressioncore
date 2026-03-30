"""
Cleanup docs/ Directory

Identifies and archives orphaned files:
- .resolved.* versions
- Old IDS exports
- .metadata.json files
- Orphaned media files

Created: January 18, 2026
Author: Agent0 (SAL)
"""
import shutil
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Add project roots
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    print("=== docs/ Directory Cleanup Analysis ===\n")

    docs_dir = project_root / "docs"
    archive_dir = docs_dir / "archive" / "2026-01-cleanup"

    # Categories to clean
    cleanup_candidates = defaultdict(list)

    # 1. Find .resolved.* files
    for f in docs_dir.rglob("*.resolved.*"):
        cleanup_candidates["resolved_versions"].append(f)

    # 2. Find old IDS exports (keep only latest)
    ids_exports = sorted(docs_dir.glob("ids_export_*.json"), reverse=True)
    if len(ids_exports) > 1:
        cleanup_candidates["old_exports"].extend(ids_exports[1:])  # Keep newest

    # 3. Find .metadata.json files
    for f in docs_dir.rglob("*.metadata.json"):
        cleanup_candidates["metadata_files"].append(f)

    # 4. Find orphaned media in docs root (should be in assets/)
    for ext in [".img", ".webp", ".png"]:
        for f in docs_dir.glob(f"*{ext}"):
            if f.parent == docs_dir:  # Only root level
                cleanup_candidates["orphaned_media"].append(f)

    # Report
    total = 0
    for category, files in cleanup_candidates.items():
        print(f"📁 {category}: {len(files)} files")
        total += len(files)
        for f in files[:5]:
            print(f"   - {f.relative_to(docs_dir)}")
        if len(files) > 5:
            print(f"   ... and {len(files) - 5} more")
        print()

    print(f"=== Total Cleanup Candidates: {total} ===\n")

    # Check for --execute flag
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        print("⚠️  EXECUTING CLEANUP (moving files to archive)...\n")

        # Create archive directory
        archive_dir.mkdir(parents=True, exist_ok=True)

        moved = 0
        for category, files in cleanup_candidates.items():
            category_dir = archive_dir / category
            category_dir.mkdir(exist_ok=True)

            for f in files:
                try:
                    dest = category_dir / f.name
                    shutil.move(str(f), str(dest))
                    moved += 1
                except Exception as e:
                    print(f"   ERROR moving {f.name}: {e}")

        print(f"✅ Moved {moved} files to {archive_dir.relative_to(docs_dir)}")

        # Generate cleanup report
        report_path = archive_dir / "cleanup_report.md"
        with open(report_path, "w") as f:
            f.write(f"# Cleanup Report - {datetime.now().strftime('%B %d, %Y')}\n\n")
            f.write("**Executed by:** Agent0 (SAL)\n\n")
            f.write("## Summary\n\n")
            f.write(f"Total files archived: {moved}\n\n")
            for category, files in cleanup_candidates.items():
                f.write(f"### {category}\n")
                for file in files:
                    f.write(f"- {file.name}\n")
                f.write("\n")
        print(f"📄 Report saved: {report_path.relative_to(docs_dir)}")
    else:
        print("Run with --execute to perform cleanup:")
        print(f"  python {Path(__file__).name} --execute")


if __name__ == "__main__":
    main()
