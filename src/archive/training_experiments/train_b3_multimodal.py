
import os
import yaml
import argparse
import torch
import logging
from torch.utils.data import DataLoader
from accelerate import Accelerator
from accelerate.utils import set_seed
from tqdm.auto import tqdm
from typing import Dict, Any

# Import B3 Architecture
from src.core.models.impressioncore_b3_architecture import (
    ImpressionCoreB3Model,
    B3Config,
    B3TrainingConfig # Assuming this class exists or mapping dict to it
)

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def load_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


import glob
import webdataset as wds
from transformers import GPT2TokenizerFast
from functools import partial

def preprocess_sample(sample, tokenizer, max_length=4096):
    """
    Transform raw sample into model inputs.
    """
    # Helper to safely decode bytes or string
    def safe_decode(val):
        if isinstance(val, (bytes, bytearray)):
            try:
                return val.decode("utf-8")
            except UnicodeDecodeError:
                # Fallback for non-utf8 characters common in some datasets
                return val.decode("latin-1", errors="replace")
        return str(val) if val is not None else ""

    # Find modality key (usually modality.txt)
    modality = safe_decode(sample.get("modality.txt", b"unknown"))

    # Initialize inputs
    input_ids = torch.zeros(max_length, dtype=torch.long)
    attention_mask = torch.zeros(max_length, dtype=torch.long)

    if modality == "text":
        # Handle various text extensions
        raw_text = sample.get("data.txt", sample.get("data.json"))
        if raw_text:
            text = safe_decode(raw_text)
            tokens = tokenizer(text, max_length=max_length, truncation=True, padding="max_length", return_tensors="pt")
            input_ids = tokens["input_ids"][0]
            attention_mask = tokens["attention_mask"][0]

    elif modality in ["video", "face", "image"]:
        # Placeholder for video/image processing
        # In real impl: decode video/image -> tensor
        pass

    # Standard return dict matching B3 forward signature
    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        # "pixel_values": ...,
        # "audio_values": ...
    }

def create_dataloaders(config_dict, accelerator):
    batch_size = config_dict["training"]["batch_size"]

    # Find shards
    shard_path = "F:/data/processed/shards/b3_multimodal_shard-*.tar"
    shards = glob.glob(shard_path)
    if not shards:
        logger.warning(f"No shards found at {shard_path}. Using empty dataset for sanity check.")
        return DataLoader([], batch_size=batch_size)

    # Convert to URI format for Windows
    # Note: WebDataset on Windows needs 'file:' scheme but NO '///' for drive paths
    # to avoid leading slash in open().
    # e.g. file:F:/data/... -> parses to path F:/data/... which open() likes.
    shards = [f"file:{s.replace(os.sep, '/')}" for s in shards]

    logger.info(f"Found {len(shards)} shards")

    # Initialize Tokenizer
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token

    # Build Pipeline
    dataset = (
        wds.WebDataset(shards, resampled=True, shardshuffle=False)
        .shuffle(1000)
        # .decode() # Manual decoding in preprocess_sample
        .map(partial(preprocess_sample, tokenizer=tokenizer, max_length=config_dict["model"]["max_seq_length"]))
        .to_tuple("input_ids", "attention_mask") # Extract for collation
        # .batched(batch_size) # We use DataLoader for batching usually, or internal batching
    )

    # Use standard DataLoader for collation/batching convenience with Accelerate
    # WebDataset is iterable, so num_workers works differently
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        num_workers=config_dict["training"]["num_workers"]
    )

    return dataloader

def main():
    parser = argparse.ArgumentParser(description="Train ImpressionCore B3 Multimodal Model")
    parser.add_argument("--config", type=str, default="config/b3_pretraining_config.yaml", help="Path to config file")
    parser.add_argument("--resume_from_checkpoint", type=str, default=None, help="Path to checkpoint to resume from")
    args = parser.parse_args()

    # 1. Load Configuration
    config_dict = load_config(args.config)

    # Initialize Accelerator
    accelerator = Accelerator(
        gradient_accumulation_steps=config_dict["training"]["gradient_accumulation_steps"],
        mixed_precision=config_dict["training"].get("mixed_precision", "fp16"),
        log_with="tensorboard",
        project_dir=config_dict["directories"]["logging_dir"]
    )

    # Set Seed
    set_seed(config_dict["training"]["seed"])

    if accelerator.is_main_process:
        os.makedirs(config_dict["directories"]["output_dir"], exist_ok=True)
        logger.info(f"Loaded configuration from {args.config}")

    # 2. Initialize Model
    # Map YAML config to B3Config object
    b3_config = B3Config(
        embed_dim=config_dict["model"]["embed_dim"],
        num_heads=config_dict["model"]["num_heads"],
        num_layers=config_dict["model"]["num_layers"],
        vocab_size=config_dict["model"]["vocab_size"],
        num_experts=config_dict["model"]["num_experts"],
        expert_dim=config_dict["model"]["expert_dim"],
        experts_per_token=config_dict["model"]["experts_per_token"],
        image_embed_dim=config_dict["model"]["image_embed_dim"],
        audio_embed_dim=config_dict["model"]["audio_embed_dim"],
        phoneme_vocab_size=config_dict["model"]["phoneme_vocab_size"],
        max_seq_length=config_dict["model"]["max_seq_length"],
        dropout=config_dict["model"]["dropout"],
        use_mhc=config_dict["model"]["use_mhc"],
        mhc_iterations=config_dict["model"]["mhc_iterations"]
    )

    model = ImpressionCoreB3Model(b3_config)

    # 3. Setup Dataset using WebDataset
    train_dataloader = create_dataloaders(config_dict, accelerator)

    # 4. Setup Optimizer & Scheduler
    optimizer_cls = torch.optim.AdamW
    optimizer = optimizer_cls(
        model.parameters(),
        lr=float(config_dict["training"]["learning_rate"]),
        weight_decay=config_dict["training"]["weight_decay"]
    )

    # 5. Prepare with Accelerator
    model, optimizer, train_dataloader = accelerator.prepare(
        model, optimizer, train_dataloader
    )

    # 6. Training Loop
    total_batch_size = (
        config_dict["training"]["batch_size"]
        * accelerator.num_processes
        * config_dict["training"]["gradient_accumulation_steps"]
    )

    logger.info("***** Running training *****")
    logger.info(f"  Num Epochs = {100}") # Virtual epochs for streaming
    logger.info(f"  Instantaneous batch size per device = {config_dict['training']['batch_size']}")
    logger.info(f"  Total train batch size (w/ parallel, distributed & accumulation) = {total_batch_size}")

    global_step = 0
    max_steps = config_dict["training"]["max_steps"]

    progress_bar = tqdm(range(max_steps), disable=not accelerator.is_local_main_process)

    model.train()

    # Loop over iterable dataset
    try:
        for step, batch in enumerate(train_dataloader):
            # ... Unpack batch ...
            if isinstance(batch, list):
                 inputs = {"input_ids": batch[0], "attention_mask": batch[1]}
            else:
                 inputs = batch

            # Add labels for causal language modeling
            if "labels" not in inputs:
                inputs["labels"] = inputs["input_ids"].clone()

            with accelerator.accumulate(model):
                outputs = model(**inputs)
                # Robust extraction of loss from model output dict
                if isinstance(outputs, dict):
                    loss = outputs.get("loss")
                else:
                    loss = getattr(outputs, "loss", None)

                if loss is None:
                    raise ValueError(f"Model output does not contain loss. Keys: {outputs.keys() if isinstance(outputs, dict) else 'N/A'}")

                accelerator.backward(loss)

                if accelerator.sync_gradients:
                    accelerator.clip_grad_norm_(model.parameters(), config_dict["training"]["grad_clip"])
                    optimizer.step()
                    # scheduler.step() # Add scheduler
                    optimizer.zero_grad()
                    progress_bar.update(1)
                    global_step += 1

                    if global_step % config_dict["checkpointing"]["save_steps"] == 0:
                        save_path = os.path.join(config_dict["directories"]["output_dir"], f"checkpoint-{global_step}")
                        accelerator.save_state(save_path)
                        logger.info(f"Saved state to {save_path}")

            if global_step >= max_steps:
                 break
    except KeyboardInterrupt:
        logger.info("Interrupt detected. Saving final state before exit...")
        save_path = os.path.join(config_dict["directories"]["output_dir"], f"checkpoint-last-{global_step}")
        accelerator.save_state(save_path)
        logger.info(f"Graceful shutdown complete. Final state saved to {save_path}")

    logger.info("Training complete.")

if __name__ == "__main__":
    main()
