import json
import random
import sqlite3
from pathlib import Path


class ToolDatasetGenerator:
    """Generates synthetic dataset for RLM Tool Use (Dictionary)."""

    def __init__(self, db_path: str = "data/knowledge/dictionary.db"):
        self.db_path = db_path
        self.words = self._load_words()

    def _load_words(self) -> list[str]:
        """Load a sample of words from the dictionary."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Get 5000 random words that are "common" enough (length > 3)
            cursor.execute('SELECT word FROM dictionary WHERE length(word) > 3 ORDER BY RANDOM() LIMIT 5000')
            words = [row[0] for row in cursor.fetchall()]
            conn.close()
            return words
        except Exception as e:
            print(f"Error loading words: {e}")
            return ["example", "test", "word"] # Fallback

    def generate(self, count: int = 1000) -> list[dict]:
        """Generate dataset entries."""
        data = []
        templates = [
            ("Define {word}.", "(DICT-LOOKUP \"{word}\")"),
            ("What means {word}?", "(DICT-LOOKUP \"{word}\")"),
            ("What is the definition of {word}?", "(DICT-LOOKUP \"{word}\")"),
            ("Explain the word {word}.", "(DICT-LOOKUP \"{word}\")"),
            ("Look up {word}.", "(DICT-LOOKUP \"{word}\")"),
            ("Dictionary definition for {word}", "(DICT-LOOKUP \"{word}\")"),
            ("What represents {word}?", "(DICT-LOOKUP \"{word}\")"),
            ("Tell me about {word}.", "(DICT-DEF \"{word}\")"), # Use detailed def for broad questions
            ("Full definition of {word}", "(DICT-DEF \"{word}\")"),
            ("Etymology of {word}", "(DICT-DEF \"{word}\")")
        ]

        print(f"Generating {count} samples from {len(self.words)} words...")

        for _ in range(count):
            word = random.choice(self.words)
            # Clean word (remove quotes etc for the query, but keep in prompt)
            clean_word = word.replace('"', '')

            template, action_template = random.choice(templates)

            prompt = template.format(word=clean_word)
            action = action_template.format(word=clean_word)

            data.append({
                "instruction": prompt,
                "input": "",
                "output": action,
                "type": "tool_use"
            })

        return data

if __name__ == "__main__":
    generator = ToolDatasetGenerator()
    dataset = generator.generate(2000)

    output_path = Path("data/datasets/rlm_dictionary_tool.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2)

    print(f"Saved {len(dataset)} samples to {output_path}")
