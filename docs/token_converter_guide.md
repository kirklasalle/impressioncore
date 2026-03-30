# Token Converter Tool Guide

The Token Converter Tool allows you to convert tokenized content between different file formats for better interoperability with various systems.

## Usage

```bash
python -m impressioncore.token_converter_tool input_file output_file [options]
```

### Arguments

- `input_file`: Path to the input token file
- `output_file`: Path to save the converted token file
- `--input-format`: Input file format (inferred from extension if not specified)
- `--output-format`: Output file format (inferred from extension if not specified)

### Supported Formats

- `json`: JSON format with token IDs in an array
- `numpy`: NumPy binary format
- `torch`: PyTorch tensor format
- `text`: Plain text format with space-separated token IDs

### Examples

Convert from JSON to PyTorch format:

```bash
python -m impressioncore.token_converter_tool tokens.json tokens.pt
```

Convert from PyTorch to NumPy format:

```bash
python -m impressioncore.token_converter_tool tokens.pt tokens.npy
```

Explicitly specify formats:

```bash
python -m impressioncore.token_converter_tool tokens.dat tokens.txt --input-format=json --output-format=text
```

## Integration with Tokenizers

Token files produced by ImpressionCore tokenizers can be directly used with this tool:

```bash
# First, tokenize a text file
python -m impressioncore.tokenize_utility tokenize-text mytext.txt tokens.json

# Convert the tokens to PyTorch format
python -m impressioncore.token_converter_tool tokens.json tokens.pt

# Use the tokens in your PyTorch code
```

## Batch Processing

For batch conversion of multiple files, you can use shell scripting:

```bash
# Example bash script
for file in *.json; do
    python -m impressioncore.token_converter_tool "$file" "${file%.json}.pt"
done
```
