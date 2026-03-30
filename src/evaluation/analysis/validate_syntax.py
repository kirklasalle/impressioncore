#!/usr/bin/env python3
"""Simple syntax validation for analyze_unified_data.py"""

import ast


def validate_syntax(filename):
    """Validate Python syntax in a file."""
    try:
        with open(filename, encoding='utf-8') as f:
            content = f.read()

        # Parse the file to check for syntax errors
        ast.parse(content, filename)
        print(f"SUCCESS: {filename} has valid Python syntax")
        return True

    except SyntaxError as e:
        print(f"SYNTAX ERROR in {filename}:")
        print(f"  Line {e.lineno}: {e.text.strip() if e.text else 'Unknown'}")
        print(f"  Error: {e.msg}")
        return False
    except Exception as e:
        print(f"ERROR reading {filename}: {e}")
        return False

if __name__ == "__main__":
    if validate_syntax("analyze_unified_data.py"):
        print("File is ready for execution!")
    else:
        print("File needs syntax fixes before it can run!")
