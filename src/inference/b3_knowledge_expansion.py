"""
ImpressionCore B3 Knowledge Base Expansion System

Created: October 04, 2025
Updated: October 04, 2025
Author: Kirk LaSalle; GitHub Copilot
Tags: #rag #knowledge_expansion #embeddings #multimodal
Category: Inference
Status: Active

Purpose:
    Comprehensive knowledge base expansion for ImpressionCore B3 RAG system.

    Phase 1: Load existing 76K multimodal embeddings (IMMEDIATE)
    Phase 2: Generate embeddings for text corpora (HIGH PRIORITY)
    Phase 3: Generate embeddings for educational content
    Phase 4: Generate embeddings for conversational data

Strategic Approach:
    "Intelligence scales with knowledge" - More embeddings = Better AI
    Target: 100K+ embeddings across text/image/audio modalities

Knowledge Sources:
    ✅ READY: 76,340 multimodal embeddings (3.6GB) - LOAD IMMEDIATELY
    📚 Text: 33GB WikiText-103 corpus (~16M potential embeddings)
    🎓 Educational: 31MB K12 content (~15K potential embeddings)
    💬 Conversational: 99MB OpenAI history (~50K potential embeddings)
    🎤 Audio: 6.5GB transcriptions (~1.3M potential embeddings)
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import RAG infrastructure
try:
    from b3_rag_infrastructure import B3EmbeddingSearcher
    logger.info("✅ Loaded B3EmbeddingSearcher")
except ImportError:
    logger.error("❌ Failed to import B3EmbeddingSearcher")
    raise

# Import sentence-transformers for generation
try:
    from sentence_transformers import SentenceTransformer
    logger.info("✅ sentence-transformers available")
except ImportError:
    logger.error("❌ sentence-transformers not available")
    raise


@dataclass
class ExpansionPhase:
    """Represents a knowledge expansion phase."""
    name: str
    priority: int
    source_path: Path
    target_embeddings: int
    estimated_time_minutes: int
    description: str
    completed: bool = False


class B3KnowledgeExpansion:
    """
    Comprehensive knowledge base expansion system.

    Implements multi-phase strategy:
    1. Load existing multimodal embeddings (76K vectors)
    2. Generate text corpus embeddings (WikiText-103)
    3. Generate educational embeddings (K12 content)
    4. Generate conversational embeddings (OpenAI history)
    """

    def __init__(
        self,
        f_data_root: str = "F:/data",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialize knowledge expansion system.

        Args:
            f_data_root: Root directory for F:/data
            model_name: Sentence transformer model for embedding generation
        """
        self.f_data_root = Path(f_data_root)
        self.model_name = model_name

        # Initialize RAG searcher
        self.searcher = B3EmbeddingSearcher(
            f_data_root=str(self.f_data_root),
            use_sentence_transformers=True
        )

        # Load embedding model for generation
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info(f"✅ Model loaded: {self.model.get_sentence_embedding_dimension()}-dim")

        # Define expansion phases
        self.phases = self._define_expansion_phases()

        logger.info("🚀 B3KnowledgeExpansion initialized")

    def _define_expansion_phases(self) -> list[ExpansionPhase]:
        """Define knowledge expansion phases with priorities."""
        return [
            ExpansionPhase(
                name="Load Multimodal Embeddings",
                priority=1,
                source_path=self.f_data_root / "embeddings/b3_39m_128k/multimodal_batches",
                target_embeddings=76340,
                estimated_time_minutes=5,
                description="Load existing 76K multimodal embeddings - IMMEDIATE VALUE!"
            ),
            ExpansionPhase(
                name="Generate Educational Embeddings",
                priority=2,
                source_path=self.f_data_root / "datasets/educational",
                target_embeddings=15000,
                estimated_time_minutes=10,
                description="K12 educational content - high-quality, structured knowledge"
            ),
            ExpansionPhase(
                name="Generate Conversational Embeddings",
                priority=3,
                source_path=self.f_data_root / "datasets/OpenAI-DataExport_Kirk_LaSalle",
                target_embeddings=50000,
                estimated_time_minutes=15,
                description="OpenAI conversation history - natural dialogue patterns"
            ),
            ExpansionPhase(
                name="Generate Text Corpus Embeddings (Sample)",
                priority=4,
                source_path=self.f_data_root / "datasets/text",
                target_embeddings=10000,
                estimated_time_minutes=30,
                description="WikiText-103 sample - general knowledge (full corpus too large)"
            )
        ]

    def execute_phase_1_load_multimodal(self) -> bool:
        """
        Phase 1: Load existing 76K multimodal embeddings.

        CRITICAL: These embeddings are ALREADY GENERATED!
        Just need to load them into RAG system.

        Returns:
            True if successful
        """
        logger.info("\n" + "="*80)
        logger.info("PHASE 1: LOAD MULTIMODAL EMBEDDINGS")
        logger.info("="*80)
        logger.info("🎯 Target: Load 76,340 existing embeddings")
        logger.info("⏱️  Estimated time: 5 minutes")
        logger.info("")

        try:
            success = self.searcher.load_multimodal_embeddings()

            if success:
                logger.info("\n✅ PHASE 1 COMPLETE!")
                logger.info(f"   Loaded: {len(self.searcher.embeddings.get('multimodal', [])):,} embeddings")
                logger.info(f"   Dimension: {self.searcher.embeddings['multimodal'].shape[1]}")
                logger.info(f"   Memory: {self.searcher.embeddings['multimodal'].nbytes / (1024**2):.2f} MB")
                self.phases[0].completed = True
                return True
            else:
                logger.error("❌ PHASE 1 FAILED - Multimodal embeddings not loaded")
                return False

        except Exception as e:
            logger.error(f"❌ PHASE 1 ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

    def execute_phase_2_educational(self) -> bool:
        """
        Phase 2: Generate embeddings for educational content.

        Sources:
        - F:/data/datasets/educational/ (4,711 files, 23MB)
        - F:/data/datasets/educational_corpus_complete/ (69 files, 8MB)
        - F:/data/datasets/educational_corpus_enhanced_v2/ (34 files, 0.8MB)

        Returns:
            True if successful
        """
        logger.info("\n" + "="*80)
        logger.info("PHASE 2: GENERATE EDUCATIONAL EMBEDDINGS")
        logger.info("="*80)
        logger.info("🎯 Target: Generate ~15,000 educational embeddings")
        logger.info("⏱️  Estimated time: 10 minutes")
        logger.info("")

        try:
            # Load educational text files
            edu_paths = [
                self.f_data_root / "datasets/educational",
                self.f_data_root / "datasets/educational_corpus_complete",
                self.f_data_root / "datasets/educational_corpus_enhanced_v2"
            ]

            texts = []
            metadata = []

            for edu_path in edu_paths:
                if not edu_path.exists():
                    continue

                logger.info(f"Scanning: {edu_path.name}")

                # Load .txt files
                for txt_file in edu_path.rglob("*.txt"):
                    try:
                        with open(txt_file, encoding='utf-8', errors='ignore') as f:
                            content = f.read().strip()
                            if len(content) > 50:  # Skip tiny files
                                texts.append(content)
                                metadata.append({
                                    "source": txt_file.name,
                                    "category": "educational",
                                    "subcategory": edu_path.name
                                })
                    except Exception as e:
                        logger.warning(f"Failed to load {txt_file.name}: {e}")

                # Load .json files
                for json_file in edu_path.rglob("*.json"):
                    try:
                        with open(json_file, encoding='utf-8') as f:
                            data = json.load(f)
                            # Extract text content
                            if isinstance(data, dict):
                                text_content = data.get('text', '') or data.get('content', '')
                                if text_content and len(text_content) > 50:
                                    texts.append(text_content)
                                    metadata.append({
                                        "source": json_file.name,
                                        "category": "educational",
                                        "subcategory": edu_path.name
                                    })
                            elif isinstance(data, list):
                                for item in data:
                                    if isinstance(item, dict):
                                        text_content = item.get('text', '') or item.get('content', '')
                                        if text_content and len(text_content) > 50:
                                            texts.append(text_content)
                                            metadata.append({
                                                "source": json_file.name,
                                                "category": "educational",
                                                "subcategory": edu_path.name
                                            })
                    except Exception as e:
                        logger.warning(f"Failed to load {json_file.name}: {e}")

            logger.info(f"\n📚 Loaded {len(texts)} educational texts")

            if not texts:
                logger.warning("⚠️ No educational texts found")
                return False

            # Generate embeddings
            logger.info("🔄 Generating embeddings...")
            embeddings = self.model.encode(
                texts,
                batch_size=32,
                show_progress_bar=True,
                normalize_embeddings=True
            )

            # Save embeddings
            output_dir = self.f_data_root / "embeddings/sentence_transformers/educational_expanded"
            output_dir.mkdir(parents=True, exist_ok=True)

            np.save(output_dir / "embeddings.npy", embeddings)

            # Save metadata
            with open(output_dir / "metadata.json", 'w', encoding='utf-8') as f:
                json.dump({
                    "count": len(embeddings),
                    "dimension": embeddings.shape[1],
                    "model": self.model_name,
                    "texts": metadata
                }, f, indent=2)

            # Save mapping
            mapping = {i: meta["source"] for i, meta in enumerate(metadata)}
            with open(output_dir / "mapping.json", 'w', encoding='utf-8') as f:
                json.dump(mapping, f, indent=2)

            logger.info("\n✅ PHASE 2 COMPLETE!")
            logger.info(f"   Generated: {len(embeddings):,} embeddings")
            logger.info(f"   Saved to: {output_dir}")

            self.phases[1].completed = True
            return True

        except Exception as e:
            logger.error(f"❌ PHASE 2 ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

    def execute_phase_3_conversational(self) -> bool:
        """
        Phase 3: Generate embeddings for OpenAI conversation history.

        High-value conversational data for natural dialogue patterns.

        Returns:
            True if successful
        """
        logger.info("\n" + "="*80)
        logger.info("PHASE 3: GENERATE CONVERSATIONAL EMBEDDINGS")
        logger.info("="*80)
        logger.info("🎯 Target: Generate ~50,000 conversational embeddings")
        logger.info("⏱️  Estimated time: 15 minutes")
        logger.info("")

        try:
            openai_path = self.f_data_root / "datasets/OpenAI-DataExport_Kirk_LaSalle"

            if not openai_path.exists():
                logger.warning(f"⚠️ OpenAI export not found: {openai_path}")
                return False

            texts = []
            metadata = []

            # Load JSON conversation files
            for json_file in openai_path.rglob("*.json"):
                try:
                    with open(json_file, encoding='utf-8') as f:
                        data = json.load(f)

                        # Extract conversations
                        if isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict):
                                    # Try different conversation formats
                                    message = item.get('message', '') or item.get('text', '') or item.get('content', '')
                                    if message and len(message) > 20:
                                        texts.append(message)
                                        metadata.append({
                                            "source": json_file.name,
                                            "category": "conversational",
                                            "role": item.get('role', 'unknown')
                                        })
                        elif isinstance(data, dict):
                            # Single conversation
                            message = data.get('message', '') or data.get('text', '') or data.get('content', '')
                            if message and len(message) > 20:
                                texts.append(message)
                                metadata.append({
                                    "source": json_file.name,
                                    "category": "conversational",
                                    "role": data.get('role', 'unknown')
                                })

                except Exception as e:
                    logger.warning(f"Failed to load {json_file.name}: {e}")

            # Load .txt files
            for txt_file in openai_path.rglob("*.txt"):
                try:
                    with open(txt_file, encoding='utf-8', errors='ignore') as f:
                        content = f.read().strip()
                        # Split into conversation chunks (simple approach)
                        chunks = [c.strip() for c in content.split('\n\n') if len(c.strip()) > 20]
                        texts.extend(chunks)
                        metadata.extend([{
                            "source": txt_file.name,
                            "category": "conversational",
                            "role": "mixed"
                        }] * len(chunks))
                except Exception as e:
                    logger.warning(f"Failed to load {txt_file.name}: {e}")

            logger.info(f"\n💬 Loaded {len(texts)} conversational texts")

            if not texts:
                logger.warning("⚠️ No conversational texts found")
                return False

            # Generate embeddings
            logger.info("🔄 Generating embeddings...")
            embeddings = self.model.encode(
                texts,
                batch_size=32,
                show_progress_bar=True,
                normalize_embeddings=True
            )

            # Save embeddings
            output_dir = self.f_data_root / "embeddings/sentence_transformers/conversational"
            output_dir.mkdir(parents=True, exist_ok=True)

            np.save(output_dir / "embeddings.npy", embeddings)

            # Save metadata
            with open(output_dir / "metadata.json", 'w', encoding='utf-8') as f:
                json.dump({
                    "count": len(embeddings),
                    "dimension": embeddings.shape[1],
                    "model": self.model_name,
                    "texts": metadata
                }, f, indent=2)

            # Save mapping
            mapping = {i: meta["source"] for i, meta in enumerate(metadata)}
            with open(output_dir / "mapping.json", 'w', encoding='utf-8') as f:
                json.dump(mapping, f, indent=2)

            logger.info("\n✅ PHASE 3 COMPLETE!")
            logger.info(f"   Generated: {len(embeddings):,} embeddings")
            logger.info(f"   Saved to: {output_dir}")

            self.phases[2].completed = True
            return True

        except Exception as e:
            logger.error(f"❌ PHASE 3 ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

    def execute_all_phases(self):
        """Execute all expansion phases in priority order."""
        logger.info("\n" + "="*80)
        logger.info("🚀 IMPRESSIONCORE B3 KNOWLEDGE BASE EXPANSION")
        logger.info("="*80)
        logger.info("\nStarting comprehensive knowledge expansion...")
        logger.info(f"Total phases: {len(self.phases)}")
        logger.info("")

        results = []

        for i, phase in enumerate(self.phases, 1):
            logger.info(f"\n{'='*80}")
            logger.info(f"STARTING PHASE {i}/{len(self.phases)}: {phase.name}")
            logger.info(f"{'='*80}")

            if i == 1:
                success = self.execute_phase_1_load_multimodal()
            elif i == 2:
                success = self.execute_phase_2_educational()
            elif i == 3:
                success = self.execute_phase_3_conversational()
            else:
                logger.info("⏭️  Skipping additional phases for now")
                success = False

            results.append((phase.name, success))

        # Summary
        logger.info("\n" + "="*80)
        logger.info("📊 EXPANSION SUMMARY")
        logger.info("="*80)

        for phase_name, success in results:
            status = "✅ SUCCESS" if success else "❌ FAILED"
            logger.info(f"{status}: {phase_name}")

        total_success = sum(1 for _, s in results if s)
        logger.info(f"\nCompleted: {total_success}/{len(results)} phases")

        # Calculate total embeddings
        total_embeddings = 0
        if "multimodal" in self.searcher.embeddings:
            total_embeddings += len(self.searcher.embeddings["multimodal"])

        logger.info(f"\n🎯 TOTAL KNOWLEDGE BASE SIZE: {total_embeddings:,} embeddings")
        logger.info("="*80 + "\n")


def main():
    """Run knowledge base expansion."""
    print("ImpressionCore B3 Knowledge Base Expansion System")
    print("="*80)

    # Initialize expansion system
    expansion = B3KnowledgeExpansion(
        f_data_root="F:/data",
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Execute all phases
    expansion.execute_all_phases()

    print("\n✅ Knowledge base expansion complete!")


if __name__ == "__main__":
    main()
