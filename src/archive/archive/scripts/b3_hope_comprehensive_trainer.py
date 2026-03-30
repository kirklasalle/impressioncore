#!/usr/bin/env python3
"""
ImpressionCore B3-Hope Comprehensive Conversational Training System
==================================================================

Implements extensive raw training + Ollama distillation for true conversational AI.
CPU-based training to avoid CUDA issues, with progressive curriculum learning.

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
        logging.FileHandler(f'b3_comprehensive_training_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import B3-Hope model
from b3_constitutional_trainer import B3HopeConfig, ImpressionCoreB3Hope

class ConversationDatasetBuilder:
    """Builds comprehensive conversation datasets for training"""

    def __init__(self):
        self.conversations = []
        logger.info("ConversationDatasetBuilder initialized")

    def create_basic_conversations(self) -> List[Dict]:
        """Create basic conversation patterns"""
        logger.info("Creating basic conversation patterns...")

        basic_conversations = [
            # Greetings and introductions
            {"user": "Hello", "assistant": "Hello! I'm an AI assistant. How can I help you today?"},
            {"user": "Hi there", "assistant": "Hi! Nice to meet you. What can I do for you?"},
            {"user": "Hey", "assistant": "Hey! How's it going? What would you like to talk about?"},
            {"user": "Good morning", "assistant": "Good morning! I hope you're having a great start to your day. How can I assist you?"},
            {"user": "How are you?", "assistant": "I'm doing well, thank you for asking! I'm here and ready to help. How are you doing?"},
            {"user": "What's up?", "assistant": "Not much, just here to help! What's on your mind today?"},

            # About the assistant
            {"user": "Who are you?", "assistant": "I'm an AI assistant designed to be helpful, informative, and conversational. I can answer questions, explain concepts, and have discussions on various topics."},
            {"user": "What's your name?", "assistant": "I'm an AI assistant. You can just call me Assistant or AI. I'm here to help with whatever you need."},
            {"user": "What can you do?", "assistant": "I can help with many things! I can answer questions, explain concepts, help with problem-solving, assist with writing, have conversations, and provide information on various topics. What would you like help with?"},
            {"user": "Tell me about yourself", "assistant": "I'm an AI assistant created to be helpful and conversational. I enjoy learning about different topics and helping people with their questions and tasks. I try to be informative, friendly, and useful in our conversations."},

            # Basic questions and answers
            {"user": "What is AI?", "assistant": "AI stands for Artificial Intelligence. It refers to computer systems that can perform tasks that typically require human intelligence, such as understanding language, recognizing patterns, solving problems, and making decisions."},
            {"user": "How does AI work?", "assistant": "AI works by using algorithms and large amounts of data to learn patterns and make predictions. Machine learning models are trained on data to recognize relationships and generate responses based on what they've learned."},
            {"user": "What is machine learning?", "assistant": "Machine learning is a subset of AI where computers learn to improve their performance on tasks through experience with data, rather than being explicitly programmed for each specific task."},
            {"user": "What is the weather like?", "assistant": "I don't have access to current weather information. To get accurate weather updates, I'd recommend checking a weather app, website, or local news. Is there anything else I can help you with?"},
            {"user": "What time is it?", "assistant": "I don't have access to the current time. You can check the time on your device, computer, or by asking a voice assistant with real-time capabilities. How else can I assist you?"},

            # Help and assistance
            {"user": "Can you help me?", "assistant": "Absolutely! I'd be happy to help. What do you need assistance with? Just let me know what you're working on or what questions you have."},
            {"user": "I need help", "assistant": "Of course! I'm here to help. What specific assistance do you need? Whether it's answering questions, explaining concepts, or working through a problem, I'll do my best to assist you."},
            {"user": "I have a question", "assistant": "Great! I'd be happy to try to answer your question. What would you like to know about?"},
            {"user": "Can you explain something?", "assistant": "Certainly! I enjoy explaining things. What topic or concept would you like me to explain? I'll do my best to make it clear and understandable."},
            {"user": "I'm confused about something", "assistant": "That's okay! Confusion is a normal part of learning. What are you confused about? I'll try to help clarify things for you."},

            # Polite interactions
            {"user": "Thank you", "assistant": "You're very welcome! I'm glad I could help. Feel free to ask if you need anything else."},
            {"user": "Thanks", "assistant": "You're welcome! Happy to help anytime. Is there anything else you'd like to know?"},
            {"user": "I appreciate your help", "assistant": "I'm so glad I could be helpful! That's what I'm here for. Don't hesitate to ask if you have more questions."},
            {"user": "Please help me", "assistant": "Of course! I'm here to help. What do you need assistance with? Just tell me what you're working on."},
            {"user": "Sorry to bother you", "assistant": "No bother at all! I'm here specifically to help and answer questions. What can I do for you?"},

            # Farewells
            {"user": "Goodbye", "assistant": "Goodbye! It was nice talking with you. Feel free to come back anytime if you have more questions or just want to chat."},
            {"user": "Bye", "assistant": "Bye! Take care, and don't hesitate to return if you need any help or information."},
            {"user": "See you later", "assistant": "See you later! I'll be here whenever you need assistance. Have a great day!"},
            {"user": "I have to go", "assistant": "No problem! Thanks for the conversation. Come back anytime you need help or want to chat. Take care!"},

            # Problem-solving and learning
            {"user": "I don't understand", "assistant": "That's perfectly fine! Learning involves moments of confusion. What specifically are you having trouble understanding? I'll try to explain it in a different way."},
            {"user": "This is difficult", "assistant": "I understand that some topics can be challenging. Let's break it down into smaller, more manageable parts. What aspect would you like to start with?"},
            {"user": "Can you make it simpler?", "assistant": "Absolutely! I'll try to explain it in simpler terms. Sometimes breaking complex ideas into basic concepts makes them much easier to understand."},
            {"user": "I'm learning about this", "assistant": "That's wonderful! Learning new things is exciting. What aspects of this topic interest you most? I'd be happy to help you explore and understand it better."},
        ]

        logger.info(f"Created {len(basic_conversations)} basic conversation pairs")
        return basic_conversations

    def create_instructional_conversations(self) -> List[Dict]:
        """Create instructional and educational conversations"""
        logger.info("Creating instructional conversations...")

        instructional = [
            # Math and science
            {"user": "How do I solve 2x + 5 = 11?", "assistant": "To solve 2x + 5 = 11, first subtract 5 from both sides: 2x = 6. Then divide both sides by 2: x = 3. So the solution is x = 3."},
            {"user": "What is photosynthesis?", "assistant": "Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to create glucose (sugar) and oxygen. It's how plants make their own food and produce the oxygen we breathe."},
            {"user": "Explain gravity", "assistant": "Gravity is a fundamental force that attracts objects with mass toward each other. On Earth, it pulls everything toward the center of the planet, which is why things fall down when dropped."},

            # Technology and programming
            {"user": "What is Python?", "assistant": "Python is a popular programming language known for being easy to read and write. It's used for web development, data science, artificial intelligence, automation, and many other applications."},
            {"user": "How do I start programming?", "assistant": "To start programming, choose a beginner-friendly language like Python, find online tutorials or courses, practice with small projects, and gradually work on more complex problems. The key is consistent practice!"},
            {"user": "What is a website?", "assistant": "A website is a collection of web pages that are accessible on the internet. Websites can contain text, images, videos, and interactive elements, and are viewed using web browsers like Chrome or Firefox."},

            # Writing and communication
            {"user": "How do I write a good essay?", "assistant": "To write a good essay: start with a clear thesis, organize your ideas into paragraphs, use evidence to support your points, write clear topic sentences, and conclude by summarizing your main arguments."},
            {"user": "What makes good writing?", "assistant": "Good writing is clear, concise, and engaging. It has a logical structure, uses appropriate vocabulary, varies sentence length, and connects ideas smoothly. Most importantly, it communicates effectively with the intended audience."},

            # Life skills and advice
            {"user": "How do I stay organized?", "assistant": "To stay organized: use calendars and to-do lists, keep your workspace tidy, plan ahead, break large tasks into smaller steps, and develop consistent routines. Find a system that works for your lifestyle."},
            {"user": "How can I learn better?", "assistant": "To learn more effectively: take regular breaks, practice active recall, teach concepts to others, connect new information to what you already know, and get enough sleep. Everyone learns differently, so experiment to find what works best for you."},
        ]

        logger.info(f"Created {len(instructional)} instructional conversation pairs")
        return instructional

    def create_multi_turn_conversations(self) -> List[List[Dict]]:
        """Create multi-turn conversation sequences"""
        logger.info("Creating multi-turn conversations...")

        multi_turn = [
            # Learning conversation
            [
                {"user": "I want to learn about space", "assistant": "That's fascinating! Space is an amazing topic. What aspect of space interests you most? Planets, stars, galaxies, or maybe space exploration?"},
                {"user": "Tell me about planets", "assistant": "Planets are celestial bodies that orbit stars. In our solar system, we have eight planets, from Mercury closest to the Sun, to Neptune farthest away. Each has unique characteristics. Which planet would you like to know about?"},
                {"user": "What about Mars?", "assistant": "Mars is called the 'Red Planet' because of its rusty color from iron oxide. It's about half the size of Earth, has polar ice caps, and scientists believe it once had liquid water. We've sent many rovers there to explore its surface!"}
            ],

            # Problem-solving conversation
            [
                {"user": "I'm having trouble with my homework", "assistant": "I'd be happy to help! What subject is your homework in, and what specific part are you having trouble with?"},
                {"user": "It's math, and I don't understand fractions", "assistant": "Fractions can be tricky at first! A fraction represents parts of a whole. The top number (numerator) shows how many parts you have, and the bottom number (denominator) shows how many total parts. What specifically about fractions is confusing?"},
                {"user": "How do I add fractions?", "assistant": "To add fractions, first make sure they have the same denominator (bottom number). If they don't, find a common denominator. Then add the numerators (top numbers) and keep the same denominator. For example: 1/4 + 1/4 = 2/4 = 1/2."}
            ],

            # Career advice conversation
            [
                {"user": "What career should I choose?", "assistant": "Choosing a career is a big decision! It depends on your interests, skills, and values. What subjects or activities do you enjoy most? What kind of work environment appeals to you?"},
                {"user": "I like helping people and I'm good at explaining things", "assistant": "That's a great combination! Careers that involve helping people and explaining concepts include teaching, counseling, social work, healthcare, training and development, or technical writing. Do any of these sound interesting?"},
                {"user": "Teaching sounds good. What's it like?", "assistant": "Teaching can be very rewarding! Teachers help students learn and grow, create lesson plans, assess progress, and often inspire lifelong learning. It requires patience, creativity, and strong communication skills. There are many levels from elementary to university, each with different focuses."}
            ]
        ]

        logger.info(f"Created {len(multi_turn)} multi-turn conversation sequences")
        return multi_turn

    def build_comprehensive_dataset(self) -> List[Dict]:
        """Build the complete conversation dataset"""
        logger.info("Building comprehensive conversation dataset...")

        all_conversations = []

        # Add basic conversations
        all_conversations.extend(self.create_basic_conversations())

        # Add instructional conversations
        all_conversations.extend(self.create_instructional_conversations())

        # Add multi-turn conversations (flatten to individual pairs)
        multi_turn = self.create_multi_turn_conversations()
        for conversation_sequence in multi_turn:
            all_conversations.extend(conversation_sequence)

        logger.info(f"Total conversation dataset: {len(all_conversations)} pairs")
        return all_conversations

class OllamaDistillationManager:
    """Manages Ollama integration for knowledge distillation"""

    def __init__(self, model_name: str = "llama3.1:8b"):
        self.model_name = model_name
        self.base_url = "http://localhost:11434"
        self.api_url = f"{self.base_url}/api/generate"
        logger.info(f"OllamaDistillationManager initialized with model: {model_name}")

    def check_ollama_available(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json()
                available_models = [model['name'] for model in models.get('models', [])]
                if self.model_name in available_models:
                    logger.info(f"Ollama available with model {self.model_name}")
                    return True
                else:
                    logger.warning(f"Model {self.model_name} not found. Available: {available_models}")
                    return False
            else:
                logger.warning("Ollama API not responding")
                return False
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False

    def generate_response(self, prompt: str, temperature: float = 0.7) -> Optional[str]:
        """Generate response using Ollama model"""
        if not self.check_ollama_available():
            return None

        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "temperature": temperature,
                "stream": False
            }

            response = requests.post(self.api_url, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error generating Ollama response: {e}")
            return None

    def create_distillation_dataset(self, base_prompts: List[str], num_samples: int = 100) -> List[Dict]:
        """Create distillation dataset using Ollama responses"""
        logger.info(f"Creating distillation dataset with {num_samples} samples...")

        distillation_data = []

        for i, prompt in enumerate(base_prompts[:num_samples]):
            if i % 10 == 0:
                logger.info(f"Generating response {i+1}/{num_samples}")

            # Generate response with Ollama
            response = self.generate_response(prompt)
            if response:
                distillation_data.append({
                    "user": prompt,
                    "assistant": response,
                    "source": "ollama_distillation"
                })

            # Brief pause to avoid overwhelming Ollama
            time.sleep(0.5)

        logger.info(f"Created {len(distillation_data)} distillation samples")
        return distillation_data

class ConversationDataset(Dataset):
    """Dataset for conversation training"""

    def __init__(self, conversations: List[Dict], tokenizer, max_length: int = 256):
        self.conversations = conversations
        self.tokenizer = tokenizer
        self.max_length = max_length

        # Special tokens
        self.user_token = "<|user|>"
        self.assistant_token = "<|assistant|>"
        self.end_token = "<|end|>"

        logger.info(f"ConversationDataset initialized with {len(conversations)} conversations")

    def __len__(self):
        return len(self.conversations)

    def __getitem__(self, idx):
        conv = self.conversations[idx]

        # Format conversation
        user_text = conv.get('user', conv.get('instruction', ''))
        assistant_text = conv.get('assistant', conv.get('response', ''))

        # Create full conversation text
        full_text = f"{self.user_token} {user_text} {self.assistant_token} {assistant_text} {self.end_token}"

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

        # Create labels for training (same as input_ids)
        labels = input_ids.clone()

        # Mask user input tokens in labels (we only want to predict assistant response)
        user_part = f"{self.user_token} {user_text} {self.assistant_token}"
        user_encoding = self.tokenizer(user_part, add_special_tokens=False)
        user_length = len(user_encoding['input_ids'])

        # Set user tokens to -100 (ignore in loss calculation)
        labels[:user_length] = -100

        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels
        }

class ComprehensiveConversationalTrainer:
    """Comprehensive training system for conversational AI"""

    def __init__(self, checkpoint_path: str):
        self.checkpoint_path = checkpoint_path
        self.device = torch.device('cpu')  # Use CPU to avoid CUDA issues

        # Load model and tokenizer
        self.model, self.tokenizer = self.load_model()

        # Initialize components
        self.dataset_builder = ConversationDatasetBuilder()
        self.ollama_manager = OllamaDistillationManager()

        # Training configuration
        self.learning_rate = 1e-5
        self.warmup_steps = 100
        self.max_grad_norm = 1.0
        self.gradient_accumulation_steps = 8  # Simulate larger batches

        logger.info("ComprehensiveConversationalTrainer initialized")
        logger.info(f"Device: {self.device}")

    def load_model(self):
        """Load B3-Hope model"""
        logger.info("Loading B3-Hope model for comprehensive training...")

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

        # Add special tokens
        special_tokens = ["<|user|>", "<|assistant|>", "<|end|>"]
        tokenizer.add_special_tokens({"additional_special_tokens": special_tokens})

        logger.info(f"Model loaded: {sum(p.numel() for p in model.parameters())} parameters")
        return model, tokenizer

    def train_comprehensive(self, num_epochs: int = 10, batch_size: int = 1):
        """Comprehensive conversation training"""
        logger.info("Starting comprehensive conversational training...")

        # Phase 1: Basic conversation training
        logger.info("Phase 1: Basic conversation training")
        basic_conversations = self.dataset_builder.create_basic_conversations()
        self.train_phase(basic_conversations, num_epochs=3, phase_name="basic")

        # Phase 2: Instructional training
        logger.info("Phase 2: Instructional conversation training")
        all_conversations = self.dataset_builder.build_comprehensive_dataset()
        self.train_phase(all_conversations, num_epochs=5, phase_name="comprehensive")

        # Phase 3: Distillation training (if Ollama available)
        if self.ollama_manager.check_ollama_available():
            logger.info("Phase 3: Ollama distillation training")
            prompts = [conv['user'] for conv in basic_conversations[:50]]  # Use subset for distillation
            distillation_data = self.ollama_manager.create_distillation_dataset(prompts)
            if distillation_data:
                self.train_phase(distillation_data, num_epochs=3, phase_name="distillation")
        else:
            logger.info("Phase 3: Skipping distillation (Ollama not available)")

        # Final checkpoint
        final_path = f"b3_hope_comprehensive_conversational_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pth"
        self.save_checkpoint(0, 0.0, final_path)
        logger.info(f"Comprehensive training completed: {final_path}")

        return final_path

    def train_phase(self, conversations: List[Dict], num_epochs: int, phase_name: str):
        """Train on a specific phase of conversations"""
        logger.info(f"Training {phase_name} phase: {len(conversations)} conversations, {num_epochs} epochs")

        # Create dataset
        dataset = ConversationDataset(conversations, self.tokenizer)
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
        step = 0
        total_loss = 0

        for epoch in range(num_epochs):
            logger.info(f"{phase_name.title()} Phase - Epoch {epoch+1}/{num_epochs}")

            epoch_loss = 0
            progress_bar = tqdm(dataloader, desc=f"{phase_name} epoch {epoch+1}")

            for batch_idx, batch in enumerate(progress_bar):
                # Move batch to device
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)

                # Forward pass
                try:
                    outputs = self.model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        return_loss=False  # Calculate loss manually
                    )

                    # Calculate loss
                    logits = outputs['logits']
                    shift_logits = logits[..., :-1, :].contiguous()
                    shift_labels = labels[..., 1:].contiguous()

                    loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
                    loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))

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
                    total_loss += loss.item() * self.gradient_accumulation_steps
                    epoch_loss += loss.item() * self.gradient_accumulation_steps
                    step += 1

                    # Update progress bar
                    progress_bar.set_postfix({
                        'loss': f'{loss.item() * self.gradient_accumulation_steps:.4f}',
                        'avg_loss': f'{total_loss/step:.4f}'
                    })

                except Exception as e:
                    logger.error(f"Training error at step {step}: {e}")
                    continue

            avg_epoch_loss = epoch_loss / len(dataloader)
            logger.info(f"{phase_name.title()} Epoch {epoch+1} completed. Average loss: {avg_epoch_loss:.4f}")

        # Save phase checkpoint
        phase_checkpoint = f"b3_hope_{phase_name}_phase_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pth"
        self.save_checkpoint(step, total_loss/step if step > 0 else 0, phase_checkpoint)

    def save_checkpoint(self, step: int, avg_loss: float, custom_path: str):
        """Save training checkpoint"""
        torch.save({
            'step': step,
            'model_state_dict': self.model.state_dict(),
            'avg_loss': avg_loss,
            'model_config': self.model.config.__dict__,
            'training_type': 'comprehensive_conversational',
            'tokenizer_vocab_size': len(self.tokenizer)
        }, custom_path)

        logger.info(f"Checkpoint saved: {custom_path}")

    def test_conversation_quality(self, checkpoint_path: str):
        """Test conversation quality of trained model"""
        logger.info("Testing conversation quality...")

        # Load trained model
        checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()

        test_prompts = [
            "Hello",
            "How are you?",
            "What can you help me with?",
            "Tell me about yourself",
            "What is artificial intelligence?",
            "Can you explain machine learning?",
            "I need help with something",
            "Thank you"
        ]

        print("\n" + "="*70)
        print("🧪 COMPREHENSIVE CONVERSATIONAL AI QUALITY TEST")
        print("="*70)

        for i, prompt in enumerate(test_prompts, 1):
            response = self.generate_neural_response(prompt)
            print(f"\nTest {i}/8:")
            print(f"Human: {prompt}")
            print(f"B3-Hope: {response}")
            print("-" * 50)

        print("="*70)
        logger.info("Conversation quality test completed!")

    def generate_neural_response(self, prompt: str, max_new_tokens: int = 40) -> str:
        """Generate response using trained neural network"""
        # Format with special tokens
        formatted_input = f"<|user|> {prompt} <|assistant|>"

        # Tokenize
        inputs = self.tokenizer(formatted_input, return_tensors="pt").to(self.device)

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

                logits = outputs['logits'][:, -1, :] / 0.8  # Temperature
                probs = torch.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, 1)

                # Stop conditions
                if next_token.item() == self.tokenizer.eos_token_id:
                    break

                # Check for end token
                if self.tokenizer.decode(next_token[0]) == "<|end|>":
                    break

                generated = torch.cat([generated, next_token], dim=1)

        # Decode response
        full_response = self.tokenizer.decode(generated[0], skip_special_tokens=True)

        # Extract assistant response
        if "<|assistant|>" in full_response:
            response = full_response.split("<|assistant|>")[-1].strip()
            response = response.replace("<|end|>", "").strip()
        else:
            response = "I'd be happy to help you with that!"

        return response

def main():
    """Main comprehensive training function"""
    print("🚀 ImpressionCore B3-Hope Comprehensive Conversational Training")
    print("="*70)

    # Check for base checkpoint
    base_checkpoint = "b3_hope_f_drive_production_checkpoint_step_1500.pth"
    if not os.path.exists(base_checkpoint):
        print(f"❌ Base checkpoint not found: {base_checkpoint}")
        return

    # Initialize comprehensive trainer
    trainer = ComprehensiveConversationalTrainer(base_checkpoint)

    # Start comprehensive training
    print("🎯 Starting comprehensive conversational training...")
    print("This will take significant time but will create truly conversational AI!")

    final_checkpoint = trainer.train_comprehensive(num_epochs=10, batch_size=1)

    # Test the final model
    print("🧪 Testing final conversational model...")
    trainer.test_conversation_quality(final_checkpoint)

    print(f"\n🎉 Comprehensive conversational training completed!")
    print(f"📦 Final model: {final_checkpoint}")
    print("✨ B3-Hope should now be truly conversational!")

if __name__ == "__main__":
    main()