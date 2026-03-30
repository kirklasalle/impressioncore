#!/usr/bin/env python3
"""
ImpressionCore B3-Hope Real-Time Conversation Tester
===================================================

Interactive conversation testing system for evaluating model improvements
during and after fine-tuning.

Created: October 2, 2025
Author: Kirk LaSalle; GitHub Copilot
Purpose: Test conversation quality in real-time
"""

import os
import sys
import torch
from transformers import AutoTokenizer
import logging
from datetime import datetime
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import B3-Hope model
from b3_constitutional_trainer import B3HopeConfig, ImpressionCoreB3Hope

class InteractiveConversationTester:
    """Real-time conversation testing system"""

    def __init__(self, checkpoint_path: str):
        self.checkpoint_path = checkpoint_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        print("🤖 Loading ImpressionCore B3-Hope for conversation...")
        self.model, self.tokenizer = self.load_model()
        print(f"✅ Model loaded on {self.device}")

    def load_model(self):
        """Load the B3-Hope model"""
        # Load model architecture
        config = B3HopeConfig()
        model = ImpressionCoreB3Hope(config)

        # Load checkpoint
        if os.path.exists(self.checkpoint_path):
            checkpoint = torch.load(self.checkpoint_path, map_location='cpu', weights_only=False)
            model.load_state_dict(checkpoint['model_state_dict'])

            # Check if this is a fine-tuned conversational model
            training_type = checkpoint.get('training_type', 'base')
            if training_type == 'conversational_fine_tuning':
                print("🎯 Loaded conversational fine-tuned model!")
            else:
                print("📝 Loaded base model (may need conversational fine-tuning)")
        else:
            print(f"❌ Checkpoint not found: {self.checkpoint_path}")
            sys.exit(1)

        # Move to device and set to eval mode
        model = model.to(self.device)
        model.eval()

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
        tokenizer.pad_token = tokenizer.eos_token

        return model, tokenizer

    def generate_response(self, prompt: str, max_new_tokens: int = 50, temperature: float = 0.8) -> str:
        """Generate a conversational response"""
        # Format for conversation
        formatted_prompt = f"Human: {prompt}\nAssistant: "

        # Tokenize
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.device)

        # Generate
        with torch.no_grad():
            generated = inputs['input_ids'].clone()

            for _ in range(max_new_tokens):
                attention_mask = torch.ones_like(generated)

                outputs = self.model(
                    input_ids=generated,
                    attention_mask=attention_mask,
                    return_loss=False
                )

                logits = outputs['logits'][:, -1, :] / temperature
                probs = torch.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, 1)

                # Stop conditions
                if next_token.item() == self.tokenizer.eos_token_id:
                    break

                generated = torch.cat([generated, next_token], dim=1)

                # Stop at natural conversation breaks
                decoded_token = self.tokenizer.decode(next_token[0])
                if decoded_token in ['\n', '\r'] and len(generated[0]) > len(inputs['input_ids'][0]) + 5:
                    break

        # Decode and clean up
        full_response = self.tokenizer.decode(generated[0], skip_special_tokens=True)
        response = full_response[len(formatted_prompt):].strip()

        # Clean up artifacts
        response = response.split("Human:")[0].strip()
        response = response.split("Assistant:")[0].strip()

        return response if response else "I'd be happy to help you with that!"

    def quick_evaluation(self):
        """Quick evaluation with standard prompts"""
        test_prompts = [
            "Hello, how are you?",
            "What can you help me with?",
            "Tell me about yourself",
            "What is artificial intelligence?",
            "Can you help me with math?",
            "Thank you"
        ]

        print("\n" + "="*60)
        print("🧪 QUICK CONVERSATION EVALUATION")
        print("="*60)

        for i, prompt in enumerate(test_prompts, 1):
            print(f"\nTest {i}/6:")
            print(f"Human: {prompt}")

            response = self.generate_response(prompt)
            print(f"B3-Hope: {response}")
            print("-" * 40)

        print("="*60)

    def interactive_mode(self):
        """Interactive conversation mode"""
        print("\n" + "="*60)
        print("💬 INTERACTIVE CONVERSATION MODE")
        print("="*60)
        print("Type 'quit', 'exit', or 'q' to end the conversation")
        print("Type 'eval' for quick evaluation")
        print("Type 'help' for commands")
        print("-" * 60)

        conversation_history = []

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'eval':
                    self.quick_evaluation()
                    continue
                elif user_input.lower() == 'help':
                    print("\nCommands:")
                    print("  'eval' - Run quick evaluation")
                    print("  'quit'/'exit'/'q' - End conversation")
                    print("  'help' - Show this help")
                    continue
                elif not user_input:
                    continue

                # Generate response
                response = self.generate_response(user_input)
                print(f"B3-Hope: {response}")

                # Add to history
                conversation_history.append({
                    'user': user_input,
                    'assistant': response,
                    'timestamp': datetime.now().isoformat()
                })

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue

        # Save conversation history
        if conversation_history:
            history_file = f"conversation_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            import json
            with open(history_file, 'w') as f:
                json.dump(conversation_history, f, indent=2)
            print(f"💾 Conversation saved to: {history_file}")

def find_latest_checkpoint():
    """Find the latest checkpoint file"""
    # Look for fine-tuned conversational models first
    conversational_files = [f for f in os.listdir('.') if f.startswith('b3_hope_conversational') and f.endswith('.pth')]
    if conversational_files:
        latest = max(conversational_files, key=os.path.getctime)
        print(f"🎯 Found conversational model: {latest}")
        return latest

    # Fall back to production checkpoint
    production_checkpoint = "b3_hope_f_drive_production_checkpoint_step_1500.pth"
    if os.path.exists(production_checkpoint):
        print(f"📝 Using production checkpoint: {production_checkpoint}")
        return production_checkpoint

    print("❌ No checkpoint found!")
    return None

def main():
    """Main function"""
    print("🎯 ImpressionCore B3-Hope Interactive Conversation Tester")
    print("="*60)

    # Find the best available checkpoint
    checkpoint_path = find_latest_checkpoint()
    if not checkpoint_path:
        return

    # Initialize tester
    tester = InteractiveConversationTester(checkpoint_path)

    # Ask user what they want to do
    print("\nWhat would you like to do?")
    print("1. Quick evaluation (6 test prompts)")
    print("2. Interactive conversation")
    print("3. Both")

    choice = input("\nChoice (1/2/3): ").strip()

    if choice == '1':
        tester.quick_evaluation()
    elif choice == '2':
        tester.interactive_mode()
    elif choice == '3':
        tester.quick_evaluation()
        input("\nPress Enter to start interactive mode...")
        tester.interactive_mode()
    else:
        print("Running quick evaluation by default...")
        tester.quick_evaluation()

if __name__ == "__main__":
    main()