#!/usr/bin/env python3
"""
B3-Hope Targeted Training Dataset Generator
============================================

Creates curated dataset addressing specific weaknesses identified in evaluation:
- Simple greetings (currently 40% fallback rate)
- Short prompts (currently triggering empty responses)
- Edge cases (single-word prompts, questions marks)

Total: 2,500+ high-quality training examples

Created: October 4, 2025
Author: Kirk LaSalle; GitHub Copilot
"""

import json
from typing import List, Dict
import random

class TargetedDatasetGenerator:
    """Generates targeted training data for identified weaknesses"""

    def __init__(self):
        self.dataset = []

    def generate_greeting_data(self, count: int = 1000) -> List[Dict]:
        """
        Generate greeting/response pairs.
        Addresses 40% fallback rate in greetings category.
        """
        print(f"Generating {count} greeting examples...")

        greetings = [
            # Simple greetings
            "Hello", "Hi", "Hey", "Greetings",
            "Good morning", "Good afternoon", "Good evening", "Good day",
            "Hi there", "Hey there", "Hello there",
            "Howdy", "Yo", "Sup", "What's up", "What's happening",

            # Formal greetings
            "Good to see you", "Nice to meet you", "Pleased to meet you",
            "Welcome", "Salutations",

            # Casual greetings
            "Hey buddy", "Hey friend", "Hi friend",
            "What's good", "How's it going", "How goes it",

            # Question greetings
            "How are you?", "How are you doing?", "How have you been?",
            "How's your day?", "How's everything?", "How's life?",
            "Are you there?", "You around?", "You available?",
        ]

        responses = [
            "Hello! How can I assist you today?",
            "Hi there! I'm here to help. What can I do for you?",
            "Greetings! What would you like to know?",
            "Hello! I'd be happy to help you with anything you need.",
            "Hi! Feel free to ask me anything.",
            "Hey! What can I help you with today?",
            "Good day! How may I assist you?",
            "Hello! I'm ready to help. What's on your mind?",
            "Hi! I'm here and ready to assist. What do you need?",
            "Greetings! I'm here to help with any questions you have.",
        ]

        examples = []
        for _ in range(count):
            greeting = random.choice(greetings)
            response = random.choice(responses)
            examples.append({
                'prompt': greeting,
                'response': response,
                'category': 'greeting'
            })

        return examples

    def generate_help_request_data(self, count: int = 1000) -> List[Dict]:
        """
        Generate help request/response pairs.
        Addresses 20% fallback rate in assistance category.
        """
        print(f"Generating {count} help request examples...")

        help_requests = [
            # Direct help requests
            "Can you help me?", "Can you assist me?", "Can you help?",
            "I need help", "I need assistance", "I need your help",
            "Help me", "Assist me", "Help", "Assistance needed",

            # Question-based requests
            "I have a question", "I have questions", "Can I ask you something?",
            "May I ask a question?", "I'd like to ask something",

            # Clarification requests
            "I don't understand", "I'm confused", "This confuses me",
            "Can you explain?", "Can you clarify?", "Please explain",
            "Please clarify", "I need clarification", "Explain this",

            # Support requests
            "I need support", "Can you support me?", "I need guidance",
            "Can you guide me?", "I need advice", "Can you advise me?",

            # Learning requests
            "I want to learn", "Teach me", "Can you teach me?",
            "I'd like to know", "Tell me about", "Inform me",
        ]

        responses = [
            "I'd be happy to help! What specifically can I assist you with?",
            "Of course! What do you need help with?",
            "Absolutely! Please tell me more about what you need.",
            "I'm here to help. What's your question?",
            "Sure! What would you like to know?",
            "I'd love to assist you. What can I explain?",
            "Happy to help! What topic interests you?",
            "Certainly! What would you like me to clarify?",
            "I'm here for you. What do you need assistance with?",
            "Yes! How can I support you today?",
        ]

        examples = []
        for _ in range(count):
            request = random.choice(help_requests)
            response = random.choice(responses)
            examples.append({
                'prompt': request,
                'response': response,
                'category': 'help_request'
            })

        return examples

    def generate_edge_case_data(self, count: int = 500) -> List[Dict]:
        """
        Generate edge case examples.
        Addresses empty responses on unusual inputs.
        """
        print(f"Generating {count} edge case examples...")

        edge_cases = [
            # Single word prompts
            ("?", "I'd be happy to help! What's your question?"),
            ("!", "Hello! How can I assist you?"),
            ("...", "I'm listening. What would you like to know?"),
            ("Hmm", "Is there something specific you're curious about?"),
            ("Okay", "Great! What can I help you with?"),
            ("Yes", "Wonderful! What would you like to know?"),
            ("No", "I understand. Is there anything else I can help with?"),
            ("Maybe", "I see. What are you considering?"),
            ("Wait", "Of course. Take your time. What do you need?"),
            ("Um", "Yes? How can I assist you?"),
            ("Uh", "I'm here. What can I do for you?"),

            # Very short prompts
            ("AI", "Artificial Intelligence is my specialty! What would you like to know about AI?"),
            ("ML", "Machine Learning is fascinating! What aspect interests you?"),
            ("Python", "Python is a great programming language! What would you like to know about it?"),
            ("Code", "Programming is exciting! What coding topic interests you?"),
            ("Data", "Data science is a powerful field! What would you like to learn?"),

            # Incomplete sentences
            ("Tell me", "I'd be happy to! What would you like me to tell you about?"),
            ("Show me", "I'd love to help! What would you like to see or understand?"),
            ("Explain", "Certainly! What topic would you like me to explain?"),
            ("Describe", "Sure! What would you like me to describe?"),
            ("Define", "Of course! What term would you like defined?"),

            # Common typos/variations
            ("pls help", "Happy to help! What do you need?"),
            ("plz explain", "Of course! What would you like me to explain?"),
            ("thx", "You're welcome! Is there anything else?"),
            ("ty", "You're welcome! How else can I help?"),
            ("k", "Okay! What would you like to know?"),
        ]

        examples = []

        # Use predefined edge cases
        for prompt, response in edge_cases:
            examples.append({
                'prompt': prompt,
                'response': response,
                'category': 'edge_case'
            })

        # Generate additional variations
        while len(examples) < count:
            prompt, response = random.choice(edge_cases)
            # Add slight variations
            if random.random() < 0.3:
                prompt = prompt.lower()
            elif random.random() < 0.3:
                prompt = prompt.upper()

            examples.append({
                'prompt': prompt,
                'response': response,
                'category': 'edge_case'
            })

        return examples[:count]

    def generate_complete_dataset(self) -> List[Dict]:
        """Generate complete targeted training dataset"""
        print("\n" + "="*80)
        print("TARGETED TRAINING DATASET GENERATION")
        print("="*80 + "\n")

        # Generate each category
        greetings = self.generate_greeting_data(1000)
        help_requests = self.generate_help_request_data(1000)
        edge_cases = self.generate_edge_case_data(500)

        # Combine all examples
        self.dataset = greetings + help_requests + edge_cases

        # Shuffle dataset
        random.shuffle(self.dataset)

        print(f"\n{'='*80}")
        print("DATASET GENERATION COMPLETE")
        print(f"{'='*80}")
        print(f"Total examples: {len(self.dataset)}")
        print(f"  - Greetings: {len(greetings)}")
        print(f"  - Help Requests: {len(help_requests)}")
        print(f"  - Edge Cases: {len(edge_cases)}")
        print(f"{'='*80}\n")

        return self.dataset

    def save_dataset(self, filename: str = "b3_targeted_training_data.json"):
        """Save dataset to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.dataset, f, indent=2, ensure_ascii=False)

        print(f"Dataset saved to: {filename}")

        # Also create a text version for inspection
        text_filename = filename.replace('.json', '.txt')
        with open(text_filename, 'w', encoding='utf-8') as f:
            f.write("B3-HOPE TARGETED TRAINING DATASET\n")
            f.write("="*80 + "\n\n")

            for i, example in enumerate(self.dataset[:50], 1):  # Show first 50
                f.write(f"Example {i} ({example['category']}):\n")
                f.write(f"Prompt: {example['prompt']}\n")
                f.write(f"Response: {example['response']}\n")
                f.write("-"*80 + "\n\n")

            f.write(f"... and {len(self.dataset) - 50} more examples\n")

        print(f"Sample text saved to: {text_filename}")

    def generate_statistics(self):
        """Generate dataset statistics"""
        if not self.dataset:
            print("No dataset generated yet!")
            return

        print("\n" + "="*80)
        print("DATASET STATISTICS")
        print("="*80)

        # Count by category
        categories = {}
        for example in self.dataset:
            cat = example['category']
            categories[cat] = categories.get(cat, 0) + 1

        print("\nCategory Distribution:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count} ({count/len(self.dataset)*100:.1f}%)")

        # Average lengths
        prompt_lengths = [len(ex['prompt']) for ex in self.dataset]
        response_lengths = [len(ex['response']) for ex in self.dataset]

        print(f"\nPrompt Statistics:")
        print(f"  Average length: {sum(prompt_lengths)/len(prompt_lengths):.1f} characters")
        print(f"  Min length: {min(prompt_lengths)}")
        print(f"  Max length: {max(prompt_lengths)}")

        print(f"\nResponse Statistics:")
        print(f"  Average length: {sum(response_lengths)/len(response_lengths):.1f} characters")
        print(f"  Min length: {min(response_lengths)}")
        print(f"  Max length: {max(response_lengths)}")

        print("="*80 + "\n")


def main():
    """Main execution"""
    generator = TargetedDatasetGenerator()

    # Generate complete dataset
    dataset = generator.generate_complete_dataset()

    # Generate statistics
    generator.generate_statistics()

    # Save dataset
    generator.save_dataset("b3_targeted_training_data.json")

    print("\n✓ Dataset generation complete!")
    print("✓ Ready for Phase 2 fine-tuning")


if __name__ == "__main__":
    main()
