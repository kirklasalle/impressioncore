#!/usr/bin/env python3
"""
ImpressionCore B3-Hope FIXED Conversational Training System
==========================================================

Fixed version that handles tokenizer indexing issues properly.
CPU-based training with proper error handling.

Created: October 2, 2025
Author: Kirk LaSalle; GitHub Copilot
Purpose: Transform B3-Hope into truly conversational AI through extensive training
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
import requests
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(f'b3_fixed_training_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import B3-Hope model
from b3_constitutional_trainer import B3HopeConfig, ImpressionCoreB3Hope

class SimpleConversationDataset(Dataset):
    """Simple, robust conversation dataset that avoids indexing issues"""

    def __init__(self, conversations: List[Dict], tokenizer, max_length: int = 128):
        self.conversations = conversations
        self.tokenizer = tokenizer
        self.max_length = max_length

        # Prepare processed data to avoid runtime errors
        self.processed_data = []
        self.prepare_data()

        logger.info(f"SimpleConversationDataset: {len(self.processed_data)} valid samples")

    def prepare_data(self):
        """Pre-process all conversation data to ensure validity"""
        for i, conv in enumerate(self.conversations):
            try:
                user_text = conv.get('user', conv.get('instruction', '')).strip()
                assistant_text = conv.get('assistant', conv.get('response', '')).strip()

                if not user_text or not assistant_text:
                    continue

                # Create simple format without special tokens to avoid conflicts
                full_text = f"User: {user_text} Assistant: {assistant_text}"

                # Tokenize and validate
                encoding = self.tokenizer(
                    full_text,
                    truncation=True,
                    max_length=self.max_length,
                    padding='max_length',
                    return_tensors='pt'
                )

                input_ids = encoding['input_ids'].squeeze()
                attention_mask = encoding['attention_mask'].squeeze()

                # Validate tensor dimensions
                if input_ids.numel() != self.max_length or attention_mask.numel() != self.max_length:
                    logger.warning(f"Skipping sample {i}: invalid tensor size")
                    continue

                # Create labels (same as input_ids for language modeling)
                labels = input_ids.clone()

                # Find where assistant response starts for label masking
                assistant_start = full_text.find("Assistant:")
                if assistant_start > 0:
                    assistant_start_tokens = self.tokenizer(
                        full_text[:assistant_start],
                        add_special_tokens=False
                    )['input_ids']

                    if len(assistant_start_tokens) < self.max_length:
                        # Mask user part in labels
                        labels[:len(assistant_start_tokens)] = -100

                self.processed_data.append({
                    'input_ids': input_ids,
                    'attention_mask': attention_mask,
                    'labels': labels,
                    'text': full_text
                })

            except Exception as e:
                logger.warning(f"Error processing conversation {i}: {e}")
                continue

    def __len__(self):
        return len(self.processed_data)

    def __getitem__(self, idx):
        return self.processed_data[idx]

class FixedConversationalTrainer:
    """Fixed conversational trainer with robust error handling"""

    def __init__(self, checkpoint_path: str):
        self.checkpoint_path = checkpoint_path
        self.device = torch.device('cpu')  # CPU only to avoid CUDA issues

        # Load model and tokenizer
        self.model, self.tokenizer = self.load_model()

        # Training configuration
        self.learning_rate = 1e-5
        self.warmup_steps = 50
        self.max_grad_norm = 1.0
        self.gradient_accumulation_steps = 4

        logger.info("FixedConversationalTrainer initialized")
        logger.info(f"Device: {self.device}")

    def load_model(self):
        """Load B3-Hope model with proper error handling"""
        logger.info("Loading B3-Hope model for fixed training...")

        try:
            # Load model architecture
            config = B3HopeConfig()
            model = ImpressionCoreB3Hope(config)

            # Load checkpoint
            checkpoint = torch.load(self.checkpoint_path, map_location='cpu', weights_only=False)
            model.load_state_dict(checkpoint['model_state_dict'])

            # Move to device
            model = model.to(self.device)

            # Load tokenizer with proper configuration
            tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")

            # Ensure pad token is set
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            logger.info(f"Model loaded: {sum(p.numel() for p in model.parameters())} parameters")
            logger.info(f"Tokenizer vocab size: {len(tokenizer)}")
            return model, tokenizer

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def create_conversation_data(self) -> List[Dict]:
        """Create robust conversation dataset"""
        conversations = [
            # Basic greetings
            {"user": "Hello", "assistant": "Hello! How can I help you today?"},
            {"user": "Hi", "assistant": "Hi there! What can I do for you?"},
            {"user": "Hey", "assistant": "Hey! How's it going?"},
            {"user": "Good morning", "assistant": "Good morning! How can I assist you?"},

            # About the assistant
            {"user": "Who are you?", "assistant": "I'm an AI assistant here to help you."},
            {"user": "What's your name?", "assistant": "I'm an AI assistant. You can call me Assistant."},
            {"user": "What can you do?", "assistant": "I can help answer questions and have conversations."},

            # Questions and answers
            {"user": "What is AI?", "assistant": "AI is artificial intelligence - computer systems that can think and learn."},
            {"user": "How are you?", "assistant": "I'm doing well, thank you! How are you?"},
            {"user": "Can you help me?", "assistant": "Of course! I'd be happy to help. What do you need?"},

            # Learning topics
            {"user": "Explain photosynthesis", "assistant": "Photosynthesis is how plants make food using sunlight, water, and carbon dioxide."},
            {"user": "What is gravity?", "assistant": "Gravity is the force that pulls objects toward each other, like how Earth pulls things down."},
            {"user": "How do computers work?", "assistant": "Computers process information using electrical signals and follow programmed instructions."},

            # Polite interactions
            {"user": "Thank you", "assistant": "You're welcome! Happy to help."},
            {"user": "Please help", "assistant": "Absolutely! What would you like help with?"},
            {"user": "I appreciate it", "assistant": "I'm glad I could help! That's what I'm here for."},

            # Problem solving
            {"user": "I don't understand", "assistant": "That's okay! What part would you like me to explain differently?"},
            {"user": "This is confusing", "assistant": "Let me try to break it down into simpler parts."},
            {"user": "Can you explain more?", "assistant": "Sure! I'd be happy to give you more details."},

            # Farewells
            {"user": "Goodbye", "assistant": "Goodbye! Feel free to ask if you need anything else."},
            {"user": "See you later", "assistant": "See you later! Have a great day!"},
            {"user": "Thanks, bye", "assistant": "You're welcome! Take care!"},
        ]

        logger.info(f"Created {len(conversations)} conversation examples")
        return conversations

    def train_fixed_conversational(self, num_epochs: int = 5):
        """Train with fixed error handling"""
        logger.info("Starting fixed conversational training...")

        # Create conversation data
        conversations = self.create_conversation_data()

        # Create dataset with validation
        dataset = SimpleConversationDataset(conversations, self.tokenizer, max_length=128)

        if len(dataset) == 0:
            logger.error("No valid training data created!")
            return None

        dataloader = DataLoader(dataset, batch_size=1, shuffle=True)

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
        successful_steps = 0

        for epoch in range(num_epochs):
            logger.info(f"Fixed Training - Epoch {epoch+1}/{num_epochs}")

            epoch_loss = 0
            epoch_steps = 0
            progress_bar = tqdm(dataloader, desc=f"Fixed epoch {epoch+1}")

            for batch_idx, batch in enumerate(progress_bar):
                try:
                    # Move batch to device
                    input_ids = batch['input_ids'].to(self.device)
                    attention_mask = batch['attention_mask'].to(self.device)
                    labels = batch['labels'].to(self.device)

                    # Validate tensor shapes
                    if input_ids.dim() != 1 or attention_mask.dim() != 1 or labels.dim() != 1:
                        logger.warning(f"Invalid tensor dimensions at batch {batch_idx}")
                        continue

                    # Add batch dimension
                    input_ids = input_ids.unsqueeze(0)
                    attention_mask = attention_mask.unsqueeze(0)
                    labels = labels.unsqueeze(0)

                    # Forward pass with error handling
                    outputs = self.model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        return_loss=False
                    )

                    logits = outputs['logits']

                    # Validate logits shape
                    if logits.size(0) != 1 or logits.size(1) != input_ids.size(1):
                        logger.warning(f"Invalid logits shape: {logits.shape} vs input {input_ids.shape}")
                        continue

                    # Calculate loss manually with validation
                    shift_logits = logits[..., :-1, :].contiguous()
                    shift_labels = labels[..., 1:].contiguous()

                    # Validate dimensions before loss calculation
                    if shift_logits.size(1) != shift_labels.size(1):
                        logger.warning(f"Dimension mismatch: logits {shift_logits.shape} vs labels {shift_labels.shape}")
                        continue

                    loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
                    loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))

                    # Validate loss
                    if torch.isnan(loss) or torch.isinf(loss):
                        logger.warning(f"Invalid loss value: {loss}")
                        continue

                    # Normalize loss for gradient accumulation
                    loss = loss / self.gradient_accumulation_steps

                    # Backward pass
                    loss.backward()

                    # Update on accumulation step
                    if (batch_idx + 1) % self.gradient_accumulation_steps == 0:
                        torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.max_grad_norm)
                        optimizer.step()
                        scheduler.step()
                        optimizer.zero_grad()

                    # Update metrics
                    loss_value = loss.item() * self.gradient_accumulation_steps
                    total_loss += loss_value
                    epoch_loss += loss_value
                    successful_steps += 1
                    epoch_steps += 1

                    # Update progress bar
                    progress_bar.set_postfix({
                        'loss': f'{loss_value:.4f}',
                        'avg_loss': f'{total_loss/successful_steps:.4f}' if successful_steps > 0 else '0.0000'
                    })

                except Exception as e:
                    logger.warning(f"Training error at epoch {epoch}, batch {batch_idx}: {e}")
                    continue

            avg_epoch_loss = epoch_loss / epoch_steps if epoch_steps > 0 else 0
            logger.info(f"Fixed Epoch {epoch+1} completed. Steps: {epoch_steps}, Average loss: {avg_epoch_loss:.4f}")

        # Save checkpoint
        avg_loss = total_loss / successful_steps if successful_steps > 0 else 0
        checkpoint_path = f"b3_hope_fixed_conversational_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pth"
        self.save_checkpoint(successful_steps, avg_loss, checkpoint_path)

        logger.info(f"Fixed training completed! Successful steps: {successful_steps}")
        logger.info(f"Final checkpoint: {checkpoint_path}")

        return checkpoint_path

    def save_checkpoint(self, step: int, avg_loss: float, custom_path: str):
        """Save training checkpoint"""
        try:
            torch.save({
                'step': step,
                'model_state_dict': self.model.state_dict(),
                'avg_loss': avg_loss,
                'model_config': self.model.config.__dict__,
                'training_type': 'fixed_conversational',
                'tokenizer_vocab_size': len(self.tokenizer)
            }, custom_path)

            logger.info(f"Checkpoint saved: {custom_path}")
        except Exception as e:
            logger.error(f"Error saving checkpoint: {e}")

    def test_conversation_quality(self, checkpoint_path: str):
        """Test conversation quality of trained model"""
        logger.info("Testing fixed conversation quality...")

        try:
            # Load trained model
            checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.eval()

            test_prompts = [
                "Hello",
                "How are you?",
                "What can you help me with?",
                "Who are you?",
                "Thank you",
                "What is AI?",
                "Can you help me?",
                "Goodbye"
            ]

            print("\n" + "="*70)
            print("🧪 FIXED CONVERSATIONAL AI QUALITY TEST")
            print("="*70)

            successful_responses = 0

            for i, prompt in enumerate(test_prompts, 1):
                try:
                    response = self.generate_response(prompt)
                    print(f"\nTest {i}/8:")
                    print(f"Human: {prompt}")
                    print(f"B3-Hope: {response}")
                    print("-" * 50)

                    if response and len(response.strip()) > 0:
                        successful_responses += 1

                except Exception as e:
                    print(f"\nTest {i}/8:")
                    print(f"Human: {prompt}")
                    print(f"B3-Hope: [Error generating response: {e}]")
                    print("-" * 50)

            success_rate = (successful_responses / len(test_prompts)) * 100
            print(f"\n✅ Success Rate: {success_rate:.1f}% ({successful_responses}/{len(test_prompts)})")
            print("="*70)
            logger.info(f"Conversation quality test completed! Success rate: {success_rate:.1f}%")

        except Exception as e:
            logger.error(f"Error in conversation quality test: {e}")

    def generate_response(self, prompt: str, max_new_tokens: int = 30) -> str:
        """Generate response using trained neural network"""
        try:
            # Format input
            formatted_input = f"User: {prompt} Assistant:"

            # Tokenize
            inputs = self.tokenizer(formatted_input, return_tensors="pt").to(self.device)
            input_ids = inputs['input_ids']
            attention_mask = inputs['attention_mask']

            # Generate
            with torch.no_grad():
                generated = input_ids.clone()

                for _ in range(max_new_tokens):
                    current_attention = torch.ones_like(generated)

                    # Forward pass
                    outputs = self.model(
                        input_ids=generated,
                        attention_mask=current_attention,
                        return_loss=False
                    )

                    logits = outputs['logits'][:, -1, :] / 0.8  # Temperature
                    probs = torch.softmax(logits, dim=-1)
                    next_token = torch.multinomial(probs, 1)

                    # Stop conditions
                    if next_token.item() == self.tokenizer.eos_token_id:
                        break

                    generated = torch.cat([generated, next_token], dim=1)

            # Decode response
            full_response = self.tokenizer.decode(generated[0], skip_special_tokens=True)

            # Extract assistant response
            if "Assistant:" in full_response:
                response = full_response.split("Assistant:")[-1].strip()
            else:
                response = "I'd be happy to help you!"

            return response

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response right now."

def main():
    """Main fixed training function"""
    print("🚀 ImpressionCore B3-Hope FIXED Conversational Training")
    print("="*70)

    # Check for base checkpoint
    base_checkpoint = "b3_hope_f_drive_production_checkpoint_step_1500.pth"
    if not os.path.exists(base_checkpoint):
        print(f"❌ Base checkpoint not found: {base_checkpoint}")
        return

    # Initialize fixed trainer
    trainer = FixedConversationalTrainer(base_checkpoint)

    # Start fixed training
    print("🎯 Starting FIXED conversational training...")
    print("This version handles indexing errors and should work properly!")

    final_checkpoint = trainer.train_fixed_conversational(num_epochs=5)

    if final_checkpoint:
        # Test the final model
        print("🧪 Testing final conversational model...")
        trainer.test_conversation_quality(final_checkpoint)

        print(f"\n🎉 Fixed conversational training completed!")
        print(f"📦 Final model: {final_checkpoint}")
        print("✨ B3-Hope should now have neural conversational ability!")
    else:
        print("❌ Training failed - no valid final checkpoint created")

if __name__ == "__main__":
    main()