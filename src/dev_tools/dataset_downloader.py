#!/usr/bin/env python3
"""
ImpressionCore-B1 Dataset Downloader
Downloads all critical training datasets with progress tracking and verification.
"""

import os
import sys
import requests
import hashlib
import tarfile
import zipfile
import shutil
from pathlib import Path
from typing import Optional, Tuple
import time

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

try:
    from src.core.utils.rich_enhancements import console, progress_bar, status_spinner
    from src.core.utils.rich_logging import RichLogger
except ImportError:
    # Fallback to basic logging if rich not available
    import logging
    console = None
    progress_bar = None
    status_spinner = None
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

class DatasetDownloader:
    """Robust dataset downloader with progress tracking and verification."""
    
    def __init__(self, base_path: str = "src/data/datasets"):
        self.base_path = Path(base_path)
        self.downloads = []
        
        # Initialize rich logger if available
        if console:
            self.logger = RichLogger("DatasetDownloader")
        else:
            self.logger = logger
    
    def download_file(self, url: str, filepath: Path, expected_size: Optional[int] = None, 
                     expected_md5: Optional[str] = None) -> bool:
        """Download a file with progress tracking and verification."""
        
        # Create directory if it doesn't exist
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Skip if file already exists and is valid
        if filepath.exists():
            if expected_size and filepath.stat().st_size == expected_size:
                self.logger.info(f"File already exists and size matches: {filepath}")
                return True
            elif expected_md5 and self.verify_md5(filepath, expected_md5):
                self.logger.info(f"File already exists and MD5 matches: {filepath}")
                return True
        
        self.logger.info(f"Downloading {url} -> {filepath}")
        
        try:
            # Start download with streaming
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get file size from headers
            total_size = int(response.headers.get('content-length', 0))
            
            if console and progress_bar:
                # Use rich progress bar
                with progress_bar() as progress:
                    task = progress.add_task(f"Downloading {filepath.name}", total=total_size)
                    
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                progress.update(task, advance=len(chunk))
            else:
                # Fallback progress
                downloaded = 0
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                print(f"\rProgress: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='')
                
                print()  # New line after progress
            
            # Verify download
            if expected_size and filepath.stat().st_size != expected_size:
                self.logger.error(f"Size mismatch: expected {expected_size}, got {filepath.stat().st_size}")
                return False
            
            if expected_md5 and not self.verify_md5(filepath, expected_md5):
                self.logger.error(f"MD5 mismatch for {filepath}")
                return False
            
            self.logger.info(f"Successfully downloaded: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Download failed for {url}: {e}")
            if filepath.exists():
                filepath.unlink()  # Remove partial file
            return False
    
    def verify_md5(self, filepath: Path, expected_md5: str) -> bool:
        """Verify MD5 hash of a file."""
        if not filepath.exists():
            return False
        
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        
        return hasher.hexdigest() == expected_md5
    
    def download_critical_datasets(self):
        """Download the critical datasets in priority order."""
        
        datasets = [
            # Priority 1: LJSpeech (smallest audio dataset)
            {
                "name": "LJSpeech",
                "url": "https://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2",
                "path": self.base_path / "audio" / "ljspeech" / "LJSpeech-1.1.tar.bz2",
                "size": None,  # ~2.6GB
                "md5": None
            },
            
            # Priority 2: LibriSpeech Alignments (critical for phonemes)
            {
                "name": "LibriSpeech Alignments",
                "url": "https://zenodo.org/record/2619474/files/librispeech_alignments.zip",
                "path": self.base_path / "audio" / "alignments" / "librispeech_alignments.zip",
                "size": 623 * 1024 * 1024,  # 623MB
                "md5": "2bab567d0ace651a4ba254e813629f46"
            },
            
            # Priority 3: COCO Validation Images (smaller image set)
            {
                "name": "COCO Val 2017",
                "url": "http://images.cocodataset.org/zips/val2017.zip",
                "path": self.base_path / "images" / "coco2017" / "val2017.zip",
                "size": None,  # ~1GB
                "md5": None
            },
            
            # Priority 4: COCO Annotations
            {
                "name": "COCO Annotations",
                "url": "http://images.cocodataset.org/annotations/annotations_trainval2017.zip",
                "path": self.base_path / "images" / "coco2017" / "annotations_trainval2017.zip",
                "size": None,  # ~241MB
                "md5": None
            },
        ]
        
        success_count = 0
        
        for i, dataset in enumerate(datasets, 1):
            self.logger.info(f"[{i}/{len(datasets)}] Starting download: {dataset['name']}")
            
            success = self.download_file(
                url=dataset["url"],
                filepath=dataset["path"],
                expected_size=dataset.get("size"),
                expected_md5=dataset.get("md5")
            )
            
            if success:
                success_count += 1
                self.downloads.append(dataset["path"])
            else:
                self.logger.error(f"Failed to download: {dataset['name']}")
        
        self.logger.info(f"Download summary: {success_count}/{len(datasets)} successful")
        return success_count == len(datasets)
    
    def extract_datasets(self):
        """Extract downloaded archives."""
        import tarfile
        import zipfile
        
        extraction_map = {
            ".tar.bz2": self.extract_tar_bz2,
            ".zip": self.extract_zip,
            ".tar.gz": self.extract_tar_gz,
        }
        
        for filepath in self.downloads:
            if not filepath.exists():
                continue
            
            # Determine extraction method
            for ext, extract_func in extraction_map.items():
                if str(filepath).endswith(ext):
                    self.logger.info(f"Extracting: {filepath}")
                    try:
                        extract_func(filepath)
                        self.logger.info(f"Successfully extracted: {filepath}")
                    except Exception as e:
                        self.logger.error(f"Extraction failed for {filepath}: {e}")
                    break
    
    def extract_tar_bz2(self, filepath: Path):
        """Extract tar.bz2 files."""
        with tarfile.open(filepath, 'r:bz2') as tar:
            tar.extractall(filepath.parent)
    
    def extract_zip(self, filepath: Path):
        """Extract zip files."""
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(filepath.parent)
    
    def extract_tar_gz(self, filepath: Path):
        """Extract tar.gz files."""
        with tarfile.open(filepath, 'r:gz') as tar:
            tar.extractall(filepath.parent)

def main():
    """Main download function."""
    print("🚀 ImpressionCore-B1 Dataset Downloader")
    print("=" * 50)
    
    # Change to project root
    os.chdir(Path(__file__).parent.parent.parent.parent)
    
    downloader = DatasetDownloader()
    
    print("📥 Starting critical dataset downloads...")
    success = downloader.download_critical_datasets()
    
    if success:
        print("\n✅ All downloads completed successfully!")
        
        print("\n📦 Extracting archives...")
        downloader.extract_datasets()
        
        print("\n🎯 Ready for training! Run the following to validate:")
        print("python src/interfaces/cli/impressioncore_b1_cuda_cli.py --test-datasets")
        
    else:
        print("\n❌ Some downloads failed. Check the logs above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
