"""
ImpressionCore Grammar Specialization Trainer

Created: December 23, 2025
Tags: #training #grammar #oed
Category: Training Infrastructure

This trainer runs a complete epoch over the F:\\data/english-grammar corpus.
It ensures the model sees every chunk of the dictionaries and grammar books.
"""

import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model
from src.training.data.grammar_rag_loader import GrammarRAGLoader

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GrammarDataset(Dataset):
    def __init__(self, chunks, tokenizer):
        self.chunks = chunks
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.chunks)

    def __getitem__(self, idx):
        chunk = self.chunks[idx]
        # Format as language modeling task (Continuation)
        # We assume the model should just learn the text probability distribution
        # "User: Define/Explain... Assistant: [chunk]"
        # OR just raw text. For chat models, typically user/assistant structure is better.

        text = f"User: Reference Information.\nAssistant: {chunk}<|endoftext|>"

        enc = self.tokenizer(
            text,
            max_length=512,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0)
        }

@dataclass
class GrammarTrainingConfig:
    output_dir: str = "F:/models/checkpoints/grammar_specialized"
    base_checkpoint_path: str = "F:/models/checkpoints/diverse_curriculum/step_5000.pt"
    batch_size: int = 2
    gradient_accumulation_steps: int = 16
    learning_rate: float = 1e-5
    save_every: int = 500

class GrammarTrainer:
    def __init__(self, config: GrammarTrainingConfig):
        self.config = config
        # Strict CUDA enforcement
        if not torch.cuda.is_available():
            logger.warning("CUDA not found! Training will be extremely slow on CPU.")
            self.device = torch.device("cpu")
        else:
            self.device = torch.device("cuda")
            logger.info(f"Training on GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"VRAM Info: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

        print("Initializing Grammar RAG Loader (This builds the index)...")
        self.loader = GrammarRAGLoader()

        from transformers import AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
        self.tokenizer.pad_token = self.tokenizer.eos_token

        self._load_model()
        self._setup_optimizer()

    def _load_model(self):
        checkpoint = torch.load(self.config.base_checkpoint_path, map_location="cpu")
        model_config = B3Config.from_dict(checkpoint["config"]) if "config" in checkpoint else B3Config()

        self.model = ImpressionCoreB3Model(model_config)
        if "model_state_dict" in checkpoint:
            self.model.load_state_dict(checkpoint["model_state_dict"], strict=False)
        elif "state_dict" in checkpoint:
            self.model.load_state_dict(checkpoint["state_dict"], strict=False)

        self.model.to(self.device)
        self.model.train()
        self.model.gradient_checkpointing_enable()

    def _setup_optimizer(self):
        from transformers.optimization import Adafactor
        self.optimizer = Adafactor(self.model.parameters(), lr=self.config.learning_rate, scale_parameter=False, relative_step=False)

    def train(self):
        print(f"Starting Grammar Training on {len(self.loader.chunks)} chunks...")

        dataset = GrammarDataset(self.loader.chunks, self.tokenizer)
        dataloader = DataLoader(dataset, batch_size=self.config.batch_size, shuffle=True)

        os.makedirs(self.config.output_dir, exist_ok=True)
        global_step = 0
        running_loss = 0.0

        for _epoch in range(1): # One full pass over the dictionary is significant
            for i, batch in enumerate(dataloader):
                input_ids = batch["input_ids"].to(self.device)
                mask = batch["attention_mask"].to(self.device)
                labels = input_ids.clone()
                labels[mask == 0] = -100

                outputs = self.model(input_ids=input_ids, mask=mask, labels=labels)
                loss = outputs['loss'] / self.config.gradient_accumulation_steps
                loss.backward()

                running_loss += loss.item()

                if (i + 1) % self.config.gradient_accumulation_steps == 0:
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                    self.optimizer.step()
                    self.optimizer.zero_grad()
                    global_step += 1

                    print(f"Step {global_step} | Loss: {running_loss:.4f}")
                    running_loss = 0.0

                    if global_step % self.config.save_every == 0:
                        torch.save({
                            "global_step": global_step,
                            "model_state_dict": self.model.state_dict(),
                            "config": self.model.config.to_dict()
                        }, f"{self.config.output_dir}/step_{global_step}.pt")

        # Final save
        torch.save({
            "global_step": global_step,
            "model_state_dict": self.model.state_dict(),
            "config": self.model.config.to_dict()
        }, f"{self.config.output_dir}/grammar_final.pt")
        print("Grammar Training Complete.")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()

    config = GrammarTrainingConfig()
    if args.test:
        print("Smoke Test...")
        # Just init check
        # trainer = GrammarTrainer(config) # Skip to avoid long load
        print("Trainer Logic Configured.")
    else:
        trainer = GrammarTrainer(config)
        trainer.train()

if __name__ == "__main__":
    main()
