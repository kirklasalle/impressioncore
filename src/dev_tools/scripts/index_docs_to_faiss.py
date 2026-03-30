"""
Index Documentation to FAISS for Semantic Search

This script indexes all markdown documentation from docs/ into the FAISS
vector database, enabling semantic search through IDS.

Created: January 18, 2026
Author: Agent0 (SAL)
"""
import sys
from pathlib import Path

# Add project roots
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


def extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter or markdown header metadata."""
    metadata = {}
    lines = content.split('\n')

    # Check for YAML frontmatter
    if lines[0].strip() == '---':
        for _i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                break
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip().lower()] = value.strip()

    # Check for markdown header (Created:, Updated:, etc.)
    for line in lines[:20]:
        if line.startswith('**Created:**'):
            metadata['created'] = line.replace('**Created:**', '').strip()
        elif line.startswith('**Updated:**'):
            metadata['updated'] = line.replace('**Updated:**', '').strip()
        elif line.startswith('**Tags:**'):
            metadata['tags'] = line.replace('**Tags:**', '').strip()
        elif line.startswith('**Category:**'):
            metadata['category'] = line.replace('**Category:**', '').strip()
        elif line.startswith('# '):
            metadata['title'] = line.replace('# ', '').strip()

    return metadata


def get_content_excerpt(content: str, max_chars: int = 500) -> str:
    """Get a meaningful excerpt from the document content."""
    lines = content.split('\n')

    # Skip frontmatter/header
    start_idx = 0
    in_frontmatter = False
    for i, line in enumerate(lines):
        if i == 0 and line.strip() == '---':
            in_frontmatter = True
            continue
        if in_frontmatter and line.strip() == '---':
            start_idx = i + 1
            break
        if line.startswith('---'):
            start_idx = i + 1
            break

    # Get content after headers
    content_lines = []
    for line in lines[start_idx:]:
        # Skip empty lines and metadata
        if not line.strip():
            continue
        if line.startswith('**') and ':**' in line:
            continue
        content_lines.append(line)
        if len(' '.join(content_lines)) > max_chars:
            break

    return ' '.join(content_lines)[:max_chars]


def main():
    try:
        from src.orchestrator.vector_connector import VectorMemoryConnector

        print("=== IDS Documentation Indexing to FAISS ===\n")

        docs_dir = project_root / "docs"
        connector = VectorMemoryConnector()

        # Find all markdown files
        md_files = list(docs_dir.rglob("*.md"))
        print(f"Found {len(md_files)} markdown files to index\n")

        indexed = 0
        skipped = 0

        for md_file in md_files:
            try:
                # Skip resolved versions and archives
                if '.resolved' in md_file.name:
                    skipped += 1
                    continue
                if 'archive' in str(md_file).lower():
                    skipped += 1
                    continue

                content = md_file.read_text(encoding='utf-8', errors='ignore')

                # Extract metadata
                metadata = extract_frontmatter(content)
                excerpt = get_content_excerpt(content)

                # Create searchable text
                rel_path = md_file.relative_to(docs_dir)
                title = metadata.get('title', md_file.stem.replace('_', ' ').title())

                searchable_text = f"Document: {title}\nPath: {rel_path}\n"
                if metadata.get('tags'):
                    searchable_text += f"Tags: {metadata['tags']}\n"
                if metadata.get('category'):
                    searchable_text += f"Category: {metadata['category']}\n"
                searchable_text += f"Content: {excerpt}"

                # Add to FAISS
                connector.add_memory(
                    text=searchable_text,
                    metadata={
                        "type": "documentation",
                        "file_path": str(rel_path),
                        "title": title,
                        "tags": metadata.get('tags', ''),
                        "category": metadata.get('category', ''),
                        "source": "index_docs_to_faiss.py"
                    }
                )
                indexed += 1

                if indexed % 50 == 0:
                    print(f"  Indexed {indexed} documents...")

            except Exception as e:
                print(f"  ERROR: {md_file.name}: {e}")
                skipped += 1

        print("\n=== Indexing Complete ===")
        print(f"Indexed: {indexed}")
        print(f"Skipped: {skipped}")
        print(f"Index path: {connector.index_path}")

        # Verification
        print("\n=== Verification Search ===")
        results = connector.search("Prime Directive governance laws", top_k=3)
        if results:
            print("SUCCESS: Semantic search is working!")
            for r in results[:3]:
                meta = r.get('metadata', {})
                print(f"  - {meta.get('title', 'N/A')}: {meta.get('file_path', 'N/A')}")
        else:
            print("WARNING: Search returned no results.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
