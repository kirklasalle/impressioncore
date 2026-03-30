# ImpressionCore-B1 Direct Download List
**Created:** 2025-01-10 15:30  
**Purpose:** Exact URLs and destination paths for manual download

## CRITICAL DATASETS - DIRECT LINKS

### 1. LJSpeech Dataset (AUDIO - Priority 1)
**URL:** https://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2  
**Destination:** `d:/Projects/impressioncore/src/data/datasets/audio/ljspeech/LJSpeech-1.1.tar.bz2`  
**Size:** ~2.6 GB  
**Extract to:** `d:/Projects/impressioncore/src/data/datasets/audio/ljspeech/`

### 2. LibriSpeech Alignments (AUDIO - Priority 1)
**URL:** https://zenodo.org/record/2619474/files/librispeech_alignments.zip  
**Destination:** `d:/Projects/impressioncore/src/data/datasets/audio/alignments/librispeech_alignments.zip`  
**Size:** 623 MB  
**Extract to:** `d:/Projects/impressioncore/src/data/datasets/audio/alignments/`

### 3. LibriSpeech Clean 100 (AUDIO - Core Training)
**URL:** https://www.openslr.org/resources/12/train-clean-100.tar.gz  
**Destination:** `d:/Projects/impressioncore/src/data/datasets/audio/librispeech/train-clean-100.tar.gz`  
**Size:** 6.3 GB  
**Extract to:** `d:/Projects/impressioncore/src/data/datasets/audio/librispeech/`

### 4. LibriSpeech Dev Clean (AUDIO - Validation)
**URL:** https://www.openslr.org/resources/12/dev-clean.tar.gz  
**Destination:** `d:/Projects/impressioncore/src/data/datasets/audio/librispeech/dev-clean.tar.gz`  
**Size:** 337 MB  
**Extract to:** `d:/Projects/impressioncore/src/data/datasets/audio/librispeech/`

### 5. LibriSpeech Test Clean (AUDIO - Testing)
**URL:** https://www.openslr.org/resources/12/test-clean.tar.gz  
**Destination:** `d:/Projects/impressioncore/src/data/datasets/audio/librispeech/test-clean.tar.gz`  
**Size:** 346 MB  
**Extract to:** `d:/Projects/impressioncore/src/data/datasets/audio/librispeech/`

### 6. COCO 2017 Validation Images (IMAGES - Priority 1)
**URL:** http://images.cocodataset.org/zips/val2017.zip  
**Destination:** `d:/Projects/impressioncore/src/data/datasets/images/coco2017/val2017.zip`  
**Size:** 1 GB  
**Extract to:** `d:/Projects/impressioncore/src/data/datasets/images/coco2017/val2017/`

### 7. COCO 2017 Annotations (IMAGES - Priority 1)
**URL:** http://images.cocodataset.org/annotations/annotations_trainval2017.zip  
**Destination:** `d:/Projects/impressioncore/src/data/datasets/images/coco2017/annotations/annotations_trainval2017.zip`  
**Size:** 241 MB  
**Extract to:** `d:/Projects/impressioncore/src/data/datasets/images/coco2017/annotations/`

### 8. COCO 2017 Training Images (IMAGES - Priority 2)
**URL:** http://images.cocodataset.org/zips/train2017.zip  
**Destination:** `d:/Projects/impressioncore/src/data/datasets/images/coco2017/train2017.zip`  
**Size:** 18 GB  
**Extract to:** `d:/Projects/impressioncore/src/data/datasets/images/coco2017/train2017/`

## TEXT DATASETS (Priority 3)

### 9. WikiText-103 (TEXT)
**URL:** https://s3.amazonaws.com/research.metamind.io/wikitext/wikitext-103-v1.zip  
**Destination:** `d:/Projects/impressioncore/src/data/datasets/text/wikitext/wikitext-103-v1.zip`  
**Size:** 183 MB  
**Extract to:** `d:/Projects/impressioncore/src/data/datasets/text/wikitext/`

### 10. BookCorpus (Alternative - HuggingFace)
**URL:** https://huggingface.co/datasets/bookcorpus  
**Destination:** Use HuggingFace datasets library  
**Size:** ~4 GB  
**Extract to:** `d:/Projects/impressioncore/src/data/datasets/text/bookcorpus/`

## DOWNLOAD COMMANDS (Copy-Paste Ready)

```bash
# Create all directories first
mkdir -p d:/Projects/impressioncore/src/data/datasets/audio/ljspeech
mkdir -p d:/Projects/impressioncore/src/data/datasets/audio/alignments
mkdir -p d:/Projects/impressioncore/src/data/datasets/audio/librispeech
mkdir -p d:/Projects/impressioncore/src/data/datasets/images/coco2017/val2017
mkdir -p d:/Projects/impressioncore/src/data/datasets/images/coco2017/train2017
mkdir -p d:/Projects/impressioncore/src/data/datasets/images/coco2017/annotations
mkdir -p d:/Projects/impressioncore/src/data/datasets/text/wikitext
mkdir -p d:/Projects/impressioncore/src/data/datasets/text/bookcorpus

# Download commands (use wget, curl, or browser)
wget https://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2 -O "d:/Projects/impressioncore/src/data/datasets/audio/ljspeech/LJSpeech-1.1.tar.bz2"

wget https://zenodo.org/record/2619474/files/librispeech_alignments.zip -O "d:/Projects/impressioncore/src/data/datasets/audio/alignments/librispeech_alignments.zip"

wget https://www.openslr.org/resources/12/train-clean-100.tar.gz -O "d:/Projects/impressioncore/src/data/datasets/audio/librispeech/train-clean-100.tar.gz"

wget https://www.openslr.org/resources/12/dev-clean.tar.gz -O "d:/Projects/impressioncore/src/data/datasets/audio/librispeech/dev-clean.tar.gz"

wget https://www.openslr.org/resources/12/test-clean.tar.gz -O "d:/Projects/impressioncore/src/data/datasets/audio/librispeech/test-clean.tar.gz"

wget http://images.cocodataset.org/zips/val2017.zip -O "d:/Projects/impressioncore/src/data/datasets/images/coco2017/val2017.zip"

wget http://images.cocodataset.org/annotations/annotations_trainval2017.zip -O "d:/Projects/impressioncore/src/data/datasets/images/coco2017/annotations/annotations_trainval2017.zip"

wget http://images.cocodataset.org/zips/train2017.zip -O "d:/Projects/impressioncore/src/data/datasets/images/coco2017/train2017.zip"

wget https://s3.amazonaws.com/research.metamind.io/wikitext/wikitext-103-v1.zip -O "d:/Projects/impressioncore/src/data/datasets/text/wikitext/wikitext-103-v1.zip"
```

## EXTRACTION COMMANDS (After Download)

```bash
# Extract LJSpeech
cd d:/Projects/impressioncore/src/data/datasets/audio/ljspeech
tar -xjf LJSpeech-1.1.tar.bz2

# Extract LibriSpeech Alignments
cd d:/Projects/impressioncore/src/data/datasets/audio/alignments
unzip librispeech_alignments.zip

# Extract LibriSpeech datasets
cd d:/Projects/impressioncore/src/data/datasets/audio/librispeech
tar -xzf train-clean-100.tar.gz
tar -xzf dev-clean.tar.gz
tar -xzf test-clean.tar.gz

# Extract COCO datasets
cd d:/Projects/impressioncore/src/data/datasets/images/coco2017
unzip val2017.zip -d val2017/
unzip train2017.zip -d train2017/
unzip annotations/annotations_trainval2017.zip -d annotations/

# Extract WikiText
cd d:/Projects/impressioncore/src/data/datasets/text/wikitext
unzip wikitext-103-v1.zip
```

## TOTAL SIZE ESTIMATE
- **Priority 1 (Essential):** ~10.5 GB
- **Priority 2 (Training):** ~24 GB additional
- **Priority 3 (Text):** ~4.2 GB additional
- **TOTAL:** ~38.7 GB

## VERIFICATION AFTER DOWNLOAD
After downloading and extracting, run:
```bash
cd d:/Projects/impressioncore
python src/interfaces/cli/impressioncore_b1_cuda_cli.py --test-datasets
```
