"""
Download and prepare SQuAD 2.0 dataset for Q&A training.

SQuAD 2.0 (Stanford Question Answering Dataset) contains 130K+ question-answer
pairs based on Wikipedia articles. It's perfect for teaching factual Q&A.

Created: October 8, 2025
Author: Kirk LaSalle; GitHub Copilot
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Tuple
import requests
from tqdm import tqdm
import random

# Dataset URLs
SQUAD_TRAIN_URL = "https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v2.0.json"
SQUAD_DEV_URL = "https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v2.0.json"

# Output paths
OUTPUT_DIR = Path("F:/data/qa_datasets/squad")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def download_file(url: str, output_path: Path) -> None:
    """Download file with progress bar."""
    print(f"📥 Downloading from {url}...")

    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))

    with open(output_path, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

    print(f"   ✅ Saved to {output_path}")


def extract_qa_pairs(squad_data: Dict) -> List[Tuple[str, str, str]]:
    """
    Extract question-answer pairs from SQuAD format.

    Returns:
        List of (context, question, answer) tuples
    """
    qa_pairs = []

    for article in squad_data['data']:
        for paragraph in article['paragraphs']:
            context = paragraph['context']

            for qa in paragraph['qas']:
                question = qa['question']

                # Skip unanswerable questions (SQuAD 2.0 includes these)
                if qa['is_impossible']:
                    continue

                # Get first answer (there may be multiple acceptable answers)
                if qa['answers']:
                    answer = qa['answers'][0]['text']
                    qa_pairs.append((context, question, answer))

    return qa_pairs


def format_for_training(qa_pairs: List[Tuple[str, str, str]],
                        include_context: bool = False) -> List[Dict]:
    """
    Format Q&A pairs for training.

    Args:
        qa_pairs: List of (context, question, answer) tuples
        include_context: Whether to include passage context in question

    Returns:
        List of formatted training examples
    """
    formatted = []

    for context, question, answer in qa_pairs:
        if include_context:
            # For questions that need context (reading comprehension)
            full_question = f"Context: {context}\n\nQuestion: {question}"
        else:
            # For standalone factual questions
            full_question = question

        formatted.append({
            'question': full_question,
            'answer': answer,
            'context': context  # Keep for reference
        })

    return formatted


def create_train_val_split(data: List[Dict],
                           val_ratio: float = 0.05) -> Tuple[List[Dict], List[Dict]]:
    """Split data into training and validation sets."""
    random.shuffle(data)

    split_idx = int(len(data) * (1 - val_ratio))
    train_data = data[:split_idx]
    val_data = data[split_idx:]

    return train_data, val_data


def save_dataset(data: List[Dict], output_path: Path) -> None:
    """Save dataset to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"   ✅ Saved {len(data)} pairs to {output_path}")


def main():
    """Download and prepare SQuAD dataset."""
    print("=" * 70)
    print("SQUAD 2.0 DATASET DOWNLOAD AND PREPARATION")
    print("=" * 70)

    # Download raw SQuAD files
    train_raw_path = OUTPUT_DIR / "squad_train_raw.json"
    dev_raw_path = OUTPUT_DIR / "squad_dev_raw.json"

    if not train_raw_path.exists():
        download_file(SQUAD_TRAIN_URL, train_raw_path)
    else:
        print(f"   ✅ Training file already exists: {train_raw_path}")

    if not dev_raw_path.exists():
        download_file(SQUAD_DEV_URL, dev_raw_path)
    else:
        print(f"   ✅ Dev file already exists: {dev_raw_path}")

    # Load and parse
    print("\n📊 Extracting Q&A pairs...")

    with open(train_raw_path, 'r', encoding='utf-8') as f:
        train_raw = json.load(f)

    with open(dev_raw_path, 'r', encoding='utf-8') as f:
        dev_raw = json.load(f)

    train_pairs = extract_qa_pairs(train_raw)
    dev_pairs = extract_qa_pairs(dev_raw)

    print(f"   ✅ Extracted {len(train_pairs)} training pairs")
    print(f"   ✅ Extracted {len(dev_pairs)} dev pairs")

    # Format for training
    print("\n🔄 Formatting for training...")

    # Create two versions: with and without context

    # Version 1: Standalone questions (better for general Q&A)
    train_formatted_standalone = format_for_training(train_pairs, include_context=False)
    dev_formatted_standalone = format_for_training(dev_pairs, include_context=False)

    # Version 2: With context (reading comprehension style)
    train_formatted_context = format_for_training(train_pairs, include_context=True)
    dev_formatted_context = format_for_training(dev_pairs, include_context=True)

    # Save standalone version (recommended for general Q&A)
    print("\n💾 Saving standalone version (recommended)...")
    save_dataset(
        train_formatted_standalone,
        OUTPUT_DIR / "squad_train_standalone.json"
    )
    save_dataset(
        dev_formatted_standalone,
        OUTPUT_DIR / "squad_dev_standalone.json"
    )

    # Save context version
    print("\n💾 Saving context version (reading comprehension)...")
    save_dataset(
        train_formatted_context,
        OUTPUT_DIR / "squad_train_with_context.json"
    )
    save_dataset(
        dev_formatted_context,
        OUTPUT_DIR / "squad_dev_with_context.json"
    )

    # Create smaller training set (optional - for faster iteration)
    print("\n📦 Creating smaller subset (25K pairs for quick testing)...")
    train_small, val_small = create_train_val_split(
        train_formatted_standalone[:25000],
        val_ratio=0.1
    )
    save_dataset(train_small, OUTPUT_DIR / "squad_train_small.json")
    save_dataset(val_small, OUTPUT_DIR / "squad_val_small.json")

    # Statistics
    print("\n" + "=" * 70)
    print("📊 DATASET STATISTICS")
    print("=" * 70)
    print(f"SQuAD 2.0 Training pairs: {len(train_formatted_standalone)}")
    print(f"SQuAD 2.0 Dev pairs: {len(dev_formatted_standalone)}")
    print(f"Small subset (train): {len(train_small)}")
    print(f"Small subset (val): {len(val_small)}")

    # Sample examples
    print("\n" + "=" * 70)
    print("📝 SAMPLE Q&A PAIRS")
    print("=" * 70)

    for i, example in enumerate(random.sample(train_formatted_standalone, 5), 1):
        print(f"\nExample {i}:")
        print(f"Question: {example['question'][:100]}...")
        print(f"Answer:   {example['answer'][:100]}...")

    print("\n" + "=" * 70)
    print("✅ SQUAD DATASET PREPARATION COMPLETE")
    print("=" * 70)
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print("\nRecommended for training: squad_train_standalone.json")
    print("                         squad_dev_standalone.json")
    print("\nNext step: Run download_eli5_dataset.py")


if __name__ == "__main__":
    main()
