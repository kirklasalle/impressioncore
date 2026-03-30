#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/core/utils/fix_src_imports.py
**Category:** Core Implementation
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\core\\utils\\fix_src_imports.py
# Category:** Core Implementation
# Status:** Active

"""
Script to recursively scan and fix all Python files in the project that use 'from src.' or 'import src.' imports.
It will replace them with the correct import path (removing the 'src.' prefix).

Usage:
    python src/core/utils/fix_src_imports.py

This script will print all files it modifies and the lines changed.
"""
import os
import re

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')

SRC_IMPORT_PATTERN = re.compile(r'^(\s*)(from|import)\s+src(\.[\w\.]+)', re.MULTILINE)


def fix_imports_in_file(filepath):
    try:
        with open(filepath, encoding='utf-8') as f:
            content = f.read()
        new_content, n = SRC_IMPORT_PATTERN.subn(lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)}", content)
        if n > 0:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"[FIXED] {filepath} ({n} import(s) updated)")
                return True
            except PermissionError:
                print(f"[SKIPPED - PERMISSION DENIED] {filepath}")
                return False
        return False
    except Exception as e:
        print(f"[ERROR] {filepath}: {e}")
        return False

def scan_and_fix(directory):
    for root, _dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                fix_imports_in_file(filepath)

if __name__ == '__main__':
    print(f"Scanning for 'src.' imports in: {SRC_DIR}")
    scan_and_fix(SRC_DIR)
    print("Done.")
