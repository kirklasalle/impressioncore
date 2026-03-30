"""
Initialize FAISS Vector Index for Agent0Core Memory

This script pre-creates and seeds the FAISS index so that
semantic memory recall works correctly.
"""
import sys
from pathlib import Path

# Add project roots
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def main():
    try:
        from src.orchestrator.vector_connector import VectorMemoryConnector

        print("=== FAISS Vector Index Initialization ===\n")

        # 1. Initialize connector (this creates the db directory)
        connector = VectorMemoryConnector()

        # 2. Seed with foundational knowledge
        seed_data = [
            {
                "text": "The Kinect color stream is connected to MJPEG Stream ID 98. Depth is 105, IR is 106.",
                "type": "system_config",
            },
            {
                "text": "ImpressionCore uses the Unified Triad (Left Hemisphere, Right Hemisphere, Colossus) for cognitive processing.",
                "type": "architecture",
            },
            {
                "text": "Agent0Core is governed by the Prime Directive: 7 laws for intelligent systems including Stability, Hardware, and Truth.",
                "type": "governance",
            },
            {
                "text": "The Intelligent Documentation System (IDS) indexes project files and provides semantic search over documentation.",
                "type": "system_info",
            },
            {
                "text": "The VectorMemoryConnector uses all-MiniLM-L6-v2 sentence transformer for semantic embeddings.",
                "type": "technical",
            },
        ]

        print(f"Seeding {len(seed_data)} foundational memories...\n")

        for i, item in enumerate(seed_data, 1):
            connector.add_memory(
                text=item["text"],
                metadata={"type": item["type"], "source": "init_vector_index.py"}
            )
            print(f"  [{i}/{len(seed_data)}] {item['type']}: {item['text'][:50]}...")

        print("\n=== Initialization Complete ===")
        print(f"Index path: {connector.index_path}")

        # 3. Verify by searching
        print("\n=== Verification Search ===")
        results = connector.search("Kinect stream ID", top_k=2)
        if results:
            print("SUCCESS: Index is searchable!")
            for r in results:
                print(f"  - {r.get('text', 'N/A')[:60]}...")
        else:
            print("WARNING: Search returned no results. Index may be empty.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
