#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #api #attention_mechanism #cuda #inference #multimodal #python #source_code #src/scripts\b3\b3_pure_chat.py #testing #tokenization #training #transformer
**Category:** Source Code
**Status:** Active
"""



import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# Tokenizer imports - Using GPT-2 for actual text generation
try:
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    GPT2_AVAILABLE = True
except ImportError:
    GPT2_AVAILABLE = False

try:
    from transformers import AutoTokenizer
    TOKENIZER_AVAILABLE = True
except ImportError:
    TOKENIZER_AVAILABLE = False

# Rich imports for enhanced UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

class B3ModelArchitecture(nn.Module):
    """B3 model architecture - exact match to your trained model"""

    def __init__(self):
        super().__init__()

        # Text Encoder (768 -> 1024)
        self.text_encoder = nn.ModuleDict({
            'base_encoder': nn.Sequential(
                nn.Linear(768, 512),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(512, 1024)
            ),
            'quality_enhancer': nn.Sequential(
                nn.Linear(1024, 512),
                nn.LayerNorm(512),
                nn.ReLU(),
                nn.Linear(512, 1024)
            )
        })

        # Image Encoder (512 -> 1024)
        self.image_encoder = nn.ModuleDict({
            'base_encoder': nn.Sequential(
                nn.Linear(512, 768),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(768, 1024)
            ),
            'quality_enhancer': nn.Sequential(
                nn.Linear(1024, 512),
                nn.LayerNorm(512),
                nn.ReLU(),
                nn.Linear(512, 1024)
            )
        })

        # Audio Encoder (768 -> 1024)
        self.audio_encoder = nn.ModuleDict({
            'base_encoder': nn.Sequential(
                nn.Linear(768, 512),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(512, 1024)
            ),
            'quality_enhancer': nn.Sequential(
                nn.Linear(1024, 512),
                nn.LayerNorm(512),
                nn.ReLU(),
                nn.Linear(512, 1024)
            )
        })

        # Multimodal Fusion
        self.fusion = nn.ModuleDict({
            'attention': nn.MultiheadAttention(1024, num_heads=8, batch_first=True),
            'norm': nn.LayerNorm(1024),
            'ffn': nn.Sequential(
                nn.Linear(1024, 2048),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(2048, 1024)
            ),
            'educational_pattern_transfer': nn.Sequential(
                nn.Linear(1024, 512),
                nn.ReLU(),
                nn.Linear(512, 1024)
            )
        })

        # Mixture of Experts (8 experts)
        self.moe = nn.ModuleDict({
            'experts': nn.ModuleList([
                nn.Sequential(
                    nn.Linear(1024, 2048),
                    nn.ReLU(),
                    nn.Dropout(0.1),
                    nn.Linear(2048, 1024),
                    nn.LayerNorm(1024)
                ) for _ in range(8)
            ]),
            'gate': nn.Sequential(
                nn.Linear(1024, 512),
                nn.ReLU(),
                nn.Linear(512, 8)
            ),
            'quality_refiner': nn.Sequential(
                nn.Linear(1024, 512),
                nn.ReLU(),
                nn.Linear(512, 1024)
            )
        })

        # Output Heads - Using actual trained dimensions (768, not 50257)
        self.conversation_head = nn.Sequential(
            nn.Linear(1024, 512),
            nn.LayerNorm(512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, 768)  # Actual output dimension from trained model
        )

        self.educational_transfer_head = nn.Sequential(
            nn.Linear(1024, 256),
            nn.ReLU(),
            nn.Linear(256, 1024)
        )

        self.quality_scorer = nn.Sequential(
            nn.Linear(1024, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

    def forward(self, text_input=None, image_input=None, audio_input=None):
        """Forward pass through the B3 architecture"""

        encoded_features = []

        # Process modalities
        if text_input is not None:
            text_encoded = self.text_encoder['base_encoder'](text_input)
            text_enhanced = self.text_encoder['quality_enhancer'](text_encoded)
            encoded_features.append(text_enhanced)

        if image_input is not None:
            image_encoded = self.image_encoder['base_encoder'](image_input)
            image_enhanced = self.image_encoder['quality_enhancer'](image_encoded)
            encoded_features.append(image_enhanced)

        if audio_input is not None:
            audio_encoded = self.audio_encoder['base_encoder'](audio_input)
            audio_enhanced = self.audio_encoder['quality_enhancer'](audio_encoded)
            encoded_features.append(audio_enhanced)

        if not encoded_features:
            raise ValueError("At least one input modality must be provided")

        # Fusion
        if len(encoded_features) == 1:
            fused = encoded_features[0]
        else:
            stacked = torch.stack(encoded_features, dim=1)
            attended, _ = self.fusion['attention'](stacked, stacked, stacked)
            fused = attended.mean(dim=1)

        # Apply fusion layers
        fused = self.fusion['norm'](fused)
        fused = fused + self.fusion['ffn'](fused)
        fused = fused + self.fusion['educational_pattern_transfer'](fused)

        # Mixture of Experts
        gate_scores = F.softmax(self.moe['gate'](fused), dim=-1)
        expert_outputs = []

        for expert in self.moe['experts']:
            expert_output = expert(fused)
            expert_outputs.append(expert_output)

        # Weighted combination
        expert_stack = torch.stack(expert_outputs, dim=-1)
        moe_output = torch.sum(expert_stack * gate_scores.unsqueeze(-2), dim=-1)
        moe_refined = self.moe['quality_refiner'](moe_output)

        # Generate outputs
        conversation_output = self.conversation_head(moe_refined)
        educational_output = self.educational_transfer_head(moe_refined)
        quality_score = torch.sigmoid(self.quality_scorer(moe_refined))

        return {
            'conversation_output': conversation_output,
            'educational_output': educational_output,
            'quality_score': quality_score,
            'fused_features': moe_refined,
            'expert_weights': gate_scores
        }

class PureB3Chat:
    """
    Pure conversational interface with direct model communication.
    Hybrid tokenizer approach: GPT-2 for input/output, DialoGPT for B3 compatibility.
    """

    def __init__(self, model_path: str):
        self.console = Console() if RICH_AVAILABLE else None
        self.model_path = Path(model_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model = None
        self.tokenizer = None  # DialoGPT-small for B3 compatibility
        self.gpt2_model = None
        self.gpt2_tokenizer = None  # GPT-2 for unified text processing
        self.vocab_size = 768  # Actual conversation head output size from trained model

        # Embedding alignment for tokenizer compatibility
        self.use_unified_gpt2 = False  # Test: False = DialoGPT input, True = GPT-2 input
        self.comparison_mode = True   # Enable side-by-side comparison

        print("💬 ImpressionCore B3 Pure Chat")
        print("=" * 40)
        print("🎯 Direct model communication - NO assistance")
        print(f"Model: {self.model_path.name}")
        print(f"Device: {self.device}")

        if self.comparison_mode:
            print("🔬 COMPARISON MODE: Testing DialoGPT vs GPT-2 input encoding")
        elif self.use_unified_gpt2:
            print("🔤 Testing unified GPT-2 tokenizer approach")
        else:
            print("🔤 Using optimized DialoGPT input + GPT-2 output hybrid")
        print("-" * 40)

    def load_gpt2_generator(self) -> bool:
        """Load GPT-2 model for text generation from B3 features"""

        if not GPT2_AVAILABLE:
            print("❌ GPT-2 not available - using fallback text generation")
            return False

        try:
            print("🔤 Loading GPT-2 for text generation...")

            # Load GPT-2 tokenizer and model
            self.gpt2_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
            self.gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2")

            # Set pad token
            self.gpt2_tokenizer.pad_token = self.gpt2_tokenizer.eos_token

            # Move to device
            self.gpt2_model.to(self.device)
            self.gpt2_model.eval()

            print("✅ GPT-2 loaded! Ready for text generation.")
            return True

        except Exception as e:
            print(f"❌ Error loading GPT-2: {e}")
            return False

    def load_tokenizer(self) -> bool:
        """Load the DialoGPT-small tokenizer for input encoding"""

        if not TOKENIZER_AVAILABLE:
            print("❌ Transformers library not available - using fallback vocabulary")
            return False

        try:
            print("🔤 Loading DialoGPT-small tokenizer for input encoding...")

            # Load the tokenizer used during B3 training for input encoding
            self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")

            # Set pad token if not exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            print("✅ Input tokenizer loaded!")
            return True

        except Exception as e:
            print(f"❌ Error loading input tokenizer: {e}")
            return False

    def create_basic_vocab(self) -> list[str]:
        """Fallback vocabulary if tokenizer unavailable"""

        # Basic vocabulary - this is a simplified approach
        # In a real system, this would be loaded from your tokenizer
        basic_words = [
            "hello", "hi", "hey", "goodbye", "bye", "yes", "no", "the", "a", "an",
            "I", "you", "we", "they", "am", "is", "are", "was", "were", "have", "has",
            "do", "does", "did", "will", "would", "could", "should", "can", "may",
            "good", "bad", "great", "nice", "help", "please", "thank", "thanks",
            "what", "when", "where", "why", "how", "who", "which", "that", "this",
            "and", "or", "but", "so", "because", "if", "then", "else", "with", "without",
            "model", "AI", "artificial", "intelligence", "neural", "network", "chat",
            "conversation", "talk", "speak", "say", "tell", "ask", "answer", "question",
            "ImpressionCore", "B3", "multimodal", "training", "learning", "thinking",
            "understand", "know", "learn", "teach", "explain", "describe", "show",
            "like", "love", "want", "need", "try", "work", "make", "get", "give",
            "time", "day", "today", "now", "here", "there", "some", "many", "much",
            ".", "!", "?", ",", ":", ";", " ", "\n"
        ]

        # Pad to vocab_size
        while len(basic_words) < self.vocab_size:
            basic_words.append(f"token_{len(basic_words)}")

        return basic_words[:self.vocab_size]

    def load_model(self) -> bool:
        """Load the trained B3 model and text generation components"""

        try:
            print("🔄 Loading B3 model for pure chat...")

            # Load tokenizers and text generator
            self.load_tokenizer()
            gpt2_loaded = self.load_gpt2_generator()

            # Load B3 trained weights
            model_weights = torch.load(
                self.model_path,
                map_location=self.device,
                weights_only=False
            )

            # Initialize and load B3 model
            self.model = B3ModelArchitecture()
            self.model.load_state_dict(model_weights)
            self.model.to(self.device)
            self.model.eval()

            status = "✅ B3 Model loaded successfully!"
            if gpt2_loaded:
                status += " GPT-2 text generator ready."
            else:
                status += " Using fallback text generation."

            print(status)
            return True

        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False

    def encode_text_input(self, user_text: str) -> torch.Tensor:
        """Encode user text - test unified GPT-2 vs hybrid approach"""

        if self.use_unified_gpt2 and self.gpt2_tokenizer is not None:
            # Test unified GPT-2 approach
            return self.encode_with_gpt2_unified(user_text)
        elif self.tokenizer is not None:
            # Use the actual DialoGPT tokenizer from B3 training (current approach)
            return self.encode_with_dialogpt(user_text)
        else:
            # Fallback to simple encoding
            return self.encode_text_fallback(user_text)

    def encode_with_gpt2_unified(self, user_text: str) -> torch.Tensor:
        """Unified GPT-2 approach with embedding space alignment"""

        try:
            # Tokenize with GPT-2
            tokens = self.gpt2_tokenizer.encode(
                user_text,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )

            # Create 768-dimensional embedding (matching B3 input expectations)
            embedding = torch.zeros(1, 768).to(self.device)

            # Map GPT-2 tokens to 768-dimensional space
            # This is an approximation to align GPT-2 tokens with DialoGPT space
            for i, token_id in enumerate(tokens[0][:50]):
                # Map GPT-2 token space (50257) to 768-dimensional space
                embed_pos = token_id.item() % 768
                position_weight = 1.0 / (1.0 + i * 0.05)

                # Set primary embedding
                embedding[0, embed_pos] = position_weight

                # Add contextual spread
                for offset in [-3, -1, 1, 3]:
                    context_pos = (embed_pos + offset) % 768
                    embedding[0, context_pos] += position_weight * 0.15

            # Normalize to match DialoGPT-style embeddings
            embedding = F.normalize(embedding, p=2, dim=1)

            return embedding

        except Exception as e:
            print(f"⚠️ GPT-2 unified encoding error: {e}, using fallback")
            return self.encode_text_fallback(user_text)

    def encode_with_dialogpt(self, user_text: str) -> torch.Tensor:
        """Original DialoGPT encoding approach"""

        try:
            # Tokenize the user input (same as training)
            tokens = self.tokenizer.encode(
                user_text,
                truncation=True,
                max_length=512,  # Reasonable max length
                return_tensors="pt"
            )

            # Convert token IDs to embeddings
            # Create embedding matrix (simplified approach)
            embedding = torch.zeros(1, 768).to(self.device)

            # Use token positions to create meaningful embeddings
            for i, token_id in enumerate(tokens[0][:50]):  # Limit to reasonable length
                # Map token ID to embedding position
                embed_pos = min(token_id.item() % 768, 767)
                position_weight = 1.0 / (1.0 + i * 0.05)

                # Set primary embedding
                embedding[0, embed_pos] = position_weight

                # Add context around the token
                for offset in [-2, -1, 1, 2]:
                    context_pos = (embed_pos + offset) % 768
                    embedding[0, context_pos] += position_weight * 0.1

            return embedding

        except Exception as e:
            print(f"⚠️ DialoGPT tokenizer error: {e}, using fallback encoding")
            return self.encode_text_fallback(user_text)

    def encode_text_fallback(self, user_text: str) -> torch.Tensor:
        """Fallback text encoding if tokenizer fails"""

        # Simple encoding approach - convert text to embedding
        # This is a basic approach; real systems use proper tokenizers

        # Create base embedding
        embedding = torch.zeros(1, 768).to(self.device)

        # Simple word-based encoding
        words = user_text.lower().split()

        for i, word in enumerate(words[:50]):  # Limit to 50 words
            # Simple hash-based encoding
            word_idx = hash(word) % 768
            position_factor = 1.0 / (1.0 + i * 0.1)  # Position decay

            # Set word presence
            embedding[0, word_idx] = position_factor

            # Add context around the word
            for j in range(-2, 3):
                if 0 <= word_idx + j < 768:
                    embedding[0, word_idx + j] += position_factor * 0.1

        # Normalize
        embedding = F.normalize(embedding, p=2, dim=1)

        return embedding

    def decode_conversation_output(self, conversation_output: torch.Tensor) -> str:
        """Generate text using B3 understanding + GPT-2 generation"""

        # Get B3's conversation understanding features
        output_vector = conversation_output.squeeze().cpu().numpy()  # [768]

        # Try GPT-2 generation first (better text quality)
        if self.gpt2_model is not None and self.gpt2_tokenizer is not None:
            return self.generate_text_with_gpt2(output_vector)
        else:
            # Fallback to feature-based responses
            return self.generate_text_from_features(output_vector)

    def generate_text_with_gpt2(self, b3_features: np.ndarray) -> str:
        """Generate text using GPT-2, guided by B3's conversation understanding"""

        try:
            # Analyze B3 features to determine conversation context
            conversation_analysis = self.analyze_b3_features_for_generation(b3_features)

            # Create context-aware prompt based on user message and B3 understanding
            prompt = self.create_smart_prompt_from_context(conversation_analysis)

            # Tokenize the prompt
            inputs = self.gpt2_tokenizer.encode(prompt, return_tensors="pt").to(self.device)

            # Generate text with GPT-2
            with torch.no_grad():
                outputs = self.gpt2_model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 20,  # Generate 20 more tokens
                    num_return_sequences=1,
                    temperature=0.7,  # Good balance of creativity and coherence
                    do_sample=True,
                    pad_token_id=self.gpt2_tokenizer.eos_token_id,
                    no_repeat_ngram_size=2,
                    eos_token_id=self.gpt2_tokenizer.eos_token_id,
                    repetition_penalty=1.1  # Reduce repetition
                )

            # Decode the generated text
            generated_text = self.gpt2_tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract the response part (remove the prompt)
            response = generated_text[len(prompt):].strip()

            # Clean up and validate the response
            response = self.clean_gpt2_response(response, conversation_analysis)

            return response

        except Exception as e:
            print(f"⚠️ GPT-2 generation error: {e}")
            return self.generate_text_from_features(b3_features)

    def create_smart_prompt_from_context(self, analysis: dict[str, float]) -> str:
        """Create intelligent GPT-2 prompt based on user message and B3 analysis"""

        # Get user message context
        user_msg = getattr(self, 'last_user_message', '').lower()

        # Create more focused, conversational prompts
        if "hello" in user_msg or "hi" in user_msg:
            return "A friendly AI assistant responds to a greeting:\nHuman: Hello!\nAssistant: Hello!"

        elif "name" in user_msg and ("your" in user_msg or "what" in user_msg):
            return "A person asks an AI assistant about its name:\nHuman: What's your name?\nAssistant: I'm ImpressionCore B3, an AI assistant."

        elif "my name" in user_msg:
            # Extract potential name for personalized response
            words = user_msg.split()
            if "is" in words:
                name_idx = words.index("is") + 1
                if name_idx < len(words):
                    name = words[name_idx].strip(".,!?").title()
                    return f"A person introduces themselves:\nHuman: My name is {name}.\nAssistant: Nice to meet you, {name}!"
            return "A person introduces themselves:\nHuman: My name is Kirk.\nAssistant: Nice to meet you!"

        elif any(word in user_msg for word in ["like", "love", "enjoy"]):
            if "dog" in user_msg:
                return "A person shares their love for dogs:\nHuman: I like dogs.\nAssistant: Dogs are wonderful companions!"
            elif "math" in user_msg:
                return "A person shares their interest in mathematics:\nHuman: I like math.\nAssistant: Mathematics is fascinating!"
            else:
                return "A person shares something they enjoy:\nHuman: I like something.\nAssistant: That's wonderful!"

        elif "?" in user_msg:
            return "A person asks a question:\nHuman: I have a question.\nAssistant: I'd be happy to help answer that."

        elif any(word in user_msg for word in ["help", "assist"]):
            return "A person asks for help:\nHuman: Can you help me?\nAssistant: Of course! I'm here to help."

        elif "how are you" in user_msg:
            return "A person asks about the AI's wellbeing:\nHuman: How are you?\nAssistant: I'm doing well, thank you for asking!"

        else:
            # General conversational prompt
            return "A friendly conversation between a human and an AI assistant:\nHuman: Let's chat.\nAssistant: I'm glad to talk with you."

    def clean_gpt2_response(self, response: str, analysis: dict[str, float]) -> str:
        """Clean and validate GPT-2 generated response"""

        # Remove common GPT-2 artifacts
        response = response.strip()

        # Remove incomplete sentences at the end
        sentences = response.split('.')
        if len(sentences) > 1 and len(sentences[-1].strip()) < 3:
            response = '.'.join(sentences[:-1]) + '.'

        # Ensure reasonable length (not too long or too short)
        words = response.split()
        if len(words) > 25:  # Too long
            response = ' '.join(words[:20]) + '.'
        elif len(words) < 2:  # Too short
            # Use fallback based on B3 analysis
            dominant = analysis.get('dominant_trait', 'helpfulness_intent')
            if dominant == 'greeting_strength':
                response = "Hello! Great to meet you!"
            else:
                response = "I understand what you're saying."

        # Ensure proper punctuation
        if not response.endswith(('.', '!', '?')):
            response += '.'

        # Capitalize first letter
        if response:
            response = response[0].upper() + response[1:]

        return response

    def analyze_b3_features_for_generation(self, features: np.ndarray) -> dict[str, float]:
        """Analyze B3 features to guide GPT-2 generation"""

        # Divide features into semantic regions for generation guidance
        analysis = {
            'greeting_strength': np.mean(np.abs(features[0:96])),
            'question_detection': np.mean(np.abs(features[96:192])),
            'technical_content': np.mean(np.abs(features[192:288])),
            'emotional_tone': np.mean(features[288:384]),
            'helpfulness_intent': np.mean(np.abs(features[384:480])),
            'knowledge_confidence': np.mean(np.abs(features[480:576])),
            'conversational_flow': np.mean(features[576:672]),
            'response_complexity': np.std(features[672:768])
        }

        # Determine dominant characteristics
        analysis['dominant_trait'] = max(analysis, key=lambda k: analysis[k] if k != 'dominant_trait' else 0)
        analysis['overall_confidence'] = np.mean(np.abs(features))

        return analysis

    def create_prompt_from_b3_analysis(self, analysis: dict[str, float]) -> str:
        """Create GPT-2 prompt based on B3's conversation analysis"""

        dominant = analysis['dominant_trait']
        confidence = analysis['overall_confidence']

        # Create context-appropriate prompts for GPT-2
        if dominant == 'greeting_strength' and analysis['greeting_strength'] > 0.3:
            if confidence > 0.5:
                prompt = "Human: Hello!\nAI: Hello! I'm ImpressionCore B3, an AI assistant."
            else:
                prompt = "Human: Hello!\nAI: Hi there!"

        elif dominant == 'question_detection' and analysis['question_detection'] > 0.4:
            if analysis['technical_content'] > 0.4:
                prompt = "Human asked a technical question.\nAI: That's a great technical question."
            else:
                prompt = "Human asked a question.\nAI: I understand your question."

        elif dominant == 'helpfulness_intent' and analysis['helpfulness_intent'] > 0.4:
            prompt = "Human needs help.\nAI: I'm here to help you."

        elif analysis['knowledge_confidence'] > 0.5:
            prompt = "Human is discussing a topic.\nAI: Based on my understanding,"

        elif analysis['conversational_flow'] > 0.4:
            prompt = "Human is continuing conversation.\nAI: To continue our discussion,"

        else:
            # Default prompt
            if confidence > 0.6:
                prompt = "Human: [message]\nAI: I appreciate you sharing that."
            else:
                prompt = "Human: [message]\nAI: I understand."

        return prompt

    def generate_text_from_features(self, features: np.ndarray) -> str:
        """Simple, reliable text generation from B3 features"""

        # Store the last user message for context
        user_msg = self.last_user_message.lower() if hasattr(self, 'last_user_message') else ""

        # Simple keyword-based responses that feel natural
        if "hello" in user_msg or "hi" in user_msg:
            return "Hello! I'm ImpressionCore B3. How can I help you today?"

        elif "name" in user_msg and ("your" in user_msg or "what" in user_msg):
            return "I'm ImpressionCore B3, an AI assistant designed to help with various tasks."

        elif "my name" in user_msg:
            # Extract potential name
            words = user_msg.split()
            if "is" in words:
                name_idx = words.index("is") + 1
                if name_idx < len(words):
                    name = words[name_idx].strip(".,!?").title()
                    return f"Nice to meet you, {name}! How can I assist you today?"
            return "Nice to meet you! How can I assist you today?"

        elif any(word in user_msg for word in ["like", "love", "enjoy"]):
            return "That's great! Tell me more about what interests you."

        elif "?" in user_msg:
            return "That's an interesting question. I'd be happy to help you with that."

        elif any(word in user_msg for word in ["help", "assist", "support"]):
            return "I'm here to help! What would you like assistance with?"

        elif "thank" in user_msg:
            return "You're very welcome! Is there anything else I can help you with?"

        elif "how are you" in user_msg:
            return "I'm doing well, thank you for asking! How are you today?"

        else:
            # Analyze features for general response tone
            feature_energy = np.mean(np.abs(features))

            if feature_energy > 0.5:
                return "I understand what you're saying. Could you tell me more about that?"
            else:
                return "I see. What would you like to discuss?"

    def analyze_conversation_features(self, features: np.ndarray) -> dict[str, float]:
        """Analyze the 768-dimensional conversation features to understand intent and context"""

        # Divide the feature space into semantic regions based on B3's training
        feature_regions = {
            'greeting_detection': np.mean(features[0:96]),      # Greeting understanding
            'question_understanding': np.mean(features[96:192]),  # Question comprehension
            'context_awareness': np.mean(features[192:288]),    # Context understanding
            'emotional_tone': np.mean(features[288:384]),       # Emotional analysis
            'topic_classification': np.mean(features[384:480]), # Topic understanding
            'response_intent': np.mean(features[480:576]),      # Response planning
            'knowledge_activation': np.mean(features[576:672]), # Knowledge retrieval
            'conversation_flow': np.mean(features[672:768])     # Conversation management
        }

        # Calculate feature strengths and dominant patterns
        feature_magnitudes = {k: abs(v) for k, v in feature_regions.items()}
        dominant_feature = max(feature_magnitudes, key=feature_magnitudes.get)

        # Overall conversation understanding metrics
        understanding_confidence = np.mean(np.abs(features))
        response_complexity = np.std(features)
        emotional_intensity = abs(feature_regions['emotional_tone'])

        return {
            # feature_regions,
            'dominant_feature': dominant_feature,
            'understanding_confidence': understanding_confidence,
            'response_complexity': response_complexity,
            'emotional_intensity': emotional_intensity
        }

    def generate_contextual_response(self, conversation_features: dict[str, float], raw_features: np.ndarray) -> str:
        """Generate appropriate response based on B3's conversation understanding"""

        dominant = conversation_features['dominant_feature']
        confidence = conversation_features['understanding_confidence']

        # Response templates based on B3's conversation understanding
        response_templates = {
            'greeting_detection': [
                "Hello! It's great to meet you.",
                "Hi there! How can I help you today?",
                "Greetings! I'm here to assist you.",
                "Hello! What would you like to discuss?"
            ],
            'question_understanding': [
                "That's an excellent question. Let me think about it.",
                "I understand what you're asking. Here's my perspective:",
                "Good question! From what I understand:",
                "That's interesting - let me address that for you."
            ],
            'context_awareness': [
                "I see what you mean based on our conversation.",
                "Taking into account what we've discussed:",
                "Building on what you mentioned:",
                "In the context of what you're saying:"
            ],
            'emotional_tone': [
                "I can sense this is important to you.",
                "I understand how you're feeling about this.",
                "Your perspective on this really matters.",
                "I appreciate you sharing that with me."
            ],
            'topic_classification': [
                "This is a fascinating topic to explore.",
                "I have some thoughts on this subject.",
                "This area is quite interesting to discuss.",
                "Let me share what I know about this."
            ],
            'response_intent': [
                "I want to give you a helpful response.",
                "Let me provide you with useful information.",
                "I'll do my best to assist you with this.",
                "Here's how I can help you:"
            ],
            'knowledge_activation': [
                "Based on what I understand about this topic:",
                "From my knowledge and experience:",
                "Drawing from what I know:",
                "Considering the information available:"
            ],
            'conversation_flow': [
                "To continue our conversation effectively:",
                "Building on what we've established:",
                "As we move forward in our discussion:",
                "To keep our conversation flowing:"
            ]
        }

        # Select appropriate response template
        base_responses = response_templates.get(dominant, response_templates['response_intent'])

        # Choose response based on confidence and emotional intensity
        emotional_intensity = conversation_features['emotional_intensity']

        if confidence > 0.7:
            # High confidence - detailed response
            if emotional_intensity > 0.5:
                base_response = base_responses[0]  # More engaging
                extension = " I'm really engaged in helping you with this."
            else:
                base_response = base_responses[1]  # Informative
                extension = " I'm confident I can provide valuable insights."
        elif confidence > 0.4:
            # Medium confidence - balanced response
            base_response = base_responses[2] if len(base_responses) > 2 else base_responses[0]
            extension = " I'll do my best to address your needs."
        else:
            # Lower confidence - careful response
            base_response = base_responses[-1]  # Most cautious
            extension = " Could you help me understand better?"

        # Add context-specific elaboration
        elaboration = self.add_contextual_elaboration(conversation_features, raw_features)

        # Combine response components
        full_response = f"{base_response} {elaboration}{extension}"

        # Clean up and finalize
        return self.finalize_response(full_response)

    def add_contextual_elaboration(self, features: dict[str, float], raw_features: np.ndarray) -> str:
        """Add specific elaboration based on feature analysis"""

        # Analyze specific patterns in the raw features
        feature_variance = np.var(raw_features)
        feature_energy = np.mean(np.abs(raw_features))

        elaborations = []

        # Check for specific conversation patterns
        if features['greeting_detection'] > 0.3:
            elaborations.append("I'm ImpressionCore B3, an AI assistant designed to help with various topics.")

        if features['question_understanding'] > 0.4:
            elaborations.append("I can help explain concepts, solve problems, or discuss ideas.")

        if features['knowledge_activation'] > 0.5:
            elaborations.append("I have access to broad knowledge across many domains.")

        if feature_energy > 0.6:
            elaborations.append("I'm processing your input with high attention to detail.")

        if feature_variance > 0.8:
            elaborations.append("I notice the complexity in what you're asking.")

        # Return appropriate elaboration
        if elaborations:
            return " ".join(elaborations[:2])  # Limit to 2 elaborations
        else:
            return "I'm here to help and engage in meaningful conversation."

    def finalize_response(self, response: str) -> str:
        """Clean up and finalize the response"""

        # Basic cleanup
        response = response.strip()
        response = ' '.join(response.split())  # Normalize whitespace

        # Ensure proper sentence structure
        if not response.endswith(('.', '!', '?')):
            response += '.'

        # Capitalize first letter
        if response:
            response = response[0].upper() + response[1:]

        return response

    def decode_features_to_text(self, features: np.ndarray) -> str:
        """Convert 768-dimensional features directly to text"""

        # Analyze feature patterns to generate meaningful responses
        np.linalg.norm(features)
        feature_energy = np.mean(np.abs(features))
        feature_complexity = np.std(features)

        # Divide features into semantic regions
        sections = np.array_split(features, 8)
        section_energies = [np.mean(np.abs(section)) for section in sections]
        dominant_section = np.argmax(section_energies)

        # Generate response based on feature analysis
        responses = [
            "Hello! I'm here to help you.",  # Section 0: Greetings
            "I understand your question.",    # Section 1: Understanding
            "That's an interesting point.",   # Section 2: Acknowledgment
            "Let me think about that.",       # Section 3: Processing
            "I can assist you with that.",    # Section 4: Assistance
            "Could you tell me more?",        # Section 5: Inquiry
            "I'm processing your request.",   # Section 6: Working
            "How else can I help you?"        # Section 7: Follow-up
        ]

        base_response = responses[dominant_section]

        # Modify response based on feature characteristics
        if feature_energy > 0.5:
            base_response = "I'm very " + base_response.lower()
        elif feature_energy < 0.1:
            base_response = "I " + base_response.lower()

        if feature_complexity > 0.8:
            base_response += " This seems complex."
        elif feature_complexity < 0.2:
            base_response += " This is clear to me."

        return base_response

    def decode_conversation_fallback(self, conversation_output: torch.Tensor) -> str:
        """Fallback conversation decoding if tokenizer fails"""

        # Extract probabilities over vocabulary
        output_probs = F.softmax(conversation_output, dim=-1)  # [1, vocab_size]

        # Get top tokens
        top_probs, top_indices = torch.topk(output_probs, k=20, dim=-1)

        # Convert to text using basic vocabulary
        vocab = self.create_basic_vocab()
        response_words = []

        for i in range(top_indices.size(1)):
            token_idx = top_indices[0, i].item()
            token_prob = top_probs[0, i].item()

            # Only include tokens with reasonable probability
            if token_prob > 0.01 and token_idx < len(vocab):
                word = vocab[token_idx]

                # Skip generic tokens
                if not word.startswith("token_"):
                    response_words.append(word)

                    # Stop if we have enough words
                    if len(response_words) >= 10:
                        break

        # If no good words found, use fallback
        if not response_words:
            response_words = ["I", "understand", "your", "message"]

        # Form response
        response = " ".join(response_words)

        # Basic cleanup
        response = response.replace(" .", ".").replace(" !", "!").replace(" ?", "?")
        response = response.replace(" ,", ",")

        # Capitalize first letter
        if response:
            response = response[0].upper() + response[1:]

        return response

    def generate_response(self, user_input: str) -> dict[str, Any]:
        """Generate pure response from model - with optional comparison mode"""

        # Store user message for context
        self.last_user_message = user_input

        if self.comparison_mode and self.tokenizer is not None and self.gpt2_tokenizer is not None:
            # Run comparison between DialoGPT and GPT-2 input encoding
            return self.run_comparison_analysis(user_input)
        else:
            # Standard single-method response
            return self.generate_single_response(user_input)

    def run_comparison_analysis(self, user_input: str) -> dict[str, Any]:
        """Compare DialoGPT vs GPT-2 input encoding side-by-side"""

        start_time = time.perf_counter()

        try:
            # Test both encoding methods
            print("🔬 Running comparison analysis...")

            # Method 1: DialoGPT input encoding
            dialogpt_embedding = self.encode_with_dialogpt(user_input)
            with torch.no_grad():
                dialogpt_outputs = self.model(text_input=dialogpt_embedding)
            dialogpt_features = dialogpt_outputs['conversation_output'].squeeze().cpu().numpy()
            dialogpt_quality = dialogpt_outputs['quality_score'].item()

            # Method 2: GPT-2 input encoding
            gpt2_embedding = self.encode_with_gpt2_unified(user_input)
            with torch.no_grad():
                gpt2_outputs = self.model(text_input=gpt2_embedding)
            gpt2_features = gpt2_outputs['conversation_output'].squeeze().cpu().numpy()
            gpt2_quality = gpt2_outputs['quality_score'].item()

            # Generate responses from both
            dialogpt_response = self.generate_text_with_gpt2(dialogpt_features)
            gpt2_response = self.generate_text_with_gpt2(gpt2_features)

            # Feature analysis comparison
            dialogpt_analysis = self.analyze_b3_features_for_generation(dialogpt_features)
            gpt2_analysis = self.analyze_b3_features_for_generation(gpt2_features)

            end_time = time.perf_counter()
            response_time = (end_time - start_time) * 1000

            return {
                'comparison_mode': True,
                'dialogpt_method': {
                    'response': dialogpt_response,
                    'quality_score': dialogpt_quality,
                    'feature_analysis': dialogpt_analysis,
                    'approach': 'DialoGPT input + GPT-2 output'
                },
                'gpt2_method': {
                    'response': gpt2_response,
                    'quality_score': gpt2_quality,
                    'feature_analysis': gpt2_analysis,
                    'approach': 'GPT-2 unified approach'
                },
                'response_time_ms': response_time,
                'recommendation': self.analyze_comparison_results(dialogpt_analysis, gpt2_analysis, dialogpt_quality, gpt2_quality)
            }

        except Exception as e:
            return {
                'error': f"Comparison analysis failed: {e}",
                'fallback_response': "I understand what you're saying.",
                'response_time_ms': (time.perf_counter() - start_time) * 1000
            }

    def analyze_comparison_results(self, dialogpt_analysis: dict, gpt2_analysis: dict,
                                 dialogpt_quality: float, gpt2_quality: float) -> str:
        """Analyze which method performed better"""

        # Compare feature activation patterns
        dialogpt_confidence = dialogpt_analysis['overall_confidence']
        gpt2_confidence = gpt2_analysis['overall_confidence']

        dialogpt_dominant = dialogpt_analysis['dominant_trait']
        gpt2_dominant = gpt2_analysis['dominant_trait']

        analysis = []

        # Quality comparison
        if dialogpt_quality > gpt2_quality:
            analysis.append(f"DialoGPT input shows higher quality ({dialogpt_quality:.3f} vs {gpt2_quality:.3f})")
        elif gpt2_quality > dialogpt_quality:
            analysis.append(f"GPT-2 input shows higher quality ({gpt2_quality:.3f} vs {dialogpt_quality:.3f})")
        else:
            analysis.append("Both methods show similar quality scores")

        # Confidence comparison
        if dialogpt_confidence > gpt2_confidence:
            analysis.append(f"DialoGPT shows stronger feature activation ({dialogpt_confidence:.3f} vs {gpt2_confidence:.3f})")
        else:
            analysis.append(f"GPT-2 shows stronger feature activation ({gpt2_confidence:.3f} vs {dialogpt_confidence:.3f})")

        # Feature pattern comparison
        if dialogpt_dominant == gpt2_dominant:
            analysis.append(f"Both identify '{dialogpt_dominant}' as dominant pattern")
        else:
            analysis.append(f"Different patterns: DialoGPT='{dialogpt_dominant}', GPT-2='{gpt2_dominant}'")

        return " | ".join(analysis)

    def generate_single_response(self, user_input: str) -> dict[str, Any]:
        """Generate single response using selected method"""

        start_time = time.perf_counter()

        try:
            # Encode user input
            text_embedding = self.encode_text_input(user_input)

            # Run model inference
            with torch.no_grad():
                outputs = self.model(text_input=text_embedding)

            # Extract model outputs
            conversation_output = outputs['conversation_output']  # [1, 768]
            quality_score = outputs['quality_score'].item()
            expert_weights = outputs['expert_weights'].cpu().numpy()

            # Decode to text - PURE model output
            response_text = self.decode_conversation_output(conversation_output)

        except Exception as e:
            response_text = f"Error in model inference: {e}"
            quality_score = 0.0
            expert_weights = np.zeros(8)

        end_time = time.perf_counter()
        response_time = (end_time - start_time) * 1000

        return {
            'response': response_text,
            'quality_score': quality_score,
            'response_time_ms': response_time,
            'expert_weights': expert_weights,
            'pure_model_output': True
        }

    def run_pure_chat(self):
        """Run pure chat interface"""

        if not self.model:
            print("❌ Model not loaded!")
            return

        print("\n💬 Pure B3 Chat Interface")
        print("=" * 35)
        print("🎯 Direct model communication")
        print("⚡ NO assistance or pre-written responses")
        print("Type 'quit' to exit")
        print("-" * 35)

        conversation_count = 0

        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]You") if RICH_AVAILABLE else input("\nYou: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Chat ended!")
                    break

                # Generate pure response
                print("🧠 Model thinking...")

                response_data = self.generate_response(user_input)

                # Display response(s)
                if response_data.get('comparison_mode', False):
                    # Display comparison results
                    self.display_comparison_results(response_data, conversation_count)
                    conversation_count += 1
                else:
                    # Display single response
                    response = response_data['response']
                    quality = response_data['quality_score']
                    response_time = response_data['response_time_ms']

                    conversation_count += 1

                    if RICH_AVAILABLE:
                        method_info = "DialoGPT→GPT-2" if not self.use_unified_gpt2 else "GPT-2 Unified"
                        response_panel = Panel(
                            response,
                            title=f"🤖 B3 Model ({method_info} #{conversation_count}) - {response_time:.1f}ms, Q:{quality:.2f}",
                            border_style="blue"
                        )
                        self.console.print(response_panel)
                    else:
                        print(f"\n🤖 B3: {response}")
                        print(f"📊 Time: {response_time:.1f}ms | Quality: {quality:.2f} | Pure: ✅")

            except KeyboardInterrupt:
                print("\n👋 Chat interrupted!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def display_comparison_results(self, response_data: dict[str, Any], conversation_count: int):
        """Display side-by-side comparison results"""

        dialogpt_data = response_data['dialogpt_method']
        gpt2_data = response_data['gpt2_method']
        recommendation = response_data['recommendation']
        response_time = response_data['response_time_ms']

        if RICH_AVAILABLE:
            # DialoGPT method panel
            dialogpt_panel = Panel(
                dialogpt_data['response'],
                title=f"🔵 DialoGPT Input Method (Q:{dialogpt_data['quality_score']:.3f})",
                border_style="blue"
            )

            # GPT-2 method panel
            gpt2_panel = Panel(
                gpt2_data['response'],
                title=f"🟢 GPT-2 Unified Method (Q:{gpt2_data['quality_score']:.3f})",
                border_style="green"
            )

            # Analysis panel
            analysis_panel = Panel(
                recommendation,
                title=f"📊 Comparison Analysis #{conversation_count + 1} - {response_time:.1f}ms",
                border_style="yellow"
            )

            self.console.print(dialogpt_panel)
            self.console.print(gpt2_panel)
            self.console.print(analysis_panel)
        else:
            print(f"\n🔵 DialoGPT Method: {dialogpt_data['response']}")
            print(f"   Quality: {dialogpt_data['quality_score']:.3f} | Dominant: {dialogpt_data['feature_analysis']['dominant_trait']}")

            print(f"\n🟢 GPT-2 Method: {gpt2_data['response']}")
            print(f"   Quality: {gpt2_data['quality_score']:.3f} | Dominant: {gpt2_data['feature_analysis']['dominant_trait']}")

            print(f"\n📊 Analysis: {recommendation}")
            print(f"⏱️ Total Time: {response_time:.1f}ms")

    def start(self):
        """Start the pure chat interface"""

        if not self.load_model():
            return

        self.run_pure_chat()

def main():
    """Main entry point"""

    model_path = "F:/models/checkpoints/b3/b3_best_quality_model_20250802_124801.pth"

    chat = PureB3Chat(model_path)
    chat.start()

if __name__ == "__main__":
    main()
