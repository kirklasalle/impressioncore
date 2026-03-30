#!/usr/bin/env python3
"""
Fix docstring escape sequence warnings in ImpressionCore AI modules.

This script fixes invalid escape sequences in docstrings by converting
backslashes to forward slashes in file paths.
"""

import os
import re


def fix_escape_sequences_in_file(filepath):
    """Fix escape sequences in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix file path escape sequences in docstrings
        # Pattern: File: path\with\backslashes -> File: path/with/forward/slashes
        pattern = r'(File: [^\n]*?)\\([^\n]*)'
        
        def replace_backslashes(match):
            prefix = match.group(1)
            suffix = match.group(2)
            # Replace all backslashes with forward slashes in the path
            fixed_path = suffix.replace('\\', '/')
            return prefix + '/' + fixed_path
        
        # Keep applying the pattern until no more matches
        while re.search(pattern, content):
            content = re.sub(pattern, replace_backslashes, content)
        
        # Write back the fixed content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False


def main():
    """Fix escape sequences in all Python files in core/ai/."""
    fixed_count = 0
    error_count = 0
    
    # Walk through all Python files in core/ai/
    for root, dirs, files in os.walk('core/ai'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                print(f"Fixing: {filepath}")
                
                if fix_escape_sequences_in_file(filepath):
                    fixed_count += 1
                else:
                    error_count += 1
    
    print(f"\nFixed {fixed_count} files")
    if error_count > 0:
        print(f"Errors in {error_count} files")


if __name__ == "__main__":
    main()
