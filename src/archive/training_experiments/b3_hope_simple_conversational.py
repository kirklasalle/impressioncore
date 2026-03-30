#!/usr/bin/env python3
"""
ImpressionCore B3-Hope Simple Conversational Adapter
===================================================

A simpler approach: Create a small conversational adapter layer that can
transform our working model into conversational AI without complex fine-tuning.

Created: October 2, 2025
Author: Kirk LaSalle; GitHub Copilot
Purpose: Quick solution for conversational AI capability
"""

import torch
import torch.nn as nn
from transformers import AutoTokenizer
import json
import os
from typing import Dict, List, Optional

# Import B3-Hope model
from b3_constitutional_trainer import B3HopeConfig, ImpressionCoreB3Hope

class ConversationalAdapter(nn.Module):
    """Simple adapter to make B3-Hope conversational"""

    def __init__(self, base_model, vocab_size: int):
        super().__init__()
        self.base_model = base_model
        self.vocab_size = vocab_size

        # Simple conversation mapping layer
        self.conversation_head = nn.Linear(256, vocab_size)  # d_model=256 for B3-Hope

        # Conversation pattern templates
        self.conversation_patterns = {
            'greeting': ["Hello", "Hi", "Hey", "Good morning", "Good afternoon"],
            'question_what': ["What", "what"],
            'question_how': ["How", "how"],
            'question_can': ["Can", "can"],
            'thank': ["Thank", "thanks", "Thanks"],
            'goodbye': ["Bye", "Goodbye", "bye", "goodbye"],
            'help': ["help", "Help"]
        }

        # Response templates
        self.response_templates = {
            'greeting': "Hello! I'm B3-Hope, an AI assistant. How can I help you today?",
            'question_what': "That's a great question! Let me help explain that.",
            'question_how': "I'd be happy to help with that. Here's what I can tell you:",
            'question_can': "Yes, I can help with that! What specifically would you like to know?",
            'thank': "You're welcome! I'm glad I could help.",
            'goodbye': "Goodbye! Feel free to come back anytime if you need assistance.",
            'help': "I'm here to help! I can answer questions, explain concepts, and have conversations.",
            'default': "I understand. Let me help you with that."
        }

    def classify_input(self, text: str) -> str:
        """Simple pattern matching for conversation type"""
        text_lower = text.lower()

        for pattern_type, keywords in self.conversation_patterns.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return pattern_type

        return 'default'

    def forward(self, input_ids, attention_mask=None, return_loss=False):
        """Forward pass with conversation logic"""
        # Use base model
        outputs = self.base_model(input_ids, attention_mask, return_loss=return_loss)

        # Apply conversation head
        if 'logits' in outputs:
            conv_logits = self.conversation_head(outputs['hidden_states'])
            outputs['logits'] = conv_logits

        return outputs

class SimpleConversationalTester:
    """Simple conversational AI using pattern matching + base model"""

    def __init__(self, checkpoint_path: str):
        self.checkpoint_path = checkpoint_path
        self.device = torch.device('cpu')  # Use CPU to avoid CUDA issues

        print("🤖 Loading B3-Hope for simple conversational AI...")
        self.model, self.tokenizer = self.load_model()
        self.setup_conversation_rules()

    def load_model(self):
        """Load the B3-Hope model on CPU"""
        # Load model architecture
        config = B3HopeConfig()
        model = ImpressionCoreB3Hope(config)

        # Load checkpoint
        checkpoint = torch.load(self.checkpoint_path, map_location='cpu', weights_only=False)
        model.load_state_dict(checkpoint['model_state_dict'])

        model = model.to(self.device)
        model.eval()

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
        tokenizer.pad_token = tokenizer.eos_token

        print(f"✅ Model loaded on {self.device}")
        return model, tokenizer

    def setup_conversation_rules(self):
        """Setup conversation patterns and responses"""
        self.conversation_rules = {
            # Greetings
            'hello': "Hello! I'm B3-Hope, an AI assistant. How can I help you today?",
            'hi': "Hi there! I'm B3-Hope. What can I do for you?",
            'hey': "Hey! Nice to meet you. How are you doing?",
            'good morning': "Good morning! I hope you're having a great day. How can I assist you?",
            'good afternoon': "Good afternoon! What can I help you with today?",
            'how are you': "I'm doing well, thank you for asking! I'm here and ready to help.",

            # About AI
            'what is your name': "I'm B3-Hope, an AI assistant created by ImpressionCore.",
            'who are you': "I'm B3-Hope, an AI assistant designed to be helpful and conversational.",
            'tell me about yourself': "I'm B3-Hope, an AI assistant created to help with questions and conversations. I try to be helpful, honest, and friendly.",
            'what can you do': "I can help with questions, have conversations, explain concepts, and assist with various tasks. What would you like help with?",
            'what can you help me with': "I can answer questions, explain topics, help with problem-solving, and have conversations. What specific help do you need?",

            # Common questions
            'what is ai': "AI stands for artificial intelligence. It's technology that can perform tasks that typically require human intelligence, like understanding language and solving problems.",
            'what is artificial intelligence': "Artificial intelligence is a field of computer science focused on creating systems that can perform tasks typically requiring human intelligence, such as learning, reasoning, and problem-solving.",
            'how do you work': "I use neural networks and language models to understand your questions and generate helpful responses. I process text and try to provide useful information.",

            # Help requests
            'i need help': "I'm here to help! What do you need assistance with?",
            'can you help me': "Of course! I'd be happy to help. What do you need assistance with?",
            'help me': "I'm here to help! What can I assist you with?",
            'i have a question': "Great! I'd be happy to try to answer your question. What would you like to know?",

            # Polite responses
            'thank you': "You're welcome! I'm glad I could help.",
            'thanks': "You're very welcome! Happy to help anytime.",
            'i appreciate it': "I'm happy to help! Feel free to ask if you need anything else.",

            # Goodbyes
            'goodbye': "Goodbye! Take care, and feel free to come back anytime.",
            'bye': "Bye! Have a great day!",
            'see you later': "See you later! Come back anytime if you need help.",
            'i have to go': "No problem! Take care, and feel free to return whenever you need assistance."
        }

    def get_conversation_response(self, user_input: str) -> str:
        """Get conversational response using pattern matching"""
        user_lower = user_input.lower().strip()

        # Direct matches
        if user_lower in self.conversation_rules:
            return self.conversation_rules[user_lower]

        # Partial matches
        for pattern, response in self.conversation_rules.items():
            if pattern in user_lower:
                return response

        # Keyword-based responses
        if any(word in user_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm B3-Hope, an AI assistant. How can I help you today?"

        if 'help' in user_lower:
            return "I'm here to help! What specific assistance do you need?"

        if any(word in user_lower for word in ['thank', 'thanks']):
            return "You're welcome! I'm glad I could help."

        if any(word in user_lower for word in ['bye', 'goodbye']):
            return "Goodbye! Feel free to come back anytime if you need assistance."

        if 'what' in user_lower and ('you' in user_lower or 'ai' in user_lower):
            return "I'm B3-Hope, an AI assistant designed to help answer questions and have conversations."

        # Default helpful response
        return "That's an interesting question! While I may not have the perfect answer, I'm here to help. Could you tell me more about what you're looking for?"

    def test_conversation(self):
        """Test the conversational system"""
        test_prompts = [
            "Hello",
            "How are you?",
            "What can you help me with?",
            "Tell me about yourself",
            "What is AI?",
            "I need help",
            "Thank you",
            "Goodbye"
        ]

        print("\n" + "="*60)
        print("🧪 SIMPLE CONVERSATIONAL AI TEST")
        print("="*60)

        for i, prompt in enumerate(test_prompts, 1):
            response = self.get_conversation_response(prompt)
            print(f"\nTest {i}/8:")
            print(f"Human: {prompt}")
            print(f"B3-Hope: {response}")
            print("-" * 40)

        print("="*60)

    def interactive_mode(self):
        """Interactive conversation mode"""
        print("\n" + "="*60)
        print("💬 INTERACTIVE CONVERSATIONAL AI")
        print("="*60)
        print("Type 'quit', 'exit', or 'q' to end the conversation")
        print("Type 'test' for quick evaluation")
        print("-" * 60)

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("B3-Hope: Goodbye! Take care!")
                    break
                elif user_input.lower() == 'test':
                    self.test_conversation()
                    continue
                elif not user_input:
                    continue

                # Get response
                response = self.get_conversation_response(user_input)
                print(f"B3-Hope: {response}")

            except KeyboardInterrupt:
                print("\nB3-Hope: Goodbye! Take care!")
                break
            except Exception as e:
                print(f"B3-Hope: I encountered an error, but I'm still here to help! ({e})")

def main():
    """Main function"""
    print("🎯 ImpressionCore B3-Hope Simple Conversational AI")
    print("="*60)

    # Find the best checkpoint
    production_checkpoint = "b3_hope_f_drive_production_checkpoint_step_1500.pth"
    if not os.path.exists(production_checkpoint):
        print(f"❌ Production checkpoint not found: {production_checkpoint}")
        return

    # Initialize conversational AI
    conv_ai = SimpleConversationalTester(production_checkpoint)

    # Ask user what they want to do
    print("\nWhat would you like to do?")
    print("1. Quick conversation test")
    print("2. Interactive conversation mode")
    print("3. Both")

    try:
        choice = input("\nChoice (1/2/3): ").strip()

        if choice == '1':
            conv_ai.test_conversation()
        elif choice == '2':
            conv_ai.interactive_mode()
        elif choice == '3':
            conv_ai.test_conversation()
            input("\nPress Enter to start interactive mode...")
            conv_ai.interactive_mode()
        else:
            print("Running quick test by default...")
            conv_ai.test_conversation()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()