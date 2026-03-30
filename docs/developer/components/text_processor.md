# Text Processor

**Created:** May 21, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\developer\components\text_processor.md #attention_mechanism #documentation #memory_management #multimodal #pytorch #tokenization #training #transformer  
**Category:** Developer Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

responsible_party: @GitHubCopilot
last_updated: 2025-05-31
---

# Text Processor Component

## 1. Overview

The Text Processor component is responsible for ingesting raw text data, cleaning it, tokenizing it into a numerical format suitable for language models, and preparing inputs (like input IDs, attention masks, and token type IDs) for various downstream NLP tasks within the ImpressionCore-B1 model. This includes text understanding, feature extraction for multimodal fusion, and input to generative language models.

This document outlines the canonical design for the `TextProcessor`.

## 2. Responsibilities

- **Text Ingestion**: Load text data from strings, files, or other sources.
- **Text Cleaning & Normalization**:
  - Lowercasing.
  - Removing HTML tags, special characters, or irrelevant symbols.
  - Unicode normalization.
  - Handling contractions, emojis, URLs, etc. (policy-based).
- **Tokenization**:
  - Splitting text into tokens (words, subwords, characters) based on a chosen tokenizer (e.g., WordPiece, BPE, SentencePiece, Unigram).
  - Converting tokens to numerical IDs using a predefined vocabulary.
- **Input Formatting**:
  - Generating `input_ids`, `attention_mask`, and optionally `token_type_ids`.
  - Padding sequences to a consistent length within a batch or to a model's maximum sequence length.
  - Truncating sequences that exceed the maximum length.
- **Output**: Provide tensors or numerical arrays consumable by language models (e.g., Transformers).

## 3. Architecture

```mermaid
graph TD
    A[Raw Text Input] --> B(Load Text);
    B --> C{Text Cleaning & Normalization};
    C --> D(Tokenization);
    D -- Tokens --> E{Convert to IDs};
    E -- Input IDs --> F{Padding & Truncation};
    F --> G[Generate Attention Mask];
    F --> H[Generate Token Type IDs (optional)];
    
    subgraph TextProcessor
        B
        C
        D
        E
        F
        G
        H
    end

    I[Output: Model Inputs]
    F -- Padded/Truncated IDs --> I;
    G -- Attention Mask --> I;
    H -- Token Type IDs --> I;
    
    I --> X[Language Model / Multimodal Fusion];
    
    J[Tokenizer & Vocab] --> D;
    J --> E;
```

## 4. Detailed Design

### 4.1. Input

- **Raw Text Data**:
  - Type: String, list of strings (for batching), file path.
  - Encoding: Assume UTF-8 unless specified.

### 4.2. Core Modules

#### 4.2.1. Text Cleaner/Normalizer

- **Purpose**: Standardize text and remove noise before tokenization.
- **Libraries**: `re` (regex), `unicodedata`, `bs4` (BeautifulSoup for HTML), custom rules.
- **Functionality (Configurable Steps)**:
  - **Lowercasing**: Convert all text to lowercase.
  - **HTML Stripping**: Remove HTML tags.
  - **Special Character Removal**: Remove or replace specific special characters, punctuation (policy-dependent).
  - **Unicode Normalization**: e.g., `NFC` or `NFKC`.
  - **Whitespace Normalization**: Consolidate multiple spaces, remove leading/trailing whitespace.
  - **(Optional) Contraction Expansion**: e.g., "don't" -> "do not".
  - **(Optional) Emoji/URL Handling**: Replace with special tokens or remove.

#### 4.2.2. Tokenizer

- **Purpose**: Segment text into tokens and map them to numerical IDs. This is the core of the text processor.
- **Libraries**: `transformers` (Hugging Face tokenizers), `tokenizers` (Hugging Face's standalone library), `sentencepiece`, custom implementations.
- **Functionality**:
  - **Load Tokenizer**: Instantiate a tokenizer from a pretrained model name/path or a local vocabulary file (e.g., `vocab.txt`, `merges.txt`, `tokenizer.json`).
    - Common types: WordPiece (BERT), BPE (GPT-2, RoBERTa), SentencePiece (XLNet, T5), Unigram.
  - **Tokenization**: Apply the tokenizer's algorithm to convert cleaned text strings into sequences of tokens.
  - **ID Conversion**: Convert tokens to their corresponding integer IDs from the tokenizer's vocabulary.
  - **Special Tokens**: Handle special tokens like `[CLS]`, `[SEP]`, `[PAD]`, `[UNK]`, `[MASK]` by adding them appropriately or using their IDs.
- *Memory Implication*: Vocabulary size and tokenizer complexity can impact memory for the tokenizer object itself. The primary memory impact comes from the generated ID sequences.

#### 4.2.3. Input Formatter (Padding & Truncation)

- **Purpose**: Ensure all input sequences for a model have a consistent length.
- **Functionality**:
  - **Padding**: Add padding tokens (using `[PAD]` token ID) to sequences shorter than the `max_length` or the longest sequence in a batch. Padding can be on the right (post-padding) or left (pre-padding).
  - **Truncation**: Remove tokens from sequences longer than `max_length`. Truncation can be from the end (most common), beginning, or a "longest_first" strategy for pairs of sequences.
  - **Attention Mask Generation**: Create a binary mask (typically 0s and 1s) indicating which tokens are actual content (1) and which are padding (0). This tells the model to ignore padding tokens during self-attention.
  - **Token Type IDs (Segment IDs) Generation**: For tasks involving pairs of sentences (e.g., question answering, sentence pair classification), generate IDs indicating which sentence each token belongs to (e.g., 0 for sentence A, 1 for sentence B).
- *Memory Implication*: `max_length` directly determines the size of the input tensors. Longer sequences require more memory. Dynamic padding (to the max length in the current batch) can be more memory-efficient than padding all sequences to a global `max_length` if sequence lengths vary significantly.

### 4.3. Output

- **Model Inputs**:
  - A dictionary or structured object (e.g., Hugging Face `BatchEncoding`) containing:
    - `input_ids`: Tensor of token IDs (e.g., `torch.Tensor` or `tf.Tensor`). Shape: `(batch_size, sequence_length)`.
    - `attention_mask`: Tensor indicating which tokens to attend to. Shape: `(batch_size, sequence_length)`.
    - `token_type_ids` (optional): Tensor for segment distinction. Shape: `(batch_size, sequence_length)`.
- **Data Type**: Typically `int64` for IDs and masks.

## 5. Configuration Parameters

- `tokenizer_name_or_path`: string (e.g., `\"bert-base-uncased\"`, path to local tokenizer files).
- `max_length`: integer (e.g., 128, 512).
- `padding_strategy`: string (e.g., `\"max_length\"`, `\"longest\"` for dynamic batch padding).
- `truncation_strategy`: string (e.g., `\"longest_first\"`, `\"only_first\"`, `\"only_second\"`).
- `add_special_tokens`: boolean (true/false).
- `return_tensors`: string (e.g., `\"pt\"` for PyTorch, `\"tf\"` for TensorFlow, `\"np\"` for NumPy).
- `text_cleaning_config`: dictionary defining cleaning steps (e.g., `{\"lowercase\": true, \"remove_html\": true}`).
- `do_lower_case` (often part of tokenizer config).

## 6. Memory and Performance Considerations

- **`max_length`**: The most significant factor for memory. Choose the smallest `max_length` that captures most of your data's information.
- **Vocabulary Size**: Larger vocabularies mean larger embedding layers in the model.
- **Tokenizer Speed**: Some tokenizers are faster than others. Rust-based tokenizers from Hugging Face (`tokenizers` library) are generally very fast.
- **Batch Processing**: Tokenizing and formatting text in batches is more efficient.
- **Dynamic Padding**: Padding to the maximum length in the current batch instead of a global maximum can save considerable memory and computation, especially with variable-length inputs.
- **Caching**: Cache tokenized results if processing the same text multiple times, especially during development or for static datasets.

## 7. Error Handling

- Errors loading tokenizer or vocabulary.
- Input text encoding issues.
- Configuration errors.
- Log errors and provide informative messages.

## 8. Dependencies

- `transformers` (Hugging Face)
- `tokenizers` (Hugging Face, often a dependency of `transformers`)
- `sentencepiece` (for certain tokenizers like XLNet, T5)
- `numpy`
- `torch` or `tensorflow` (if returning tensors)
- `re`, `unicodedata`, `bs4` (for text cleaning)

## 9. Future Enhancements

- Support for more advanced text cleaning and preprocessing pipelines (e.g., spell correction, grammar checking, if relevant).
- Integration with custom or specialized tokenizers.
- On-the-fly text augmentation (e.g., back-translation, synonym replacement) for training.
- More sophisticated handling of out-of-vocabulary (OOV) words if not using subword tokenizers.

This canonical design provides a foundational TextProcessor. Specific implementations will reside in `src/core/processors/text_processor.py` or similar, leveraging libraries like Hugging Face Transformers.
