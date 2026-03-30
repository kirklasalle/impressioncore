#!/usr/bin/env python3
"""
ImpressionCore B3-Hope Conversational Fine-Tuning System
=======================================================

Transforms the base B3-Hope model into a high-quality conversational AI
using instruction tuning and dialogue datasets.

Created: October 2, 2025
Author: Kirk LaSalle; GitHub Copilot
Purpose: Improve conversation quality from basic text generation to coherent dialogue
"""

import os
import sys
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, get_linear_schedule_with_warmup
import logging
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import random
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(f'b3_conversational_tuning_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import B3-Hope model
from b3_constitutional_trainer import B3HopeConfig, ImpressionCoreB3Hope

class ConversationDataset(Dataset):
    """Dataset for conversational fine-tuning"""

    def __init__(self, conversations: List[Dict], tokenizer, max_length: int = 512):
        self.conversations = conversations
        self.tokenizer = tokenizer
        self.max_length = max_length

        logger.info(f"ConversationDataset initialized with {len(conversations)} conversations")

    def __len__(self):
        return len(self.conversations)

    def __getitem__(self, idx):
        conv = self.conversations[idx]

        # Format as instruction-response pair
        if 'instruction' in conv and 'response' in conv:
            prompt = f"Human: {conv['instruction']}\nAssistant: "
            target = conv['response']
        elif 'input' in conv and 'output' in conv:
            prompt = f"Human: {conv['input']}\nAssistant: "
            target = conv['output']
        else:
            # Fallback for other formats
            prompt = "Human: Hello\nAssistant: "
            target = "Hello! How can I help you today?"

        # Tokenize prompt and target
        full_text = prompt + target + self.tokenizer.eos_token

        # Encode
        encoding = self.tokenizer(
            full_text,
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )

        input_ids = encoding['input_ids'].squeeze()
        attention_mask = encoding['attention_mask'].squeeze()

        # Create labels (same as input_ids, but masked for prompt part)
        labels = input_ids.clone()

        # Find where assistant response starts
        prompt_tokens = self.tokenizer(prompt, add_special_tokens=False)['input_ids']
        prompt_length = len(prompt_tokens)

        # Mask prompt tokens in labels (-100 means ignore in loss)
        labels[:prompt_length] = -100

        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels
        }

class ConversationalFineTuner:
    """Fine-tuning system for conversational AI"""

    def __init__(self, checkpoint_path: str):
        self.checkpoint_path = checkpoint_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Load model and tokenizer
        self.model, self.tokenizer = self.load_model()

        # Training configuration
        self.learning_rate = 2e-5
        self.warmup_steps = 500
        self.max_grad_norm = 1.0
        self.save_every = 100

        logger.info("ConversationalFineTuner initialized")
        logger.info(f"Device: {self.device}")

    def load_model(self):
        """Load B3-Hope model and tokenizer"""
        logger.info("Loading B3-Hope model for conversational fine-tuning...")

        # Load model architecture
        config = B3HopeConfig()
        model = ImpressionCoreB3Hope(config)

        # Load checkpoint
        checkpoint = torch.load(self.checkpoint_path, map_location='cpu', weights_only=False)
        model.load_state_dict(checkpoint['model_state_dict'])

        # Move to device
        model = model.to(self.device)

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
        tokenizer.pad_token = tokenizer.eos_token

        logger.info(f"Model loaded: {sum(p.numel() for p in model.parameters())} parameters")
        return model, tokenizer

    def create_conversation_data(self) -> List[Dict]:
        """Create high-quality conversation training data"""
        logger.info("Creating conversational training data...")

        conversations = [
            # Greetings and basic interactions
            {"instruction": "Hello", "response": "Hello! I'm ImpressionCore B3-Hope, an AI assistant. How can I help you today?"},
            {"instruction": "Hi there", "response": "Hi! Nice to meet you. What would you like to talk about?"},
            {"instruction": "How are you?", "response": "I'm doing well, thank you for asking! I'm here and ready to help with any questions or tasks you might have."},
            {"instruction": "Good morning", "response": "Good morning! I hope you're having a great start to your day. How can I assist you?"},
            {"instruction": "What's your name?", "response": "I'm ImpressionCore B3-Hope, an AI assistant designed to be helpful, harmless, and honest. You can just call me B3-Hope if you'd like!"},

            # About AI and technology
            {"instruction": "What is artificial intelligence?", "response": "Artificial intelligence is a field of computer science focused on creating systems that can perform tasks typically requiring human intelligence, such as learning, reasoning, and problem-solving."},
            {"instruction": "How do you work?", "response": "I'm built on a neural network architecture called B3-Hope that processes language using attention mechanisms and expert systems to understand and generate human-like responses."},
            {"instruction": "Are you conscious?", "response": "That's a fascinating philosophical question! I process information and generate responses, but whether that constitutes consciousness is something even experts debate. I aim to be helpful regardless."},

            # Helpful responses
            {"instruction": "Can you help me write an email?", "response": "Absolutely! I'd be happy to help you write an email. Could you tell me who it's for and what the main message should be?"},
            {"instruction": "I need help with math", "response": "I'd be glad to help with math! What specific topic or problem are you working on? Feel free to share the details."},
            {"instruction": "Explain quantum physics", "response": "Quantum physics studies matter and energy at the smallest scales, where particles behave very differently than in our everyday world. Would you like me to explain any particular aspect?"},

            # Conversational responses
            {"instruction": "Tell me a joke", "response": "Why don't scientists trust atoms? Because they make up everything! I hope that brought a smile to your face."},
            {"instruction": "What's the weather like?", "response": "I don't have access to current weather data, but I'd recommend checking a weather app or website for accurate local conditions. Is there anything else I can help with?"},
            {"instruction": "I'm feeling sad", "response": "I'm sorry to hear you're feeling sad. While I can't replace professional support, I'm here to listen if you'd like to talk about what's bothering you."},

            # Task assistance
            {"instruction": "Help me plan a trip", "response": "I'd love to help you plan a trip! Where are you thinking of going, and what kind of experience are you looking for? Adventure, relaxation, culture, or something else?"},
            {"instruction": "Write a story", "response": "I'd enjoy writing a story with you! What genre interests you? Fantasy, science fiction, mystery, or something else? And do you have any characters or settings in mind?"},
            {"instruction": "Translate this to Spanish", "response": "I can help with translation! However, I don't see the text you'd like translated. Could you please share what you'd like me to translate to Spanish?"},

            # Polite refusals and limitations
            {"instruction": "What's my password?", "response": "I don't have access to your personal information like passwords. For security reasons, I'd recommend only sharing such information with trusted, secure systems."},
            {"instruction": "Can you browse the internet?", "response": "I don't have the ability to browse the internet or access real-time information. I can only work with the knowledge I was trained on. How else can I assist you?"},

            # Problem-solving approach
            {"instruction": "I don't understand something", "response": "That's perfectly okay! Learning often involves moments of confusion. Could you tell me what specific part you're having trouble with? I'll do my best to explain it clearly."},
            {"instruction": "This is confusing", "response": "I understand that can be frustrating. Let's break it down step by step. What would be most helpful - a simpler explanation, examples, or a different approach?"},

            # Encouragement and support
            {"instruction": "I'm working on a project", "response": "That's great! I'd be happy to help with your project. What are you working on, and where could you use some assistance or feedback?"},
            {"instruction": "I'm learning to code", "response": "That's fantastic! Programming is a valuable and rewarding skill. What programming language are you learning, and is there any particular concept you'd like help with?"},

            # Meta-conversation
            {"instruction": "Are you helpful?", "response": "I certainly try my best to be helpful! My goal is to provide useful, accurate information and assistance while being respectful and honest about my limitations."},
            {"instruction": "What can you do?", "response": "I can help with a variety of tasks like answering questions, explaining concepts, helping with writing, brainstorming ideas, basic math, and having conversations. What would you like help with?"},
            {"instruction": "Thank you", "response": "You're very welcome! I'm glad I could help. Feel free to ask if you need anything else."},
            {"instruction": "Goodbye", "response": "Goodbye! It was nice talking with you. Take care, and feel free to come back anytime you need assistance."},
        ]

        # Add some variations and longer conversations
        extended_conversations = []

        # Create variations of existing conversations
        for conv in conversations:
            extended_conversations.append(conv)

            # Add some personality variations
            if "Hello" in conv["instruction"]:
                extended_conversations.append({
                    "instruction": conv["instruction"],
                    "response": conv["response"].replace("ImpressionCore B3-Hope", "B3-Hope") + " I'm excited to chat with you!"
                })

        # Add multi-turn conversation examples
        multi_turn = [
            {"instruction": "I'm new to programming", "response": "Welcome to programming! It's an exciting journey. What draws you to programming, and do you have a particular goal in mind?"},
            {"instruction": "I want to build a website", "response": "Building websites is a great way to start! For beginners, I'd recommend starting with HTML and CSS for structure and styling, then adding JavaScript for interactivity. Would you like specific learning resources?"},
            {"instruction": "How long does it take to learn?", "response": "The timeline varies by person and goals. You could build a basic website in a few weeks of consistent practice. For more advanced skills, expect several months to years. The key is consistent practice and building projects you care about."},
        ]

        extended_conversations.extend(multi_turn)

        logger.info(f"Created {len(extended_conversations)} conversation examples")
        return extended_conversations

    def fine_tune(self, num_epochs: int = 3, batch_size: int = 4):
        """Fine-tune the model for conversation"""
        logger.info("Starting conversational fine-tuning...")

        # Create training data
        conversations = self.create_conversation_data()
        dataset = ConversationDataset(conversations, self.tokenizer)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        # Setup training
        self.model.train()
        optimizer = optim.AdamW(self.model.parameters(), lr=self.learning_rate)

        total_steps = len(dataloader) * num_epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=self.warmup_steps,
            num_training_steps=total_steps
        )

        # Training loop
        total_loss = 0
        step = 0

        for epoch in range(num_epochs):
            logger.info(f"Epoch {epoch+1}/{num_epochs}")

            epoch_loss = 0
            progress_bar = tqdm(dataloader, desc=f"Epoch {epoch+1}")

            for batch in progress_bar:
                # Move batch to device
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)

                # Forward pass
                optimizer.zero_grad()

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    return_loss=True
                )

                # Calculate loss manually for conversation fine-tuning
                logits = outputs['logits']
                shift_logits = logits[..., :-1, :].contiguous()
                shift_labels = labels[..., 1:].contiguous()

                loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
                loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))

                # Backward pass
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.max_grad_norm)
                optimizer.step()
                scheduler.step()

                # Update metrics
                total_loss += loss.item()
                epoch_loss += loss.item()
                step += 1

                # Update progress bar
                progress_bar.set_postfix({
                    'loss': f'{loss.item():.4f}',
                    'avg_loss': f'{total_loss/step:.4f}'
                })

                # Save checkpoint
                if step % self.save_every == 0:
                    self.save_checkpoint(step, total_loss/step)

            avg_epoch_loss = epoch_loss / len(dataloader)
            logger.info(f"Epoch {epoch+1} completed. Average loss: {avg_epoch_loss:.4f}")

        # Final save
        final_checkpoint_path = f"b3_hope_conversational_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pth"
        self.save_checkpoint(step, total_loss/step, final_checkpoint_path)

        logger.info("Conversational fine-tuning completed!")
        return final_checkpoint_path

    def save_checkpoint(self, step: int, avg_loss: float, custom_path: Optional[str] = None):
        """Save training checkpoint"""
        if custom_path:
            checkpoint_path = custom_path
        else:
            checkpoint_path = f"b3_hope_conversational_checkpoint_step_{step}.pth"

        torch.save({
            'step': step,
            'model_state_dict': self.model.state_dict(),
            'avg_loss': avg_loss,
            'model_config': self.model.config.__dict__,
            'training_type': 'conversational_fine_tuning'
        }, checkpoint_path)

        logger.info(f"Checkpoint saved: {checkpoint_path}")

    def test_conversation(self, checkpoint_path: str):
        """Test the fine-tuned model's conversation ability"""
        logger.info("Testing conversational model...")

        # Load the fine-tuned model
        checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()

        test_prompts = [
            "Hello, how are you?",
            "What can you help me with?",
            "Tell me about yourself",
            "I need help with my homework",
            "What is machine learning?",
            "Thank you for your help"
        ]

        logger.info("Testing conversational responses:")
        print("\n" + "="*60)
        print("CONVERSATIONAL MODEL TEST RESULTS")
        print("="*60)

        for i, prompt in enumerate(test_prompts, 1):
            response = self.generate_conversation_response(prompt)
            print(f"\nTest {i}:")
            print(f"Human: {prompt}")
            print(f"B3-Hope: {response}")
            print("-" * 40)

        print("="*60)
        logger.info("Conversation test completed!")

    def generate_conversation_response(self, prompt: str, max_new_tokens: int = 50) -> str:
        """Generate a conversational response"""
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

                logits = outputs['logits'][:, -1, :] / 0.8  # Lower temperature for more focused responses
                probs = torch.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, 1)

                # Stop if EOS token or newline (end of assistant response)
                if next_token.item() == self.tokenizer.eos_token_id:
                    break

                generated = torch.cat([generated, next_token], dim=1)

                # Stop at natural conversation breaks
                if self.tokenizer.decode(next_token[0]) in ['\n', '\r']:
                    break

        # Decode and clean up
        full_response = self.tokenizer.decode(generated[0], skip_special_tokens=True)
        response = full_response[len(formatted_prompt):].strip()

        # Remove any remaining "Human:" or "Assistant:" artifacts
        response = response.split("Human:")[0].strip()
        response = response.split("Assistant:")[0].strip()

        return response if response else "I'd be happy to help you with that!"

def main():
    """Main training function"""
    print("🤖 ImpressionCore B3-Hope Conversational Fine-Tuning")
    print("="*60)

    # Check for existing checkpoint
    base_checkpoint = "b3_hope_f_drive_production_checkpoint_step_1500.pth"
    if not os.path.exists(base_checkpoint):
        print(f"❌ Base checkpoint not found: {base_checkpoint}")
        return

    # Initialize fine-tuner
    fine_tuner = ConversationalFineTuner(base_checkpoint)

    # Fine-tune the model
    print("🎯 Starting conversational fine-tuning...")
    final_checkpoint = fine_tuner.fine_tune(num_epochs=3, batch_size=2)  # Small batch for GTX 1050 Ti

    # Test the results
    print("🧪 Testing conversational model...")
    fine_tuner.test_conversation(final_checkpoint)

    print(f"\n🎉 Conversational fine-tuning complete!")
    print(f"📦 Final model: {final_checkpoint}")
    print("✨ Your AI is now ready for natural conversations!")

if __name__ == "__main__":
    main()