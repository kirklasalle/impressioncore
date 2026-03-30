# ImpressionCore Examples

This directory contains example scripts for testing and training various components of the ImpressionCore system.

## Setup

Before running these examples, make sure you have:

1. Activated the virtual environment:

   ```
   cd /d:/Projects/impressioncore
   venv\Scripts\activate
   ```

2. Installed all required dependencies:

   ```
   pip install -r requirements.txt
   ```

## Available Examples

### Component Tests

- **test_all_components.py**: Tests the core components of ImpressionCore

  ```
  python examples/test_all_components.py
  ```

### Training Scripts

- **train_vae.py**: Trains a Variational Autoencoder for image generation

  ```
  python examples/train_vae.py --dataset mnist --batch-size 64 --epochs 10
  ```

- **train_documents.py**: Trains the ImpressionCore model on individual document files

  ```
  python examples/train_documents.py
  ```

- **mixed_corpus_training.py**: Trains on multiple text files with advanced options

  ```
  python examples/mixed_corpus_training.py
  ```

## Data Directories

- **trainingdocs/**: Place your .txt files here for document training
- **data/**: Images and datasets will be automatically downloaded here
- **output/**: Training results will be saved here
- **models/checkpoints/**: Model checkpoints will be saved here

## Troubleshooting

If you encounter errors:

1. Check that all required directories exist
2. Ensure your Python environment has all dependencies installed
3. For CUDA errors, verify your GPU drivers are up-to-date
4. See docs/TROUBLESHOOTING.md for common issues and solutions

## Example Text Data

For text training, you can use:

- Project Gutenberg books (make sure to strip headers/footers)
- Wikipedia articles in plain text format
- Your own writing samples (.txt files)

Place these in the "trainingdocs" directory before running document training scripts.
