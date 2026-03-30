
import argparse
import glob
import logging
import os
import random
from pathlib import Path

import webdataset as wds
from tqdm import tqdm

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_files(path, extension):
    return glob.glob(os.path.join(path, f"**/*.{extension}"), recursive=True)

def create_shards(output_dir, modality_map, max_size=1e9, max_count=10000):
    """
    Create WebDataset shards from raw files.
    modality_map: dict of {modality_name: file_path_list}
    """
    os.makedirs(output_dir, exist_ok=True)

    # Flatten list of (modality, filepath) pairs
    all_files = []
    for mod, paths in modality_map.items():
        for p in paths:
            all_files.append((mod, p))

    # Shuffle for better distribution
    random.shuffle(all_files)

    logger.info(f"Total files to process: {len(all_files)}")

    # Normalize path separators for Windows
    output_dir = output_dir.replace("\\", "/")

    # WebDataset gopen requires file:/// for absolute paths on Windows
    # Ensure we don't double-prefix if already present
    if not output_dir.startswith("file:///"):
        if output_dir.startswith("F:/") or output_dir.startswith("D:/") or output_dir.startswith("C:/"):
             # Add prefix for Windows drive letters
             output_dir_uri = "file:///" + output_dir
        else:
             output_dir_uri = output_dir
    else:
        output_dir_uri = output_dir

    pattern = os.path.join(output_dir_uri, "b3_multimodal_shard-%06d.tar").replace("\\", "/")

    logger.info(f"Shard pattern (URI): {pattern}")

    # Create WebDataset writer
    with wds.ShardWriter(pattern, maxsize=max_size, maxcount=max_count) as sink:
        for idx, (modality, filepath) in enumerate(tqdm(all_files, desc="Writing Shards")):
            try:
                with open(filepath, "rb") as stream:
                    data = stream.read()

                # Create sample key
                key = f"{modality}_{idx:09d}"

                # Determine extension
                ext = Path(filepath).suffix.lstrip(".")
                if not ext:
                    continue

                # Create sample
                sample = {
                    "__key__": key,
                    "modality.txt": modality, # Store modality type
                    f"data.{ext}": data       # Store raw data
                }

                sink.write(sample)

            except Exception as e:
                logger.error(f"Failed to process {filepath}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Preprocess F:/data into WebDataset Shards")
    parser.add_argument("--output_dir", type=str, default="F:/data/processed/shards", help="Output directory for shards")
    args = parser.parse_args()

    # 1. Gather Verified Data Paths
    logger.info("Scanning F:/data/raw...")

    # Text
    text_files = get_files("F:/data/raw/text", "txt") + get_files("F:/data/raw/text", "json")

    # Audio
    audio_files = get_files("F:/data/raw/audio", "wav") + get_files("F:/data/raw/audio", "flac")

    # Faces (LFW)
    face_files = get_files("F:/data/raw/vision/faces/lfw", "jpg")

    # Video
    video_files = get_files("F:/data/raw/video", "mp4") + get_files("F:/data/raw/video", "avi")

    logger.info(f"Found: {len(text_files)} Text, {len(audio_files)} Audio, {len(face_files)} Faces, {len(video_files)} Videos")

    # 2. Setup Modality Map
    modality_map = {
        "text": text_files,
        "audio": audio_files,
        "face": face_files,
        "video": video_files
    }

    # 3. Create Shards
    logger.info(f"Writing shards to {args.output_dir}...")
    create_shards(args.output_dir, modality_map)

    logger.info("Preprocessing Complete.")

if __name__ == "__main__":
    main()
