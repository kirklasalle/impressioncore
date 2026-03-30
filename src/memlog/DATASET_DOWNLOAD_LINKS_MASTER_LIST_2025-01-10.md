# ImpressionCore-B1 Dataset Download Links Master List
**Created:** 2025-01-10  
**Author:** GitHub Copilot  
**Purpose:** Complete master list of exact download links for training datasets - DO NOT LOSE THIS!

## CRITICAL AUDIO DATASETS (Priority 1)

### 1. LibriSpeech with Phoneme Alignments
**Primary Source:** Zenodo (Loren Lugosch - Montreal Forced Aligner)
- **Direct Download:** https://zenodo.org/record/2619474
- **File:** librispeech_alignments.zip (623.0 MB)
- **MD5:** 2bab567d0ace651a4ba254e813629f46
- **Content:** 980 hours with phoneme + word alignments
- **Alternative:** HuggingFace: https://huggingface.co/datasets/gilkeyio/librispeech-alignments

**LibriSpeech Base Dataset:**
- **Primary Source:** OpenSLR
- **URL:** https://www.openslr.org/12
- **Subsets Needed:**
  - train-clean-100.tar.gz (6.3G)
  - train-clean-360.tar.gz (23G) 
  - dev-clean.tar.gz (337M)
  - test-clean.tar.gz (346M)

### 2. LJSpeech Dataset
**Primary Source:** Keith Ito
- **Official URL:** https://keithito.com/LJ-Speech-Dataset/
- **Direct Download:** https://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2
- **Size:** ~2.6 GB
- **Content:** 13,100 audio clips, single female speaker, 24 hours total
- **Alternative:** HuggingFace: https://huggingface.co/datasets/keithito/lj_speech

### 3. Mozilla CommonVoice (Backup Option)
**Primary Source:** Mozilla
- **URL:** https://commonvoice.mozilla.org/en/datasets
- **Latest:** Common Voice Corpus 21.0 (85.6 GB full, 781.24 MB delta)
- **Date:** 3/18/2025
- **Language:** English subset
- **Format:** MP3 + text files

## CRITICAL IMAGE DATASETS (Priority 2)

### 4. COCO Dataset (2017)
**Primary Source:** COCO Official
- **Base URL:** https://cocodataset.org/
- **Images:**
  - Train 2017: http://images.cocodataset.org/zips/train2017.zip (18GB)
  - Val 2017: http://images.cocodataset.org/zips/val2017.zip (1GB)
  - Test 2017: http://images.cocodataset.org/zips/test2017.zip (6GB)
- **Annotations:**
  - Train/Val 2017: http://images.cocodataset.org/annotations/annotations_trainval2017.zip (241MB)
  - Image Info Test 2017: http://images.cocodataset.org/annotations/image_info_test2017.zip (1MB)
- **Alternative:** HuggingFace: https://huggingface.co/datasets/rafaelpadilla/coco2017

### 5. Simple Image Dataset (Fallback)
**Generate locally using:**
- Unsplash API: https://unsplash.com/developers
- Pixabay API: https://pixabay.com/api/docs/
- Or use src/dev_tools/examples/prepare_training_data.py

## TEXT DATASETS (Priority 3)

### 6. Text Corpus Options
**Option A: Generate from existing sources**
- Wikipedia dumps: https://dumps.wikimedia.org/enwiki/
- Project Gutenberg: https://www.gutenberg.org/
- Use src/dev_tools/examples/prepare_training_data.py

**Option B: Pre-made text datasets**
- OpenWebText: https://github.com/jcpeterson/openwebtext
- BookCorpus alternative: https://github.com/soskek/bookcorpus

## DOWNLOAD STRATEGY AND ORDER

### Immediate Downloads (Start with these)
1. **LJSpeech** - Smallest, fastest download, good for initial testing
2. **LibriSpeech alignments** - Critical for phoneme training
3. **COCO val2017** - Smaller image set for validation

### Secondary Downloads (After testing)
4. **LibriSpeech train-clean-100** - Manageable training set
5. **COCO train2017** - Full image training set
6. **LibriSpeech larger sets** - If VRAM allows

### Tertiary Downloads (If needed)
7. **CommonVoice subset** - Additional speech variety
8. **Text corpus** - Can be generated locally

## DOWNLOAD COMMANDS

### Using wget (Git Bash)
```bash
# LJSpeech
wget https://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2

# LibriSpeech Alignments
wget https://zenodo.org/record/2619474/files/librispeech_alignments.zip

# COCO Val 2017
wget http://images.cocodataset.org/zips/val2017.zip
wget http://images.cocodataset.org/annotations/annotations_trainval2017.zip

# LibriSpeech Base
wget https://www.openslr.org/resources/12/train-clean-100.tar.gz
```

### Using Python (if wget fails)
```python
import requests
import os

def download_file(url, filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

# Example usage
download_file('https://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2', 'LJSpeech-1.1.tar.bz2')
```

## EXTRACTION AND PLACEMENT

### Target Directory Structure
```
src/data/datasets/
├── audio/
│   ├── ljspeech/           # Extract LJSpeech-1.1.tar.bz2 here
│   ├── librispeech/        # Extract LibriSpeech here
│   └── alignments/         # Extract librispeech_alignments.zip here
├── images/
│   ├── coco2017/
│   │   ├── train2017/      # Extract train2017.zip here
│   │   ├── val2017/        # Extract val2017.zip here
│   │   └── annotations/    # Extract annotations here
│   └── simple/             # Generated images
├── text/
│   ├── wikipedia/          # Wikipedia extracts
│   ├── gutenberg/          # Project Gutenberg texts
│   └── generated/          # Generated sample text
└── multimodal/             # Cross-modal datasets
```

### Extraction Commands
```bash
# Navigate to datasets directory
cd d:/Projects/impressioncore/src/data/datasets

# Extract LJSpeech
mkdir -p audio/ljspeech
tar -xjf LJSpeech-1.1.tar.bz2 -C audio/ljspeech

# Extract LibriSpeech Alignments
mkdir -p audio/alignments
unzip librispeech_alignments.zip -d audio/alignments

# Extract COCO
mkdir -p images/coco2017/{train2017,val2017,annotations}
unzip val2017.zip -d images/coco2017/
unzip annotations_trainval2017.zip -d images/coco2017/
```

## VERIFICATION CHECKLIST

### After Each Download
- [ ] Check file size matches expected size
- [ ] Verify MD5 hash if provided
- [ ] Test extraction/decompression
- [ ] Validate directory structure
- [ ] Run sample data loading test

### Dataset Validation Commands
```bash
# Verify LJSpeech structure
python src/data/dataset_manager.py --validate-audio ljspeech

# Verify COCO structure  
python src/data/dataset_manager.py --validate-images coco2017

# Test full dataset loading
python src/interfaces/cli/impressioncore_b1_cuda_cli.py --test-datasets
```

## MINIMUM VIABLE DATASETS (For 4GB VRAM)

### Phase 1: Basic Testing
- **LJSpeech:** ~100 audio samples (13MB subset)
- **COCO Val:** ~500 images (50MB subset)
- **Text:** 1,000 generated samples (1MB)

### Phase 2: Training Validation
- **LJSpeech:** Full dataset (2.6GB)
- **COCO Val:** Full validation set (1GB)
- **LibriSpeech:** train-clean-100 subset (6.3GB)

### Phase 3: Production Training
- **LibriSpeech:** Full clean sets + alignments
- **COCO:** Full train2017 set
- **Additional datasets** as VRAM allows

## TROUBLESHOOTING

### Common Download Issues
1. **403 Forbidden:** Try different user agent or direct browser download
2. **Timeout:** Use resume capability with wget -c
3. **Slow speeds:** Try alternative mirrors or sources
4. **Disk space:** Monitor available space before large downloads

### Alternative Sources
- **Academic Torrents:** https://academictorrents.com/
- **Kaggle Datasets:** https://www.kaggle.com/datasets
- **AWS Open Data:** https://registry.opendata.aws/
- **Google Cloud Public Datasets:** https://cloud.google.com/datasets

## BACKUP PLAN

If primary sources fail:
1. Use HuggingFace dataset hub as backup
2. Generate synthetic data using existing scripts
3. Download smaller subsets for initial development
4. Use academic institution mirrors if available

---
**CRITICAL:** Save this file and DO NOT delete these URLs. They are the exact sources needed to rebuild the ImpressionCore-B1 training datasets.
