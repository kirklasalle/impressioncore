#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #multimodal #python #source_code #src/core/utils/generate_b2_embeddings.py #testing #tokenization
**Category:** Core Implementation
**Status:** Active
"""









# Generate B2 Embeddings

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #cuda #multimodal #python #source_code #src\\core\\utils\\generate_b2_embeddings.py #testing #tokenization
# Category:** Core Implementation
# Status:** Active

"""
generate_b2_embeddings.py
-------------------------
Automates B2 embedding generation for all dataset splits.

Usage:
    python src/core/utils/generate_b2_embeddings.py --dataset_root F:/datasets --embedding_root F:/b2_embeddings --splits train val test
"""
import argparse
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from PIL import Image

from core.ai.preprocessing.audio_processor import AudioProcessor
from core.ai.preprocessing.image_processor import ImageProcessor

# --- Real B2 Model and Preprocessing Imports ---
from core.kernel.b2_multimodal_model import B2MultimodalModel


def load_b2_embedding_model(device='cuda' if torch.cuda.is_available() else 'cpu'):  # noqa: B008
    # Load the real B2 multimodal model
    model = B2MultimodalModel()
    model.eval()
    model.to(device)
    return model

def get_tokenizer():
    # Use a simple whitespace tokenizer for demonstration; replace with your production tokenizer
    class SimpleTokenizer:
        def __call__(self, text, return_tensors=None, padding=True, truncation=True, max_length=512):
            tokens = text.split()
            ids = [min(hash(t) % 50257, 50256) for t in tokens][:max_length]
            tensor = torch.tensor([ids], dtype=torch.long)
            return {'input_ids': tensor}
    return SimpleTokenizer()

def get_image_processor():
    return ImageProcessor().process

def get_audio_processor():
    return AudioProcessor().process

def preprocess_image(image_path):
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img).astype(np.float32) / 255.0
    tensor = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0)  # (1, 3, H, W)
    return tensor

def preprocess_audio(audio_path):
    arr, sr = sf.read(audio_path)
    arr = arr.astype(np.float32)
    tensor = torch.from_numpy(arr).unsqueeze(0)  # (1, samples)
    return tensor

def preprocess_video(video_path):
    # Placeholder: expects pre-extracted frame features as .npy
    arr = np.load(video_path)
    tensor = torch.from_numpy(arr).unsqueeze(0)  # (1, frames, features)
    return tensor


def generate_embeddings_for_split(model, tokenizer, image_processor, audio_processor, split_path, output_root, device):
    modalities = ['text', 'images', 'audio', 'video']
    for modality in modalities:
        input_dir = split_path / modality
        output_dir = output_root / modality
        output_dir.mkdir(parents=True, exist_ok=True)
        if not input_dir.exists():
            print(f"[WARN] {modality} input dir missing: {input_dir}")
            continue
        files = list(input_dir.glob('*'))
        if not files:
            print(f"[WARN] No files for {modality} in {input_dir}")
            continue
        print(f"[INFO] Generating {modality} embeddings for {len(files)} files...")
        for sample_file in files:
            try:
                if modality == 'text' and sample_file.suffix in ['.txt', '.json']:
                    with open(sample_file, encoding='utf-8') as f:
                        text = f.read()
                    tokens = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
                    input_ids = tokens['input_ids'].to(device)
                    with torch.no_grad():
                        emb = model.text_encoder(input_ids)
                        pooled = emb.mean(dim=1).cpu().numpy()[0]
                elif modality == 'images' and sample_file.suffix in ['.jpg', '.png', '.jpeg']:
                    img_tensor = preprocess_image(sample_file).to(device)
                    img_tensor = image_processor(img_tensor)
                    with torch.no_grad():
                        emb = model.vision_encoder(img_tensor)
                        pooled = emb.mean(dim=1).cpu().numpy()[0]
                elif modality == 'audio' and sample_file.suffix in ['.wav', '.flac', '.mp3']:
                    audio_tensor = preprocess_audio(sample_file).to(device)
                    audio_tensor = audio_processor(audio_tensor)
                    with torch.no_grad():
                        emb = model.audio_encoder(audio_tensor)
                        pooled = emb.mean(dim=1).cpu().numpy()[0]
                elif modality == 'video' and sample_file.suffix in ['.npy']:
                    video_tensor = preprocess_video(sample_file).to(device)
                    with torch.no_grad():
                        emb = model.video_encoder(video_tensor)
                        pooled = emb.mean(dim=1).cpu().numpy()[0]
                else:
                    print(f"[SKIP] Unsupported file type: {sample_file}")
                    continue
                out_path = output_dir / (sample_file.stem + '.npy')
                np.save(out_path, pooled)
                print(f"[OK] Saved {modality} embedding: {out_path}")
            except Exception as e:
                print(f"[FAIL] {modality} {sample_file}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Generate B2 embeddings for all splits and modalities.")
    parser.add_argument('--dataset_root', type=str, required=True, help='Path to dataset root')
    parser.add_argument('--embedding_root', type=str, required=True, help='Path to output embedding root')
    parser.add_argument('--splits', nargs='+', default=['train', 'val', 'test'], help='Dataset splits to process')
    args = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = load_b2_embedding_model(device)
    tokenizer = get_tokenizer()
    image_processor = get_image_processor()
    audio_processor = get_audio_processor()

    for split in args.splits:
        split_path = Path(args.dataset_root) / split
        output_root = Path(args.embedding_root) / split
        if not split_path.exists():
            print(f"[ERROR] Dataset split missing: {split_path}")
            continue
        print(f"[INFO] Generating embeddings for split: {split}")
        generate_embeddings_for_split(model, tokenizer, image_processor, audio_processor, split_path, output_root, device)

if __name__ == "__main__":
    main()
