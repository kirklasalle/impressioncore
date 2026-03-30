"""
Create mixed Q&A + Conversation dataset for balanced training.

Mix: 70% Q&A (SQuAD + ELI5) + 30% Conversation (DailyDialog)
This balances instruction-following with conversational ability.

Created: October 8, 2025
Author: Kirk LaSalle; GitHub Copilot
"""

import argparse
import json
import random
from pathlib import Path
from typing import List, Dict
from collections import Counter

# Input paths
SQUAD_DIR = Path("F:/data/qa_datasets/squad")
ELI5_DIR = Path("F:/data/qa_datasets/eli5")
CONVERSATION_DIR = Path("F:/data/conversations")

# Output paths
OUTPUT_DIR = Path("F:/data/qa_datasets/mixed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(file_path: Path) -> List[Dict]:
    """Load JSON dataset."""
    print(f"📥 Loading {file_path.name}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"   ✅ Loaded {len(data)} examples")
    return data


def convert_to_unified_format(examples: List[Dict], source: str) -> List[Dict]:
    """
    Convert different formats to unified Q&A format.

    Unified format:
    {
        'question': str,
        'answer': str,
        'source': str,  # 'squad', 'eli5', 'conversation'
        'type': str     # 'factual', 'explanation', 'conversation'
    }
    """
    unified = []

    for example in examples:
        # Determine type based on source and content
        if source == 'squad':
            entry = {
                'question': example['question'],
                'answer': example['answer'],
                'source': 'squad',
                'type': 'factual'
            }
        elif source == 'eli5':
            entry = {
                'question': example['question'],
                'answer': example['answer'],
                'source': 'eli5',
                'type': 'explanation'
            }
        elif source == 'conversation':
            # DailyDialog format
            if 'question' in example and 'answer' in example:
                entry = {
                    'question': example['question'],
                    'answer': example['answer'],
                    'source': 'dailydialog',
                    'type': 'conversation'
                }
            else:
                continue  # Skip malformed entries
        else:
            continue

        unified.append(entry)

    return unified


def create_mixed_dataset(
    squad_data: List[Dict],
    eli5_data: List[Dict],
    conversation_data: List[Dict],
    target_size: int = 50000,
    qa_ratio: float = 0.70
) -> List[Dict]:
    """
    Create mixed dataset with specified ratio.

    Args:
        squad_data: SQuAD Q&A pairs
        eli5_data: ELI5 Q&A pairs
        conversation_data: Conversation pairs
        target_size: Total dataset size
        qa_ratio: Ratio of Q&A data (e.g., 0.70 = 70% Q&A, 30% conversation)

    Returns:
        Mixed dataset
    """
    print(f"\n🔀 Creating mixed dataset...")
    print(f"   Target size: {target_size}")
    print(f"   Q&A ratio: {qa_ratio*100:.0f}% ({int(target_size*qa_ratio)} pairs)")
    print(f"   Conversation ratio: {(1-qa_ratio)*100:.0f}% ({int(target_size*(1-qa_ratio))} pairs)")

    # Calculate target counts
    qa_count = int(target_size * qa_ratio)
    conversation_count = target_size - qa_count

    # Split Q&A between SQuAD and ELI5 (50/50)
    squad_count = qa_count // 2
    eli5_count = qa_count - squad_count

    print(f"\n   Breakdown:")
    print(f"   - SQuAD (factual): {squad_count} pairs")
    print(f"   - ELI5 (explanatory): {eli5_count} pairs")
    print(f"   - DailyDialog (conversation): {conversation_count} pairs")

    # Sample from each dataset
    random.shuffle(squad_data)
    random.shuffle(eli5_data)
    random.shuffle(conversation_data)

    squad_sample = squad_data[:squad_count]
    eli5_sample = eli5_data[:eli5_count]
    conversation_sample = conversation_data[:conversation_count]

    # Combine and shuffle
    mixed = squad_sample + eli5_sample + conversation_sample
    random.shuffle(mixed)

    print(f"\n   ✅ Created mixed dataset with {len(mixed)} pairs")

    return mixed


def analyze_dataset(data: List[Dict]) -> None:
    """Print dataset statistics."""
    print("\n" + "=" * 70)
    print("📊 DATASET ANALYSIS")
    print("=" * 70)

    # Count by source
    sources = Counter(d['source'] for d in data)
    print("\nBy Source:")
    for source, count in sources.items():
        print(f"   {source:15s}: {count:6d} ({count/len(data)*100:5.1f}%)")

    # Count by type
    types = Counter(d['type'] for d in data)
    print("\nBy Type:")
    for type_, count in types.items():
        print(f"   {type_:15s}: {count:6d} ({count/len(data)*100:5.1f}%)")

    # Length statistics
    question_lengths = [len(d['question'].split()) for d in data]
    answer_lengths = [len(d['answer'].split()) for d in data]

    print("\nLength Statistics:")
    print(f"   Question length: avg={sum(question_lengths)/len(question_lengths):.1f}, "
          f"min={min(question_lengths)}, max={max(question_lengths)}")
    print(f"   Answer length:   avg={sum(answer_lengths)/len(answer_lengths):.1f}, "
          f"min={min(answer_lengths)}, max={max(answer_lengths)}")


def save_dataset(data: List[Dict], output_path: Path) -> None:
    """Save dataset to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Saved {len(data)} pairs to {output_path}")


def format_for_training(data: List[Dict]) -> List[Dict]:
    """
    Format data for GPT-2 training.

    Converts to: "Question: {question}\nAnswer: {answer}"
    """
    formatted = []

    for example in data:
        formatted.append({
            'text': f"Question: {example['question']}\nAnswer: {example['answer']}",
            'source': example['source'],
            'type': example['type']
        })

    return formatted


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for dataset generation."""
    parser = argparse.ArgumentParser(
        description="Create mixed Q&A + conversation dataset with configurable ratios."
    )
    parser.add_argument(
        "--target-size",
        type=int,
        default=50000,
        help="Total number of training pairs to generate (default: 50000)."
    )
    parser.add_argument(
        "--val-size",
        type=int,
        default=2500,
        help="Total number of validation pairs to generate (default: 2500)."
    )
    parser.add_argument(
        "--qa-ratio",
        type=float,
        default=0.70,
        help="Fraction of samples sourced from Q&A datasets (0-1, default: 0.70)."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible sampling (default: 42)."
    )
    return parser.parse_args()


def main():
    """Create mixed Q&A + conversation dataset."""
    args = parse_args()

    if not 0.0 < args.qa_ratio < 1.0:
        raise ValueError("--qa-ratio must be between 0 and 1 (exclusive).")

    random.seed(args.seed)
    print("=" * 70)
    print("MIXED Q&A + CONVERSATION DATASET CREATION")
    print("=" * 70)

    # Load datasets
    print("\n📥 Loading source datasets...")

    squad_train = load_json(SQUAD_DIR / "squad_train_standalone.json")

    # Try to load ELI5 or alternative explanatory dataset
    explanatory_dir = Path("F:/data/qa_datasets/explanatory")
    if (explanatory_dir / "explanatory_qa_train.json").exists():
        print("   Using alternative explanatory Q&A dataset")
        eli5_train = load_json(explanatory_dir / "explanatory_qa_train.json")
        eli5_val = load_json(explanatory_dir / "explanatory_qa_val.json")
    elif (ELI5_DIR / "eli5_train_50k.json").exists():
        print("   Using ELI5 dataset")
        eli5_train = load_json(ELI5_DIR / "eli5_train_50k.json")
        eli5_val = load_json(ELI5_DIR / "eli5_val.json")
    else:
        print("   ⚠️  No explanatory dataset found - using SQuAD only")
        # Double up on SQuAD to fill the explanatory slot
        eli5_train = squad_train.copy()
        eli5_val = []

    conversation_train = load_json(CONVERSATION_DIR / "hybrid_qa_train.json")
    squad_val = load_json(SQUAD_DIR / "squad_dev_standalone.json")
    conversation_val = load_json(CONVERSATION_DIR / "hybrid_qa_val.json")

    # Convert to unified format
    print("\n🔄 Converting to unified format...")

    squad_train_unified = convert_to_unified_format(squad_train, 'squad')
    eli5_train_unified = convert_to_unified_format(eli5_train, 'eli5')
    conversation_train_unified = convert_to_unified_format(conversation_train, 'conversation')

    squad_val_unified = convert_to_unified_format(squad_val, 'squad')
    eli5_val_unified = convert_to_unified_format(eli5_val, 'eli5')
    conversation_val_unified = convert_to_unified_format(conversation_val, 'conversation')

    # Create mixed training set (70% Q&A, 30% conversation)
    mixed_train = create_mixed_dataset(
        squad_train_unified,
        eli5_train_unified,
        conversation_train_unified,
        target_size=args.target_size,
        qa_ratio=args.qa_ratio
    )

    # Create mixed validation set (same ratio)
    mixed_val = create_mixed_dataset(
        squad_val_unified,
        eli5_val_unified,
        conversation_val_unified,
        target_size=args.val_size,
        qa_ratio=args.qa_ratio
    )

    # Analyze datasets
    print("\n" + "=" * 70)
    print("TRAINING SET")
    analyze_dataset(mixed_train)

    print("\n" + "=" * 70)
    print("VALIDATION SET")
    analyze_dataset(mixed_val)

    # Save in original format (for analysis)
    print("\n" + "=" * 70)
    print("💾 SAVING DATASETS")
    print("=" * 70)

    save_dataset(mixed_train, OUTPUT_DIR / "mixed_qa_conversation_train.json")
    save_dataset(mixed_val, OUTPUT_DIR / "mixed_qa_conversation_val.json")

    # Format for training
    print("\n🔄 Formatting for training...")
    train_formatted = format_for_training(mixed_train)
    val_formatted = format_for_training(mixed_val)

    save_dataset(train_formatted, OUTPUT_DIR / "mixed_train_formatted.json")
    save_dataset(val_formatted, OUTPUT_DIR / "mixed_val_formatted.json")

    # Sample examples
    print("\n" + "=" * 70)
    print("📝 SAMPLE MIXED EXAMPLES")
    print("=" * 70)

    for i, example in enumerate(random.sample(mixed_train, 5), 1):
        print(f"\nExample {i} ({example['type']} from {example['source']}):")
        print(f"Question: {example['question'][:80]}...")
        print(f"Answer:   {example['answer'][:80]}...")

    print("\n" + "=" * 70)
    print("✅ MIXED DATASET CREATION COMPLETE")
    print("=" * 70)
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print("\nDatasets created:")
    print("  ✅ mixed_train_formatted.json (50K pairs for training)")
    print("  ✅ mixed_val_formatted.json (2.5K pairs for validation)")
    print("\nNext step: Run train_with_true_qa_dataset.py")


if __name__ == "__main__":
    main()
