#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #deployment #memory_management #python #source_code #src/scripts/miscellaneous/educational_embedding_scanner.py #testing
**Category:** Source Code
**Status:** Active
"""



import os
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

class EducationalEmbeddingScanner:
    """Scanner specifically for educational embeddings"""

    def __init__(self):
        self.embedding_root = Path("F:/data/embeddings")
        self.educational_keywords = [
            # Core educational terms
            'educational', 'education', 'k12', 'curriculum', 'school', 'learning',
            'student', 'teacher', 'grade', 'standards', 'academic',

            # Specific standards
            'common_core', 'ngss', 'social_studies', 'ela', 'english_language_arts',
            'science_standards', 'math_standards', 'history_standards',

            # Educational levels
            'elementary', 'middle_school', 'high_school', 'kindergarten',
            'first_grade', 'second_grade', 'third_grade', 'fourth_grade',
            'fifth_grade', 'sixth_grade', 'seventh_grade', 'eighth_grade',
            'ninth_grade', 'tenth_grade', 'eleventh_grade', 'twelfth_grade',

            # Subject areas
            'mathematics', 'science', 'reading', 'writing', 'history',
            'geography', 'civics', 'arts', 'music', 'physical_education',

            # Learning concepts
            'lesson', 'homework', 'assignment', 'test', 'quiz', 'exam',
            'textbook', 'workbook', 'worksheet', 'activity'
        ]

    def scan_for_educational_embeddings(self) -> dict:
        """Comprehensive scan for educational embeddings"""
        results = {
            'found_files': [],
            'total_count': 0,
            'total_size_gb': 0,
            'by_keyword': {},
            'by_directory': {}
        }

        console.print("🔍 Scanning for educational embeddings...")

        if not self.embedding_root.exists():
            console.print(f"⚠️ Embedding root not found: {self.embedding_root}")
            return results

        # Initialize keyword tracking
        for keyword in self.educational_keywords:
            results['by_keyword'][keyword] = []

        # Scan all embedding files
        for root, _dirs, files in os.walk(self.embedding_root):
            root_path = Path(root)

            for file in files:
                if file.endswith(('.npy', '.pt', '.safetensors')):
                    filepath = root_path / file
                    file_lower = file.lower()
                    path_lower = str(filepath).lower()

                    # Check if this file matches educational keywords
                    is_educational = False
                    matched_keywords = []

                    for keyword in self.educational_keywords:
                        if keyword in file_lower or keyword in path_lower:
                            is_educational = True
                            matched_keywords.append(keyword)
                            results['by_keyword'][keyword].append(str(filepath))

                    if is_educational:
                        try:
                            size_bytes = filepath.stat().st_size
                            size_gb = size_bytes / (1024**3)

                            file_info = {
                                'path': str(filepath),
                                'name': file,
                                'size_gb': size_gb,
                                'keywords': matched_keywords,
                                'directory': str(root_path.relative_to(self.embedding_root))
                            }

                            results['found_files'].append(file_info)
                            results['total_count'] += 1
                            results['total_size_gb'] += size_gb

                            # Track by directory
                            dir_key = str(root_path.relative_to(self.embedding_root))
                            if dir_key not in results['by_directory']:
                                results['by_directory'][dir_key] = []
                            results['by_directory'][dir_key].append(file_info)

                        except Exception as e:
                            console.print(f"⚠️ Error processing {filepath}: {e}")

        return results

    def display_results(self, results: dict):
        """Display comprehensive educational embedding results"""

        # Summary
        console.print(Panel.fit(
            f"📚 Educational Embedding Scan Results\n"
            f"Found: {results['total_count']} files\n"
            f"Total Size: {results['total_size_gb']:.3f} GB",
            title="Educational Scan Summary",
            style="bold green"
        ))

        if results['total_count'] == 0:
            console.print("⚠️ NO EDUCATIONAL EMBEDDINGS FOUND!")
            console.print("This explains why educational category was skipped.")
            console.print("\n💡 Recommendations:")
            console.print("  1. Check if educational embeddings are in a different location")
            console.print("  2. Verify educational content was properly integrated")
            console.print("  3. Run educational embedding generation if missing")
            return

        # Detailed file listing
        if results['found_files']:
            console.print("\n📋 Educational Embedding Files:")
            table = Table()
            table.add_column("File", style="cyan")
            table.add_column("Directory", style="yellow")
            table.add_column("Size (GB)", justify="right", style="green")
            table.add_column("Keywords", style="blue")

            # Sort by size (largest first)
            sorted_files = sorted(results['found_files'], key=lambda x: x['size_gb'], reverse=True)

            for file_info in sorted_files[:20]:  # Show top 20
                keywords_str = ", ".join(file_info['keywords'][:3])  # First 3 keywords
                if len(file_info['keywords']) > 3:
                    keywords_str += "..."

                table.add_row(
                    file_info['name'],
                    file_info['directory'],
                    f"{file_info['size_gb']:.4f}",
                    keywords_str
                )

            console.print(table)

            if len(results['found_files']) > 20:
                console.print(f"... and {len(results['found_files']) - 20} more files")

        # Directory breakdown
        if results['by_directory']:
            console.print("\n📁 Educational Files by Directory:")
            dir_table = Table()
            dir_table.add_column("Directory", style="cyan")
            dir_table.add_column("Files", justify="right", style="yellow")
            dir_table.add_column("Total Size (GB)", justify="right", style="green")

            for directory, files in results['by_directory'].items():
                total_size = sum(f['size_gb'] for f in files)
                dir_table.add_row(directory, str(len(files)), f"{total_size:.3f}")

            console.print(dir_table)

        # Keyword analysis
        console.print("\n🏷️ Most Common Educational Keywords:")
        keyword_counts = {k: len(v) for k, v in results['by_keyword'].items() if v}
        if keyword_counts:
            sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)

            keyword_table = Table()
            keyword_table.add_column("Keyword", style="cyan")
            keyword_table.add_column("Files", justify="right", style="yellow")

            for keyword, count in sorted_keywords[:10]:  # Top 10
                keyword_table.add_row(keyword, str(count))

            console.print(keyword_table)

def main():
    """Run educational embedding scan"""
    console.print(Panel.fit(
        "🎓 Educational Embedding Scanner\n"
        "Finding ALL Educational Content for Priority Loading",
        title="Educational Scan",
        style="bold blue"
    ))

    scanner = EducationalEmbeddingScanner()
    results = scanner.scan_for_educational_embeddings()
    scanner.display_results(results)

    # Recommendations
    console.print("\n💡 Next Steps:")
    if results['total_count'] > 0:
        console.print("  ✅ Educational embeddings found - updating loader priorities")
        console.print("  🔧 Enhanced memory management will now include educational content")
        console.print("  🚀 Re-run B3 deployment with educational priority protection")
    else:
        console.print("  ⚠️ No educational embeddings found - may need regeneration")
        console.print("  🔍 Check if educational content is in different location")
        console.print("  📚 Consider running educational embedding generation")

if __name__ == "__main__":
    main()
