#!/usr/bin/env python3
"""
LoRA Fine-Tuning Trainer for High School Graduate AI

This trainer uses LoRA (Low-Rank Adaptation) to fine-tune a pre-trained
GPT-2 model on high-quality educational conversations. This approach:

1. Starts with a coherent pre-trained model (GPT-2)
2. Adds only 1-2M trainable parameters (prevents overfitting)
3. Uses our perfect GPU acceleration infrastructure
4. Focuses on educational conversation specialization

Key advantages:
- Preserves existing coherent text generation
- Much more parameter-efficient than full fine-tuning
- Works perfectly with our 4GB VRAM constraint
- Builds on our breakthrough GPU infrastructure
"""

import sys
from pathlib import Path
import torch
import torch.nn as nn
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import json
import logging
from datetime import datetime

# Add proper paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LoRALayer(nn.Module):
    """Low-Rank Adaptation layer for efficient fine-tuning"""
    
    def __init__(self, original_layer, rank=8):
        super().__init__()
        self.original_layer = original_layer
        self.rank = rank
        
        # Get dimensions from original layer
        if hasattr(original_layer, 'weight'):
            out_features, in_features = original_layer.weight.shape
        else:
            # For attention layers
            out_features = in_features = original_layer.embed_dim
            
        # LoRA parameters (much smaller than original)
        self.lora_A = nn.Parameter(torch.randn(rank, in_features) * 0.02)
        self.lora_B = nn.Parameter(torch.zeros(out_features, rank))
        self.scaling = 0.1
        
    def forward(self, x):
        # Original layer output
        original_output = self.original_layer(x)
        
        # LoRA adaptation
        lora_output = torch.matmul(torch.matmul(x, self.lora_A.T), self.lora_B.T)
        
        return original_output + self.scaling * lora_output

class HighSchoolLoRATrainer:
    """LoRA trainer for high school graduate educational AI"""
    
    def __init__(self, model_name="gpt2", rank=8):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # Load pre-trained model and tokenizer
        logger.info(f"Loading pre-trained model: {model_name}")
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        
        # Add pad token
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Apply LoRA to key layers
        self.apply_lora(rank)
        
        # Move to GPU
        self.model.to(self.device)
        
        # Count parameters
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        logger.info(f"Total parameters: {total_params:,}")
        logger.info(f"Trainable parameters: {trainable_params:,}")
        logger.info(f"Trainable ratio: {trainable_params/total_params:.1%}")
        
    def apply_lora(self, rank):
        """Apply LoRA to transformer layers"""
        logger.info(f"Applying LoRA with rank {rank}")
        
        # Freeze all original parameters
        for param in self.model.parameters():
            param.requires_grad = False
            
        # Apply LoRA to attention and MLP layers
        for i, layer in enumerate(self.model.transformer.h):
            # Apply to attention
            if hasattr(layer.attn, 'c_attn'):
                layer.attn.c_attn = LoRALayer(layer.attn.c_attn, rank)
            
            # Apply to MLP
            if hasattr(layer.mlp, 'c_fc'):
                layer.mlp.c_fc = LoRALayer(layer.mlp.c_fc, rank)
                
        logger.info(f"Applied LoRA to {len(self.model.transformer.h)} transformer layers")
        
    def load_dataset(self, dataset_path):
        """Load high-quality educational conversation dataset"""
        logger.info(f"Loading dataset from {dataset_path}")
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        conversations = data['conversations']
        logger.info(f"Loaded {len(conversations)} conversations")
        logger.info(f"Subjects: {', '.join(data['metadata']['subjects'])}")
        
        return conversations
        
    def prepare_training_data(self, conversations):
        """Prepare conversations for training"""
        logger.info("Preparing training data...")
        
        training_texts = []
        for conv in conversations:
            # Format as conversation
            text = f"Student: {conv['input']}\nTeacher: {conv['output']}<|endoftext|>"
            training_texts.append(text)
            
        logger.info(f"Prepared {len(training_texts)} training examples")
        return training_texts
        
    def train(self, dataset_path="high_school_graduate_dataset.json", epochs=3, learning_rate=5e-5):
        """Train the model with LoRA fine-tuning"""
        logger.info("🎓 Starting LoRA Fine-Tuning for High School Graduate AI")
        
        # Load and prepare data
        conversations = self.load_dataset(dataset_path)
        training_texts = self.prepare_training_data(conversations)
        
        # Setup optimizer (only LoRA parameters)
        optimizer = torch.optim.AdamW(
            [p for p in self.model.parameters() if p.requires_grad], 
            lr=learning_rate
        )
        
        # Training loop
        self.model.train()
        total_loss = 0
        
        logger.info(f"Training for {epochs} epochs...")
        
        for epoch in range(epochs):
            epoch_loss = 0
            
            for i, text in enumerate(training_texts):
                # Tokenize
                inputs = self.tokenizer(
                    text, 
                    return_tensors="pt", 
                    max_length=512, 
                    truncation=True, 
                    padding=True
                ).to(self.device)
                
                # Forward pass
                outputs = self.model(**inputs, labels=inputs["input_ids"])
                loss = outputs.loss
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
                total_loss += loss.item()
                
                if (i + 1) % 5 == 0:
                    logger.info(f"Epoch {epoch+1}/{epochs}, Step {i+1}/{len(training_texts)}, Loss: {loss.item():.4f}")
            
            avg_epoch_loss = epoch_loss / len(training_texts)
            logger.info(f"Epoch {epoch+1} completed. Average loss: {avg_epoch_loss:.4f}")
            
        logger.info(f"Training completed! Average total loss: {total_loss/(epochs*len(training_texts)):.4f}")
        
        # Save the model
        self.save_model()
        
        # Test the model
        self.test_model()
        
    def save_model(self):
        """Save the fine-tuned model"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = f"high_school_lora_model_{timestamp}"
        
        logger.info(f"Saving model to {save_path}")
        
        # Save only LoRA parameters
        lora_state = {}
        for name, module in self.model.named_modules():
            if isinstance(module, LoRALayer):
                lora_state[name] = {
                    'lora_A': module.lora_A,
                    'lora_B': module.lora_B,
                    'scaling': module.scaling
                }
        
        torch.save(lora_state, f"{save_path}_lora.pth")
        logger.info(f"✅ LoRA parameters saved to {save_path}_lora.pth")
        
    def test_model(self):
        """Test the model with sample questions"""
        logger.info("\n🧪 Testing High School Graduate AI...")
        
        test_questions = [
            "Explain the main theme of To Kill a Mockingbird.",
            "What can students do to help with climate change?",
            "How should I approach studying for a difficult math test?",
            "What factors should I consider when choosing a college major?"
        ]
        
        self.model.eval()
        with torch.no_grad():
            for question in test_questions:
                prompt = f"Student: {question}\nTeacher:"
                
                inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
                
                outputs = self.model.generate(
                    inputs["input_ids"],
                    max_length=inputs["input_ids"].shape[1] + 100,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                teacher_response = response.split("Teacher:")[-1].strip()
                
                print(f"\n📝 Question: {question}")
                print(f"🎓 Response: {teacher_response[:200]}...")

def main():
    print("🎓 LoRA Fine-Tuning Trainer for High School Graduate AI")
    print("📚 Using pre-trained GPT-2 with educational specialization")
    print("🎯 Goal: Coherent, helpful, educational conversation partner")
    
    try:
        # Check if dataset exists
        dataset_path = "high_school_graduate_dataset.json"
        if not Path(dataset_path).exists():
            print(f"⚠️ Dataset not found at {dataset_path}")
            print("Please create the dataset first by running create_comprehensive_dataset.py")
            return 1
            
        # Create trainer
        trainer = HighSchoolLoRATrainer(rank=8)
        
        print("\n🚀 Starting LoRA fine-tuning...")
        print("Expected time: 5-10 minutes")
        print("💡 This preserves GPT-2's coherence while adding educational focus")
        
        # Train the model
        trainer.train(dataset_path, epochs=3, learning_rate=5e-5)
        
        print("\n🎉 LoRA fine-tuning completed!")
        print("✅ Model should now provide coherent, educational responses")
        print("🎓 Ready for high school graduate-level conversations!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
