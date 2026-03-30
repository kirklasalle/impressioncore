
⚠️ ARCHIVED FILE
This file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.

#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** July-25-2025
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #api #attention_mechanism #command_line #cuda #deployment #documentation #gpu_optimization #inference #memory_management #multimodal #performance #python #pytorch #security #source_code #src/dev_tools/ids_header_updater.py #testing #tokenization #training #transformer #web_interface
**Category:** Development Tools
**Status:** Deprecated
"""










import os
import re
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class ImpressionCoreIDSHeaderUpdater:
    """
    Automated header standardization utility for ImpressionCore IDS system.
    Updates all documentation and code files with standardized headers.
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.updated_files = []
        self.skipped_files = []
        self.errors = []

        # Standard header templates for different file types
        self.markdown_header_template = """# {title}

**Created:** {created_date}
**Updated:** {updated_date}
**Author:** {author}
**Tags:** {tags}
**Category:** {category}
**Status:** {status}"""

        self.python_header_template = '''#!/usr/bin/env python3
"""
{title}

**Created:** {created_date}
**Updated:** {updated_date}
**Author:** {author}
**Tags:** {tags}
**Category:** {category}
**Status:** {status}
"""'''

        # File type mappings
        self.file_categories = {
            'docs/user/': 'User Documentation',
            'docs/developer/': 'Developer Documentation',
            'docs/reference/': 'Reference Documentation',
            'docs/process/': 'Process Documentation',
            'docs/archive/': 'Archive',
            'docs/assets/': 'Assets',
            'src/core/': 'Core Implementation',
            'src/training/': 'Training System',
            'src/memlog/': 'System Logs',
            'src/utils/': 'Utility Functions',
            'src/identity/': 'Identity Management',
            'src/interfaces/': 'Interface Definitions',
            'src/services/': 'Service Implementation',
            'src/data/': 'Data Processing',
            'src/benchmarks/': 'Performance Benchmarks',
            'src/tests/': 'Testing Framework',
            'src/deployment/': 'Deployment Tools',
            'src/dev_tools/': 'Development Tools',
            'src/assistant/': 'AI Assistant Features',
            'src/user_data/': 'User Data Management'
        }

    def determine_category(self, file_path: Path) -> str:
        """Determine the appropriate category for a file based on its path."""
        path_str = str(file_path).replace('\\', '/')

        for path_prefix, category in self.file_categories.items():
            if path_prefix in path_str:
                return category

        # Default categories
        if file_path.suffix == '.md':
            return 'Documentation'
        elif file_path.suffix == '.py':
            return 'Source Code'
        elif file_path.suffix in ['.yaml', '.yml']:
            return 'Configuration'
        elif file_path.suffix == '.json':
            return 'Data/Configuration'
        else:
            return 'Other'

    def extract_existing_tags(self, content: str) -> List[str]:
        """Extract existing tags from file content."""
        tags = []

        # Look for existing tag patterns
        tag_patterns = [
            r'#\w+(?:_\w+)*',  # #tag_format
            r'@\w+',            # @tag
            r'\*\*Tags:\*\*\s*(.+)',  # **Tags:** format
        ]

        for pattern in tag_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            tags.extend(matches)

        return list(set(tags))

    def generate_smart_tags(self, file_path: Path, content: str) -> str:
        """Generate intelligent tags based on file content and path."""
        tags = set()

        # Path-based tags
        path_parts = str(file_path).lower().split('/')
        for part in path_parts:
            if part and part not in ['src', 'docs', 'projects', 'impressioncore']:
                tags.add(f'#{part.replace("-", "_").replace(" ", "_")}')

        # Content-based tags
        content_lower = content.lower()

        # Technology tags
        tech_keywords = {
            'pytorch': '#pytorch',
            'cuda': '#cuda',
            'gpu': '#gpu_optimization',
            'memory': '#memory_management',
            'training': '#training',
            'inference': '#inference',
            'multimodal': '#multimodal',
            'transformer': '#transformer',
            'attention': '#attention_mechanism',
            'tokenizer': '#tokenization',
            'api': '#api',
            'web': '#web_interface',
            'cli': '#command_line',
            'test': '#testing',
            'benchmark': '#performance',
            'security': '#security',
            'deployment': '#deployment',
            'documentation': '#documentation'
        }

        for keyword, tag in tech_keywords.items():
            if keyword in content_lower:
                tags.add(tag)

        # File type tags
        if file_path.suffix == '.md':
            tags.add('#documentation')
        elif file_path.suffix == '.py':
            tags.add('#python')
            tags.add('#source_code')
        elif file_path.suffix in ['.yaml', '.yml']:
            tags.add('#configuration')

        return ' '.join(sorted(list(tags)))

    def update_file_header(self, file_path: Path) -> bool:
        """Update a single file with standardized header."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Skip if file is empty
            if not content.strip():
                self.skipped_files.append(str(file_path))
                return False

            # Extract title from first line or filename
            lines = content.split('\n')
            title = "Untitled Document"

            if lines and lines[0].startswith('#'):
                title = lines[0].lstrip('# ').strip()
            else:
                title = file_path.stem.replace('_', ' ').replace('-', ' ').title()

            # Determine dates
            created_date = "October-15-2024"  # Default creation date
            updated_date = datetime.datetime.now().strftime("%B-%d-%Y")

            # Try to extract existing dates - handle both old and new formats
            created_match = re.search(r'\*\*Created:\*\*\s*(\d{4}-\d{2}-\d{2}|\w+-\d{1,2}-\d{4})', content)
            if created_match:
                date_str = created_match.group(1)
                # Convert old format to new format if needed
                if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                    try:
                        parsed_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                        created_date = parsed_date.strftime("%B-%d-%Y")
                    except Exception:
                        created_date = date_str  # Keep original if parsing fails
                else:
                    created_date = date_str  # Already in correct format

            # Determine author
            author = "ImpressionCore Team"
            if 'memlog' in str(file_path).lower():
                author = "System Generated"
            elif 'vrgc' in str(file_path).lower():
                author = "Virtually Robotic GitHub Copilot"
            elif 'kirk' in content.lower() or 'lasalle' in content.lower():
                author = "Kirk LaSalle"

            # Generate tags
            tags = self.generate_smart_tags(file_path, content)

            # Determine category and status
            category = self.determine_category(file_path)
            status = "Active"
            if 'archive' in str(file_path).lower():
                status = "Archived"
            elif 'deprecated' in content.lower():
                status = "Deprecated"

            # Create new header based on file type
            if file_path.suffix == '.py':
                template = self.python_header_template
            else:
                template = self.markdown_header_template

            new_header = template.format(
                title=title,
                created_date=created_date,
                updated_date=updated_date,
                author=author,
                tags=tags,
                category=category,
                status=status
            )

            # Replace existing header or add new one
            if file_path.suffix == '.py':
                # For Python files, look for existing shebang and docstring
                if lines and lines[0].startswith('#!'):
                    # Skip shebang, find docstring or add new one
                    content_start = 1
                    while content_start < len(lines) and (lines[content_start].strip() == '' or lines[content_start].startswith('#')):
                        content_start += 1

                    # Check if there's a docstring
                    if content_start < len(lines) and lines[content_start].strip().startswith('"""'):
                        # Find end of docstring
                        docstring_end = content_start + 1
                        while docstring_end < len(lines) and not lines[docstring_end].strip().endswith('"""'):
                            docstring_end += 1
                        content_start = docstring_end + 1

                    # Reconstruct with new header
                    remaining_content = '\n'.join(lines[content_start:])
                    new_content = new_header + '\n\n' + remaining_content
                else:
                    # No shebang, add header at beginning
                    new_content = new_header + '\n\n' + content
            else:
                # For markdown files
                if lines and lines[0].startswith('#'):
                    # Find end of existing header block
                    header_end = 1
                    for i, line in enumerate(lines[1:], 1):
                        if line.startswith('**') or line.strip() == '':
                            header_end = i + 1
                        else:
                            break

                    # Find first content line (skip empty lines after header)
                    content_start = header_end
                    while content_start < len(lines) and lines[content_start].strip() == '':
                        content_start += 1

                    # Reconstruct file with new header
                    new_content = new_header + '\n\n' + '\n'.join(lines[content_start:])
                else:
                    # Add header to beginning
                    new_content = new_header + '\n\n' + content

            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            self.updated_files.append(str(file_path))
            return True

        except Exception as e:
            self.errors.append(f"{file_path}: {str(e)}")
            return False

    def process_directory(self, extensions: List[str] = ['.md', '.py']) -> Dict:
        """Process all files in the project directory."""
        total_files = 0

        for ext in extensions:
            for file_path in self.project_root.rglob(f'*{ext}'):
                # Skip certain directories
                skip_dirs = ['.git', '__pycache__', '.venv', 'node_modules', '.pytest_cache']
                if any(skip_dir in str(file_path) for skip_dir in skip_dirs):
                    continue

                total_files += 1
                self.update_file_header(file_path)

        return {
            'total_files': total_files,
            'updated_files': len(self.updated_files),
            'skipped_files': len(self.skipped_files),
            'errors': len(self.errors)
        }

    def generate_report(self) -> str:
        """Generate a comprehensive update report."""
        stats = self.process_directory()

        report = f"""# ImpressionCore IDS Header Update Report

**Date:** {datetime.datetime.now().strftime("%B-%d-%Y")}
**Status:** Complete

## Summary Statistics
- **Total Files Processed:** {stats['total_files']}
- **Successfully Updated:** {stats['updated_files']}
- **Skipped:** {stats['skipped_files']}
- **Errors:** {stats['errors']}

## Updated Files
{chr(10).join(f'- {file}' for file in self.updated_files[:20])}
{'...' if len(self.updated_files) > 20 else ''}

## Errors
{chr(10).join(f'- {error}' for error in self.errors)}

## Next Steps
1. Verify header formatting
2. Update documentation index
3. Regenerate IDS tags
4. Validate links and references
"""

        return report

if __name__ == "__main__":
    updater = ImpressionCoreIDSHeaderUpdater()
    print("Starting ImpressionCore IDS Header Standardization...")
    print("Processing .md and .py files...")

    report = updater.generate_report()
    print(report)

    # Save report
    report_path = Path("docs/IDS_HEADER_UPDATE_REPORT_2025-07-25.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\\nReport saved to: {report_path}")
