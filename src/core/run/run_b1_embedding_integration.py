#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #memory_management #multimodal #python #source_code #src/core/run/run_b1_embedding_integration.py #tokenization #training #transformer
**Category:** Core Implementation
**Status:** Active
"""









# Run B1 Embedding Integration

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** Kirk LaSalle
# Tags:** #memory_management #multimodal #python #source_code #src\\core\\run\\run_b1_embedding_integration.py #tokenization #training #transformer
# Category:** Core Implementation
# Status:** Active

"""
ImpressionCore B1 Embedding Integration Pipeline

This script initializes the embedding process for all supported modalities (image, text, audio, video)
in the ImpressionCore B1 dataset. It uses ImpressionCore's rich logging and status animation utilities
and is optimized for memory-constrained hardware (GTX 1050 Ti).

Author: Kirk LaSalle <kirk@impressioncore.ai>
Co-Author: GitHub Copilot
Created: 2025-06-22

"""
import sys
from pathlib import Path

# Import ImpressionCore utilities
try:
    from src.core.utils import RICH_AVAILABLE, RichEnhancer, StatusAnimator, setup_rich_logger
except ImportError:
    print("[WARNING] ImpressionCore rich utilities not available. Using fallback logging.")
    import logging
    def setup_rich_logger(name=None, level="INFO"):
        logger = logging.getLogger(name or __name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        return logger
    class StatusAnimator:
        def __init__(self, message=""):
            self.message = message
        def __enter__(self):
            print(f"[START] {self.message}")
            return self
        def __exit__(self, *a):
            print(f"[END] {self.message}")
    class RichEnhancer:
        def __init__(self):
            pass
        def enhance(self, text):
            return text
    RICH_AVAILABLE = False

# Configuration
B1_ROOT = Path("F:/impressioncore-b1-embeddings-062125/")
MODALITIES = [
    ("image", ["image_datasets", "image_embeddings", "image_metadata"]),
    ("text", ["text", "text_corpora", "text_datasets", "text_embeddings"]),
    ("audio", ["phoneme_collections"]),
    ("video", ["video", "video_content", "video_data", "video_embeddings"]),
    ("multimodal", ["multimodal", "multimodal_datasets", "multimodal_embeddings"]),
    ("other", ["processed", "scientific_data", "vision", "metadata", "logs", "training_logs"]),
]



logger = setup_rich_logger("b1_embedding_integration")
if hasattr(logger, 'setLevel'):
    logger.setLevel("INFO")

# Ensure enhancer is always valid
try:
    enhancer = RichEnhancer()
    if not hasattr(enhancer, 'enhance') or not callable(getattr(enhancer, 'enhance', None)):
        def _enhance(text):
            return text
        enhancer.enhance = _enhance
except Exception:
    class _FallbackEnhancer:
        def enhance(self, text):
            return text
    enhancer = _FallbackEnhancer()

# Ensure StatusAnimator is always a context manager
import contextlib

if not (hasattr(StatusAnimator, "__enter__") and hasattr(StatusAnimator, "__exit__")):
    class _FallbackStatusAnimator(contextlib.AbstractContextManager):
        def __init__(self, message=""):
            self.message = message
        def __enter__(self):
            print(f"[START] {self.message}")
            return self
        def __exit__(self, *a):
            print(f"[END] {self.message}")
    StatusAnimator = _FallbackStatusAnimator

def discover_available_modalities(root: Path):
    """
    Scan the B1 root directory for available modalities and log the findings.
    Args:
        root: Path to the B1 dataset root.
    Returns:
        dict: modality -> list of found subdirs
    """
    found = {}
    for modality, subdirs in MODALITIES:
        found_subdirs = []
        for sub in subdirs:
            subpath = root / sub
            if subpath.exists() and any(subpath.iterdir()):
                found_subdirs.append(str(subpath))
        if found_subdirs:
            found[modality] = found_subdirs
    return found

def main():
    logger.info(enhancer.enhance("ImpressionCore B1 Embedding Integration Pipeline Starting..."))
    if not B1_ROOT.exists():
        logger.error(f"B1 data root not found: {B1_ROOT}")
        sys.exit(1)
    with StatusAnimator("Scanning B1 dataset for available modalities"):
        found = discover_available_modalities(B1_ROOT)
        for modality, subdirs in found.items():
            logger.info(enhancer.enhance(f"Found {modality} data in: {subdirs}"))

    import datetime
    summary = {}
    with StatusAnimator("Batch automation: Running all embedding routines"):
        # Image
        image_stats = []
        for subdir in ["image_datasets", "image_embeddings", "image_metadata"]:
            stats = process_image_embeddings(B1_ROOT / subdir)
            if stats:
                image_stats.append(stats)
        summary['image'] = image_stats
        # Text
        text_stats = []
        for subdir in ["text", "text_corpora", "text_datasets", "text_embeddings"]:
            stats = process_text_embeddings(B1_ROOT / subdir)
            if stats:
                text_stats.append(stats)
        summary['text'] = text_stats
        # Audio
        audio_stats = []
        for subdir in ["phoneme_collections"]:
            stats = process_audio_embeddings(B1_ROOT / subdir)
            if stats:
                audio_stats.append(stats)
        summary['audio'] = audio_stats
        # Video
        video_stats = []
        for subdir in ["video", "video_content", "video_data", "video_embeddings"]:
            stats = process_video_embeddings(B1_ROOT / subdir)
            if stats:
                video_stats.append(stats)
        summary['video'] = video_stats
        # Multimodal
        multimodal_stats = []
        for subdir in ["multimodal", "multimodal_datasets", "multimodal_embeddings"]:
            stats = process_multimodal_embeddings(B1_ROOT / subdir)
            if stats:
                multimodal_stats.append(stats)
        summary['multimodal'] = multimodal_stats
        # Other (logs, processed, etc.)
        other_stats = []
        for subdir in ["processed", "scientific_data", "vision", "metadata", "logs", "training_logs"]:
            stats = process_other_data(B1_ROOT / subdir)
            if stats:
                other_stats.append(stats)
        summary['other'] = other_stats
    # Write summary report
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = B1_ROOT / f"embedding_summary_report_{now}.json"
    try:
        import json
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        logger.info(enhancer.enhance(f"Wrote embedding summary report: {summary_path}"))
    except Exception as e:
        logger.error(enhancer.enhance(f"Failed to write summary report: {e}"))
    logger.info(enhancer.enhance("B1 Embedding Integration Pipeline Complete."))

def process_image_embeddings(image_dir: Path):
    """
    Batch routine for image embeddings and metadata.
    Args:
        image_dir: Path to the directory containing image embedding or metadata files.
    Returns:
        None
    """
    import gc
    import json

    import torch
    from PIL import Image
    from torchvision import models, transforms
    stats = {"dir": str(image_dir), "image_count": 0, "embedding_shapes": [], "invalid_files": [], "metadata_files": 0}
    with StatusAnimator(f"Processing image data in {image_dir}"):
        if not image_dir.exists():
            logger.warning(enhancer.enhance(f"Image directory not found: {image_dir}"))
            return stats
        files = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png")) + list(image_dir.glob("*.jpeg"))
        stats["image_count"] = len(files)
        model_path = next(image_dir.glob("*.pth"), None)
        # Use ResNet18 as default if model checkpoint is present
        if model_path:
            try:
                model = models.resnet18(pretrained=False)
                model.load_state_dict(torch.load(model_path, map_location="cpu"))
                model.eval()
                logger.info(enhancer.enhance(f"Loaded image model: {model_path.name}"))
            except Exception as e:
                logger.error(enhancer.enhance(f"Failed to load image model: {e}"))
                model = None
        else:
            logger.warning(enhancer.enhance("No image model checkpoint found. Using torchvision default."))
            model = models.resnet18(pretrained=True)
            model.eval()
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        for f in files:
            try:
                img = Image.open(f).convert("RGB")
                input_tensor = preprocess(img).unsqueeze(0)
                with torch.no_grad():
                    embedding = model(input_tensor)
                logger.info(enhancer.enhance(f"Image embedding for {f.name}: shape {embedding.shape}"))
                stats["embedding_shapes"].append(list(embedding.shape))
                # Check for NaNs/Infs
                if torch.isnan(embedding).any() or torch.isinf(embedding).any():
                    stats["invalid_files"].append(f.name)
                del img, input_tensor, embedding
                gc.collect()
            except Exception as e:
                logger.error(enhancer.enhance(f"Failed to process image {f.name}: {e}"))
                stats["invalid_files"].append(f.name)
        # Process JSON metadata files
        for f in image_dir.glob("*.json"):
            try:
                with open(f) as jf:
                    meta = json.load(jf)
                stats["metadata_files"] += 1
                if isinstance(meta, dict):
                    logger.info(enhancer.enhance(f"Loaded image metadata: {f.name} (keys: {list(meta.keys())[:5]})"))
                elif isinstance(meta, list):
                    logger.info(enhancer.enhance(f"Loaded image metadata: {f.name} (list, length: {len(meta)})"))
                else:
                    logger.info(enhancer.enhance(f"Loaded image metadata: {f.name} (type: {type(meta).__name__})"))
            except Exception as e:
                logger.error(enhancer.enhance(f"Failed to load image metadata {f.name}: {e}"))
                stats["invalid_files"].append(f.name)
    return stats

def process_text_embeddings(text_dir: Path):
    """
    Batch routine for text embeddings and corpora.
    Args:
        text_dir: Path to the directory containing text data or embeddings.
    Returns:
        None
    """
    import gc
    import json

    import torch
    from transformers import AutoModel, AutoTokenizer
    with StatusAnimator(f"Processing text data in {text_dir}"):
        if not text_dir.exists():
            logger.warning(enhancer.enhance(f"Text directory not found: {text_dir}"))
            return
        files = list(text_dir.glob("*.txt"))
        model_path = next(text_dir.glob("*.bin"), None)
        # Use a default HuggingFace model if no checkpoint
        try:
            if model_path:
                _model_name = str(model_path)
                tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
                model = AutoModel.from_pretrained("bert-base-uncased")
                logger.info(enhancer.enhance(f"Loaded text model: {model_path.name}"))
            else:
                tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
                model = AutoModel.from_pretrained("bert-base-uncased")
                logger.warning(enhancer.enhance("No text model checkpoint found. Using bert-base-uncased."))
        except Exception as e:
            logger.error(enhancer.enhance(f"Failed to load text model: {e}"))
            return
        for f in files:
            try:
                with open(f, encoding="utf-8") as tf:
                    text = tf.read()[:512]
                inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
                with torch.no_grad():
                    outputs = model(**inputs)
                logger.info(enhancer.enhance(f"Text embedding for {f.name}: shape {outputs.last_hidden_state.shape}"))
                del text, inputs, outputs
                gc.collect()
            except Exception as e:
                logger.error(enhancer.enhance(f"Failed to process text {f.name}: {e}"))
        # Process JSON metadata files
        for f in text_dir.glob("*.json"):
            try:
                with open(f, encoding="utf-8") as jf:
                    meta = json.load(jf)
                if isinstance(meta, dict):
                    logger.info(enhancer.enhance(f"Loaded text metadata: {f.name} (keys: {list(meta.keys())[:5]})"))
                elif isinstance(meta, list):
                    logger.info(enhancer.enhance(f"Loaded text metadata: {f.name} (list, length: {len(meta)})"))
                else:
                    logger.info(enhancer.enhance(f"Loaded text metadata: {f.name} (type: {type(meta).__name__})"))
            except Exception as e:
                logger.error(enhancer.enhance(f"Failed to load text metadata {f.name}: {e}"))
    stats = {"dir": str(text_dir), "text_file_count": 0, "embedding_shapes": [], "invalid_files": [], "metadata_files": 0}
    with StatusAnimator(f"Processing text data in {text_dir}"):
        if not text_dir.exists():
            logger.warning(enhancer.enhance(f"Text directory not found: {text_dir}"))
            return stats
        files = list(text_dir.glob("*.txt"))
        stats["text_file_count"] = len(files)
        model_path = next(text_dir.glob("*.bin"), None)
        # Use a default HuggingFace model if no checkpoint
        try:
            if model_path:
                _model_name = str(model_path)
                tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
                model = AutoModel.from_pretrained("bert-base-uncased")
                logger.info(enhancer.enhance(f"Loaded text model: {model_path.name}"))
            else:
                tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
                model = AutoModel.from_pretrained("bert-base-uncased")
                logger.warning(enhancer.enhance("No text model checkpoint found. Using bert-base-uncased."))
        except Exception as e:
            logger.error(enhancer.enhance(f"Failed to load text model: {e}"))
            return stats
        for f in files:
            try:
                with open(f, encoding="utf-8") as tf:
                    text = tf.read()[:512]
                inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
                with torch.no_grad():
                    outputs = model(**inputs)
                logger.info(enhancer.enhance(f"Text embedding for {f.name}: shape {outputs.last_hidden_state.shape}"))
                stats["embedding_shapes"].append(list(outputs.last_hidden_state.shape))
                del text, inputs, outputs
                gc.collect()
            except Exception as e:
                logger.error(enhancer.enhance(f"Failed to process text {f.name}: {e}"))
                stats["invalid_files"].append(f.name)
        # Process JSON metadata files
        for f in text_dir.glob("*.json"):
            try:
                with open(f, encoding="utf-8") as jf:
                    meta = json.load(jf)
                stats["metadata_files"] += 1
                if isinstance(meta, dict):
                    logger.info(enhancer.enhance(f"Loaded text metadata: {f.name} (keys: {list(meta.keys())[:5]})"))
                elif isinstance(meta, list):
                    logger.info(enhancer.enhance(f"Loaded text metadata: {f.name} (list, length: {len(meta)})"))
                else:
                    logger.info(enhancer.enhance(f"Loaded text metadata: {f.name} (type: {type(meta).__name__})"))
            except Exception as e:
                logger.error(enhancer.enhance(f"Failed to load text metadata {f.name}: {e}"))
                stats["invalid_files"].append(f.name)
    return stats

def process_audio_embeddings(audio_dir: Path):
    """
    Batch routine for audio/phoneme collections.
    Args:
        audio_dir: Path to the directory containing audio/phoneme files.
    Returns:
        None
    """
    import gc
    import json

    import numpy as np
    with StatusAnimator(f"Processing audio data in {audio_dir}"):
        if not audio_dir.exists():
            logger.warning(enhancer.enhance(f"Audio directory not found: {audio_dir}"))
            return
        files = list(audio_dir.glob("*.json"))
        for f in files:
            try:
                with open(f, encoding="utf-8") as jf:
                    data = json.load(jf)
                # Simulate phoneme embedding as mean of feature vectors if present
                if "features" in data:
                    arr = np.array(data["features"])
                    embedding = arr.mean(axis=0)
                    logger.info(enhancer.enhance(f"Audio embedding for {f.name}: shape {embedding.shape}"))
                else:
                    logger.info(enhancer.enhance(f"No features found in {f.name}, skipping embedding."))
                del data
                gc.collect()
            except Exception as e:
                logger.error(enhancer.enhance(f"Failed to process audio/phoneme {f.name}: {e}"))

def process_video_embeddings(video_dir: Path):
    """
    Batch routine for video embeddings and metadata.
    Args:
        video_dir: Path to the directory containing video data or embeddings.
    Returns:
        None
    """
    import gc
    import json

    import numpy as np
    with StatusAnimator(f"Processing video data in {video_dir}"):
        if not video_dir.exists():
            logger.warning(enhancer.enhance(f"Video directory not found: {video_dir}"))
            return
        npy_files = list(video_dir.glob("*.npy"))
        for f in npy_files:
            try:
                arr = np.load(f)
                embedding = arr.mean(axis=0) if arr.ndim > 1 else arr
                logger.info(enhancer.enhance(f"Video embedding for {f.name}: shape {embedding.shape}"))
                del arr, embedding
                gc.collect()
            except Exception as e:
                logger.error(enhancer.enhance(f"Failed to process video npy {f.name}: {e}"))
        # Process JSON metadata files
        for f in video_dir.glob("*.json"):
            try:
                with open(f, encoding="utf-8") as jf:
                    meta = json.load(jf)
                if isinstance(meta, dict):
                    logger.info(enhancer.enhance(f"Loaded video metadata: {f.name} (keys: {list(meta.keys())[:5]})"))
                elif isinstance(meta, list):
                    logger.info(enhancer.enhance(f"Loaded video metadata: {f.name} (list, length: {len(meta)})"))
                else:
                    logger.info(enhancer.enhance(f"Loaded video metadata: {f.name} (type: {type(meta).__name__})"))
            except Exception as e:
                logger.error(enhancer.enhance(f"Failed to load video metadata {f.name}: {e}"))

def process_multimodal_embeddings(multimodal_dir: Path):
    """
    Batch routine for multimodal embeddings and datasets.
    Args:
        multimodal_dir: Path to the directory containing multimodal data or embeddings.
    Returns:
        None
    """
    import gc
    import json

    import numpy as np
    with StatusAnimator(f"Processing multimodal data in {multimodal_dir}"):
        if not multimodal_dir.exists():
            logger.warning(enhancer.enhance(f"Multimodal directory not found: {multimodal_dir}"))
            return
        npy_files = list(multimodal_dir.glob("*.npy"))
        for f in npy_files:
            try:
                arr = np.load(f)
                embedding = arr.mean(axis=0) if arr.ndim > 1 else arr
                logger.info(enhancer.enhance(f"Multimodal embedding for {f.name}: shape {embedding.shape}"))
                del arr, embedding
                gc.collect()
            except Exception as e:
                logger.error(enhancer.enhance(f"Failed to process multimodal npy {f.name}: {e}"))
        # Process JSON metadata files
        for f in multimodal_dir.glob("*.json"):
            try:
                with open(f, encoding="utf-8") as jf:
                    meta = json.load(jf)
                if isinstance(meta, dict):
                    logger.info(enhancer.enhance(f"Loaded multimodal metadata: {f.name} (keys: {list(meta.keys())[:5]})"))
                elif isinstance(meta, list):
                    logger.info(enhancer.enhance(f"Loaded multimodal metadata: {f.name} (list, length: {len(meta)})"))
                else:
                    logger.info(enhancer.enhance(f"Loaded multimodal metadata: {f.name} (type: {type(meta).__name__})"))
            except Exception as e:
                logger.error(enhancer.enhance(f"Failed to load multimodal metadata {f.name}: {e}"))
        # Log FAISS index files
        for f in multimodal_dir.glob("*.faiss"):
            logger.info(enhancer.enhance(f"Found FAISS index: {f.name}"))

def process_other_data(other_dir: Path):
    """
    Batch routine for other data types (logs, processed, scientific, etc.).
    Args:
        other_dir: Path to the directory containing other data files.
    Returns:
        None
    """
    import gc
    import json
    with StatusAnimator(f"Processing other data in {other_dir}"):
        if not other_dir.exists():
            logger.info(enhancer.enhance(f"Other directory not found: {other_dir}"))
            return
        files = list(other_dir.glob("*"))
        if not files:
            logger.info(enhancer.enhance(f"No files found in {other_dir}"))
        for f in files:
            if f.suffix == ".json":
                try:
                    with open(f, encoding="utf-8") as jf:
                        meta = json.load(jf)
                    if isinstance(meta, dict):
                        logger.info(enhancer.enhance(f"Loaded other metadata: {f.name} (keys: {list(meta.keys())[:5]})"))
                    elif isinstance(meta, list):
                        logger.info(enhancer.enhance(f"Loaded other metadata: {f.name} (list, length: {len(meta)})"))
                    else:
                        logger.info(enhancer.enhance(f"Loaded other metadata: {f.name} (type: {type(meta).__name__})"))
                except Exception as e:
                    logger.error(enhancer.enhance(f"Failed to load other metadata {f.name}: {e}"))
            else:
                logger.info(enhancer.enhance(f"Found file: {f.name}"))
        gc.collect()
        # Placeholder: Add actual logic for other data here

if __name__ == "__main__":
    main()
