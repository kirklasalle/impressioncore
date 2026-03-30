"""
Conversation Dataset Preparation for Hybrid GPT-2 + B3 Training

Downloads and prepares high-quality conversation datasets for Path B training.
Uses DailyDialog, PersonaChat, and other sources to create diverse training data.

Target: 50,000+ conversation pairs
Format: {context: str, response: str}
Quality: Filtered for length, coherence, diversity

Created: October 6, 2025
Author: ImpressionCore Team
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Tuple
import random

# Check if datasets library is available
try:
    from datasets import load_dataset
    DATASETS_AVAILABLE = True
except ImportError:
    DATASETS_AVAILABLE = False
    print("⚠️  datasets library not available. Installing...")
    import subprocess
    subprocess.check_call(["pip", "install", "datasets"])
    from datasets import load_dataset
    DATASETS_AVAILABLE = True


class ConversationDatasetPreparer:
    """Prepares conversation datasets for hybrid model training."""

    def __init__(self, output_dir: str = "F:/data/conversations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.conversations = []
        self.stats = {
            'total_pairs': 0,
            'filtered_short': 0,
            'filtered_quality': 0,
            'sources': {}
        }

    def download_dailydialog(self) -> List[Dict[str, str]]:
        """Download and process DailyDialog dataset."""
        print("📥 Downloading DailyDialog dataset...")

        try:
            dataset = load_dataset("daily_dialog", split="train", trust_remote_code=True)
            print(f"✅ DailyDialog loaded: {len(dataset)} dialogues")

            pairs = []
            for dialogue in dataset:
                turns = dialogue['dialog']

                # Create pairs from consecutive turns
                for i in range(len(turns) - 1):
                    context = turns[i].strip()
                    response = turns[i + 1].strip()

                    if self._is_quality_pair(context, response):
                        pairs.append({
                            'context': context,
                            'response': response,
                            'source': 'dailydialog'
                        })

            print(f"✅ Extracted {len(pairs)} pairs from DailyDialog")
            self.stats['sources']['dailydialog'] = len(pairs)
            return pairs

        except Exception as e:
            print(f"⚠️  Failed to load DailyDialog: {e}")
            return []

    def download_personachat(self) -> List[Dict[str, str]]:
        """Download and process PersonaChat dataset."""
        print("📥 Downloading PersonaChat dataset...")

        try:
            dataset = load_dataset("bavard/personachat_truecased", split="train", trust_remote_code=True)
            print(f"✅ PersonaChat loaded: {len(dataset)} dialogues")

            pairs = []
            for item in dataset:
                # PersonaChat has utterances list
                if 'utterances' in item and item['utterances']:
                    history = item['utterances']

                    # Create pairs from consecutive utterances
                    for i in range(len(history) - 1):
                        context = history[i]['history'][-1] if history[i]['history'] else ""
                        response = history[i]['candidates'][0] if history[i]['candidates'] else ""

                        if self._is_quality_pair(context, response):
                            pairs.append({
                                'context': context,
                                'response': response,
                                'source': 'personachat'
                            })

            print(f"✅ Extracted {len(pairs)} pairs from PersonaChat")
            self.stats['sources']['personachat'] = len(pairs)
            return pairs

        except Exception as e:
            print(f"⚠️  Failed to load PersonaChat: {e}")
            return []

    def download_empathetic_dialogues(self) -> List[Dict[str, str]]:
        """Download and process Empathetic Dialogues dataset."""
        print("📥 Downloading Empathetic Dialogues dataset...")

        try:
            dataset = load_dataset("empathetic_dialogues", split="train", trust_remote_code=True)
            print(f"✅ Empathetic Dialogues loaded: {len(dataset)} conversations")

            pairs = []
            current_conv_id = None
            previous_utterance = None

            for item in dataset:
                conv_id = item['conv_id']
                utterance = item['utterance'].strip()

                # New conversation
                if conv_id != current_conv_id:
                    current_conv_id = conv_id
                    previous_utterance = utterance
                    continue

                # Create pair from consecutive turns
                if previous_utterance and self._is_quality_pair(previous_utterance, utterance):
                    pairs.append({
                        'context': previous_utterance,
                        'response': utterance,
                        'source': 'empathetic_dialogues'
                    })

                previous_utterance = utterance

            print(f"✅ Extracted {len(pairs)} pairs from Empathetic Dialogues")
            self.stats['sources']['empathetic_dialogues'] = len(pairs)
            return pairs

        except Exception as e:
            print(f"⚠️  Failed to load Empathetic Dialogues: {e}")
            return []

    def _is_quality_pair(self, context: str, response: str) -> bool:
        """Check if conversation pair meets quality standards."""

        # Length checks (>10 words each)
        context_words = len(context.split())
        response_words = len(response.split())

        if context_words < 3 or response_words < 3:
            self.stats['filtered_short'] += 1
            return False

        # Maximum length (avoid very long responses)
        if context_words > 100 or response_words > 100:
            self.stats['filtered_quality'] += 1
            return False

        # Basic quality checks
        if not context or not response:
            self.stats['filtered_quality'] += 1
            return False

        # Avoid repeated characters (signs of data issues)
        if any(char * 5 in context or char * 5 in response for char in "abcdefghijklmnopqrstuvwxyz"):
            self.stats['filtered_quality'] += 1
            return False

        return True

    def prepare_dataset(self, target_size: int = 50000) -> Tuple[List, List, List]:
        """Prepare complete dataset from multiple sources."""
        print("=" * 60)
        print("🚀 Starting Conversation Dataset Preparation")
        print("=" * 60)
        print(f"Target size: {target_size:,} conversation pairs\n")

        # Download from multiple sources
        all_pairs = []

        # DailyDialog (everyday conversations)
        daily_pairs = self.download_dailydialog()
        all_pairs.extend(daily_pairs)

        # PersonaChat (personality-driven)
        persona_pairs = self.download_personachat()
        all_pairs.extend(persona_pairs)

        # Empathetic Dialogues (emotion-aware)
        empathetic_pairs = self.download_empathetic_dialogues()
        all_pairs.extend(empathetic_pairs)

        print(f"\n📊 Total pairs collected: {len(all_pairs):,}")

        # Shuffle for diversity
        random.shuffle(all_pairs)

        # Limit to target size if needed
        if len(all_pairs) > target_size:
            all_pairs = all_pairs[:target_size]
            print(f"✂️  Limited to target: {len(all_pairs):,} pairs")

        # Split into train/val/test (90/5/5)
        train_size = int(0.90 * len(all_pairs))
        val_size = int(0.05 * len(all_pairs))

        train_data = all_pairs[:train_size]
        val_data = all_pairs[train_size:train_size + val_size]
        test_data = all_pairs[train_size + val_size:]

        print(f"\n📂 Dataset splits:")
        print(f"   Train: {len(train_data):,} pairs (90%)")
        print(f"   Val:   {len(val_data):,} pairs (5%)")
        print(f"   Test:  {len(test_data):,} pairs (5%)")

        # Save datasets
        self._save_dataset(train_data, "train")
        self._save_dataset(val_data, "val")
        self._save_dataset(test_data, "test")

        # Save statistics
        self._save_statistics(len(train_data), len(val_data), len(test_data))

        print("\n" + "=" * 60)
        print("✅ Dataset preparation complete!")
        print("=" * 60)

        return train_data, val_data, test_data

    def _save_dataset(self, data: List[Dict], split: str):
        """Save dataset split to JSON file."""
        output_path = self.output_dir / f"hybrid_training_{split}.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved {split} dataset: {output_path}")

    def _save_statistics(self, train_size: int, val_size: int, test_size: int):
        """Save dataset statistics."""
        stats = {
            'total_pairs': train_size + val_size + test_size,
            'train_size': train_size,
            'val_size': val_size,
            'test_size': test_size,
            'filtered_short': self.stats['filtered_short'],
            'filtered_quality': self.stats['filtered_quality'],
            'sources': self.stats['sources']
        }

        output_path = self.output_dir / "dataset_statistics.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)

        print(f"📊 Saved statistics: {output_path}")
        print(f"\n   Filtered (too short): {stats['filtered_short']:,}")
        print(f"   Filtered (quality): {stats['filtered_quality']:,}")
        print(f"   Sources breakdown:")
        for source, count in stats['sources'].items():
            print(f"      - {source}: {count:,} pairs")


def main():
    """Main execution."""
    print("🔧 Preparing conversation dataset for Hybrid GPT-2 + B3 training\n")

    # Initialize preparer
    preparer = ConversationDatasetPreparer(output_dir="F:/data/conversations")

    # Prepare dataset (target: 50,000 pairs)
    train_data, val_data, test_data = preparer.prepare_dataset(target_size=50000)

    # Sample validation
    print("\n📋 Sample conversation pairs:")
    print("-" * 60)
    for i in range(min(3, len(train_data))):
        pair = train_data[i]
        print(f"\nExample {i+1}:")
        print(f"Context:  {pair['context']}")
        print(f"Response: {pair['response']}")
        print(f"Source:   {pair['source']}")

    print("\n" + "=" * 60)
    print("✅ Ready for training! Dataset files:")
    print(f"   📁 F:/data/conversations/hybrid_training_train.json")
    print(f"   📁 F:/data/conversations/hybrid_training_val.json")
    print(f"   📁 F:/data/conversations/hybrid_training_test.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
