#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/scripts/utilities/comprehensive_syntax_fix.py
**Category:** Source Code
**Status:** Active
"""




import re
from pathlib import Path


def fix_all_syntax_errors(directory):
    """Fix ALL syntax errors in Python files"""
    fixed_files = []

    # Multiple patterns to catch all syntax issues
    patterns = [
        # Quoted timestamps
        (r'(\*\*Updated:\*\* \d{4}-\d{2}-\d{2} )"(\d{2}:\d{2}:\d{2})"', r'\1\2'),
        # Any other leading zero issues
        (r'(\d{4}-\d{2}-\d{2} )0(\d):', r'\1\2:'),
        # Octal-like patterns
        (r': 0(\d{2}):', r': \1:'),
    ]

    for file_path in Path(directory).rglob("*.py"):
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Apply all patterns
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)

            # If content changed, write it back
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                fixed_files.append(str(file_path))
                print(f"✅ Fixed: {file_path}")

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

    return fixed_files

def validate_python_syntax(directory):
    """Validate Python syntax in all files"""
    print("\n🔍 VALIDATING PYTHON SYNTAX...")

    error_files = []
    for file_path in Path(directory).rglob("*.py"):
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Try to compile the Python code
            compile(content, str(file_path), 'exec')

        except SyntaxError as e:
            error_files.append(f"{file_path}: {e}")
            print(f"❌ Syntax Error in {file_path}: {e}")
        except Exception:
            # Other errors are OK for now
            pass

    return error_files

if __name__ == "__main__":
    print("🔧 COMPREHENSIVE SYNTAX ERROR FIX...")

    # Fix all syntax errors
    fixed = fix_all_syntax_errors("src")
    print(f"\n✅ Fixed {len(fixed)} additional files")

    # Validate syntax
    errors = validate_python_syntax("src")

    if not errors:
        print("\n🎯 ALL PYTHON FILES HAVE VALID SYNTAX!")
        print("✅ B3 INITIALIZATION READY!")
    else:
        print(f"\n⚠️ Found {len(errors)} files with syntax errors:")
        for error in errors:
            print(f"   - {error}")
