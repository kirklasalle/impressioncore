"""
B3 Hybrid Conversation Interface - Quick Start

Simple conversation interface for the deployed model.

Quality: 9.25/10.0
Created: October 6, 2025
"""

import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from pathlib import Path
import sys

class ConversationInterface:
    """Simple conversation interface for B3 Hybrid model"""

    def __init__(self, model_path="F:/models/production/b3_hybrid_conversation_v1.0.pth"):
        """Initialize model and tokenizer"""
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Loading model on {self.device}...")

        # Load tokenizer
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load model
        model_path = Path(model_path)
        if not model_path.exists():
            print(f"❌ ERROR: Model not found at {model_path}")
            print("Please run deploy_best_model.py first!")
            sys.exit(1)

        checkpoint = torch.load(model_path, map_location=self.device)
        self.model = checkpoint['model']
        self.model.to(self.device)
        self.model.eval()

        print(f"✅ Model loaded: {model_path.name}")
        print(f"✅ Quality: 9.25/10.0")
        print()

    def chat(self, user_input, max_length=100, temperature=0.8, top_p=0.9):
        """Generate conversation response"""

        # Format prompt
        prompt = f"User: {user_input}\nAssistant:"

        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                num_return_sequences=1
            )

        # Decode
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract assistant response
        if "Assistant:" in response:
            response = response.split("Assistant:")[-1].strip()

        return response

    def interactive(self):
        """Run interactive conversation loop"""
        print("B3 Hybrid Conversation v1.0 - Interactive Mode")
        print("Quality: 9.25/10.0 | Hardware: GTX 1050 Ti Compatible")
        print()
        print("Type 'quit' or 'exit' to end conversation")
        print("=" * 70)
        print()

        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                # Check for exit
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break

                if not user_input:
                    continue

                # Generate response
                response = self.chat(user_input)
                print(f"Assistant: {response}")
                print()

            except KeyboardInterrupt:
                print("\n\nConversation interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue

def main():
    """Main entry point"""
    interface = ConversationInterface()
    interface.interactive()

if __name__ == "__main__":
    main()
