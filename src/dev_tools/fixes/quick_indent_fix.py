#!/usr/bin/env python3
"""
Quick indentation fix for b1_unified_model.py
Fixes the unexpected indent error around line 161.
"""
import re

def fix_indentation_error():
    """Fix the indentation error in the B1 unified model file."""
    file_path = r"D:\Projects\impressioncore\src\models\impressioncore-base\b1_unified_model.py"
    
    print("=== Quick Indentation Fix ===")
    print(f"Target file: {file_path}")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and fix the problematic lines around line 161
    fixed_lines = []
    in_try_block = False
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Look for the try block and fix indentation
        if 'try:' in line and 'phoneme_embedding_config' in lines[i+1] if i+1 < len(lines) else False:
            in_try_block = True
            fixed_lines.append(line)
            continue
            
        if in_try_block and line_num <= 175:  # Process the next several lines
            # Remove any extra indentation and apply proper indentation
            stripped = line.lstrip()
            if stripped.startswith('if not hasattr') or stripped.startswith('self.phoneme_embedding_config') or stripped.startswith('self.phoneme_extractor'):
                # These should be indented 12 spaces (3 levels)
                fixed_lines.append('            ' + stripped)
            elif stripped.startswith('except'):
                # except should be at the same level as try (8 spaces)
                fixed_lines.append('        ' + stripped)
                in_try_block = False
            elif stripped.startswith('#'):
                # Comments should be indented 12 spaces
                fixed_lines.append('            ' + stripped)
            elif stripped == '' or stripped == '\n':
                # Keep empty lines as is
                fixed_lines.append(line)
            else:
                # Default case
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Write back the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("✓ Fixed indentation errors around line 161")
    print("✓ Ready to test: python -m src.models.impressioncore-base.b1_unified_model")

if __name__ == "__main__":
    fix_indentation_error()
