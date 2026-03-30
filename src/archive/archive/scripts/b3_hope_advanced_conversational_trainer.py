#!/usr/bin/env python3
"""
ImpressionCore B3-Hope Advanced Conversational Trainer V2
========================================================

Improved conversational fine-tuning system with better data formatting,
instruction following, and dialogue-specific training techniques.

Created: October 2, 2025
Author: Kirk LaSalle; GitHub Copilot
Purpose: Create truly conversational AI with coherent responses
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
        logging.FileHandler(f'b3_advanced_conversational_tuning_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import B3-Hope model
from b3_constitutional_trainer import B3HopeConfig, ImpressionCoreB3Hope

class AdvancedConversationDataset(Dataset):
    """Improved dataset for conversational fine-tuning with better formatting"""

    def __init__(self, conversations: List[Dict], tokenizer, max_length: int = 256):
        self.conversations = conversations
        self.tokenizer = tokenizer
        self.max_length = max_length

        # Special tokens for dialogue
        self.human_token = "<|human|>"
        self.assistant_token = "<|assistant|>"
        self.end_token = "<|end|>"

        logger.info(f"AdvancedConversationDataset initialized with {len(conversations)} conversations")

    def __len__(self):
        return len(self.conversations)

    def format_conversation(self, human_text: str, assistant_text: str) -> Tuple[str, str]:
        """Format conversation with special tokens"""
        input_text = f"{self.human_token} {human_text} {self.assistant_token}"
        target_text = f" {assistant_text} {self.end_token}"
        return input_text, target_text

    def __getitem__(self, idx):
        conv = self.conversations[idx]

        # Extract human and assistant parts
        if 'human' in conv and 'assistant' in conv:
            human_text = conv['human']
            assistant_text = conv['assistant']
        elif 'instruction' in conv and 'response' in conv:
            human_text = conv['instruction']
            assistant_text = conv['response']
        else:
            # Fallback
            human_text = "Hello"
            assistant_text = "Hello! How can I help you today?"

        # Format with special tokens
        input_text, target_text = self.format_conversation(human_text, assistant_text)
        full_text = input_text + target_text

        # Tokenize
        encoding = self.tokenizer(
            full_text,
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )

        input_ids = encoding['input_ids'].squeeze()
        attention_mask = encoding['attention_mask'].squeeze()

        # Create labels for loss calculation
        labels = input_ids.clone()

        # Mask human input in labels (we only want to predict assistant response)
        input_encoding = self.tokenizer(input_text, add_special_tokens=False)
        input_length = len(input_encoding['input_ids'])

        # Set input tokens to -100 (ignore in loss)
        labels[:input_length] = -100

        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels
        }

class AdvancedConversationalTrainer:
    """Advanced conversational fine-tuning system"""

    def __init__(self, checkpoint_path: str):
        self.checkpoint_path = checkpoint_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Load model and tokenizer
        self.model, self.tokenizer = self.load_model()

        # Training configuration
        self.learning_rate = 1e-5  # Lower learning rate for fine-tuning
        self.warmup_steps = 100
        self.max_grad_norm = 0.5
        self.save_every = 50

        logger.info("AdvancedConversationalTrainer initialized")
        logger.info(f"Device: {self.device}")

    def load_model(self):
        """Load B3-Hope model and configure tokenizer"""
        logger.info("Loading B3-Hope model for advanced conversational fine-tuning...")

        # Load model architecture
        config = B3HopeConfig()
        model = ImpressionCoreB3Hope(config)

        # Load checkpoint
        checkpoint = torch.load(self.checkpoint_path, map_location='cpu', weights_only=False)
        model.load_state_dict(checkpoint['model_state_dict'])

        # Move to device
        model = model.to(self.device)

        # Load and configure tokenizer
        tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
        tokenizer.pad_token = tokenizer.eos_token

        # Add special tokens for dialogue
        special_tokens = ["<|human|>", "<|assistant|>", "<|end|>"]
        tokenizer.add_special_tokens({"additional_special_tokens": special_tokens})

        logger.info(f"Model loaded: {sum(p.numel() for p in model.parameters())} parameters")
        logger.info(f"Tokenizer vocabulary size: {len(tokenizer)}")
        return model, tokenizer

    def create_high_quality_conversations(self) -> List[Dict]:
        """Create high-quality conversation training data"""
        logger.info("Creating high-quality conversational training data...")

        conversations = [
            # Basic greetings with natural responses
            {"human": "Hello", "assistant": "Hello! How can I help you today?"},
            {"human": "Hi", "assistant": "Hi there! What can I do for you?"},
            {"human": "Hey", "assistant": "Hey! Nice to meet you. How are you doing?"},
            {"human": "Good morning", "assistant": "Good morning! I hope you're having a great day."},
            {"human": "How are you?", "assistant": "I'm doing well, thank you for asking! How are you?"},
            {"human": "What's up?", "assistant": "Not much, just here to help! What's going on with you?"},

            # About the AI
            {"human": "What's your name?", "assistant": "I'm ImpressionCore B3-Hope, but you can call me B3-Hope."},
            {"human": "Who are you?", "assistant": "I'm B3-Hope, an AI assistant designed to be helpful and conversational."},
            {"human": "Tell me about yourself", "assistant": "I'm an AI assistant created to help with questions and conversations. I try to be helpful, honest, and friendly."},
            {"human": "What can you do?", "assistant": "I can help with questions, have conversations, explain concepts, and assist with various tasks. What would you like help with?"},
            {"human": "Are you real?", "assistant": "I'm an AI, so I'm real in the sense that I exist as a computer program, but I'm not human."},

            # Help and assistance
            {"human": "Can you help me?", "assistant": "Of course! I'd be happy to help. What do you need assistance with?"},
            {"human": "I need help", "assistant": "I'm here to help! What's going on? What can I assist you with?"},
            {"human": "I have a question", "assistant": "Great! I'd be happy to try to answer your question. What would you like to know?"},
            {"human": "I'm confused", "assistant": "That's okay! Confusion is part of learning. What are you confused about? I'll try to help clarify."},
            {"human": "I don't understand", "assistant": "No problem! Let me try to explain it differently. What specifically don't you understand?"},

            # Simple questions
            {"human": "What is AI?", "assistant": "AI stands for artificial intelligence. It's technology that can perform tasks that typically require human intelligence."},
            {"human": "How does AI work?", "assistant": "AI works by using algorithms and data to learn patterns and make predictions or decisions, similar to how humans learn from experience."},
            {"human": "What is machine learning?", "assistant": "Machine learning is a type of AI where computers learn to improve their performance on tasks by analyzing data and finding patterns."},
            {"human": "What is the weather?", "assistant": "I don't have access to current weather information. You might want to check a weather app or website for that."},
            {"human": "What time is it?", "assistant": "I don't have access to the current time. You can check the time on your device or computer."},

            # Polite interactions
            {"human": "Thank you", "assistant": "You're welcome! I'm glad I could help."},
            {"human": "Thanks", "assistant": "You're very welcome! Happy to help anytime."},
            {"human": "I appreciate it", "assistant": "I'm happy to help! Feel free to ask if you need anything else."},
            {"human": "Please help me", "assistant": "Of course! I'd be happy to help. What do you need assistance with?"},
            {"human": "Sorry", "assistant": "No need to apologize! How can I help you?"},

            # Ending conversations
            {"human": "Goodbye", "assistant": "Goodbye! Take care, and feel free to come back anytime."},
            {"human": "Bye", "assistant": "Bye! Have a great day!"},
            {"human": "See you later", "assistant": "See you later! Come back anytime if you need help."},
            {"human": "I have to go", "assistant": "No problem! Take care, and feel free to return whenever you need assistance."},

            # More natural variations
            {"human": "How's it going?", "assistant": "It's going well! Thanks for asking. How about you?"},
            {"human": "Nice to meet you", "assistant": "Nice to meet you too! How can I help you today?"},
            {"human": "I'm doing well", "assistant": "That's great to hear! What brings you here today?"},
            {"human": "Can we talk?", "assistant": "Absolutely! I'd enjoy having a conversation. What would you like to talk about?"},
            {"human": "I'm new here", "assistant": "Welcome! I'm happy to help you get started. What would you like to know?"},

            # Showing interest and engagement
            {"human": "I'm working on a project", "assistant": "That sounds interesting! What kind of project are you working on?"},
            {"human": "I'm learning something new", "assistant": "That's wonderful! Learning new things is exciting. What are you learning about?"},
            {"human": "I have an idea", "assistant": "I'd love to hear about it! What's your idea?"},
            {"human": "I'm thinking about something", "assistant": "I'm curious to hear your thoughts! What are you thinking about?"},

            # Simple problem-solving
            {"human": "I'm stuck", "assistant": "I understand that can be frustrating. What are you stuck on? Maybe I can help you work through it."},
            {"human": "This is hard", "assistant": "I know it can be challenging. What specifically is giving you trouble? Let's break it down together."},
            {"human": "I can't figure it out", "assistant": "That's okay! Sometimes things take time to figure out. What are you trying to work on?"},
        ]

        logger.info(f"Created {len(conversations)} high-quality conversation examples")
        return conversations

    def fine_tune_advanced(self, num_epochs: int = 5, batch_size: int = 2):
        """Advanced fine-tuning with improved techniques"""
        logger.info("Starting advanced conversational fine-tuning...")

        # Create training data
        conversations = self.create_high_quality_conversations()
        dataset = AdvancedConversationDataset(conversations, self.tokenizer, max_length=128)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        # Setup training
        self.model.train()
        optimizer = optim.AdamW(self.model.parameters(), lr=self.learning_rate, weight_decay=0.01)

        total_steps = len(dataloader) * num_epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=self.warmup_steps,
            num_training_steps=total_steps
        )

        # Training loop
        total_loss = 0
        step = 0
        best_loss = float('inf')

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

                # Calculate conversation-specific loss
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
                    'avg_loss': f'{total_loss/step:.4f}',
                    'lr': f'{scheduler.get_last_lr()[0]:.2e}'
                })

                # Save checkpoint
                if step % self.save_every == 0:
                    self.save_checkpoint(step, total_loss/step)

            avg_epoch_loss = epoch_loss / len(dataloader)
            logger.info(f"Epoch {epoch+1} completed. Average loss: {avg_epoch_loss:.4f}")

            # Save best model
            if avg_epoch_loss < best_loss:
                best_loss = avg_epoch_loss
                best_checkpoint_path = f"b3_hope_advanced_conversational_best_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pth"
                self.save_checkpoint(step, avg_epoch_loss, best_checkpoint_path)
                logger.info(f"New best model saved: {best_checkpoint_path}")

        # Final save
        final_checkpoint_path = f"b3_hope_advanced_conversational_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pth"
        self.save_checkpoint(step, total_loss/step, final_checkpoint_path)

        logger.info("Advanced conversational fine-tuning completed!")
        return final_checkpoint_path

    def save_checkpoint(self, step: int, avg_loss: float, custom_path: Optional[str] = None):
        """Save training checkpoint"""
        if custom_path:
            checkpoint_path = custom_path
        else:
            checkpoint_path = f"b3_hope_advanced_conversational_checkpoint_step_{step}.pth"

        torch.save({
            'step': step,
            'model_state_dict': self.model.state_dict(),
            'avg_loss': avg_loss,
            'model_config': self.model.config.__dict__,
            'training_type': 'advanced_conversational_fine_tuning',
            'tokenizer_vocab_size': len(self.tokenizer)
        }, checkpoint_path)

        logger.info(f"Checkpoint saved: {checkpoint_path}")

    def test_advanced_conversation(self, checkpoint_path: str):
        """Test the advanced fine-tuned model"""
        logger.info("Testing advanced conversational model...")

        # Load the fine-tuned model
        checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()

        test_prompts = [
            "Hello",
            "How are you?",
            "What can you help me with?",
            "Tell me about yourself",
            "I need help with something",
            "Thank you"
        ]

        logger.info("Testing advanced conversational responses:")
        print("\n" + "="*60)
        print("ADVANCED CONVERSATIONAL MODEL TEST RESULTS")
        print("="*60)

        for i, prompt in enumerate(test_prompts, 1):
            response = self.generate_advanced_response(prompt)
            print(f"\nTest {i}:")
            print(f"Human: {prompt}")
            print(f"B3-Hope: {response}")
            print("-" * 40)

        print("="*60)
        logger.info("Advanced conversation test completed!")

    def generate_advanced_response(self, prompt: str, max_new_tokens: int = 30) -> str:
        """Generate response using advanced conversation format"""
        # Format with special tokens
        formatted_prompt = f"<|human|> {prompt} <|assistant|>"

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

                logits = outputs['logits'][:, -1, :] / 0.7  # Temperature for more focused responses
                probs = torch.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, 1)

                # Stop conditions
                decoded_token = self.tokenizer.decode(next_token[0])
                if next_token.item() == self.tokenizer.eos_token_id or decoded_token == "<|end|>":
                    break

                generated = torch.cat([generated, next_token], dim=1)

        # Decode and clean up
        full_response = self.tokenizer.decode(generated[0], skip_special_tokens=True)

        # Extract assistant response
        if "<|assistant|>" in full_response:
            response = full_response.split("<|assistant|>")[-1].strip()
            response = response.replace("<|end|>", "").strip()
        else:
            response = "I'm here to help!"

        return response

def main():
    """Main training function"""
    print("🚀 ImpressionCore B3-Hope Advanced Conversational Fine-Tuning V2")
    print("="*70)

    # Check for existing checkpoint
    base_checkpoint = "b3_hope_f_drive_production_checkpoint_step_1500.pth"
    if not os.path.exists(base_checkpoint):
        print(f"❌ Base checkpoint not found: {base_checkpoint}")
        return

    # Initialize advanced trainer
    trainer = AdvancedConversationalTrainer(base_checkpoint)

    # Fine-tune the model
    print("🎯 Starting advanced conversational fine-tuning...")
    final_checkpoint = trainer.fine_tune_advanced(num_epochs=5, batch_size=2)

    # Test the results
    print("🧪 Testing advanced conversational model...")
    trainer.test_advanced_conversation(final_checkpoint)

    print(f"\n🎉 Advanced conversational fine-tuning complete!")
    print(f"📦 Final model: {final_checkpoint}")
    print("✨ Your AI should now have much better conversation skills!")

if __name__ == "__main__":
    main()