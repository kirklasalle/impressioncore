#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #command_line #cuda #memory_management #multimodal #python #source_code #src/training/embed_b2_datasets.py #tokenization #training
**Category:** Training System
**Status:** Active
"""









# Embed B2 Datasets

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #command_line #cuda #memory_management #multimodal #python #source_code #src\\training\\embed_b2_datasets.py #tokenization #training
# Category:** Training System
# Status:** Active

"""
B2 Dataset Embedding Automation Script

- Processes all curated data in F:/b2_datasets/ (text, images, audio, video)
- Converts each file to a fixed-size embedding using pre-trained or user-specified encoders
- Saves embeddings as .npy files in F:/b2_embeddings/[modality]/
- Generates an embedding catalogue for downstream training

Author: GitHub Copilot
Date: 2025-06-29
"""
import os
import sys
import json
from pathlib import Path

import numpy as np
import torch
from tqdm import tqdm
from src.core.kernel.b2_multimodal_model import TextEncoder, VisionEncoder, AudioEncoder, VideoEncoder
from src.core.utils.rich_logging import get_rich_logger
from src.core.utils.rich_status_animation import StatusAnimation

# === CONFIG ===
DATA_ROOT = Path('F:/b2_datasets')
EMBED_ROOT = Path('F:/b2_embeddings')
CATALOGUE_PATH = DATA_ROOT / 'b2_data_catalogue.json'



# === Advanced memory optimization and context window management ===
from src.models.b2_multimodal.core.memory_optimization import apply_memory_optimizations
def optimize_embed_config(embed_config):
    import torch.nn as nn
    dummy = nn.Identity()
    apply_memory_optimizations(dummy, embed_config)
    return embed_config

EMBED_CONFIG = {
    'embed_dim': 768,
    'max_seq_length': 128000,
    'max_seq_len': 128000,
    'vocab_size': 50257
}
EMBED_CONFIG = optimize_embed_config(EMBED_CONFIG)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger = get_rich_logger("embed_b2_datasets")

# Encoder configs (update as needed)
TEXT_EMBED_DIM = EMBED_CONFIG['embed_dim']
VISION_EMBED_DIM = EMBED_CONFIG['embed_dim']
AUDIO_EMBED_DIM = EMBED_CONFIG['embed_dim']
VIDEO_EMBED_DIM = EMBED_CONFIG['embed_dim']
VOCAB_SIZE = EMBED_CONFIG['vocab_size']

text_encoder = TextEncoder(VOCAB_SIZE, TEXT_EMBED_DIM).to(device).eval()
vision_encoder = VisionEncoder(VISION_EMBED_DIM).to(device).eval()
audio_encoder = AudioEncoder(AUDIO_EMBED_DIM).to(device).eval()
video_encoder = VideoEncoder(VIDEO_EMBED_DIM).to(device).eval()

def encode_text(text_path):
    import re
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()
    # Character-level tokenizer to avoid ord() errors on multi-character strings
    tokens = [ord(c) % VOCAB_SIZE for c in text if c.isprintable()]
    tokens = tokens[:128000]  # Truncate to max context
    tokens_arr = np.array(tokens)
    if tokens_arr.size == 0:
        print(f"[DEBUG] encode_text: empty file or no valid tokens, returning zeros")
        return np.zeros(TEXT_EMBED_DIM, dtype=np.float32)
    print(f"[DEBUG] encode_text: min token={tokens_arr.min()}, max token={tokens_arr.max()}, VOCAB_SIZE={VOCAB_SIZE}")
    # Clamp tokens to [0, VOCAB_SIZE-1] to avoid out-of-bounds
    tokens_arr = np.clip(tokens_arr, 0, VOCAB_SIZE-1)
    tokens = torch.tensor(tokens_arr, dtype=torch.long, device=device).unsqueeze(0)
    with torch.no_grad():
        emb = text_encoder(tokens)
        emb = emb.mean(dim=1).squeeze().cpu().numpy()
    return emb.astype(np.float32)

def encode_image(image_path):
    from PIL import Image
    img = Image.open(image_path).convert('RGB')
    img = img.resize((224, 224))
    arr = np.array(img).astype(np.float32) / 255.0
    # arr = np.clip(arr, 0.0, 1.0)  # Remove debug and clamp for images for now
    arr = torch.tensor(arr, dtype=torch.float32, device=device).permute(2, 0, 1).unsqueeze(0)
    with torch.no_grad():
        emb = vision_encoder(arr)
        emb = emb.mean(dim=1).squeeze().cpu().numpy()
    return emb.astype(np.float32)

def encode_audio(audio_path):
    import soundfile as sf
    data, sr = sf.read(audio_path)
    # Assume mono, 80-dim Mel (simulate if not available)
    if data.ndim > 1:
        data = data.mean(axis=1)
    # Simulate Mel: reshape to (seq, 80)
    mel = np.resize(data, (min(2048, len(data)//80), 80))
    print(f"[DEBUG] encode_audio: min={mel.min()}, max={mel.max()}, shape={mel.shape}")
    mel = np.clip(mel, -1.0, 1.0)
    # Transpose to [1, 80, frames] for AudioEncoder
    mel = torch.tensor(mel, dtype=torch.float32, device=device).unsqueeze(0).transpose(1, 2)
    with torch.no_grad():
        emb = audio_encoder(mel)
        emb = emb.mean(dim=1).squeeze().cpu().numpy()
    return emb.astype(np.float32)

def encode_video(video_path):
    # Placeholder: load video as sequence of dummy frame features
    # Replace with actual video frame feature extraction as needed
    n_frames = 16
    frame_feat = np.random.randn(n_frames, 1024).astype(np.float32)
    print(f"[DEBUG] encode_video: min={frame_feat.min()}, max={frame_feat.max()}, shape={frame_feat.shape}")
    # Optionally clamp to a reasonable range for stability
    frame_feat = np.clip(frame_feat, -5.0, 5.0)
    frames = torch.tensor(frame_feat, dtype=torch.float32, device=device).unsqueeze(0)
    with torch.no_grad():
        emb = video_encoder(frames)
        emb = emb.mean(dim=1).squeeze().cpu().numpy()
    return emb.astype(np.float32)

ENCODERS = {
    'text': encode_text,
    'images': encode_image,
    'audio': encode_audio,
    'video': encode_video
}

# === MAIN PIPELINE ===

def embed_all():
    if not CATALOGUE_PATH.exists():
        logger.error(f"Catalogue not found: {CATALOGUE_PATH}")
        return
    with open(CATALOGUE_PATH, 'r', encoding='utf-8') as f:
        catalogue = json.load(f)
    embed_catalogue = {m: [] for m in ENCODERS}
    for modality, files in catalogue.items():
        out_dir = EMBED_ROOT / modality
        out_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Embedding {len(files)} {modality} files...")
        status = StatusAnimation(len(files), description=f"Embedding {modality}")
        for i, file_path in enumerate(files):
            file_path = Path(file_path)
            try:
                embed = ENCODERS[modality](file_path)
                embed_path = out_dir / (file_path.stem + '.npy')
                np.save(embed_path, embed)
                embed_catalogue[modality].append(str(embed_path))
                status.update(i+1)
            except Exception as e:
                logger.error(f"Failed to embed {file_path}: {e}")
        status.complete(f"{modality} embedding complete.")
    # Save embedding catalogue
    embed_cat_path = EMBED_ROOT / 'b2_embedding_catalogue.json'
    with open(embed_cat_path, 'w', encoding='utf-8') as f:
        json.dump(embed_catalogue, f, indent=2)
    logger.success(f"Embeddings complete. Catalogue saved to {embed_cat_path}")

if __name__ == "__main__":
    embed_all()
