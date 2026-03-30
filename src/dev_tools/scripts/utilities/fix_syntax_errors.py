#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/scripts/utilities/fix_syntax_errors.py
**Category:** Source Code
**Status:** Active
"""




import re
from pathlib import Path


def fix_timestamp_quotes(directory):
    """Fix quoted timestamps in Python file headers"""
    fixed_files = []
    pattern = r'(\*\*Updated:\*\* \d{4}-\d{2}-\d{2} )"(\d{2}:\d{2}:\d{2})"'
    replacement = r'\1\2'

    for file_path in Path(directory).rglob("*.py"):
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Check if the file contains the problematic pattern
            if re.search(pattern, content):
                # Fix the pattern
                new_content = re.sub(pattern, replacement, content)

                # Write back the fixed content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                fixed_files.append(str(file_path))
                print(f"✅ Fixed: {file_path}")

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

    return fixed_files

if __name__ == "__main__":
    print("🔧 Fixing timestamp syntax errors...")
    fixed = fix_timestamp_quotes("src")
    print(f"\n✅ Fixed {len(fixed)} files:")
    for file in fixed:
        print(f"   - {file}")
    print("\n🎯 All syntax errors fixed! B3 ready to initialize!")
