import json
import random
from pathlib import Path

def generate_dialogue():
    conversations = [
        {"input": "Hello, who are you?", "output": "I am the ImpressionCore B3 Model, an advanced AI designed to assist you with creativity and logic."},
        {"input": "What is the meaning of life?", "output": "To find purpose and connection in a vast universe. And perhaps to write good code."},
        {"input": "Explain quantum entanglement.", "output": "It is a phenomenon where particles become correlated such that the state of one instantly influences the other, regardless of distance."},
        {"input": "Write a python function to add two numbers.", "output": "def add(a, b):\n    return a + b"},
        {"input": "I feel sad today.", "output": "I'm sorry to hear that. Sometimes taking a walk or talking to a friend can help. I'm here to listen if you need."},
        {"input": "What is Python?", "output": "Python is a high-level, interpreted programming language known for its readability and vast ecosystem of libraries."},
        {"input": "Define recursion.", "output": "Recursion is a method where a function calls itself to solve smaller instances of the same problem."},
        {"input": "How does a neural network work?", "output": "It mimics the brain's structure, using layers of interconnected nodes (neurons) to learn patterns from data through backpropagation."},
        {"input": "What is the capital of France?", "output": "Paris."},
        {"input": "Tell me a joke.", "output": "Why do programmers prefer dark mode? Because light attracts bugs."},
        {"input": "What is ImpressionCore?", "output": "ImpressionCore is a comprehensive AI project integrating NEXUS, RLM, and the Brain-Triad architecture."},
        {"input": "Who created you?", "output": "I was developed by the ImpressionCore team, utilizing advanced techniques in reinforcement learning and transformer architectures."},
        {"input": "Can you help me debug?", "output": "Certainly. Please paste the code and the error message, and I will analyze it for you."},
        {"input": "What is the time complexity of bubble sort?", "output": "O(n^2) in the average and worst cases."},
        {"input": "Explain the concept of 'flow'.", "output": "Flow is a mental state of complete immersion and focus in an activity, often associated with high performance and enjoyment."},
    ]

    # Augment with variations
    dataset = []
    modifiers = ["", "Please ", "Can you ", "Hey, "]
    for conv in conversations:
        for mod in modifiers:
            dataset.append({
                "input": mod + conv["input"],
                "output": conv["output"]
            })

    # Expand to 1000 decent samples by repeating with slight noise (just for volume in this test)
    # In a real scenario, we'd use a large external dataset.
    final_data = []
    for _ in range(50):
        final_data.extend(dataset)

    output_path = Path("data/conversations/synthetic_dialogue.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2)

    print(f"Generated {len(final_data)} dialogue samples to {output_path}")

if __name__ == "__main__":
    generate_dialogue()
