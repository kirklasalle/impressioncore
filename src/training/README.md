# ImpressionCore Training

This directory contains training scripts and configurations for the ImpressionCore framework. These scripts allow you to train various components, including tokenizers and models.

## Contents

- `train_tokenizer.py` - Script for training text and image tokenizers
- `config/` - Configuration files for training
  - `tokenizer_training.py` - Configuration for tokenizer training
  - `latent_diffusion_config.py` - Configuration for latent diffusion training
- `web/` - Web-based training interfaces

## Tokenizer Training

The `train_tokenizer.py` script supports training both text and image tokenizers.

### Training Text Tokenizers

To train a text tokenizer:

```bash
python -m training.train_tokenizer --type text --text-corpus data/text_corpus --output-dir data/tokenizer
```

Parameters:

- `--vocab-size` - Size of the vocabulary (default: 50257)
- `--config` - Path to a JSON configuration file

### Training Image Tokenizers

To train an image tokenizer:

```bash
python -m training.train_tokenizer --type image --image-dir data/image_dataset --output-dir data/tokenizer
```

Parameters:

- `--image-size` - Size of images (default: 256)
- `--patch-size` - Size of patches (default: 16)
- `--num-tokens` - Size of the token vocabulary (default: 8192)

### Training Both Tokenizers

To train both text and image tokenizers:

```bash
python -m training.train_tokenizer --type both --text-corpus data/text_corpus --image-dir data/image_dataset
```

## Configuration

You can provide a custom configuration file using the `--config` parameter. The configuration file should be a JSON file with the following structure:

```json
{
  "text": {
    "vocab_size": 50257,
    "min_frequency": 2,
    "special_tokens": ["<unk>", "<pad>", "<bos>", "<eos>", "<mask>"]
  },
  "image": {
    "image_size": 256,
    "patch_size": 16,
    "num_tokens": 8192,
    "batch_size": 64
  }
}
```

## Hardware Requirements

Tokenizer training is optimized for hardware with limited VRAM:

- Text tokenizer training is lightweight and can run on CPU
- Image tokenizer training benefits from GPU but is designed to work on GPUs with 4GB VRAM like the GTX 1050 Ti
