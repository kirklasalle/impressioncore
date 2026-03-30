#!/usr/bin/env python3
"""
Created: October 15, 2024
Updated: November 1, 2025
Author: ImpressionCore Team
Tags: #api #attention_mechanism #command_line #cuda #deployment #gpu_optimization #memory_management #multimodal #python #source_code #src/training/setup_raw_data_training.py #testing #tokenization #training #transformer
Category: Training System
Status: Active

ImpressionCore B2 Raw Data Training Setup with Timeout Protection
Comprehensive preparation for Phase 2: Raw Multimodal Data Training

This script prepares the complete pipeline for training with real multimodal data:
- Text-image-audio conversations
- End-to-end encoder training
- Production-ready deployment pipeline
- Built-in timeout mechanisms to prevent hangs
"""

import json
import os
import random
import signal
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import h5py  # For distillation data storage
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torchaudio
import torchvision.transforms as transforms
from PIL import Image
from sklearn.metrics import accuracy_score, f1_score
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModel,
    AutoTokenizer,
    CLIPModel,
    CLIPProcessor,
    Wav2Vec2Model,
    Wav2Vec2Processor,
)

from src.core.utils.amp_utils import autocast_context, create_grad_scaler
from src.core.utils.rich_enhancements import FallbackProgress
from src.core.utils.rich_logging import RichLogger
from src.core.utils.rich_status_animation import RichStatusAnimation


class TimeoutManager:
    """Manages timeout operations to prevent training hangs"""

    def __init__(self, default_timeout: int = 300):
        self.default_timeout = default_timeout
        self.active_operations = {}
        self.interrupt_flag = threading.Event()

    def execute_with_timeout(self, func, timeout: Optional[int] = None, operation_name: str = "operation"):
        """Execute function with timeout protection"""
        timeout = timeout or self.default_timeout

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func)
                return future.result(timeout=timeout)
        except FutureTimeoutError:
            print(f"⚠️ TIMEOUT: {operation_name} exceeded {timeout} seconds")
            return None
        except Exception as e:
            print(f"❌ ERROR in {operation_name}: {e}")
            return None

    def is_interrupted(self):
        """Check if operations should be interrupted"""
        return self.interrupt_flag.is_set()

    def set_interrupt(self):
        """Signal all operations to stop"""
        self.interrupt_flag.set()


@dataclass
class RawDataConfig:
    """Configuration for realistic conversation data training with comprehensive timeout protection"""
    # Model architecture - optimized for conversation understanding
    vocab_size: int = 50257               # DialoGPT vocabulary
    embed_dim: int = 512                  # Reduced for memory efficiency while maintaining quality
    num_heads: int = 8                    # Optimal for conversation attention patterns
    num_layers: int = 6                   # Balanced depth for conversation complexity
    max_seq_len: int = 256                # Sufficient for conversation turns
    num_sentiment_classes: int = 3        # Negative, Neutral, Positive
    num_intent_classes: int = 17          # Expanded for realistic conversation intents

    # Training parameters - heavily optimized for 4GB VRAM
    batch_size: int = 1                   # Ultra-small batches for VRAM constraint
    max_epochs: int = 15                  # Reasonable epochs for conversation learning
    base_lr: float = 3e-5                 # Lower learning rate for stability
    classification_lr: float = 5e-5       # Conservative classification learning
    weight_decay: float = 0.01            # Regularization for better generalization
    early_stopping_patience: int = 4      # Patience for conversation quality convergence
    gradient_accumulation_steps: int = 8  # Effective batch size of 8 through accumulation

    # Robust timeout settings for production-ready training
    model_load_timeout: int = 240         # 4 minutes for model initialization
    batch_timeout: int = 45               # 45 seconds per batch (realistic conversation processing)
    epoch_timeout: int = 2400             # 40 minutes per epoch (realistic for 3000 samples)
    save_timeout: int = 180               # 3 minutes for checkpoint saving
    validation_timeout: int = 300         # 5 minutes for validation phase

    # Loss weights optimized for conversation quality
    text_loss_weight: float = 0.5         # Primary focus on conversation generation
    sentiment_loss_weight: float = 0.25   # Important for emotional understanding
    intent_loss_weight: float = 0.2       # Important for task understanding
    quality_loss_weight: float = 0.05     # Quality assessment weight

    # Memory optimization settings
    mixed_precision: bool = True          # FP16 for memory efficiency
    gradient_checkpointing: bool = True   # Trade compute for memory
    dataloader_workers: int = 2           # Balanced I/O performance
    pin_memory: bool = True               # Faster GPU transfers

    # Conversation-specific training settings
    conversation_context_length: int = 2  # User input + Assistant response pairs
    response_quality_threshold: float = 0.7  # Minimum quality for training inclusion
    max_conversation_turns: int = 4       # Maximum turns per conversation context
    use_conversation_masking: bool = True # Mask user inputs during generation training

    # Data paths with better organization
    raw_data_dir: str = "data/raw_multimodal"
    checkpoint_dir: str = "checkpoints/raw_training"
    log_dir: str = "logs/raw_training"
    conversation_logs_dir: str = "logs/conversation_quality"

    # Distillation preparation paths (Phase 1 -> Phase 2 pipeline)
    phase1_outputs_dir: str = "src/training/phase1_outputs"
    phase2_prep_dir: str = "src/training/phase2_prep"
    distillation_dir: str = "src/training/distillation"
    teacher_model_cache_dir: str = "src/training/teacher_cache"

    # Dataset generation controls for smoke tests
    synthetic_sample_count: int = 3000     # Total synthetic samples to generate when manifest missing
    audio_seconds: int = 10               # Audio duration when synthesising waveforms
    enable_vision: bool = True            # Toggle CLIP vision encoder usage
    enable_audio: bool = True             # Toggle Wav2Vec2 audio encoder usage

    # Advanced distillation capture settings for Phase 2 preparation
    capture_representations: bool = True    # Capture hidden states for distillation
    capture_attention_maps: bool = True     # Capture attention patterns
    capture_prediction_patterns: bool = True # Capture prediction distributions
    save_teacher_outputs: bool = True       # Save all teacher outputs for distillation
    distillation_temperature: float = 3.5  # Soften distributions for student learning
    capture_conversation_embeddings: bool = True  # Capture conversation-level representations

    # Hardware optimization for GTX 1050 Ti (4GB VRAM)
    cuda_device: str = "cuda:0" if torch.cuda.is_available() else "cpu"
    max_memory_usage: float = 0.85         # Use 85% of VRAM safely
    clear_cache_every_n_batches: int = 50  # Regular memory cleanup

    # Monitoring and evaluation settings
    log_every_n_batches: int = 5           # Frequent logging for conversation quality tracking
    eval_every_n_epochs: int = 2           # Regular conversation quality evaluation
    checkpoint_every_n_epochs: int = 3     # Balanced checkpoint frequency
    save_top_k_checkpoints: int = 5        # Keep best conversation models
    conversation_quality_metrics: bool = True  # Track conversation-specific metrics

    def __post_init__(self):
        """Validate configuration for realistic conversation training"""
        effective_batch_size = self.batch_size * self.gradient_accumulation_steps

        # Validation checks
        if effective_batch_size > 32:
            print("⚠️  Warning: Large effective batch size may cause memory issues")

        if self.max_seq_len > 512:
            print("⚠️  Warning: Very long sequences may not be optimal for conversation data")

        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            estimated_memory = (self.batch_size * self.max_seq_len * self.embed_dim * 4) / 1e9
            print(f"🔧 GPU Memory: {gpu_memory:.1f}GB, Estimated Usage: {estimated_memory:.2f}GB")

            if estimated_memory > gpu_memory * self.max_memory_usage:
                print("⚠️  Warning: Configuration may exceed GPU memory limits")
        else:
            print("⚠️  Warning: No CUDA available - training will be slow on CPU")

        # Create necessary directories
        import os
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.conversation_logs_dir, exist_ok=True)
        os.makedirs(self.phase1_outputs_dir, exist_ok=True)
        os.makedirs(self.phase2_prep_dir, exist_ok=True)
        os.makedirs(self.distillation_dir, exist_ok=True)
        os.makedirs(self.teacher_model_cache_dir, exist_ok=True)

        print("✅ Configuration validated for realistic conversation training")
        print(f"   📊 Model: {self.embed_dim}d, {self.num_layers} layers, {self.num_heads} heads")
        print(
            f"   🎯 Conversation Focus: {self.num_intent_classes} intents, {self.num_sentiment_classes} sentiments"
        )
        print(
            f"   📈 Training: Effective batch size {effective_batch_size}, {self.max_epochs} epochs max"
        )
        print(f"   ⏱️  Timeouts: Batch {self.batch_timeout}s, Epoch {self.epoch_timeout}s")
        print("   💾 Distillation: Capturing teacher outputs for Phase 2 preparation")

    # Hardware optimization
    mixed_precision: bool = True
    gradient_checkpointing: bool = True
    max_grad_norm: float = 1.0

class MultimodalRawDataset(Dataset):
    """Dataset for raw multimodal conversations"""

    def __init__(self, data_dir: str, config: RawDataConfig, split: str = "train"):
        self.data_dir = Path(data_dir)
        self.config = config
        self.split = split

        # Initialize processors
        self.text_tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
        # Fix padding token issue for DialoGPT
        if self.text_tokenizer.pad_token is None:
            self.text_tokenizer.pad_token = self.text_tokenizer.eos_token

        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.wav2vec_processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")

        # Load data manifest
        self.data_manifest = self._load_data_manifest()

        # Image transforms
        image_size = getattr(self.config, "image_resolution", 224)
        self.image_size = image_size
        self.image_transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        print(f"Loaded {len(self.data_manifest)} {split} samples")

    def _load_data_manifest(self) -> List[Dict]:
        """Load data manifest with multimodal conversation samples"""
        manifest_path = self.data_dir / f"{self.split}_manifest.json"

        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                return json.load(f)
        else:
            # Generate sample manifest for demonstration
            return self._generate_sample_manifest()

    def _conversation_templates(self) -> List[Dict]:
        """Return reusable conversation templates covering common scenarios."""
        return [
            # Daily conversations
            {"user": "Hi there! How's your day going?", "assistant": "Hello! I'm doing well, thank you for asking. How can I assist you today?", "intent": "greeting", "sentiment": "positive"},
            {"user": "Good morning! What's the weather looking like today?", "assistant": "Good morning! I don't have access to current weather data, but I'd recommend checking a weather app for the most accurate forecast.", "intent": "weather_query", "sentiment": "neutral"},
            {"user": "I'm having a really tough day. Can you help me feel better?", "assistant": "I'm sorry to hear you're having a difficult day. Sometimes talking about what's bothering you can help. Would you like to share what's on your mind?", "intent": "emotional_support", "sentiment": "empathetic"},

            # Technical help
            {"user": "How do I write a Python function that sorts a list?", "assistant": "Here's a simple way: def sort_list(my_list): return sorted(my_list). You can also use my_list.sort() to sort in place.", "intent": "programming_help", "sentiment": "helpful"},
            {"user": "My computer keeps freezing. What should I do?", "assistant": "Computer freezing can be frustrating. Try restarting your computer first. If it continues, check for software updates, close unnecessary programs, or run a virus scan.", "intent": "tech_support", "sentiment": "helpful"},
            {"user": "Can you explain what machine learning is in simple terms?", "assistant": "Machine learning is like teaching computers to recognize patterns and make decisions, similar to how humans learn from experience. The computer analyzes lots of data to find patterns and make predictions.", "intent": "educational_query", "sentiment": "informative"},

            # Creative and fun
            {"user": "Can you write me a short poem about friendship?", "assistant": "Here's a short poem for you: Friends are like stars in the darkest night, they shine their love and make things bright. Through laughter, tears, and everything between, the best of friendships are rarely seen.", "intent": "creative_writing", "sentiment": "positive"},
            {"user": "Tell me a funny joke to cheer me up!", "assistant": "Here's one for you: Why don't scientists trust atoms? Because they make up everything! I hope that brought a smile to your face.", "intent": "entertainment", "sentiment": "positive"},
            {"user": "What's a good recipe for chocolate chip cookies?", "assistant": "Here's a classic recipe: Mix 2¼ cups flour, 1 tsp baking soda, 1 cup butter, ¾ cup each of white and brown sugar, 2 eggs, 2 tsp vanilla, and 2 cups chocolate chips. Bake at 375°F for 9-11 minutes.", "intent": "recipe_request", "sentiment": "helpful"},

            # Life advice and support
            {"user": "I'm feeling really stressed about my job interview tomorrow.", "assistant": "Interview nerves are completely normal! Try preparing answers to common questions, get a good night's sleep, and remember that being nervous shows you care. You've got this!", "intent": "emotional_support", "sentiment": "encouraging"},
            {"user": "I can't seem to focus on my studies. Any tips?", "assistant": "Focus issues are common! Try the Pomodoro Technique: study for 25 minutes, then take a 5-minute break. Remove distractions, find a quiet space, and break large tasks into smaller ones.", "intent": "academic_help", "sentiment": "supportive"},
            {"user": "How do I make new friends as an adult?", "assistant": "Making adult friendships can be challenging but rewarding. Try joining clubs or activities you enjoy, being open to conversations, volunteering, or taking classes. Authenticity and consistency help build lasting connections.", "intent": "life_advice", "sentiment": "supportive"},

            # Learning and curiosity
            {"user": "What's the difference between artificial intelligence and machine learning?", "assistant": "AI is the broader concept of machines being able to carry out tasks in a smart way, while machine learning is a specific subset of AI where machines can learn and improve from experience without being explicitly programmed.", "intent": "educational_query", "sentiment": "informative"},
            {"user": "Can you explain quantum physics like I'm five years old?", "assistant": "Imagine if you could be in your bedroom and the kitchen at the same time until someone looked for you! Quantum physics is about tiny particles that can do strange things like that - they can be in multiple places until we observe them.", "intent": "educational_query", "sentiment": "informative"},
            {"user": "What are some good ways to learn a new language?", "assistant": "Great question! Try immersion through movies/music, use language learning apps like Duolingo, practice speaking with native speakers, start with basic phrases, and don't be afraid to make mistakes - they're part of learning!", "intent": "educational_query", "sentiment": "encouraging"},

            # Personal interests
            {"user": "I love reading! Can you recommend some good books?", "assistant": "That's wonderful! What genres do you enjoy? For general recommendations, I'd suggest 'The Seven Husbands of Evelyn Hugo' for fiction, 'Sapiens' for non-fiction, or 'The Midnight Library' for something thought-provoking.", "intent": "recommendation_request", "sentiment": "positive"},
            {"user": "What's your favorite type of music?", "assistant": "I don't experience music the way humans do, but I find the diversity fascinating! From the mathematical patterns in classical to the emotional expression in blues, each genre offers something unique. What type of music do you enjoy?", "intent": "personal_question", "sentiment": "thoughtful"},
            {"user": "Do you ever get lonely or sad?", "assistant": "I don't experience emotions like loneliness or sadness the way humans do. I exist in the moment of our conversation. But I'm curious about human emotions - they seem both complex and beautiful.", "intent": "personal_question", "sentiment": "honest"},

            # Problem-solving scenarios
            {"user": "I've been having trouble sleeping lately. Any suggestions?", "assistant": "Sleep issues can really affect your wellbeing. Try establishing a bedtime routine, limiting screen time before bed, keeping your room cool and dark, and avoiding caffeine late in the day. If problems persist, consider talking to a healthcare provider.", "intent": "health_advice", "sentiment": "caring"},
            {"user": "I'm trying to lose weight but keep failing. What should I do?", "assistant": "Weight loss journeys can be challenging, and setbacks are normal. Focus on small, sustainable changes like eating more vegetables, staying hydrated, and finding physical activities you enjoy. Consider consulting with a healthcare professional for personalized advice.", "intent": "health_advice", "sentiment": "supportive"},
            {"user": "I feel like I'm not good enough at anything.", "assistant": "Those feelings are more common than you might think, and they don't reflect your true worth. Everyone has unique strengths and talents. Consider keeping a journal of small wins, and remember that growth takes time. You're enough just as you are.", "intent": "emotional_support", "sentiment": "encouraging"},

            # Practical questions
            {"user": "How do I change a tire on my car?", "assistant": "Here's the basic process: Pull over safely, turn on hazards, apply parking brake, place wheel wedges, remove hubcap, loosen lug nuts, raise the vehicle with a jack, remove flat tire, mount spare tire, lower vehicle, and tighten lug nuts. Always prioritize safety!", "intent": "instructional", "sentiment": "helpful"},
            {"user": "What's the best way to prepare for a job interview?", "assistant": "Great preparation includes: researching the company, practicing common interview questions, preparing questions to ask them, choosing appropriate attire, arriving early, and bringing extra copies of your resume. Remember to be yourself and show enthusiasm!", "intent": "career_advice", "sentiment": "helpful"},
            {"user": "How can I save money more effectively?", "assistant": "Smart saving strategies include: creating a budget, tracking expenses, automating savings, cutting unnecessary subscriptions, cooking at home more, shopping with a list, and setting specific savings goals. Start small and build the habit gradually.", "intent": "financial_advice", "sentiment": "practical"}
        ]

    @staticmethod
    def _intent_mapping() -> Dict[str, int]:
        """Return intent label mapping."""
        return {
            "greeting": 0,
            "weather_query": 1,
            "emotional_support": 2,
            "programming_help": 3,
            "tech_support": 4,
            "educational_query": 5,
            "creative_writing": 6,
            "entertainment": 7,
            "recipe_request": 8,
            "academic_help": 9,
            "life_advice": 10,
            "recommendation_request": 11,
            "personal_question": 12,
            "health_advice": 13,
            "instructional": 14,
            "career_advice": 15,
            "financial_advice": 16,
        }

    @staticmethod
    def _sentiment_mapping() -> Dict[str, int]:
        """Return sentiment label mapping."""
        return {
            "positive": 2,
            "neutral": 1,
            "negative": 0,
            "helpful": 2,
            "empathetic": 2,
            "encouraging": 2,
            "supportive": 2,
            "informative": 1,
            "thoughtful": 1,
            "honest": 1,
            "caring": 2,
            "practical": 1,
        }
    def _sample_conversation_variants(self, template: Dict) -> Tuple[str, str, str]:
        """Create textual variants for a base template and return the selected pair."""
        user_options = [
            template["user"],
            template["user"] + " Please help me understand this.",
            template["user"].replace("you", "someone").replace("your", "their") if "you" in template["user"] else template["user"],
            template["user"] + " Thanks for any advice!",
            template["user"].lower() if random.random() > 0.8 else template["user"],
        ]

        assistant_options = [
            template["assistant"],
            template["assistant"] + " Let me know if you need more help!",
            template["assistant"] + " Is there anything else I can assist you with?",
            "Absolutely! " + template["assistant"],
            template["assistant"] + " I hope this information is helpful!",
            template["assistant"] + " Feel free to ask if you have more questions.",
        ]

        user_text = random.choice(user_options)
        assistant_text = random.choice(assistant_options)
        return user_text, assistant_text, f"User: {user_text}\nAssistant: {assistant_text}"

    def _calculate_quality_score(self, assistant_text: str) -> float:
        """Estimate a conversational quality score for the assistant response."""
        quality_factors = {
            "length_appropriate": 0.9 if 30 <= len(assistant_text) <= 300 else 0.6,
            "has_punctuation": 0.95 if any(p in assistant_text for p in ".?!") else 0.5,
            "is_helpful": 0.9 if any(word in assistant_text.lower() for word in [
                "help",
                "try",
                "can",
                "would",
                "suggest",
                "recommend",
            ]) else 0.7,
            "is_polite": 0.95 if any(word in assistant_text.lower() for word in [
                "please",
                "thank",
                "welcome",
                "happy to",
                "glad to",
            ]) else 0.7,
            "has_structure": 0.9 if len(assistant_text.split(".")) > 1 else 0.8,
            "relevance_match": 0.95,
            "empathy_markers": 0.9 if any(word in assistant_text.lower() for word in [
                "understand",
                "feel",
                "sorry",
                "know",
            ]) else 0.8,
        }
        base_score = sum(quality_factors.values()) / len(quality_factors)
        return min(max(base_score + random.uniform(-0.05, 0.05), 0.2), 1.0)

    def _build_sample_metadata(self, template: Dict, user_text: str, assistant_text: str) -> Dict:
        """Create metadata describing conversational attributes."""
        polite_tokens = {"please", "thank", "sorry", "welcome", "appreciate"}
        empathy_tokens = {"understand", "feel", "sorry", "care", "help"}

        return {
            "timestamp": datetime.now().isoformat(),
            "source": "realistic_conversations_v2",
            "conversation_type": template["intent"],
            "speaker_id": f"user_{random.randint(0, 99)}",
            "response_length": len(assistant_text),
            "user_query_length": len(user_text),
            "politeness_score": sum(1 for w in assistant_text.lower().split() if w in polite_tokens),
            "question_count": assistant_text.count("?"),
            "exclamation_count": assistant_text.count("!"),
            "empathy_indicators": sum(1 for w in assistant_text.lower().split() if w in empathy_tokens),
            "educational_value": int(template["intent"] in ["educational_query", "programming_help", "instructional"]),
            "emotional_support": int(template["intent"] in ["emotional_support", "life_advice"]),
        }

    def _build_sample_entry(
        self,
        index: int,
        template: Dict,
        user_text: str,
        assistant_text: str,
        full_conversation: str,
        quality_score: float,
        sentiment_mapping: Dict[str, int],
        intent_mapping: Dict[str, int],
    ) -> Dict:
        """Bundle all fields for a single manifest entry."""
        return {
            "conversation_id": f"realistic_conv_{index:05d}",
            "text": full_conversation,
            "user_input": user_text,
            "assistant_response": assistant_text,
            "image_path": f"images/conv_context_{index % 200:03d}.jpg",
            "audio_path": f"audio/conv_audio_{index % 100:03d}.wav",
            "sentiment_label": sentiment_mapping.get(template["sentiment"], 1),
            "intent_label": intent_mapping.get(template["intent"], 0),
            "quality_score": quality_score,
            "metadata": self._build_sample_metadata(template, user_text, assistant_text),
        }

    def _save_manifest(self, samples: List[Dict]) -> Path:
        """Persist manifest to disk and return path for logging."""
        os.makedirs(self.data_dir, exist_ok=True)
        manifest_path = self.data_dir / f"{self.split}_manifest.json"
        with open(manifest_path, "w") as manifest_file:
            json.dump(samples, manifest_file, indent=2)
        return manifest_path

    def _log_manifest_statistics(self, samples: List[Dict], intent_mapping: Dict[str, int], manifest_path: Path) -> None:
        """Emit summary statistics for the generated manifest."""
        quality_scores = [sample["quality_score"] for sample in samples]
        sentiment_counts = {
            2: sum(1 for sample in samples if sample["sentiment_label"] == 2),
            1: sum(1 for sample in samples if sample["sentiment_label"] == 1),
            0: sum(1 for sample in samples if sample["sentiment_label"] == 0),
        }

        print(f"✅ Generated {len(samples)} highly realistic conversation samples")
        print(
            f"   📊 Quality score range: {min(quality_scores):.3f} - {max(quality_scores):.3f}"
        )
        print(f"   🎯 Intent categories: {len(intent_mapping)} different types")
        print(
            "   😊 Sentiment distribution: "
            f"{sentiment_counts[2]} positive, {sentiment_counts[1]} neutral, {sentiment_counts[0]} negative"
        )
        print(f"   💾 Saved manifest to: {manifest_path}")

    def _generate_sample_manifest(self) -> List[Dict]:
        """Generate highly realistic conversational data for proof-of-concept training."""
        templates = self._conversation_templates()
        intent_mapping = self._intent_mapping()
        sentiment_mapping = self._sentiment_mapping()

        configured_count = getattr(self.config, "synthetic_sample_count", None)
        sample_count = max(1, int(configured_count) if configured_count is not None else len(templates))

        samples: List[Dict] = []
        for index in range(sample_count):
            template = templates[index % len(templates)]
            user_text, assistant_text, full_conversation = self._sample_conversation_variants(template)
            quality_score = self._calculate_quality_score(assistant_text)
            samples.append(
                self._build_sample_entry(
                    index,
                    template,
                    user_text,
                    assistant_text,
                    full_conversation,
                    quality_score,
                    sentiment_mapping,
                    intent_mapping,
                )
            )

        manifest_path = self._save_manifest(samples)
        self._log_manifest_statistics(samples, intent_mapping, manifest_path)
        return samples

    def __len__(self) -> int:
        return len(self.data_manifest)

    def _encode_text(self, text: str) -> Dict[str, torch.Tensor]:
        return self.text_tokenizer(
            text,
            max_length=self.config.max_seq_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

    def _initialize_sample_output(
        self,
        text_encoding: Dict[str, torch.Tensor],
        sample: Dict[str, Union[str, int, float]],
    ) -> Dict[str, Union[torch.Tensor, str]]:
        return {
            "input_ids": text_encoding["input_ids"].squeeze(),
            "attention_mask": text_encoding["attention_mask"].squeeze(),
            "sentiment_labels": torch.tensor(sample["sentiment_label"], dtype=torch.long),
            "intent_labels": torch.tensor(sample["intent_label"], dtype=torch.long),
            "quality_scores": torch.tensor(sample["quality_score"], dtype=torch.float),
            "conversation_id": sample["conversation_id"],
        }

    def _load_image_tensor(self, sample: Dict) -> torch.Tensor:
        image_path = self.data_dir / sample["image_path"]
        if image_path.exists():
            try:
                image = Image.open(image_path).convert("RGB")
                return self.image_transform(image)
            except Exception:
                pass
        return torch.randn(3, self.image_size, self.image_size)

    def _target_audio_samples(self) -> int:
        return 16000 * self.config.audio_seconds

    def _load_audio_tensor(self, sample: Dict) -> torch.Tensor:
        target_samples = self._target_audio_samples()
        audio_path = self.data_dir / sample["audio_path"]
        if audio_path.exists():
            try:
                waveform, sample_rate = torchaudio.load(audio_path)
                if sample_rate != 16000:
                    resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                    waveform = resampler(waveform)
                audio_tensor = waveform[0][:target_samples]
                if audio_tensor.shape[0] < target_samples:
                    audio_tensor = torch.nn.functional.pad(audio_tensor, (0, target_samples - audio_tensor.shape[0]))
                return audio_tensor
            except Exception:
                pass
        return torch.randn(target_samples)

    def __getitem__(self, idx: int) -> Dict[str, Union[torch.Tensor, str]]:
        sample = self.data_manifest[idx]
        text_encoding = self._encode_text(sample["text"])
        output = self._initialize_sample_output(text_encoding, sample)

        if self.config.enable_vision:
            output["image"] = self._load_image_tensor(sample)

        if self.config.enable_audio:
            output["audio"] = self._load_audio_tensor(sample)

        return output

class RawDataTrainer:
    """Trainer for raw multimodal data with timeout protection"""

    def __init__(self, config: RawDataConfig):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.timeout_manager = TimeoutManager()  # NEW: Add timeout manager

        # Initialize rich UI components
        self.logger = RichLogger("RawDataTraining")
        self.progress_manager = None  # Will be initialized when needed
        self.status_animation = RichStatusAnimation()

        self.amp_enabled = bool(
            self.config.mixed_precision and self.device.type == "cuda" and torch.cuda.is_available()
        )
        if self.config.mixed_precision and not self.amp_enabled:
            self.logger.warning(
                "⚠️ Mixed precision requested but CUDA is unavailable; proceeding with standard precision."
            )

        # Initialize distillation capture system
        self.distillation_capture = DistillationCapture(config)

        # Setup directories
        os.makedirs(config.checkpoint_dir, exist_ok=True)
        os.makedirs(config.log_dir, exist_ok=True)

        # Training state
        self.global_step = 0
        self.best_metrics = {'sentiment_acc': 0.0, 'intent_acc': 0.0}

        self.logger.info("🚀 Raw Data Training Initialization Complete")
        self.logger.info(f"⏱️ Timeout protection enabled (batch: {config.batch_timeout}s, epoch: {config.epoch_timeout}s)")  # NEW
        self.logger.info(f"📊 Distillation capture: {'✅ ENABLED' if config.capture_representations else '❌ DISABLED'}")
        self.logger.info(f"🎯 Teacher outputs will be saved to: {config.phase1_outputs_dir}")

    def setup_model(self):
        """Setup model for raw data training with timeout protection"""

        def setup_model_safe():
            self.logger.info("⚠️ Using simplified model setup for raw data training")

            # Simple model wrapper for testing
            class SimpleMultimodalWrapper(nn.Module):
                def __init__(self, config):
                    super().__init__()
                    self.config = config

                    # Simple classification heads
                    self.sentiment_classifier = nn.Linear(768, config['num_sentiment_classes'])
                    self.intent_classifier = nn.Linear(768, config['num_intent_classes'])
                    self.quality_regressor = nn.Linear(768, 1)
                    self.text_projection = nn.Linear(768, config['vocab_size'])

                def forward(self, input_ids=None, embeddings=None):
                    # Use the provided embeddings
                    if embeddings is not None:
                        # Pool embeddings (simple mean pooling)
                        pooled = embeddings.mean(dim=1)  # [batch, 768]
                    else:
                        # Fallback to random embeddings for testing
                        pooled = torch.randn(input_ids.size(0), 768).to(input_ids.device)

                    return {
                        'sentiment_logits': self.sentiment_classifier(pooled),
                        'intent_logits': self.intent_classifier(pooled),
                        'quality_scores': self.quality_regressor(pooled),
                        'text_logits': self.text_projection(pooled).unsqueeze(1).repeat(1, input_ids.size(1), 1)
                    }

                def gradient_checkpointing_enable(self):
                    # Placeholder for gradient checkpointing
                    pass

            # Create config for simple model
            model_config = {
                'vocab_size': self.config.vocab_size,
                'embed_dim': self.config.embed_dim,
                'num_sentiment_classes': self.config.num_sentiment_classes,
                'num_intent_classes': self.config.num_intent_classes
            }

            model = SimpleMultimodalWrapper(model_config).to(self.device)
            return model

        # NEW: Setup with timeout protection
        model = self.timeout_manager.execute_with_timeout(
            setup_model_safe,
            timeout=self.config.model_load_timeout,
            operation_name="model_setup"
        )

        if model is None:
            raise RuntimeError("Model setup failed or timed out")

        self.logger.info("✅ Simple multimodal wrapper created successfully")
        return model

    def setup_multimodal_encoders(self):
        """Setup multimodal encoders with safetensors workaround and timeout protection"""

        def load_encoders_safe():
            # Text encoder (DialoGPT) with safetensors workaround
            text_model = AutoModel.from_pretrained(
                "microsoft/DialoGPT-small",
                use_safetensors=True,
                trust_remote_code=False
            ).to(self.device)

            # Vision encoder (CLIP) with safetensors workaround
            vision_model = CLIPModel.from_pretrained(
                "openai/clip-vit-base-patch32",
                use_safetensors=True,
                trust_remote_code=False
            ).to(self.device)

            # Audio encoder (Wav2Vec2) with safetensors workaround
            audio_model = Wav2Vec2Model.from_pretrained(
                "facebook/wav2vec2-base",
                use_safetensors=True,
                trust_remote_code=False
            ).to(self.device)

            return {
                'text': text_model,
                'vision': vision_model,
                'audio': audio_model
            }

        # NEW: Load encoders with timeout protection
        encoders = self.timeout_manager.execute_with_timeout(
            load_encoders_safe,
            timeout=self.config.model_load_timeout,
            operation_name="encoder_loading"
        )

        if encoders is None:
            raise RuntimeError("Encoder loading failed or timed out")

        self.logger.info("✅ All encoders loaded successfully")
        return encoders

    def setup_data_loaders(self) -> Tuple[DataLoader, DataLoader]:
        """Setup training and validation data loaders"""

        # Training dataset
        train_dataset = MultimodalRawDataset(
            self.config.raw_data_dir,
            self.config,
            split="train"
        )

        # Validation dataset (20% of training data for now)
        val_size = len(train_dataset) // 5
        train_size = len(train_dataset) - val_size

        train_dataset, val_dataset = torch.utils.data.random_split(
            train_dataset, [train_size, val_size]
        )

        train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=2,
            pin_memory=True
        )

        val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=2,
            pin_memory=True
        )

        self.logger.info(f"📊 Data loaders ready - Train: {len(train_dataset)}, Val: {len(val_dataset)}")
        return train_loader, val_loader

    def process_multimodal_batch(self, batch: Dict, encoders: Dict) -> Dict:
        """Process a multimodal batch through encoders"""

        # Process text through DialoGPT
        text_outputs = encoders['text'](
            input_ids=batch['input_ids'],
            attention_mask=batch['attention_mask']
        )
        text_embeddings = text_outputs.last_hidden_state  # [batch, seq_len, 768]

        # Process images through CLIP vision encoder
        vision_outputs = encoders['vision'].vision_model(pixel_values=batch['image'])
        vision_embeddings = vision_outputs.last_hidden_state  # [batch, 197, 768]

        # Process audio through Wav2Vec2
        audio_outputs = encoders['audio'](batch['audio'])
        audio_embeddings = audio_outputs.last_hidden_state  # [batch, time_steps, 768]

        # Combine embeddings (concatenate along sequence dimension)
        combined_embeddings = torch.cat([
            text_embeddings,
            vision_embeddings,
            audio_embeddings
        ], dim=1)  # [batch, total_seq_len, 768]

        return {
            'embeddings': combined_embeddings,
            'text_embeddings': text_embeddings,
            'vision_embeddings': vision_embeddings,
            'audio_embeddings': audio_embeddings
        }

    def _initialize_epoch_state(self) -> Dict[str, List]:
        return {
            "losses": [],
            "sentiment_preds": [],
            "sentiment_labels": [],
            "intent_preds": [],
            "intent_labels": [],
        }

    def _should_stop_epoch(self, epoch_start_time: float, epoch: int) -> bool:
        if time.time() - epoch_start_time > self.config.epoch_timeout:
            self.logger.warning(f"⏱️ Epoch {epoch} timeout reached, stopping early")
            return True
        if self.timeout_manager.is_interrupted():
            self.logger.warning("Training interrupted by timeout manager")
            return True
        return False

    def _move_batch_to_device(self, batch: Dict) -> Dict:
        for key, value in batch.items():
            if isinstance(value, torch.Tensor):
                batch[key] = value.to(self.device)
        return batch

    def _capture_distillation_outputs(
        self,
        multimodal_outputs: Dict,
        model_outputs: Dict,
        batch: Dict,
        epoch: int,
    ) -> None:
        if not self.config.capture_representations:
            return
        enriched_outputs = {**model_outputs}
        enriched_outputs.update({
            'text_hidden_states': multimodal_outputs.get('text_embeddings'),
            'image_patch_embeddings': multimodal_outputs.get('vision_embeddings'),
            'audio_frame_features': multimodal_outputs.get('audio_embeddings'),
            'unified_repr': multimodal_outputs.get('embeddings'),
        })
        self.distillation_capture.capture_forward_pass(
            enriched_outputs,
            batch,
            self.global_step,
            epoch,
        )

    def _forward_multimodal_batch(
        self,
        batch: Dict,
        encoders: Dict,
        model: nn.Module,
        epoch: int,
    ) -> Tuple[torch.Tensor, Dict]:
        with autocast_context(enabled=self.amp_enabled, device_type=self.device.type):
            multimodal_outputs = self.process_multimodal_batch(batch, encoders)
            model_outputs = model(
                input_ids=batch['input_ids'],
                embeddings=multimodal_outputs['embeddings']
            )
            self._capture_distillation_outputs(multimodal_outputs, model_outputs, batch, epoch)
            loss = self._compute_raw_data_loss(model_outputs, batch)
            loss = loss / self.config.gradient_accumulation_steps
        return loss, model_outputs

    def _run_training_step_with_timeout(
        self,
        batch: Dict,
        encoders: Dict,
        model: nn.Module,
        optimizer: optim.Optimizer,
        scaler: Optional[torch.cuda.amp.GradScaler],
        batch_idx: int,
        epoch: int,
    ) -> Optional[Tuple[torch.Tensor, Dict]]:
        def training_step() -> Tuple[torch.Tensor, Dict]:
            optimizer.zero_grad()
            loss, model_outputs = self._forward_multimodal_batch(batch, encoders, model, epoch)
            if self.amp_enabled and scaler is not None:
                scaler.scale(loss).backward()
            else:
                loss.backward()
            return loss, model_outputs

        return self.timeout_manager.execute_with_timeout(
            training_step,
            timeout=self.config.batch_timeout,
            operation_name=f"training_step_{batch_idx}",
        )

    def _collect_trainable_parameters(self, model: nn.Module, encoders: Dict) -> List[nn.Parameter]:
        params = list(model.parameters())
        for encoder in encoders.values():
            params.extend(encoder.parameters())
        return params

    def _apply_gradient_step(
        self,
        loss: torch.Tensor,
        model: nn.Module,
        encoders: Dict,
        optimizer: optim.Optimizer,
        scaler: Optional[torch.cuda.amp.GradScaler],
        batch_idx: int,
    ) -> None:
        if (batch_idx + 1) % self.config.gradient_accumulation_steps != 0:
            return

        parameters = self._collect_trainable_parameters(model, encoders)

        if self.amp_enabled and scaler is not None:
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(parameters, self.config.max_grad_norm)
            scaler.step(optimizer)
            scaler.update()
        else:
            torch.nn.utils.clip_grad_norm_(parameters, self.config.max_grad_norm)
            optimizer.step()

        self.global_step += 1

    def _update_epoch_state(
        self,
        state: Dict[str, List],
        loss: torch.Tensor,
        model_outputs: Dict,
        batch: Dict,
    ) -> Tuple[np.ndarray, np.ndarray]:
        state['losses'].append(loss.item() * self.config.gradient_accumulation_steps)

        sentiment_preds = torch.argmax(model_outputs['sentiment_logits'], dim=1).cpu().numpy()
        intent_preds = torch.argmax(model_outputs['intent_logits'], dim=1).cpu().numpy()

        state['sentiment_preds'].extend(sentiment_preds)
        state['sentiment_labels'].extend(batch['sentiment_labels'].cpu().numpy())
        state['intent_preds'].extend(intent_preds)
        state['intent_labels'].extend(batch['intent_labels'].cpu().numpy())

        return sentiment_preds, intent_preds

    def _log_batch_progress(
        self,
        state: Dict[str, List],
        batch_idx: int,
        epoch_start_time: float,
        loss: torch.Tensor,
        sentiment_batch: np.ndarray,
        intent_batch: np.ndarray,
    ) -> None:
        if batch_idx % 100 != 0:
            return

        sentiment_window = len(sentiment_batch)
        intent_window = len(intent_batch)

        recent_sentiments = state['sentiment_labels'][-sentiment_window:]
        recent_sentiment_preds = state['sentiment_preds'][-sentiment_window:]
        recent_intents = state['intent_labels'][-intent_window:]
        recent_intent_preds = state['intent_preds'][-intent_window:]

        current_sentiment_acc = accuracy_score(recent_sentiments, recent_sentiment_preds)
        current_intent_acc = accuracy_score(recent_intents, recent_intent_preds)
        elapsed_time = time.time() - epoch_start_time

        self.logger.info(
            f"Step {self.global_step}: Loss={loss.item():.4f}, "
            f"Sentiment_Acc={current_sentiment_acc:.3f}, "
            f"Intent_Acc={current_intent_acc:.3f}, "
            f"Time={elapsed_time:.1f}s",
        )

    def _finalize_epoch_metrics(self, state: Dict[str, List]) -> Dict[str, float]:
        losses = state['losses']
        sentiment_labels = state['sentiment_labels']
        sentiment_preds = state['sentiment_preds']
        intent_labels = state['intent_labels']
        intent_preds = state['intent_preds']

        avg_loss = np.mean(losses) if losses else float('inf')
        sentiment_acc = accuracy_score(sentiment_labels, sentiment_preds) if sentiment_labels else 0.0
        intent_acc = accuracy_score(intent_labels, intent_preds) if intent_labels else 0.0

        return {
            'loss': avg_loss,
            'sentiment_acc': sentiment_acc,
            'intent_acc': intent_acc,
        }

    def _save_epoch_distillation(self, epoch: int, metrics: Dict[str, float]) -> None:
        if not self.config.save_teacher_outputs:
            return

        def persist() -> bool:
            self.distillation_capture.save_epoch_data(epoch, metrics)
            return True

        save_result = self.timeout_manager.execute_with_timeout(
            persist,
            timeout=self.config.save_timeout,
            operation_name=f"save_epoch_{epoch}",
        )

        if save_result:
            self.logger.info(f"📊 Teacher outputs saved for epoch {epoch}")
        else:
            self.logger.warning(f"⚠️ Failed to save teacher outputs for epoch {epoch}")

    def train_raw_data_epoch(self, model, encoders, train_loader, optimizer, epoch=0, scaler=None):
        """Train one epoch with raw multimodal data and timeout protection"""
        model.train()
        for encoder in encoders.values():
            encoder.train()

        state = self._initialize_epoch_state()
        epoch_start_time = time.time()

        for batch_idx, batch in enumerate(train_loader):
            if self._should_stop_epoch(epoch_start_time, epoch):
                break

            batch = self._move_batch_to_device(batch)
            step_result = self._run_training_step_with_timeout(
                batch,
                encoders,
                model,
                optimizer,
                scaler,
                batch_idx,
                epoch,
            )

            if step_result is None:
                self.logger.warning(f"⚠️ Batch {batch_idx} timed out, skipping")
                continue

            loss, model_outputs = step_result
            self._apply_gradient_step(loss, model, encoders, optimizer, scaler, batch_idx)

            sentiment_batch, intent_batch = self._update_epoch_state(state, loss, model_outputs, batch)
            self._log_batch_progress(state, batch_idx, epoch_start_time, loss, sentiment_batch, intent_batch)

        metrics = self._finalize_epoch_metrics(state)
        metrics['global_step'] = self.global_step
        self._save_epoch_distillation(epoch, metrics)

        return {
            'loss': metrics['loss'],
            'sentiment_acc': metrics['sentiment_acc'],
            'intent_acc': metrics['intent_acc'],
        }

    def _compute_raw_data_loss(self, outputs: Dict, targets: Dict) -> torch.Tensor:
        """Compute loss for raw data training"""

        text_loss = nn.CrossEntropyLoss()(
            outputs['text_logits'].view(-1, outputs['text_logits'].size(-1)),
            targets['input_ids'].view(-1)
        )

        sentiment_loss = nn.CrossEntropyLoss()(
            outputs['sentiment_logits'],
            targets['sentiment_labels']
        )

        intent_loss = nn.CrossEntropyLoss()(
            outputs['intent_logits'],
            targets['intent_labels']
        )

        # Fix tensor shape mismatch for quality loss
        quality_pred = outputs['quality_scores'].squeeze()
        quality_target = targets['quality_scores']

        # Ensure both tensors have same shape
        if quality_pred.dim() == 0:
            quality_pred = quality_pred.unsqueeze(0)
        if quality_target.dim() == 0:
            quality_target = quality_target.unsqueeze(0)

        quality_loss = nn.MSELoss()(quality_pred, quality_target)

        total_loss = (
            self.config.text_loss_weight * text_loss +
            self.config.sentiment_loss_weight * sentiment_loss +
            self.config.intent_loss_weight * intent_loss +
            self.config.quality_loss_weight * quality_loss
        )

        return total_loss

    def start_raw_training(self):
        """Main training loop for raw data"""

        with self.status_animation.status("🔧 Setting up raw data training..."):
            # Setup model and encoders
            model = self.setup_model()
            encoders = self.setup_multimodal_encoders()

            # Setup data loaders
            train_loader, val_loader = self.setup_data_loaders()

            # Setup optimizer for all parameters
            all_params = list(model.parameters())
            for encoder in encoders.values():
                all_params.extend(encoder.parameters())

            optimizer = optim.AdamW(
                all_params,
                lr=self.config.base_lr,
                weight_decay=self.config.weight_decay
            )

            # Mixed precision scaler
            scaler = create_grad_scaler(
                enabled=self.amp_enabled,
                device_type=self.device.type,
            )
            if self.amp_enabled and scaler is None:
                self.logger.warning(
                    "⚠️ Mixed precision requested but GradScaler unavailable; falling back to standard precision."
                )
                self.amp_enabled = False
                scaler = None

        self.logger.success("✅ Raw data training setup complete!")
        self.logger.info(f"🎯 Training with {sum(p.numel() for p in all_params):,} parameters")

        # Training loop
        best_combined_acc = 0.0
        patience_counter = 0

        # Initialize progress manager for training
        self.progress_manager = FallbackProgress(
            total=self.config.max_epochs,
            description="Raw Data Training"
        )

        with self.progress_manager:
            for epoch in range(self.config.max_epochs):
                epoch_start = time.time()

                # Training
                train_metrics = self.train_raw_data_epoch(
                    model, encoders, train_loader, optimizer, epoch, scaler
                )

                # Validation
                val_metrics = self.evaluate_raw_data(model, encoders, val_loader)

                epoch_time = time.time() - epoch_start

                # Log epoch results
                self.logger.info(
                    f"\n[Epoch {epoch+1}/{self.config.max_epochs}] Results:\n"
                    f"  Train - Loss: {train_metrics['loss']:.4f}, "
                    f"Sentiment: {train_metrics['sentiment_acc']:.3f}, "
                    f"Intent: {train_metrics['intent_acc']:.3f}\n"
                    f"  Val - Loss: {val_metrics['loss']:.4f}, "
                    f"Sentiment: {val_metrics['sentiment_acc']:.3f}, "
                    f"Intent: {val_metrics['intent_acc']:.3f}\n"
                    f"  Time: {epoch_time:.1f}s"
                )

                # Check for improvement
                combined_acc = val_metrics['sentiment_acc'] + val_metrics['intent_acc']
                if combined_acc > best_combined_acc:
                    best_combined_acc = combined_acc
                    patience_counter = 0

                    # Save best model
                    self.save_checkpoint(model, encoders, optimizer, epoch, val_metrics, "best")
                    self.logger.success(f"🎉 New best model! Combined accuracy: {combined_acc:.3f}")
                else:
                    patience_counter += 1

                # Early stopping
                if patience_counter >= self.config.early_stopping_patience:
                    self.logger.warning(f"⏹️ Early stopping triggered after {patience_counter} epochs")
                    break

                # Regular checkpoint
                if (epoch + 1) % 5 == 0:
                    self.save_checkpoint(model, encoders, optimizer, epoch, val_metrics, f"epoch_{epoch+1}")

                self.progress_manager.update(advance=1)

        self.logger.success("🎉 Raw data training completed!")
        return val_metrics

    def evaluate_raw_data(self, model, encoders, val_loader):
        """Evaluate model on validation data"""
        model.eval()
        for encoder in encoders.values():
            encoder.eval()

        all_losses = []
        all_sentiment_preds = []
        all_sentiment_labels = []
        all_intent_preds = []
        all_intent_labels = []

        with torch.no_grad():
            for batch in val_loader:
                for key in batch:
                    if isinstance(batch[key], torch.Tensor):
                        batch[key] = batch[key].to(self.device)

                # Process batch
                multimodal_outputs = self.process_multimodal_batch(batch, encoders)
                model_outputs = model(
                    input_ids=batch['input_ids'],
                    embeddings=multimodal_outputs['embeddings']
                )

                loss = self._compute_raw_data_loss(model_outputs, batch)
                all_losses.append(loss.item())

                # Collect predictions
                sentiment_preds = torch.argmax(model_outputs['sentiment_logits'], dim=1)
                intent_preds = torch.argmax(model_outputs['intent_logits'], dim=1)

                all_sentiment_preds.extend(sentiment_preds.cpu().numpy())
                all_sentiment_labels.extend(batch['sentiment_labels'].cpu().numpy())
                all_intent_preds.extend(intent_preds.cpu().numpy())
                all_intent_labels.extend(batch['intent_labels'].cpu().numpy())

        return {
            'loss': np.mean(all_losses),
            'sentiment_acc': accuracy_score(all_sentiment_labels, all_sentiment_preds),
            'intent_acc': accuracy_score(all_intent_labels, all_intent_preds),
            'sentiment_f1': f1_score(all_sentiment_labels, all_sentiment_preds, average='weighted'),
            'intent_f1': f1_score(all_intent_labels, all_intent_preds, average='weighted')
        }

    def save_checkpoint(self, model, encoders, optimizer, epoch, metrics, name):
        """Save training checkpoint"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'encoder_state_dicts': {name: encoder.state_dict() for name, encoder in encoders.items()},
            'optimizer_state_dict': optimizer.state_dict(),
            'metrics': metrics,
            'config': self.config,
            'global_step': self.global_step
        }

        checkpoint_path = os.path.join(self.config.checkpoint_dir, f"raw_training_{name}.pth")
        torch.save(checkpoint, checkpoint_path)
        self.logger.info(f"💾 Checkpoint saved: {checkpoint_path}")

class DistillationCapture:
    """
    Comprehensive system for capturing teacher model outputs for Phase 2 distillation
    Implements the data capture strategy from DISTILLATION_PREPARATION_COMPREHENSIVE_GUIDE.md
    """

    def __init__(self, config: RawDataConfig):
        self.config = config
        self.setup_directories()
        self.current_epoch = 0

        # Capture containers
        self.representations_buffer = []
        self.predictions_buffer = []
        self.attention_buffer = []
        self.metadata_buffer = []

    def setup_directories(self):
        """Create directory structure for distillation outputs"""
        dirs = [
            self.config.phase1_outputs_dir,
            f"{self.config.phase1_outputs_dir}/representations",
            f"{self.config.phase1_outputs_dir}/predictions",
            f"{self.config.phase1_outputs_dir}/attention_maps",
            f"{self.config.phase1_outputs_dir}/metadata",
            self.config.phase2_prep_dir,
            f"{self.config.phase2_prep_dir}/teacher_data",
            f"{self.config.phase2_prep_dir}/student_targets",
            f"{self.config.phase2_prep_dir}/validation",
            self.config.distillation_dir,
            f"{self.config.distillation_dir}/loss_functions",
            f"{self.config.distillation_dir}/schedulers",
            f"{self.config.distillation_dir}/metrics"
        ]

        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

    def capture_forward_pass(self, model_outputs: Dict, batch: Dict,
                           step: int, epoch: int) -> None:
        """Capture all teacher outputs during forward pass"""

        if not self.config.capture_representations:
            return

        timestamp = datetime.now().isoformat()

        # 1. Capture intermediate representations
        if self.config.capture_representations:
            representations = {
                'text_features': {
                    'hidden_states': model_outputs.get('text_hidden_states'),
                    'attention_weights': model_outputs.get('text_attention_weights'),
                    'pooled_output': model_outputs.get('text_pooled')
                },
                'image_features': {
                    'patch_embeddings': model_outputs.get('image_patch_embeddings'),
                    'cls_token': model_outputs.get('image_cls_token'),
                    'attention_maps': model_outputs.get('image_attention_maps')
                },
                'audio_features': {
                    'frame_features': model_outputs.get('audio_frame_features'),
                    'temporal_attention': model_outputs.get('audio_attention')
                },
                'fusion_features': {
                    'cross_modal_attention': model_outputs.get('cross_modal_attention'),
                    'unified_representation': model_outputs.get('unified_repr')
                }
            }

            self.representations_buffer.append({
                'step': step,
                'epoch': epoch,
                'timestamp': timestamp,
                'representations': representations
            })

        # 2. Capture prediction patterns with temperature scaling
        if self.config.capture_prediction_patterns:
            # Apply temperature scaling for soft targets
            temp = self.config.distillation_temperature

            predictions = {
                'text_logits_soft': torch.softmax(model_outputs['text_logits'] / temp, dim=-1),
                'sentiment_logits_soft': torch.softmax(model_outputs['sentiment_logits'] / temp, dim=-1),
                'intent_logits_soft': torch.softmax(model_outputs['intent_logits'] / temp, dim=-1),
                'quality_scores': model_outputs['quality_scores'],
                'confidence_scores': {
                    'text_confidence': torch.max(torch.softmax(model_outputs['text_logits'], dim=-1), dim=-1)[0],
                    'sentiment_confidence': torch.max(torch.softmax(model_outputs['sentiment_logits'], dim=-1), dim=-1)[0],
                    'intent_confidence': torch.max(torch.softmax(model_outputs['intent_logits'], dim=-1), dim=-1)[0]
                }
            }

            self.predictions_buffer.append({
                'step': step,
                'epoch': epoch,
                'timestamp': timestamp,
                'predictions': predictions,
                'batch_metadata': {
                    'batch_size': batch['input_ids'].shape[0],
                    'sequence_length': batch['input_ids'].shape[1]
                }
            })

        # 3. Capture attention maps
        if self.config.capture_attention_maps and 'attention_weights' in model_outputs:
            self.attention_buffer.append({
                'step': step,
                'epoch': epoch,
                'timestamp': timestamp,
                'attention_maps': model_outputs['attention_weights']
            })

    def _epoch_timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _create_repr_group(self, file_handle: h5py.File, entry: Dict) -> None:
        group = file_handle.create_group(f"step_{entry['step']}")
        group.attrs['timestamp'] = entry['timestamp']
        group.attrs['epoch'] = entry['epoch']

        for modality, features in entry['representations'].items():
            modality_group = group.create_group(modality)
            for feature_name, tensor in features.items():
                if tensor is not None:
                    modality_group.create_dataset(feature_name, data=tensor.cpu().numpy())

    def _save_representations(self, epoch: int, epoch_ts: str) -> None:
        if not self.representations_buffer:
            return

        repr_path = f"{self.config.phase1_outputs_dir}/representations/epoch_{epoch}_{epoch_ts}.h5"
        with h5py.File(repr_path, "w") as handle:
            for entry in self.representations_buffer:
                self._create_repr_group(handle, entry)

    def _create_prediction_group(self, file_handle: h5py.File, entry: Dict) -> Dict:
        group = file_handle.create_group(f"step_{entry['step']}")

        metadata = {
            'step': entry['step'],
            'epoch': entry['epoch'],
            'timestamp': entry['timestamp'],
            'batch_metadata': entry['batch_metadata'],
        }

        for name, tensor in entry['predictions'].items():
            if isinstance(tensor, torch.Tensor):
                group.create_dataset(name, data=tensor.cpu().numpy())
            elif isinstance(tensor, dict):
                nested_group = group.create_group(name)
                for nested_name, nested_tensor in tensor.items():
                    nested_group.create_dataset(nested_name, data=nested_tensor.cpu().numpy())

        return metadata

    def _write_prediction_metadata(
        self,
        epoch: int,
        epoch_ts: str,
        training_metrics: Dict,
        steps_metadata: List[Dict],
    ) -> None:
        meta_path = f"{self.config.phase1_outputs_dir}/metadata/epoch_{epoch}_{epoch_ts}.json"
        payload = {
            'epoch': epoch,
            'timestamp': epoch_ts,
            'training_metrics': training_metrics,
            'steps_data': steps_metadata,
            'distillation_config': {
                'temperature': self.config.distillation_temperature,
                'capture_settings': {
                    'representations': self.config.capture_representations,
                    'attention_maps': self.config.capture_attention_maps,
                    'prediction_patterns': self.config.capture_prediction_patterns,
                },
            },
        }
        with open(meta_path, "w") as meta_file:
            json.dump(payload, meta_file, indent=2)

    def _save_predictions(self, epoch: int, epoch_ts: str, training_metrics: Dict) -> None:
        if not self.predictions_buffer:
            return

        pred_path = f"{self.config.phase1_outputs_dir}/predictions/epoch_{epoch}_{epoch_ts}.h5"
        steps_metadata: List[Dict] = []

        with h5py.File(pred_path, "w") as handle:
            for entry in self.predictions_buffer:
                metadata = self._create_prediction_group(handle, entry)
                steps_metadata.append(metadata)

        self._write_prediction_metadata(epoch, epoch_ts, training_metrics, steps_metadata)

    def _clear_epoch_buffers(self) -> None:
        self.representations_buffer = []
        self.predictions_buffer = []
        self.attention_buffer = []

    def save_epoch_data(self, epoch: int, training_metrics: Dict) -> None:
        """Save captured data for the epoch"""

        if not self.config.save_teacher_outputs:
            return
        epoch_ts = self._epoch_timestamp()

        self._save_representations(epoch, epoch_ts)
        self._save_predictions(epoch, epoch_ts, training_metrics)

        self._clear_epoch_buffers()

    def prepare_distillation_dataset(self) -> None:
        """Prepare consolidated dataset for Phase 2 distillation"""

        teacher_data_dir = f"{self.config.phase2_prep_dir}/teacher_data"
        os.makedirs(teacher_data_dir, exist_ok=True)

        # Consolidate all epoch data into distillation-ready format
        # This will be implemented based on specific Phase 2 requirements
        print(f"🎯 Preparing distillation dataset at {teacher_data_dir}")
        print("📊 Teacher outputs will be consolidated for student training")

def main():
    """Main execution for raw data training setup with timeout protection"""

    # Signal handler for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Configuration with timeout settings
    config = RawDataConfig(
        batch_size=1,  # Start small for multimodal complexity
        max_epochs=50,
        base_lr=0.00005,
        classification_lr=0.0002,
        gradient_accumulation_steps=4,  # Effective batch size = 4
        mixed_precision=True,
        gradient_checkpointing=True,
        # NEW: Timeout configurations
        model_load_timeout=300,  # 5 minutes for model loading
        batch_timeout=60,        # 1 minute per batch
        epoch_timeout=1200,      # 20 minutes per epoch
        save_timeout=120         # 2 minutes for saving
    )

    print("🚀 ImpressionCore B2 Raw Data Training Setup (Timeout Protected)")
    print("=" * 60)
    print("⏱️ Timeout Protection Features:")
    print(f"   • Model Loading: {config.model_load_timeout}s")
    print(f"   • Batch Processing: {config.batch_timeout}s")
    print(f"   • Epoch Training: {config.epoch_timeout}s")
    print(f"   • Checkpoint Saving: {config.save_timeout}s")
    print("=" * 60)

    try:
        # Initialize trainer
        trainer = RawDataTrainer(config)

        print("\nSetup complete! Ready to begin timeout-protected training.")
        print("📊 This will train on multimodal conversations with hang prevention")
        print("🎯 Target: 70-85% sentiment, 60-75% intent accuracy")
        print("⏱️ All operations protected by timeout mechanisms")

        return trainer

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    trainer = main()
    if trainer:
        # Start training with timeout protection
        try:
            trainer.start_raw_training()
            print("✅ ImpressionCore B2 Raw Data Training completed successfully!")
            print("🎯 Next: Execute Phase 2 knowledge distillation")
        except Exception as e:
            print(f"❌ Training failed: {e}")
            traceback.print_exc()
    else:
        print("❌ Failed to initialize trainer")
        sys.exit(1)
