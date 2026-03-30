#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/scripts/utilities/fix_octal_timestamps.py
**Category:** Source Code
**Status:** Active
"""



import re
from pathlib import Path


def fix_octal_timestamps():
    """Fix all files with problematic timestamp formats."""
    project_root = Path("d:/Projects/impressioncore")

    # Pattern to find problematic timestamps
    pattern = re.compile(r'2025-07-26 10_27_02')
    replacement = '2025-07-26 10:27:02'

    fixed_files = []
    error_files = []

    print("🔧 Fixing octal timestamp issues...")

    # Find all Python files
    for py_file in project_root.rglob("*.py"):
        try:
            with open(py_file, encoding='utf-8') as f:
                content = f.read()

            if pattern.search(content):
                # Fix the timestamp
                new_content = pattern.sub(replacement, content)

                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                fixed_files.append(str(py_file))
                print(f"✅ Fixed: {py_file.relative_to(project_root)}")

        except Exception as e:
            error_files.append((str(py_file), str(e)))
            print(f"❌ Error fixing {py_file}: {e}")

    print("\n📊 Summary:")
    print(f"   ✅ Fixed {len(fixed_files)} files")
    if error_files:
        print(f"   ❌ {len(error_files)} files had errors")

    return len(fixed_files), len(error_files)

if __name__ == "__main__":
    fixed, errors = fix_octal_timestamps()
    print(f"\n🎯 Operation complete: {fixed} files fixed, {errors} errors")
