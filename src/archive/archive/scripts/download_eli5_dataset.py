"""
Download and prepare ELI5 (Explain Like I'm 5) dataset for explanatory Q&A.

ELI5 contains 270K+ questions with long-form explanatory answers from Reddit.
Perfect for teaching models to explain concepts clearly.

Created: October 8, 2025
Author: Kirk LaSalle; GitHub Copilot
"""

import json
import os
from pathlib import Path
from typing import List, Dict
from datasets import load_dataset
from tqdm import tqdm
import random

# Output paths
OUTPUT_DIR = Path("F:/data/qa_datasets/eli5")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def download_eli5() -> Dict:
    """
    Download ELI5 dataset from HuggingFace datasets.

    Returns:
        Dict with 'train', 'validation', 'test' splits
    """
    print("📥 Downloading ELI5 dataset from HuggingFace...")
    print("   (This may take 5-10 minutes for first download)")

    # Load from HuggingFace datasets
    dataset = load_dataset("eli5", trust_remote_code=True)

    print(f"   ✅ Loaded ELI5 dataset")
    print(f"      Train: {len(dataset['train'])} examples")
    print(f"      Validation: {len(dataset['validation1'])} examples")
    print(f"      Test: {len(dataset['test'])} examples")

    return dataset


def extract_qa_pairs(dataset_split, max_pairs: int = None) -> List[Dict]:
    """
    Extract high-quality Q&A pairs from ELI5.

    Args:
        dataset_split: HuggingFace dataset split
        max_pairs: Maximum number of pairs to extract (None = all)

    Returns:
        List of {'question': str, 'answer': str} dicts
    """
    qa_pairs = []

    print(f"📊 Extracting Q&A pairs (max: {max_pairs or 'all'})...")

    for example in tqdm(dataset_split):
        question = example['title']  # ELI5 questions are in 'title' field

        # Get best answer (first answer in 'answers' dict)
        if 'answers' in example and example['answers']['text']:
            # ELI5 has multiple answers, take the first (usually highest scored)
            answer = example['answers']['text'][0]

            # Quality filters
            if len(answer) < 50:  # Skip very short answers
                continue
            if len(answer) > 2000:  # Skip extremely long answers (truncate instead)
                answer = answer[:2000] + "..."
            if not question.strip().endswith('?'):  # Ensure it's a question
                question = question.strip() + '?'

            qa_pairs.append({
                'question': question,
                'answer': answer,
                'source': 'eli5'
            })

            if max_pairs and len(qa_pairs) >= max_pairs:
                break

    return qa_pairs


def clean_reddit_formatting(text: str) -> str:
    """Remove Reddit-specific formatting."""
    # Remove markdown links
    import re
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def filter_high_quality(qa_pairs: List[Dict], min_score: int = None) -> List[Dict]:
    """
    Filter for high-quality Q&A pairs.

    Args:
        qa_pairs: List of Q&A pairs
        min_score: Minimum score threshold (if available)

    Returns:
        Filtered list
    """
    print("🔍 Filtering for high quality...")

    filtered = []
    for pair in qa_pairs:
        question = pair['question']
        answer = pair['answer']

        # Quality criteria
        if len(answer.split()) < 20:  # Skip very short explanations
            continue
        if len(answer.split()) > 500:  # Skip extremely long
            continue
        if answer.count('http') > 3:  # Skip answers with many links
            continue

        # Clean formatting
        pair['answer'] = clean_reddit_formatting(answer)
        filtered.append(pair)

    print(f"   ✅ Kept {len(filtered)}/{len(qa_pairs)} pairs")
    return filtered


def sample_balanced_topics(qa_pairs: List[Dict],
                           sample_size: int = 50000) -> List[Dict]:
    """Sample diverse questions across topics."""
    print(f"🎲 Sampling {sample_size} balanced examples...")

    if len(qa_pairs) <= sample_size:
        return qa_pairs

    # Random sample (could add topic-based sampling if needed)
    random.shuffle(qa_pairs)
    return qa_pairs[:sample_size]


def save_dataset(data: List[Dict], output_path: Path) -> None:
    """Save dataset to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"   ✅ Saved {len(data)} pairs to {output_path}")


def main():
    """Download and prepare ELI5 dataset."""
    print("=" * 70)
    print("ELI5 DATASET DOWNLOAD AND PREPARATION")
    print("=" * 70)

    # Download from HuggingFace
    dataset = download_eli5()

    # Extract Q&A pairs from train split
    print("\n📊 Processing training split...")
    train_pairs = extract_qa_pairs(
        dataset['train'],
        max_pairs=100000  # Limit to 100K for reasonable size
    )

    # Extract from validation split
    print("\n📊 Processing validation split...")
    val_pairs = extract_qa_pairs(
        dataset['validation1'],
        max_pairs=5000  # Smaller validation set
    )

    # Filter for quality
    print("\n🔍 Filtering for quality...")
    train_filtered = filter_high_quality(train_pairs)
    val_filtered = filter_high_quality(val_pairs)

    # Sample balanced subset for training
    train_sampled = sample_balanced_topics(train_filtered, sample_size=50000)

    # Save full version
    print("\n💾 Saving full version...")
    save_dataset(train_sampled, OUTPUT_DIR / "eli5_train_50k.json")
    save_dataset(val_filtered, OUTPUT_DIR / "eli5_val.json")

    # Save smaller version for testing
    print("\n💾 Saving small version (10K for quick testing)...")
    train_small = train_sampled[:9000]
    val_small = val_filtered[:1000]
    save_dataset(train_small, OUTPUT_DIR / "eli5_train_small.json")
    save_dataset(val_small, OUTPUT_DIR / "eli5_val_small.json")

    # Statistics
    print("\n" + "=" * 70)
    print("📊 DATASET STATISTICS")
    print("=" * 70)
    print(f"ELI5 Training pairs (50K): {len(train_sampled)}")
    print(f"ELI5 Validation pairs: {len(val_filtered)}")
    print(f"Small subset (train): {len(train_small)}")
    print(f"Small subset (val): {len(val_small)}")

    # Sample examples
    print("\n" + "=" * 70)
    print("📝 SAMPLE Q&A PAIRS")
    print("=" * 70)

    for i, example in enumerate(random.sample(train_sampled, 3), 1):
        print(f"\nExample {i}:")
        print(f"Question: {example['question']}")
        print(f"Answer:   {example['answer'][:200]}...")

    print("\n" + "=" * 70)
    print("✅ ELI5 DATASET PREPARATION COMPLETE")
    print("=" * 70)
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print("\nRecommended for training: eli5_train_50k.json")
    print("                         eli5_val.json")
    print("\nNext step: Run create_mixed_qa_dataset.py to combine with SQuAD")


if __name__ == "__main__":
    main()
