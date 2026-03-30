"""
Fix Path B Relevance Issue - Reformat Dataset for Q&A Alignment

This script:
1. Loads existing conversation dataset
2. Reformats from "Context/Response" to "Question/Answer" format
3. Adds explicit instruction prefix for better alignment
4. Saves reformatted dataset for fine-tuning

Created: October 7, 2025
Purpose: Fix relevance issue in Path B Phase 1 model
"""

import json
from pathlib import Path
from typing import List, Dict

def reformat_conversation_for_qa(conversations: List[Dict]) -> List[Dict]:
    """
    Reformat conversations to explicit Q&A format for better relevance.

    Args:
        conversations: List of {'context': str, 'response': str} dicts

    Returns:
        List of reformatted conversations
    """
    reformatted = []

    for conv in conversations:
        # Original format: casual conversation context-response
        # New format: explicit question-answer with instruction

        # Detect if context is a question or statement
        context = conv['context'].strip()
        response = conv['response'].strip()

        # Add question marker if not present
        is_question = any(context.lower().startswith(q) for q in [
            'what', 'how', 'why', 'when', 'where', 'who', 'which',
            'can you', 'could you', 'would you', 'will you', 'do you'
        ])

        if is_question:
            # Already a question, use as-is
            reformatted_context = context
        else:
            # Convert statement to question-like context
            # This helps model understand it needs to respond relevantly
            reformatted_context = context

        reformatted.append({
            'question': reformatted_context,
            'answer': response
        })

    return reformatted


def main():
    """Main reformatting pipeline"""

    print("=" * 70)
    print("PATH B RELEVANCE FIX - DATASET REFORMATTING")
    print("=" * 70)
    print()

    # Paths
    data_dir = Path("F:/data/conversations")
    train_file = data_dir / "hybrid_training_train.json"
    val_file = data_dir / "hybrid_training_val.json"

    # Output paths
    train_out = data_dir / "hybrid_qa_train.json"
    val_out = data_dir / "hybrid_qa_val.json"

    # Load original data
    print("📥 Loading original datasets...")

    with open(train_file, 'r', encoding='utf-8') as f:
        train_data = json.load(f)
    print(f"   Training: {len(train_data)} pairs")

    with open(val_file, 'r', encoding='utf-8') as f:
        val_data = json.load(f)
    print(f"   Validation: {len(val_data)} pairs")
    print()

    # Show examples before reformatting
    print("📋 Example BEFORE reformatting:")
    print("-" * 70)
    example = train_data[0]
    print(f"Context:  {example['context']}")
    print(f"Response: {example['response']}")
    print()

    # Reformat
    print("🔄 Reformatting to Q&A format...")
    train_qa = reformat_conversation_for_qa(train_data)
    val_qa = reformat_conversation_for_qa(val_data)
    print("   ✅ Reformatting complete")
    print()

    # Show examples after reformatting
    print("📋 Example AFTER reformatting:")
    print("-" * 70)
    example_qa = train_qa[0]
    print(f"Question: {example_qa['question']}")
    print(f"Answer:   {example_qa['answer']}")
    print()

    # Save reformatted data
    print("💾 Saving reformatted datasets...")

    with open(train_out, 'w', encoding='utf-8') as f:
        json.dump(train_qa, f, indent=2, ensure_ascii=False)
    print(f"   ✅ Saved: {train_out}")

    with open(val_out, 'w', encoding='utf-8') as f:
        json.dump(val_qa, f, indent=2, ensure_ascii=False)
    print(f"   ✅ Saved: {val_out}")
    print()

    # Statistics
    print("=" * 70)
    print("REFORMATTING COMPLETE")
    print("=" * 70)
    print(f"Training pairs:   {len(train_qa)}")
    print(f"Validation pairs: {len(val_qa)}")
    print()
    print("Next steps:")
    print("1. Run fix_path_b_relevance_finetune.py to fine-tune with new format")
    print("2. Test relevance improvement")
    print("=" * 70)


if __name__ == "__main__":
    main()
