#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #multimodal #python #source_code #src/dev_tools/data_generation/prepare_raw_data.py #testing #training
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #multimodal #python #source_code #src/dev_tools/data_generation/prepare_raw_data.py #testing #training
# Category:** Development Tools
# Status:** Active

"""
Raw Data Preparation Utility for ImpressionCore B2
Prepare and organize multimodal conversation data for training

This script helps organize real conversation data into the format expected
by the raw data training pipeline.
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd


class RawDataPreparer:
    def generate_real_manifest_from_catalogue(self, catalogue_path: str, output_dir: str | None = None, num_samples: int | None = None, dry_run: bool = False, force: bool = False, real_image_dir: str | None = None, real_audio_dir: str | None = None):
        """
        Generate a real-data manifest using only samples that have all modalities (embedding, image, audio).
        Args:
            catalogue_path: Path to b2_embedding_catalogue.json
            output_dir: Directory to write manifests (default: self.output_dir)
            num_samples: Number of samples to include (default: all aligned)
            real_image_dir: Directory containing real images (optional)
            real_audio_dir: Directory containing real audio (optional)
        """
        import random
        output_dir = Path(output_dir) if output_dir else self.output_dir
        if output_dir.exists() and not force:
            print(f"❌ Output directory {output_dir} already exists. Use --force to overwrite.")
            return
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(catalogue_path, encoding='utf-8') as f:
            catalogue = json.load(f)
        # Get embedding IDs (assume filename stem is unique ID)
        embedding_paths = []
        embedding_ids = set()
        for v in catalogue.values():
            for p in v:
                embedding_paths.append(p)
                embedding_ids.add(Path(p).stem)
        # Get image and audio IDs
        image_ids = set()
        audio_ids = set()
        if real_image_dir and Path(real_image_dir).exists():
            sorted([str(p) for p in Path(real_image_dir).glob("*.jpg")])
            image_ids = set(Path(p).stem for p in Path(real_image_dir).glob("*.jpg"))
        if real_audio_dir and Path(real_audio_dir).exists():
            sorted([str(p) for p in Path(real_audio_dir).glob("*.wav")])
            audio_ids = set(Path(p).stem for p in Path(real_audio_dir).glob("*.wav"))
        # Find intersection of IDs
        aligned_ids = list(embedding_ids & image_ids & audio_ids)
        if not aligned_ids:
            print("❌ No aligned samples found across all modalities.")
            return
        random.shuffle(aligned_ids)
        if num_samples is not None and num_samples < len(aligned_ids):
            aligned_ids = aligned_ids[:num_samples]
        # Build lookup for embedding path, image, audio
        emb_path_map = {Path(p).stem: p for p in embedding_paths}
        img_path_map = {Path(p).stem: p for p in Path(real_image_dir).glob("*.jpg")} if real_image_dir else {}
        aud_path_map = {Path(p).stem: p for p in Path(real_audio_dir).glob("*.wav")} if real_audio_dir else {}
        intents = ["greeting", "question", "request", "complaint", "compliment", "goodbye", "information", "booking", "support", "feedback"]
        sentiment_map = {"negative": 0, "neutral": 1, "positive": 2}
        sentiment_cycle = ["negative", "neutral", "positive"]
        samples = []
        for i, cid in enumerate(aligned_ids):
            intent = intents[i % len(intents)]
            sentiment = sentiment_cycle[i % len(sentiment_cycle)]
            sample = {
                'conversation_id': f"real_{i:05d}",
                'text': f"[REAL DATA] Sample {i}",
                'embedding_path': emb_path_map[cid],
                'image_path': f"images/{Path(img_path_map[cid]).name}" if cid in img_path_map else f"images/placeholder_{i:05d}.jpg",
                'audio_path': f"audio/{Path(aud_path_map[cid]).name}" if cid in aud_path_map else f"audio/placeholder_{i:05d}.wav",
                'sentiment_label': sentiment_map[sentiment],
                'intent_label': intents.index(intent),
                'quality_score': 0.8,
                'data_split': 'train' if i < int(0.8 * len(aligned_ids)) else 'val',
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'source': 'embedding_catalogue',
                    'intent_name': intent,
                    'sentiment_name': sentiment
                }
            }
            # Copy real image/audio to output_dir if present
            if cid in img_path_map:
                shutil.copy2(img_path_map[cid], output_dir / sample['image_path'])
            if cid in aud_path_map:
                shutil.copy2(aud_path_map[cid], output_dir / sample['audio_path'])
            samples.append(sample)
        # Split into train/val
        train_size = int(0.8 * len(samples))
        train_samples = samples[:train_size]
        val_samples = samples[train_size:]
        if dry_run:
            print(f"[DRY RUN] Would write {len(train_samples)} train and {len(val_samples)} val samples to {output_dir}")
            return
        with open(output_dir / "train_manifest.json", 'w') as f:
            json.dump(train_samples, f, indent=2)
        with open(output_dir / "val_manifest.json", 'w') as f:
            json.dump(val_samples, f, indent=2)
        print("✅ Aligned real-data manifest generated from catalogue:")
        print(f"   📊 Train samples: {len(train_samples)}")
        print(f"   📊 Validation samples: {len(val_samples)}")
        print(f"   📂 Manifests saved to {output_dir}")
        # Ensure placeholder files exist
        self._ensure_placeholder_files(output_dir, train_samples + val_samples)

    def _ensure_placeholder_files(self, output_dir: Path, samples: list):
        """Create placeholder image/audio files if missing."""
        img_dir = output_dir / "images"
        aud_dir = output_dir / "audio"
        img_dir.mkdir(exist_ok=True)
        aud_dir.mkdir(exist_ok=True)
        for s in samples:
            img_path = output_dir / s['image_path']
            aud_path = output_dir / s['audio_path']
            if not img_path.exists():
                with open(img_path, 'wb') as f:
                    f.write(b'\xFF\xD8\xFF\xD9')  # minimal JPEG
            if not aud_path.exists():
                with open(aud_path, 'wb') as f:
                    f.write(b'RIFF\x00\x00\x00\x00WAVE')  # minimal WAV
    """Utility to prepare raw conversation data"""

    def __init__(self, output_dir: str = "data/raw_multimodal"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.output_dir / "images").mkdir(exist_ok=True)
        (self.output_dir / "audio").mkdir(exist_ok=True)
        (self.output_dir / "text").mkdir(exist_ok=True)

        print(f"📁 Data preparation directory: {self.output_dir}")

    def create_sample_dataset(self, num_samples: int = 1000):
        """Create a sample dataset for testing the pipeline"""
        print(f"🔧 Creating sample dataset with {num_samples} samples...")

        # Sample conversation templates
        conversation_templates = [
            "Hello, how are you today?",
            "I'm feeling great, thanks for asking!",
            "Can you help me with this problem?",
            "The weather is beautiful today.",
            "I'm excited about this new project.",
            "This is frustrating, nothing works.",
            "Thank you so much for your help!",
            "I'm not sure what to do next.",
            "This looks amazing, I love it!",
            "I'm disappointed with the results."
        ]

        # Intent categories
        intents = [
            "greeting", "question", "request", "complaint",
            "compliment", "goodbye", "information", "booking",
            "support", "feedback"
        ]

        # Sentiment mapping
        sentiment_map = {"negative": 0, "neutral": 1, "positive": 2}

        samples = []

        for i in range(num_samples):
            # Select template and intent
            text = conversation_templates[i % len(conversation_templates)]
            intent = intents[i % len(intents)]

            # Assign sentiment based on text content
            if any(word in text.lower() for word in ["great", "beautiful", "excited", "amazing", "love", "thank"]):
                sentiment = "positive"
            elif any(word in text.lower() for word in ["frustrating", "disappointed", "problem"]):
                sentiment = "negative"
            else:
                sentiment = "neutral"

            sample = {
                'conversation_id': f"conv_{i:04d}",
                'text': f"{text} (Sample {i})",
                'image_path': f"images/sample_{i:04d}.jpg",
                'audio_path': f"audio/sample_{i:04d}.wav",
                'sentiment_label': sentiment_map[sentiment],
                'intent_label': intents.index(intent),
                'quality_score': 0.7 + (i % 3) * 0.1,  # 0.7, 0.8, or 0.9
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'source': 'generated_sample',
                    'speaker_id': f"speaker_{i % 5}",
                    'intent_name': intent,
                    'sentiment_name': sentiment
                }
            }
            samples.append(sample)

        # Split into train/val
        train_size = int(0.8 * len(samples))
        train_samples = samples[:train_size]
        val_samples = samples[train_size:]

        # Save manifests
        with open(self.output_dir / "train_manifest.json", 'w') as f:
            json.dump(train_samples, f, indent=2)

        with open(self.output_dir / "val_manifest.json", 'w') as f:
            json.dump(val_samples, f, indent=2)

        print("✅ Sample dataset created:")
        print(f"   📊 Train samples: {len(train_samples)}")
        print(f"   📊 Validation samples: {len(val_samples)}")
        print(f"   📂 Manifests saved to {self.output_dir}")

        # Create sample files info
        self._create_placeholder_files_info(samples)

    def _create_placeholder_files_info(self, samples: list[dict]):
        """Create info about placeholder media files"""

        info_text = """
# Placeholder Media Files

This dataset uses placeholder media files for testing the pipeline.

## Images (images/sample_XXXX.jpg)
- Replace with actual conversation-related images
- Format: JPEG, RGB, any resolution (will be resized to 224x224)
- Content: Screenshots, photos, diagrams related to conversations

## Audio (audio/sample_XXXX.wav)
- Replace with actual conversation audio
- Format: WAV, mono or stereo, any sample rate (will be resampled to 16kHz)
- Duration: Up to 10 seconds (will be padded/truncated)
- Content: Speech, ambient sounds, music related to conversations

## Real Data Integration
To use real data:
1. Place your images in the images/ directory
2. Place your audio files in the audio/ directory
3. Update the manifest JSON files with correct paths
4. Ensure sentiment_label (0-2) and intent_label (0-9) are accurate

## File Naming Convention
- Images: any name ending in .jpg, .jpeg, or .png
- Audio: any name ending in .wav, .mp3, or .flac
- Update the image_path and audio_path in manifests accordingly
"""

        with open(self.output_dir / "README.md", 'w') as f:
            f.write(info_text)

        print("📝 Created README.md with file format instructions")

    def organize_real_data(self,
                          csv_file: str | None = None,
                          image_dir: str | None = None,
                          audio_dir: str | None = None):
        """Organize real conversation data from CSV and media directories"""

        if not csv_file:
            print("⚠️ No CSV file provided. Use create_sample_dataset() for testing.")
            return

        print(f"📊 Organizing real data from {csv_file}...")

        # Read CSV data
        df = pd.read_csv(csv_file)
        required_columns = ['text', 'sentiment_label', 'intent_label']

        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            print(f"❌ Missing required columns: {missing_cols}")
            return

        samples = []

        for idx, row in df.iterrows():
            # Basic sample structure
            sample = {
                'conversation_id': f"real_{idx:04d}",
                'text': str(row['text']),
                'sentiment_label': int(row['sentiment_label']),
                'intent_label': int(row['intent_label']),
                'quality_score': float(row.get('quality_score', 0.8)),
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'source': 'real_data',
                    'csv_index': idx
                }
            }

            # Handle image files
            if image_dir and 'image_filename' in row and pd.notna(row['image_filename']):
                src_image = Path(image_dir) / row['image_filename']
                if src_image.exists():
                    dest_image = self.output_dir / "images" / f"real_{idx:04d}{src_image.suffix}"
                    shutil.copy2(src_image, dest_image)
                    sample['image_path'] = f"images/{dest_image.name}"
                else:
                    sample['image_path'] = f"images/placeholder_{idx:04d}.jpg"
            else:
                sample['image_path'] = f"images/placeholder_{idx:04d}.jpg"

            # Handle audio files
            if audio_dir and 'audio_filename' in row and pd.notna(row['audio_filename']):
                src_audio = Path(audio_dir) / row['audio_filename']
                if src_audio.exists():
                    dest_audio = self.output_dir / "audio" / f"real_{idx:04d}{src_audio.suffix}"
                    shutil.copy2(src_audio, dest_audio)
                    sample['audio_path'] = f"audio/{dest_audio.name}"
                else:
                    sample['audio_path'] = f"audio/placeholder_{idx:04d}.wav"
            else:
                sample['audio_path'] = f"audio/placeholder_{idx:04d}.wav"

            samples.append(sample)

        # Split and save
        train_size = int(0.8 * len(samples))
        train_samples = samples[:train_size]
        val_samples = samples[train_size:]

        with open(self.output_dir / "train_manifest.json", 'w') as f:
            json.dump(train_samples, f, indent=2)

        with open(self.output_dir / "val_manifest.json", 'w') as f:
            json.dump(val_samples, f, indent=2)

        print("✅ Real data organized:")
        print(f"   📊 Train samples: {len(train_samples)}")
        print(f"   📊 Validation samples: {len(val_samples)}")
        print(f"   📂 Media files copied to {self.output_dir}")

    def validate_dataset(self, check_files: bool = True):
        """Validate the prepared dataset"""
        print("🔍 Validating dataset...")

        issues = []

        # Check manifest files
        seen_ids = set()
        for split in ['train', 'val']:
            manifest_path = self.output_dir / f"{split}_manifest.json"
            if not manifest_path.exists():
                issues.append(f"Missing {split}_manifest.json")
                continue
            with open(manifest_path) as f:
                samples = json.load(f)
            print(f"📊 {split.title()} set: {len(samples)} samples")
            # Check sample structure
            for i, sample in enumerate(samples[:5]):  # Check first 5
                required_keys = [
                    'conversation_id', 'text', 'image_path', 'audio_path',
                    'sentiment_label', 'intent_label', 'quality_score'
                ]
                missing_keys = [key for key in required_keys if key not in sample]
                if missing_keys:
                    issues.append(f"{split} sample {i}: missing keys {missing_keys}")
                # Check file existence
                if check_files:
                    img_path = self.output_dir / sample.get('image_path', '')
                    aud_path = self.output_dir / sample.get('audio_path', '')
                    if not img_path.exists():
                        issues.append(f"{split} sample {i}: missing image file {img_path}")
                    if not aud_path.exists():
                        issues.append(f"{split} sample {i}: missing audio file {aud_path}")
                # Check for duplicate conversation_id
                cid = sample.get('conversation_id')
                if cid in seen_ids:
                    issues.append(f"Duplicate conversation_id: {cid}")
                seen_ids.add(cid)

        # Check label ranges
        all_samples = []
        for split in ['train', 'val']:
            manifest_path = self.output_dir / f"{split}_manifest.json"
            if manifest_path.exists():
                with open(manifest_path) as f:
                    all_samples.extend(json.load(f))

        if all_samples:
            sentiments = [s['sentiment_label'] for s in all_samples]
            intents = [s['intent_label'] for s in all_samples]

            print(f"📈 Sentiment distribution: {dict(pd.Series(sentiments).value_counts())}")
            print(f"📈 Intent distribution: {dict(pd.Series(intents).value_counts())}")

            if not all(0 <= s <= 2 for s in sentiments):
                issues.append("Sentiment labels outside range [0, 2]")

            if not all(0 <= i <= 9 for i in intents):
                issues.append("Intent labels outside range [0, 9]")

        # Report validation results
        if issues:
            print("❌ Validation issues found:")
            for issue in issues:
                print(f"   • {issue}")
        else:
            print("✅ Dataset validation passed!")
            print("🚀 Ready for raw data training!")

def main():

    parser = argparse.ArgumentParser(description="Prepare raw multimodal data")
    parser.add_argument('--output-dir', default='data/raw_multimodal', help='Output directory for prepared data')
    parser.add_argument('--create-sample', action='store_true', help='Create sample dataset for testing')
    parser.add_argument('--sample-size', type=int, default=1000, help='Number of samples to generate')
    parser.add_argument('--csv-file', type=str, help='CSV file with real conversation data')
    parser.add_argument('--image-dir', type=str, help='Directory containing image files')
    parser.add_argument('--audio-dir', type=str, help='Directory containing audio files')
    parser.add_argument('--validate', action='store_true', help='Validate prepared dataset')
    parser.add_argument('--generate-real-manifest', action='store_true', help='Generate real-data manifest from embedding catalogue')
    parser.add_argument('--catalogue-path', type=str, default='F:/b2_embeddings/b2_embedding_catalogue.json', help='Path to b2_embedding_catalogue.json (default: F:/b2_embeddings/b2_embedding_catalogue.json)')
    parser.add_argument('--real-sample-size', type=int, default=None, help='Number of real samples to use from catalogue (default: all)')
    parser.add_argument('--real-image-dir', type=str, default='F:/b2_datasets/images', help='Directory containing real images (default: F:/b2_datasets/images)')
    parser.add_argument('--real-audio-dir', type=str, default='F:/b2_datasets/audio', help='Directory containing real audio (default: F:/b2_datasets/audio)')
    parser.add_argument('--force', action='store_true', help='Force overwrite of output directory/files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without writing files')
    parser.add_argument('--no-file-check', action='store_true', help='Skip file existence checks during validation')
    args = parser.parse_args()

    preparer = RawDataPreparer(args.output_dir)

    if args.create_sample:
        preparer.create_sample_dataset(args.sample_size)
    elif args.csv_file:
        preparer.organize_real_data(args.csv_file, args.image_dir, args.audio_dir)
    elif args.generate_real_manifest:
        if not args.catalogue_path:
            print("❌ --catalogue-path is required for --generate-real-manifest")
        else:
            preparer.generate_real_manifest_from_catalogue(
                args.catalogue_path,
                output_dir=args.output_dir,
                num_samples=args.real_sample_size,
                dry_run=args.dry_run,
                force=args.force,
                real_image_dir=args.real_image_dir,
                real_audio_dir=args.real_audio_dir
            )

    if args.validate:
        preparer.validate_dataset(check_files=not args.no_file_check)

    if not (args.create_sample or args.csv_file or args.validate or args.generate_real_manifest):
        print("🔧 Raw Data Preparer - Choose an action:")
        print("  --create-sample: Generate test dataset")
        print("  --csv-file <file>: Organize real data from CSV")
        print("  --generate-real-manifest: Generate manifest from embedding catalogue")
        print("  --validate: Check dataset integrity")
        print("  --force: Overwrite output directory/files")
        print("  --dry-run: Show actions without writing files")
        print("  --no-file-check: Skip file existence checks during validation")

if __name__ == "__main__":
    main()
