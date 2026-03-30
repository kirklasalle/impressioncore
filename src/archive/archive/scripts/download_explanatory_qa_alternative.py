"""
Alternative Explanatory Q&A Dataset Generator

Since ELI5 is defunct, this script uses alternative approaches:
1. Use MS MARCO or Natural Questions for long-form answers
2. Generate synthetic explanatory Q&A from SQuAD contexts
3. Use Wikipedia-based Q&A datasets

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

# Configure HuggingFace to use F: drive
os.environ['HF_HOME'] = 'F:/huggingface_cache'
os.environ['HUGGINGFACE_HUB_CACHE'] = 'F:/huggingface_cache/hub'
os.environ['HF_DATASETS_CACHE'] = 'F:/huggingface_cache/datasets'

# Output paths
OUTPUT_DIR = Path("F:/data/qa_datasets/explanatory")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def try_alternative_datasets() -> List[Dict]:
    """
    Try multiple alternative datasets for explanatory Q&A.

    Priority order:
    1. Natural Questions (Google) - has long answers
    2. MS MARCO - has passages and answers
    3. Generate from SQuAD contexts
    """

    print("🔍 Trying alternative explanatory Q&A datasets...")

    # Try 1: Natural Questions
    try:
        print("\n📥 Attempting Natural Questions dataset...")
        dataset = load_dataset("natural_questions", trust_remote_code=True)
        print("   ✅ Natural Questions loaded successfully!")
        return extract_from_natural_questions(dataset)
    except Exception as e:
        print(f"   ❌ Natural Questions failed: {e}")

    # Try 2: MS MARCO
    try:
        print("\n📥 Attempting MS MARCO dataset...")
        dataset = load_dataset("ms_marco", "v2.1", trust_remote_code=True)
        print("   ✅ MS MARCO loaded successfully!")
        return extract_from_ms_marco(dataset)
    except Exception as e:
        print(f"   ❌ MS MARCO failed: {e}")

    # Try 3: WikiQA
    try:
        print("\n📥 Attempting WikiQA dataset...")
        dataset = load_dataset("wiki_qa", trust_remote_code=True)
        print("   ✅ WikiQA loaded successfully!")
        return extract_from_wikiqa(dataset)
    except Exception as e:
        print(f"   ❌ WikiQA failed: {e}")

    # Fallback: Generate from SQuAD
    print("\n⚠️  All alternatives failed. Using SQuAD contexts to generate explanatory Q&A...")
    return generate_explanatory_from_squad()


def extract_from_natural_questions(dataset) -> List[Dict]:
    """Extract Q&A pairs from Natural Questions."""
    print("\n🔄 Extracting from Natural Questions...")

    qa_pairs = []
    train_data = dataset['train']

    for example in tqdm(train_data.select(range(min(100000, len(train_data)))), desc="Processing"):
        try:
            question = example['question']['text']

            # Get long answer if available
            annotations = example['annotations']
            if annotations and len(annotations) > 0:
                long_answer = annotations[0].get('long_answer', {})
                if long_answer and long_answer.get('start_token', -1) >= 0:
                    # Has a valid long answer
                    answer_tokens = example['document']['tokens'][
                        long_answer['start_token']:long_answer['end_token']
                    ]
                    answer = ' '.join([t['token'] for t in answer_tokens])

                    # Filter for quality
                    if 50 < len(answer) < 2000 and len(question) > 10:
                        qa_pairs.append({
                            "question": question,
                            "answer": answer,
                            "source": "natural_questions"
                        })

                        if len(qa_pairs) >= 50000:
                            break
        except Exception as e:
            continue

    print(f"   ✅ Extracted {len(qa_pairs)} Q&A pairs from Natural Questions")
    return qa_pairs


def extract_from_ms_marco(dataset) -> List[Dict]:
    """Extract Q&A pairs from MS MARCO."""
    print("\n🔄 Extracting from MS MARCO...")

    qa_pairs = []
    train_data = dataset['train']

    for example in tqdm(train_data.select(range(min(100000, len(train_data)))), desc="Processing"):
        try:
            question = example['query']
            passages = example.get('passages', {})

            # Find passage marked as answer
            if passages and 'is_selected' in passages:
                for i, is_selected in enumerate(passages['is_selected']):
                    if is_selected == 1:
                        answer = passages['passage_text'][i]

                        # Filter for quality
                        if 50 < len(answer) < 2000 and len(question) > 10:
                            qa_pairs.append({
                                "question": question,
                                "answer": answer,
                                "source": "ms_marco"
                            })

                            if len(qa_pairs) >= 50000:
                                break

                        break
        except Exception as e:
            continue

        if len(qa_pairs) >= 50000:
            break

    print(f"   ✅ Extracted {len(qa_pairs)} Q&A pairs from MS MARCO")
    return qa_pairs


def extract_from_wikiqa(dataset) -> List[Dict]:
    """Extract Q&A pairs from WikiQA."""
    print("\n🔄 Extracting from WikiQA...")

    qa_pairs = []
    train_data = dataset['train']

    for example in tqdm(train_data, desc="Processing"):
        try:
            question = example['question']
            answer = example['answer']
            label = example['label']

            # Only use pairs marked as correct answers
            if label == 1 and 50 < len(answer) < 2000 and len(question) > 10:
                qa_pairs.append({
                    "question": question,
                    "answer": answer,
                    "source": "wikiqa"
                })

                if len(qa_pairs) >= 50000:
                    break
        except Exception as e:
            continue

    print(f"   ✅ Extracted {len(qa_pairs)} Q&A pairs from WikiQA")
    return qa_pairs


def generate_explanatory_from_squad() -> List[Dict]:
    """
    Generate explanatory Q&A by using SQuAD contexts as explanations.

    Strategy: Take SQuAD context paragraphs and create "Explain..." questions.
    """
    print("\n🔄 Generating explanatory Q&A from SQuAD contexts...")

    # Load SQuAD data
    squad_file = Path("F:/data/qa_datasets/squad/squad_train_with_context.json")
    if not squad_file.exists():
        print("   ❌ SQuAD context file not found. Cannot generate explanatory data.")
        return []

    with open(squad_file, 'r', encoding='utf-8') as f:
        squad_data = json.load(f)

    qa_pairs = []

    # Generate explanatory questions from contexts
    for item in tqdm(squad_data[:50000], desc="Generating"):
        context = item['context']
        original_question = item['question']

        # Create explanatory version
        # Extract topic from original question
        topic = extract_topic(original_question)

        if topic and 100 < len(context) < 2000:
            # Create "Explain..." question
            explanatory_q = f"Explain {topic}"

            qa_pairs.append({
                "question": explanatory_q,
                "answer": context,
                "source": "squad_generated"
            })

    print(f"   ✅ Generated {len(qa_pairs)} explanatory Q&A pairs from SQuAD")
    return qa_pairs


def extract_topic(question: str) -> str:
    """Extract main topic from a question."""
    # Remove question words
    question_words = ['what', 'who', 'where', 'when', 'why', 'how', 'which', 'whose']
    words = question.lower().split()

    # Filter out question words and short words
    topic_words = [w for w in words if w not in question_words and len(w) > 3]

    if topic_words:
        return ' '.join(topic_words[:5])  # Take first 5 significant words
    return ""


def clean_text(text: str) -> str:
    """Clean text for training."""
    # Remove excessive whitespace
    text = ' '.join(text.split())
    # Remove very long sequences of same character
    import re
    text = re.sub(r'(.)\1{5,}', r'\1\1', text)
    return text.strip()


def save_dataset(qa_pairs: List[Dict], output_name: str):
    """Save formatted dataset."""
    print(f"\n💾 Saving {len(qa_pairs)} pairs...")

    # Clean and format
    formatted = []
    for pair in qa_pairs:
        formatted.append({
            "question": clean_text(pair['question']),
            "answer": clean_text(pair['answer']),
            "source": pair['source']
        })

    # Save full dataset
    output_file = OUTPUT_DIR / f"{output_name}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted, f, indent=2, ensure_ascii=False)
    print(f"   ✅ Saved to {output_file}")

    # Create train/val split
    random.shuffle(formatted)
    split_idx = int(len(formatted) * 0.95)

    train_data = formatted[:split_idx]
    val_data = formatted[split_idx:]

    train_file = OUTPUT_DIR / f"{output_name}_train.json"
    val_file = OUTPUT_DIR / f"{output_name}_val.json"

    with open(train_file, 'w', encoding='utf-8') as f:
        json.dump(train_data, f, indent=2, ensure_ascii=False)

    with open(val_file, 'w', encoding='utf-8') as f:
        json.dump(val_data, f, indent=2, ensure_ascii=False)

    print(f"   ✅ Train: {len(train_data)} pairs → {train_file}")
    print(f"   ✅ Val: {len(val_data)} pairs → {val_file}")

    return train_file, val_file


def main():
    """Main execution."""
    print("=" * 70)
    print("ALTERNATIVE EXPLANATORY Q&A DATASET DOWNLOAD")
    print("=" * 70)

    # Try alternative datasets
    qa_pairs = try_alternative_datasets()

    if not qa_pairs:
        print("\n❌ Failed to obtain explanatory Q&A data from any source.")
        print("\n💡 SOLUTION: We can still proceed with SQuAD only (factual Q&A)")
        print("   This will reduce explanatory capability but maintain Q&A ability.")
        return None

    # Save dataset
    train_file, val_file = save_dataset(qa_pairs, "explanatory_qa")

    print("\n" + "=" * 70)
    print("✅ ALTERNATIVE EXPLANATORY DATASET COMPLETE")
    print("=" * 70)
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print(f"\n📊 Total pairs: {len(qa_pairs)}")
    print(f"   Train: {train_file.name}")
    print(f"   Val: {val_file.name}")

    # Show samples
    print("\n" + "=" * 70)
    print("📝 SAMPLE Q&A PAIRS")
    print("=" * 70)

    for i, pair in enumerate(random.sample(qa_pairs, min(5, len(qa_pairs))), 1):
        q = pair['question'][:100] + "..." if len(pair['question']) > 100 else pair['question']
        a = pair['answer'][:100] + "..." if len(pair['answer']) > 100 else pair['answer']
        print(f"\nExample {i}:")
        print(f"Question: {q}")
        print(f"Answer:   {a}")
        print(f"Source:   {pair['source']}")

    return train_file


if __name__ == "__main__":
    main()
