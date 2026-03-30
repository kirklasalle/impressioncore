
⚠️ ARCHIVED FILE
This file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.

#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** July-25-2025
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #command_line #documentation #memory_management #performance #python #security #source_code #src/dev_tools/documentation_indexer.py #testing #training
**Category:** Development Tools
**Status:** Deprecated
"""








import os
import re
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

class ImpressionCoreDocumentationIndexer:
    """
    Advanced documentation indexer for ImpressionCore IDS system.
    Generates comprehensive, categorized documentation index.
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.categories = defaultdict(list)
        self.total_files = 0

        # Enhanced category mappings
        self.category_mappings = {
            # User Documentation
            'docs/user/': 'User Documentation',
            'user_guide': 'User Documentation',
            'walkthrough': 'User Documentation',
            'tutorial': 'User Documentation',

            # Developer Documentation
            'docs/developer/': 'Developer Documentation',
            'developer_guide': 'Developer Documentation',
            'api_reference': 'Developer Documentation',
            'architecture': 'Developer Documentation',

            # Reference Documentation
            'docs/reference/': 'Reference Documentation',
            'reference': 'Reference Documentation',
            'api_docs': 'Reference Documentation',
            'technical_specs': 'Reference Documentation',

            # Process Documentation
            'docs/process/': 'Process Documentation',
            'process': 'Process Documentation',
            'workflow': 'Process Documentation',
            'procedures': 'Process Documentation',

            # Core Implementation
            'src/core/': 'Core Implementation',
            'src/kernel/': 'Core Implementation',
            'src/brainsim/': 'Core Implementation',
            'src/liaison/': 'Core Implementation',

            # Training System
            'src/training/': 'Training System',
            'training': 'Training System',
            'distillation': 'Training System',
            'optimization': 'Training System',

            # Memory Management
            'src/memlog/': 'System Logs & Memory',
            'memlog': 'System Logs & Memory',
            'memory': 'System Logs & Memory',
            'vram': 'System Logs & Memory',

            # Utilities & Tools
            'src/utils/': 'Utilities & Tools',
            'src/dev_tools/': 'Utilities & Tools',
            'utils': 'Utilities & Tools',
            'tools': 'Utilities & Tools',

            # Security & Identity
            'src/identity/': 'Security & Identity',
            'src/security/': 'Security & Identity',
            'security': 'Security & Identity',
            'auth': 'Security & Identity',
            'crypto': 'Security & Identity',

            # Interfaces & Services
            'src/interfaces/': 'Interfaces & Services',
            'src/services/': 'Interfaces & Services',
            'interface': 'Interfaces & Services',
            'service': 'Interfaces & Services',
            'api': 'Interfaces & Services',

            # Testing & Benchmarks
            'src/tests/': 'Testing & Quality Assurance',
            'src/benchmarks/': 'Testing & Quality Assurance',
            'test': 'Testing & Quality Assurance',
            'benchmark': 'Testing & Quality Assurance',
            'validation': 'Testing & Quality Assurance',

            # Data & Assets
            'src/data/': 'Data Management',
            'docs/assets/': 'Assets & Media',
            'data': 'Data Management',
            'assets': 'Assets & Media',
            'media': 'Assets & Media',

            # Archive & Legacy
            'docs/archive/': 'Archive & Legacy',
            'archive': 'Archive & Legacy',
            'deprecated': 'Archive & Legacy',
            'legacy': 'Archive & Legacy',

            # Configuration
            'config': 'Configuration',
            'configuration': 'Configuration',
            'settings': 'Configuration'
        }

    def extract_metadata(self, file_path: Path) -> Dict:
        """Extract metadata from file headers."""
        metadata = {
            'title': file_path.stem.replace('_', ' ').replace('-', ' ').title(),
            'created': 'Unknown',
            'updated': 'Unknown',
            'author': 'Unknown',
            'tags': [],
            'category': 'Other',
            'status': 'Unknown',
            'description': ''
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract title from first line
            lines = content.split('\n')
            if lines and lines[0].startswith('#'):
                metadata['title'] = lines[0].lstrip('# ').strip()

            # Extract metadata fields
            metadata_patterns = {
                'created': r'\*\*Created:\*\*\s*(.+)',
                'updated': r'\*\*Updated:\*\*\s*(.+)',
                'author': r'\*\*Author:\*\*\s*(.+)',
                'tags': r'\*\*Tags:\*\*\s*(.+)',
                'category': r'\*\*Category:\*\*\s*(.+)',
                'status': r'\*\*Status:\*\*\s*(.+)'
            }

            for field, pattern in metadata_patterns.items():
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    if field == 'tags':
                        metadata[field] = [tag.strip() for tag in value.split() if tag.startswith('#')]
                    else:
                        metadata[field] = value

            # Extract description from content
            description_lines = []
            in_description = False
            for line in lines[1:]:
                if line.strip() == '' and not in_description:
                    continue
                if line.startswith('**') and not in_description:
                    continue
                if line.startswith('#'):
                    break
                if not in_description and line.strip():
                    in_description = True
                if in_description:
                    description_lines.append(line)
                    if len(description_lines) >= 3:  # First few lines
                        break

            metadata['description'] = ' '.join(description_lines).strip()[:150] + '...' if description_lines else ''

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

        return metadata

    def categorize_file(self, file_path: Path, metadata: Dict) -> str:
        """Determine the appropriate category for a file."""
        path_str = str(file_path).lower().replace('\\', '/')

        # Check metadata category first
        if metadata.get('category') and metadata['category'] != 'Unknown':
            return metadata['category']

        # Check path-based mappings
        for path_pattern, category in self.category_mappings.items():
            if path_pattern in path_str:
                return category

        # Check filename patterns
        filename = file_path.name.lower()
        for pattern, category in self.category_mappings.items():
            if pattern in filename:
                return category

        # Default categorization
        if file_path.suffix == '.md':
            if 'docs' in path_str:
                return 'Documentation'
            else:
                return 'Project Documentation'
        elif file_path.suffix == '.py':
            return 'Source Code'
        else:
            return 'Other'

    def scan_documentation_files(self) -> None:
        """Scan all documentation files and categorize them."""
        extensions = ['.md', '.rst', '.txt']

        for ext in extensions:
            for file_path in self.project_root.rglob(f'*{ext}'):
                # Skip certain directories
                skip_dirs = ['.git', '__pycache__', '.venv', 'node_modules', '.pytest_cache']
                if any(skip_dir in str(file_path) for skip_dir in skip_dirs):
                    continue

                # Skip very small files (likely empty or templates)
                if file_path.stat().st_size < 50:
                    continue

                self.total_files += 1
                metadata = self.extract_metadata(file_path)
                category = self.categorize_file(file_path, metadata)

                # Store file info
                file_info = {
                    'path': str(file_path.relative_to(self.project_root)).replace('\\', '/'),
                    'name': file_path.stem,
                    'metadata': metadata
                }

                self.categories[category].append(file_info)

    def generate_category_section(self, category: str, files: List[Dict]) -> str:
        """Generate a documentation section for a category."""
        files.sort(key=lambda x: x['name'].lower())

        section = f"\n## {category}\n\n"
        section += f"*{len(files)} files in this category*\n\n"

        for file_info in files:
            path = file_info['path']
            name = file_info['name'].replace('_', ' ').title()
            metadata = file_info['metadata']

            # Format entry
            section += f"- **[{name}]({path})**"

            # Add status if available
            if metadata.get('status') and metadata['status'] != 'Unknown':
                status_emoji = '✅' if metadata['status'] == 'Active' else '📋'
                section += f" {status_emoji}"

            # Add description if available
            if metadata.get('description'):
                section += f"\n  {metadata['description']}"

            # Add tags if available
            if metadata.get('tags'):
                tags_str = ' '.join(metadata['tags'][:5])  # First 5 tags
                section += f"\n  *Tags: {tags_str}*"

            section += "\n"

        return section

    def generate_comprehensive_index(self) -> str:
        """Generate the complete documentation index."""
        self.scan_documentation_files()

        # Sort categories by importance
        category_order = [
            'User Documentation',
            'Developer Documentation',
            'Reference Documentation',
            'Core Implementation',
            'Training System',
            'Security & Identity',
            'Interfaces & Services',
            'Utilities & Tools',
            'Testing & Quality Assurance',
            'Data Management',
            'System Logs & Memory',
            'Configuration',
            'Process Documentation',
            'Assets & Media',
            'Project Documentation',
            'Documentation',
            'Source Code',
            'Archive & Legacy',
            'Other'
        ]

        # Header
        index_content = f"""# ImpressionCore Documentation Index

**Created:** 2024-10-15
**Updated:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Author:** ImpressionCore IDS System
**Tags:** #documentation_index #ids_system #file_organization #comprehensive_guide #automated_generation
**Category:** Reference Documentation
**Status:** Active - Auto-Generated

**Total Documents:** {self.total_files}
**Categories:** {len(self.categories)}
**Last Scan:** Complete project reorganization update

---

## Overview

This index provides comprehensive access to all ImpressionCore documentation, automatically organized by the IDS (ImpressionCore Documentation System). Following the major project reorganization, all files have been re-scanned, categorized, and tagged for optimal discoverability.

## Table of Contents

"""

        # Generate table of contents
        for category in category_order:
            if category in self.categories:
                count = len(self.categories[category])
                index_content += f"- [{category}](#{category.lower().replace(' ', '-').replace('&', '')}) ({count} files)\n"

        index_content += "\n---\n"

        # Generate detailed sections
        for category in category_order:
            if category in self.categories:
                index_content += self.generate_category_section(category, self.categories[category])

        # Footer
        index_content += f"""
---

## Index Statistics

- **Total Files Indexed:** {self.total_files}
- **Active Categories:** {len(self.categories)}
- **Auto-Generated:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **IDS Version:** Enhanced with tag support
- **Next Update:** Automatic on file changes

## Navigation Tips

- Use Ctrl+F to search for specific topics
- Click category headers to jump to sections
- File status indicators: ✅ Active, 📋 In Progress
- Tags help identify related content across categories

*This index is automatically maintained by the ImpressionCore IDS system.*
"""

        return index_content

if __name__ == "__main__":
    indexer = ImpressionCoreDocumentationIndexer()
    print("Generating comprehensive ImpressionCore documentation index...")

    index_content = indexer.generate_comprehensive_index()

    # Save the new index
    index_path = Path("docs/DOCUMENTATION_INDEX.md")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)

    print(f"Documentation index updated: {index_path}")
    print(f"Total files indexed: {indexer.total_files}")
    print(f"Categories: {len(indexer.categories)}")

    # Print category summary
    print("\nCategory Summary:")
    for category, files in sorted(indexer.categories.items()):
        print(f"  {category}: {len(files)} files")
