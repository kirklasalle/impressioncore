"""
ImpressionCore B3 Knowledge Source Inventory System

Created: October 04, 2025
Updated: October 04, 2025
Author: Kirk LaSalle; GitHub Copilot
Tags: #rag #knowledge_expansion #embeddings #inventory
Category: Inference
Status: Active

Purpose:
    Comprehensive inventory of ALL knowledge sources available in F:/data.
    Identifies what's already embedded vs what needs generation.
    Creates prioritized queue for embedding generation.

Knowledge Sources:
    - Existing embeddings: 7.2GB across 410,755 files
    - Text: 31GB WikiText, educational corpus, transcriptions
    - Audio: 11.5GB WAV files, 6.5GB TextGrid alignments
    - Vision: 56GB images, 3.3GB models
    - Multimodal: 76,340 batches (3.6GB embeddings already generated!)
    - OpenAI export: 175MB conversational data

Strategic Priority:
    1. IMMEDIATE: Leverage existing 76K multimodal embeddings (3.6GB ready!)
    2. HIGH: Text corpora (31GB WikiText, educational)
    3. MEDIUM: Audio transcriptions (phonemes, alignments)
    4. LOW: Raw audio/video (expensive to embed)
"""

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class KnowledgeSource:
    """Represents a knowledge source with metadata."""
    category: str  # text, audio, vision, multimodal
    subcategory: str  # educational, academic, conversational, etc.
    path: Path
    file_count: int
    total_size_mb: float
    file_types: list[str]
    has_embeddings: bool
    embedding_path: Path = None
    embedding_count: int = 0
    priority: int = 0  # 1=highest, 5=lowest
    notes: str = ""


class B3KnowledgeInventory:
    """
    Comprehensive inventory system for all F:/data knowledge sources.

    Scans existing embeddings, identifies unembedded content, calculates
    priorities based on size, quality, and strategic value.
    """

    def __init__(self, f_data_root: str = "F:/data"):
        """Initialize inventory system."""
        self.f_data_root = Path(f_data_root)
        self.sources: list[KnowledgeSource] = []
        self.existing_embeddings: dict[str, dict] = {}

        logger.info(f"Initializing knowledge inventory for: {self.f_data_root}")

    def scan_existing_embeddings(self) -> dict[str, dict]:
        """
        Scan F:/data/embeddings to catalog what's already embedded.

        Returns:
            Dict mapping category to embedding info (count, size, path)
        """
        embeddings_root = self.f_data_root / "embeddings"
        if not embeddings_root.exists():
            logger.warning(f"Embeddings directory not found: {embeddings_root}")
            return {}

        logger.info("Scanning existing embeddings...")
        embeddings = {}

        # Key embedding directories to check
        key_dirs = [
            "b3_39m_128k/multimodal_batches",  # 76K embeddings (3.6GB) - GOLD MINE!
            "b3_embeddings",  # 13K educational embeddings (248MB)
            "impressioncore_b3/3b",  # B3 training embeddings
            "sentence_transformers/educational",  # Our new 205 embeddings
            "dataset_enhanced",  # 1.2K enhanced embeddings
            "audio/spectrograms",  # Audio embeddings
            "text/tokenized",  # Text embeddings
            "vision/features"  # Vision embeddings
        ]

        for dir_path in key_dirs:
            full_path = embeddings_root / dir_path
            if not full_path.exists():
                continue

            # Count .npy files
            npy_files = list(full_path.rglob("*.npy"))
            if npy_files:
                total_size = sum(f.stat().st_size for f in npy_files) / (1024 * 1024)
                embeddings[dir_path] = {
                    "path": full_path,
                    "count": len(npy_files),
                    "size_mb": round(total_size, 2),
                    "files": [f.name for f in npy_files[:10]]  # Sample
                }
                logger.info(f"  Found: {dir_path} - {len(npy_files)} files ({total_size:.2f} MB)")

        self.existing_embeddings = embeddings
        return embeddings

    def scan_dataset_sources(self) -> list[KnowledgeSource]:
        """
        Scan F:/data/datasets to find unembedded content.

        Returns:
            List of KnowledgeSource objects for unembedded content
        """
        datasets_root = self.f_data_root / "datasets"
        if not datasets_root.exists():
            logger.warning(f"Datasets directory not found: {datasets_root}")
            return []

        logger.info("Scanning dataset sources...")
        sources = []

        # Text sources (HIGH PRIORITY)
        text_dir = datasets_root / "text"
        if text_dir.exists():
            txt_files = list(text_dir.rglob("*.txt"))
            json_files = list(text_dir.rglob("*.json"))
            xml_files = list(text_dir.rglob("*.xml"))

            total_files = len(txt_files) + len(json_files) + len(xml_files)
            total_size = sum(
                f.stat().st_size for f in (txt_files + json_files + xml_files)
            ) / (1024 * 1024)

            sources.append(KnowledgeSource(
                category="text",
                subcategory="general_corpus",
                path=text_dir,
                file_count=total_files,
                total_size_mb=round(total_size, 2),
                file_types=[".txt", ".json", ".xml"],
                has_embeddings=False,
                priority=1,
                notes=f"WikiText-103 + general text corpus. {total_files} files, {total_size:.0f}MB"
            ))
            logger.info(f"  Text corpus: {total_files} files ({total_size:.2f} MB)")

        # Educational sources (HIGH PRIORITY)
        edu_dirs = [
            "educational",
            "educational_corpus",
            "educational_corpus_complete",
            "educational_corpus_enhanced_v2"
        ]

        for edu_name in edu_dirs:
            edu_dir = datasets_root / edu_name
            if edu_dir.exists():
                txt_files = list(edu_dir.rglob("*.txt"))
                json_files = list(edu_dir.rglob("*.json"))

                total_files = len(txt_files) + len(json_files)
                if total_files == 0:
                    continue

                total_size = sum(
                    f.stat().st_size for f in (txt_files + json_files)
                ) / (1024 * 1024)

                sources.append(KnowledgeSource(
                    category="text",
                    subcategory="educational",
                    path=edu_dir,
                    file_count=total_files,
                    total_size_mb=round(total_size, 2),
                    file_types=[".txt", ".json"],
                    has_embeddings=False,
                    priority=1,
                    notes=f"K12 educational content from {edu_name}"
                ))
                logger.info(f"  Educational ({edu_name}): {total_files} files ({total_size:.2f} MB)")

        # Audio transcriptions (MEDIUM PRIORITY)
        audio_dir = datasets_root / "audio"
        if audio_dir.exists():
            textgrid_files = list(audio_dir.rglob("*.TextGrid"))
            txt_files = list(audio_dir.rglob("*.txt"))

            total_files = len(textgrid_files) + len(txt_files)
            total_size = sum(
                f.stat().st_size for f in (textgrid_files + txt_files)
            ) / (1024 * 1024)

            if total_files > 0:
                sources.append(KnowledgeSource(
                    category="audio",
                    subcategory="transcriptions",
                    path=audio_dir,
                    file_count=total_files,
                    file_types=[".TextGrid", ".txt"],
                    total_size_mb=round(total_size, 2),
                    has_embeddings=False,
                    priority=2,
                    notes=f"Phoneme alignments and transcriptions. {total_files} files"
                ))
                logger.info(f"  Audio transcriptions: {total_files} files ({total_size:.2f} MB)")

        # OpenAI conversation export (HIGH PRIORITY - conversational data!)
        openai_dir = datasets_root / "OpenAI-DataExport_Kirk_LaSalle"
        if openai_dir.exists():
            json_files = list(openai_dir.rglob("*.json"))
            txt_files = list(openai_dir.rglob("*.txt"))

            total_files = len(json_files) + len(txt_files)
            total_size = sum(
                f.stat().st_size for f in (json_files + txt_files)
            ) / (1024 * 1024)

            if total_files > 0:
                sources.append(KnowledgeSource(
                    category="text",
                    subcategory="conversational",
                    path=openai_dir,
                    file_count=total_files,
                    total_size_mb=round(total_size, 2),
                    file_types=[".json", ".txt"],
                    has_embeddings=False,
                    priority=1,
                    notes="OpenAI conversation history - high-quality conversational data!"
                ))
                logger.info(f"  OpenAI conversations: {total_files} files ({total_size:.2f} MB)")

        # Multimodal dataset
        multimodal_dir = datasets_root / "multimodal"
        if multimodal_dir.exists():
            jpg_files = list(multimodal_dir.rglob("*.jpg"))
            json_files = list(multimodal_dir.rglob("*.json"))

            total_files = len(jpg_files) + len(json_files)
            total_size = sum(
                f.stat().st_size for f in (jpg_files + json_files)
            ) / (1024 * 1024)

            # Check if embeddings already exist
            has_embeddings = "b3_39m_128k/multimodal_batches" in self.existing_embeddings

            if total_files > 0:
                sources.append(KnowledgeSource(
                    category="multimodal",
                    subcategory="image_captions",
                    path=multimodal_dir,
                    file_count=total_files,
                    total_size_mb=round(total_size, 2),
                    file_types=[".jpg", ".json"],
                    has_embeddings=has_embeddings,
                    embedding_path=self.f_data_root / "embeddings/b3_39m_128k/multimodal_batches" if has_embeddings else None,
                    embedding_count=76340 if has_embeddings else 0,
                    priority=1 if has_embeddings else 3,
                    notes="✅ 76K embeddings READY!" if has_embeddings else "Needs embedding generation"
                ))
                logger.info(f"  Multimodal: {total_files} files ({total_size:.2f} MB) - {'EMBEDDED ✅' if has_embeddings else 'Not embedded'}")

        self.sources = sources
        return sources

    def create_generation_plan(self) -> dict:
        """
        Create prioritized embedding generation plan.

        Returns:
            Dict with generation priorities and estimated counts
        """
        plan = {
            "immediate_high_value": [],  # Already embedded, just need to load
            "priority_1_high_impact": [],  # Text corpora, educational, conversational
            "priority_2_medium_impact": [],  # Audio transcriptions
            "priority_3_future": [],  # Raw audio/video
            "total_estimated_embeddings": 0
        }

        # Immediate: Leverage existing multimodal embeddings
        if "b3_39m_128k/multimodal_batches" in self.existing_embeddings:
            embed_info = self.existing_embeddings["b3_39m_128k/multimodal_batches"]
            plan["immediate_high_value"].append({
                "source": "Multimodal batches (READY)",
                "path": str(embed_info["path"]),
                "embedding_count": embed_info["count"],
                "size_mb": embed_info["size_mb"],
                "action": "Load existing embeddings into RAG system",
                "estimated_time": "5 minutes",
                "value": "CRITICAL - 76K multimodal embeddings ready to use!"
            })
            plan["total_estimated_embeddings"] += 76340

        # Priority 1: High-value text sources
        for source in self.sources:
            if source.priority == 1 and not source.has_embeddings:
                # Estimate embeddings based on file size (rough: 1MB text = ~500 embeddings)
                estimated_count = int(source.total_size_mb * 500)

                plan["priority_1_high_impact"].append({
                    "source": f"{source.category}/{source.subcategory}",
                    "path": str(source.path),
                    "file_count": source.file_count,
                    "size_mb": source.total_size_mb,
                    "estimated_embeddings": estimated_count,
                    "notes": source.notes
                })
                plan["total_estimated_embeddings"] += estimated_count

        # Priority 2: Medium-value sources
        for source in self.sources:
            if source.priority == 2 and not source.has_embeddings:
                estimated_count = int(source.total_size_mb * 200)  # Transcriptions less dense

                plan["priority_2_medium_impact"].append({
                    "source": f"{source.category}/{source.subcategory}",
                    "path": str(source.path),
                    "file_count": source.file_count,
                    "size_mb": source.total_size_mb,
                    "estimated_embeddings": estimated_count,
                    "notes": source.notes
                })
                plan["total_estimated_embeddings"] += estimated_count

        return plan

    def save_inventory(self, output_path: str = "knowledge_inventory.json"):
        """Save complete inventory to JSON."""
        inventory = {
            "scan_timestamp": str(Path.cwd()),
            "existing_embeddings": {
                k: {**v, "path": str(v["path"])} for k, v in self.existing_embeddings.items()
            },
            "knowledge_sources": [asdict(s) for s in self.sources],
            "generation_plan": self.create_generation_plan()
        }

        # Convert Path objects to strings
        for source in inventory["knowledge_sources"]:
            source["path"] = str(source["path"])
            if source["embedding_path"]:
                source["embedding_path"] = str(source["embedding_path"])

        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(inventory, f, indent=2)

        logger.info(f"Inventory saved to: {output_file}")
        return output_file

    def print_summary(self):
        """Print human-readable inventory summary."""
        print("\n" + "="*80)
        print("IMPRESSIONCORE B3 KNOWLEDGE INVENTORY")
        print("="*80)

        # Existing embeddings
        print(f"\n📊 EXISTING EMBEDDINGS ({len(self.existing_embeddings)} categories):")
        total_existing_size = 0
        total_existing_count = 0
        for name, info in sorted(self.existing_embeddings.items(), key=lambda x: x[1]["size_mb"], reverse=True):
            print(f"  ✅ {name}")
            print(f"     Files: {info['count']:,} | Size: {info['size_mb']:.2f} MB")
            total_existing_size += info["size_mb"]
            total_existing_count += info["count"]

        print(f"\n  TOTAL: {total_existing_count:,} embedding files, {total_existing_size:.2f} MB")

        # Knowledge sources
        print(f"\n📚 KNOWLEDGE SOURCES ({len(self.sources)} sources identified):")
        for source in sorted(self.sources, key=lambda x: (x.priority, -x.total_size_mb)):
            status = "✅ EMBEDDED" if source.has_embeddings else "⏳ Needs Generation"
            print(f"\n  Priority {source.priority} | {status}")
            print(f"  Category: {source.category}/{source.subcategory}")
            print(f"  Path: {source.path}")
            print(f"  Files: {source.file_count:,} | Size: {source.total_size_mb:.2f} MB")
            print(f"  Notes: {source.notes}")

        # Generation plan
        plan = self.create_generation_plan()
        print("\n" + "="*80)
        print("🚀 EMBEDDING GENERATION PLAN")
        print("="*80)

        print(f"\n⚡ IMMEDIATE HIGH-VALUE ({len(plan['immediate_high_value'])} sources):")
        for item in plan["immediate_high_value"]:
            print(f"  ✅ {item['source']}")
            print(f"     Embeddings: {item['embedding_count']:,} READY")
            print(f"     Action: {item['action']}")
            print(f"     Value: {item['value']}")

        print(f"\n🎯 PRIORITY 1 - HIGH IMPACT ({len(plan['priority_1_high_impact'])} sources):")
        for item in plan["priority_1_high_impact"]:
            print(f"  • {item['source']}")
            print(f"     Files: {item['file_count']:,} | Size: {item['size_mb']:.2f} MB")
            print(f"     Estimated embeddings: {item['estimated_embeddings']:,}")

        print(f"\n🔶 PRIORITY 2 - MEDIUM IMPACT ({len(plan['priority_2_medium_impact'])} sources):")
        for item in plan["priority_2_medium_impact"]:
            print(f"  • {item['source']}")
            print(f"     Estimated embeddings: {item['estimated_embeddings']:,}")

        print(f"\n📈 TOTAL ESTIMATED EMBEDDINGS: {plan['total_estimated_embeddings']:,}")
        print("="*80 + "\n")


def main():
    """Run comprehensive knowledge inventory."""
    print("Starting ImpressionCore B3 Knowledge Inventory...")

    # Initialize inventory system
    inventory = B3KnowledgeInventory(f_data_root="F:/data")

    # Scan existing embeddings
    inventory.scan_existing_embeddings()

    # Scan dataset sources
    inventory.scan_dataset_sources()

    # Print summary
    inventory.print_summary()

    # Save to JSON
    output_file = inventory.save_inventory("knowledge_inventory.json")

    print(f"\n✅ Inventory complete! Saved to: {output_file}")
    print("\nNext steps:")
    print("1. Load existing 76K multimodal embeddings (IMMEDIATE)")
    print("2. Generate embeddings for text corpora (HIGH PRIORITY)")
    print("3. Generate embeddings for educational content (HIGH PRIORITY)")
    print("4. Generate embeddings for conversational data (HIGH PRIORITY)")


if __name__ == "__main__":
    main()
