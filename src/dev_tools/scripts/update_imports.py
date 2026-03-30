#!/usr/bin/env python3
"""
Import Path Updater
===================

Updates import paths after directory restructuring.

File: dev_tools/scripts/update_imports.py
Project: ImpressionCore
Created: 2025-01-07
"""

import os
import re
import sys

def update_imports_in_file(file_path):
    """Update import statements in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Update import patterns
        patterns = [
            (r'from src\.diffusion', 'from src.core.ai.diffusion'),
            (r'from src\.multimodal', 'from src.core.ai.multimodal'),
            (r'from src\.inference', 'from src.core.ai.inference'),
            (r'from src\.preprocessing', 'from src.core.ai.preprocessing'),
            (r'from src\.tokenization', 'from src.core.ai.tokenization'),
            (r'from src\.api', 'from src.services.api'),
            (r'from src\.assistant', 'from src.services.assistant'),
            (r'from src\.backend', 'from src.services.backend'),
            (r'from src\.middleware', 'from src.services.middleware'),
            (r'from src\.web', 'from src.interfaces.web'),
            (r'from src\.frontend', 'from src.interfaces.frontend'),
            (r'from src\.cli', 'from src.interfaces.cli'),
            (r'from src\.validation', 'from src.dev_tools.validation'),
            (r'from src\.benchmarks', 'from src.dev_tools.benchmarks'),
            (r'from src\.evaluation', 'from src.dev_tools.evaluation'),
            (r'from src\.examples', 'from src.dev_tools.examples'),
            (r'from src\.visualization', 'from src.dev_tools.visualization'),
            (r'from src\.tests', 'from src.dev_tools.tests'),
            (r'from src\.jupyter', 'from src.dev_tools.jupyter'),
            (r'from src\.security', 'from src.core.security'),
            (r'from src\.knowledge', 'from src.core.knowledge'),
            (r'from src\.utils', 'from src.core.utils'),
        ]
        
        for old_pattern, new_pattern in patterns:
            content = re.sub(old_pattern, new_pattern, content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
            
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False
    
    return False

def update_imports_in_directory(directory):
    """Recursively update imports in all Python files in directory."""
    updated_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        if any(skip in root for skip in ['__pycache__', '.git', 'node_modules']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if update_imports_in_file(file_path):
                    updated_files.append(file_path)
    
    return updated_files

if __name__ == "__main__":
    # Get the src directory path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(script_dir, '..', '..', '..')
    src_dir = os.path.abspath(src_dir)
    
    print(f"Updating imports in: {src_dir}")
    updated_files = update_imports_in_directory(src_dir)
    
    if updated_files:
        print(f"\nUpdated {len(updated_files)} files:")
        for file_path in updated_files:
            print(f"  - {file_path}")
    else:
        print("\nNo files needed import updates.")
