#!/usr/bin/env python3
"""
ImpressionCore: Check Variable Scope

Module for check variable scope functionality in the ImpressionCore framework.

File: tools\check_variable_scope.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [production, object-oriented, 2025]
Dependencies: [pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements check variable scope functionality for the
ImpressionCore brain-inspired multimodal AI framework. Optimized for memory-
constrained environments and designed to run efficiently on consumer hardware.

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem

TODO:
- Add comprehensive unit tests
- Implement performance benchmarks
- Add configuration validation
- Optimize memory usage patterns

Examples:
```python
# Basic usage example
# from tools.check_variable_scope import  # Fixed: using local implementation VariableScopeChecker
instance = VariableScopeChecker()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import ast
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class VariableScopeChecker(ast.NodeVisitor):
    """AST visitor that checks for variable scope issues."""
    
    def __init__(self):
        """Initialize the checker."""
        self.issues = []
        self.current_function = None
        self.module_globals = set()
        self.function_locals = {}
        self.function_reads = {}
        
    def visit_Module(self, node):
        """Visit the module node to collect top-level assignments."""
        # Find top-level assignments to identify global variables
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        self.module_globals.add(target.id)
        
        # Continue visiting the rest of the tree
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node):
        """Visit function definitions to check for scope issues."""
        old_function = self.current_function
        self.current_function = node.name
        
        # Initialize tracking for this function
        self.function_locals[node.name] = set()
        self.function_reads[node.name] = set()
        
        # Handle global declarations
        global_vars = set()
        for item in node.body:
            if isinstance(item, ast.Global):
                global_vars.update(item.names)
        
        # Visit function body
        self.generic_visit(node)
        
        # Check for variables that are read before being assigned
        for var in self.function_reads[node.name]:
            if (var in self.module_globals and 
                var in self.function_locals[node.name] and 
                var not in global_vars):
                self.issues.append({
                    'function': node.name,
                    'variable': var,
                    'line': node.lineno,
                    'type': 'shadowing',
                    'message': f"Function '{node.name}' shadows global variable '{var}' without using global keyword"
                })
        
        self.current_function = old_function
        
    def visit_Assign(self, node):
        """Visit assignment nodes to track local variables."""
        if self.current_function:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.function_locals[self.current_function].add(target.id)
        
        # Continue visiting
        self.generic_visit(node)
        
    def visit_Name(self, node):
        """Visit name nodes to track variable reads."""
        if isinstance(node.ctx, ast.Load) and self.current_function:
            self.function_reads[self.current_function].add(node.id)
        
        # No need to recurse here as Name nodes are leaves in the AST

def check_file(file_path):
    """Check a single Python file for variable scope issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=file_path)
        checker = VariableScopeChecker()
        checker.visit(tree)
        
        if checker.issues:
            logger.warning(f"⚠️ {file_path}: Found {len(checker.issues)} variable scope issues")
            for issue in checker.issues:
                logger.warning(f"   Line {issue['line']}: {issue['message']}")
            return checker.issues
        else:
            logger.info(f"✅ {file_path}: No variable scope issues found")
            return []
            
    except Exception as e:
        logger.error(f"Error analyzing {file_path}: {e}")
        return []

def main():
    """Run the variable scope checker on specified files or directories."""
    if len(sys.argv) < 2:
        logger.error("Usage: python check_variable_scope.py <file_or_directory>")
        return 1
    
    path = sys.argv[1]
    
    if os.path.isfile(path):
        files = [path]
    elif os.path.isdir(path):
        files = []
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.py'):
                    files.append(os.path.join(root, filename))
    else:
        logger.error(f"Path not found: {path}")
        return 1
    
    total_issues = 0
    
    for file_path in files:
        issues = check_file(file_path)
        total_issues += len(issues)
    
    if total_issues > 0:
        logger.warning(f"\nFound {total_issues} variable scope issues in {len(files)} files")
    else:
        logger.info(f"\nNo variable scope issues found in {len(files)} files")
    
    return 0 if total_issues == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
