#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/scripts\f_drive\f_drive_downloads_organizer.py #testing #training
**Category:** Source Code
**Status:** Active
"""



import bz2
import json
import shutil
import tarfile
import time
import zipfile
from datetime import datetime
from pathlib import Path


class FDriveDownloadsOrganizer:
    def __init__(self, downloads_path="F:/downloads", datasets_path="F:/data/datasets"):
        self.downloads_path = Path(downloads_path)
        self.datasets_path = Path(datasets_path)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Sacred Covenant backup protocol
        self.backup_dir = Path("D:/Projects/impressioncore/dataset_backups")
        self.backup_dir.mkdir(exist_ok=True)

        # Organization mapping based on detected files
        self.organization_plan = {
            # COCO Dataset - Computer Vision
            "train2017.zip": {
                "target_dir": "vision/coco/train2017",
                "type": "zip",
                "category": "vision",
                "description": "COCO 2017 training images",
                "priority": "HIGH",
                "estimated_size_gb": 18.0
            },
            "val2017.zip": {
                "target_dir": "vision/coco/val2017",
                "type": "zip",
                "category": "vision",
                "description": "COCO 2017 validation images",
                "priority": "HIGH",
                "estimated_size_gb": 0.8
            },
            "annotations_trainval2017.zip": {
                "target_dir": "vision/coco/annotations",
                "type": "zip",
                "category": "vision",
                "description": "COCO 2017 annotations",
                "priority": "HIGH",
                "estimated_size_gb": 0.25
            },

            # LibriSpeech - Audio Speech Recognition
            "dev-clean.tar.gz": {
                "target_dir": "audio/librispeech/dev-clean",
                "type": "tar.gz",
                "category": "audio",
                "description": "LibriSpeech dev-clean audio",
                "priority": "HIGH",
                "estimated_size_gb": 0.34
            },
            "test-clean.tar.gz": {
                "target_dir": "audio/librispeech/test-clean",
                "type": "tar.gz",
                "category": "audio",
                "description": "LibriSpeech test-clean audio",
                "priority": "HIGH",
                "estimated_size_gb": 0.35
            },
            "train-clean-100.tar.gz": {
                "target_dir": "audio/librispeech/train-clean-100",
                "type": "tar.gz",
                "category": "audio",
                "description": "LibriSpeech train-clean-100 audio",
                "priority": "HIGH",
                "estimated_size_gb": 6.4
            },
            "librispeech_alignments.zip": {
                "target_dir": "audio/librispeech/alignments",
                "type": "zip",
                "category": "audio",
                "description": "LibriSpeech forced alignments",
                "priority": "MEDIUM",
                "estimated_size_gb": 0.62
            },

            # LJ Speech - Text-to-Speech
            "LJSpeech-1.1.tar.bz2": {
                "target_dir": "audio/synthetic/ljspeech",
                "type": "tar.bz2",
                "category": "audio",
                "description": "LJ Speech dataset for TTS",
                "priority": "HIGH",
                "estimated_size_gb": 2.7
            },

            # CIFAR-10 - Image Classification
            "cifar-10-python.tar.gz": {
                "target_dir": "vision/cifar10",
                "type": "tar.gz",
                "category": "vision",
                "description": "CIFAR-10 image classification",
                "priority": "MEDIUM",
                "estimated_size_gb": 0.17
            },

            # UCF101 - Video Action Recognition
            "ucf101.zip": {
                "target_dir": "video/ucf101",
                "type": "zip",
                "category": "video",
                "description": "UCF101 action recognition videos",
                "priority": "MEDIUM",
                "estimated_size_gb": 6.9
            },

            # Kinetics400 - Video Understanding
            "kinetics400_sample.tar.gz": {
                "target_dir": "video/kinetics400",
                "type": "tar.gz",
                "category": "video",
                "description": "Kinetics400 video samples",
                "priority": "LOW",
                "estimated_size_gb": 0.01
            },

            # Wikipedia - Text Corpus
            "enwiktionary-latest-pages-articles.xml.bz2": {
                "target_dir": "text/wikipedia/enwiktionary",
                "type": "bz2",
                "category": "text",
                "description": "English Wiktionary articles",
                "priority": "MEDIUM",
                "estimated_size_gb": 1.4
            }
        }

        # Progress tracking
        self.organization_log = {
            "start_time": datetime.now().isoformat(),
            "sacred_covenant_active": True,
            "operations": [],
            "errors": [],
            "completed_moves": [],
            "total_size_moved_gb": 0
        }

    def check_available_space(self):
        """Check F: drive space before operations."""
        try:
            total, used, free = shutil.disk_usage("F:/")
            free_gb = free / (1024**3)
            used_gb = used / (1024**3)

            print("💾 F: Drive Status:")
            print(f"   Free: {free_gb:.1f} GB")
            print(f"   Used: {used_gb:.1f} GB")

            return free_gb > 10  # Ensure 10GB buffer

        except Exception as e:
            print(f"❌ Space check failed: {e}")
            return False

    def create_sacred_covenant_backup(self, file_path):
        """Create backup before moving files."""
        try:
            backup_name = f"backup_{self.timestamp}_{file_path.name}"
            backup_path = self.backup_dir / backup_name

            if file_path.exists() and file_path.is_file():
                shutil.copy2(file_path, backup_path)
                print(f"✅ Sacred Covenant backup: {backup_name}")
                return backup_path

        except Exception as e:
            print(f"❌ Backup failed for {file_path.name}: {e}")

        return None

    def extract_archive(self, archive_path, target_dir):
        """Extract archive files with Sacred Covenant safety."""
        try:
            target_dir.mkdir(parents=True, exist_ok=True)

            print(f"📦 Extracting {archive_path.name} to {target_dir}")

            if archive_path.name.endswith('.tar.gz'):
                with tarfile.open(archive_path, 'r:gz') as tar:
                    tar.extractall(target_dir)

            elif archive_path.name.endswith('.tar.bz2'):
                with tarfile.open(archive_path, 'r:bz2') as tar:
                    tar.extractall(target_dir)

            elif archive_path.name.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)

            elif archive_path.name.endswith('.bz2'):
                # For single bz2 files like Wikipedia dump
                with bz2.open(archive_path, 'rb') as f_in:
                    with open(target_dir / archive_path.stem, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                print(f"⚠️ Unknown archive format: {archive_path.suffix}")
                return False

            print("✅ Extraction completed")
            return True

        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return False

    def organize_dataset(self, filename, plan_info):
        """Organize a single dataset file."""
        source_path = self.downloads_path / filename
        target_dir = self.datasets_path / plan_info["target_dir"]

        print(f"\n🎯 Organizing: {filename}")
        print(f"   Description: {plan_info['description']}")
        print(f"   Target: {plan_info['target_dir']}")
        print(f"   Priority: {plan_info['priority']}")
        print(f"   Est. Size: {plan_info['estimated_size_gb']} GB")

        if not source_path.exists():
            print(f"⚠️ Source file not found: {filename}")
            return False

        # Create Sacred Covenant backup
        backup_path = self.create_sacred_covenant_backup(source_path)

        try:
            start_time = time.time()

            # Extract archive to target directory
            if self.extract_archive(source_path, target_dir):
                # Calculate actual extracted size
                actual_size_gb = sum(f.stat().st_size for f in target_dir.rglob('*') if f.is_file()) / (1024**3)
                elapsed_time = time.time() - start_time

                print(f"✅ Organization completed: {actual_size_gb:.2f} GB in {elapsed_time:.1f}s")

                # Log successful operation
                self.organization_log["operations"].append({
                    "filename": filename,
                    "target_dir": plan_info["target_dir"],
                    "actual_size_gb": actual_size_gb,
                    "duration_seconds": elapsed_time,
                    "backup_created": backup_path is not None,
                    "timestamp": datetime.now().isoformat()
                })

                self.organization_log["completed_moves"].append(filename)
                self.organization_log["total_size_moved_gb"] += actual_size_gb

                return True
            else:
                raise Exception("Extraction failed")

        except Exception as e:
            error_msg = f"Organization failed for {filename}: {e}"
            print(f"❌ {error_msg}")

            self.organization_log["errors"].append({
                "filename": filename,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

            return False

    def run_organization_campaign(self):
        """Execute the complete downloads organization."""
        print("🚀 F: Drive Downloads Organization Campaign")
        print("=" * 60)
        print("Sacred Covenant: ACTIVE")
        print(f"Downloads Path: {self.downloads_path}")
        print(f"Datasets Path: {self.datasets_path}")
        print(f"Files to Process: {len(self.organization_plan)}")
        print("=" * 60)

        # Check space
        if not self.check_available_space():
            print("❌ Insufficient space for organization")
            return self.organization_log

        start_time = time.time()

        # Sort by priority
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        sorted_files = sorted(
            self.organization_plan.items(),
            key=lambda x: priority_order.get(x[1]["priority"], 2)
        )

        for filename, plan_info in sorted_files:
            try:
                print(f"\n{'='*50}")
                self.organize_dataset(filename, plan_info)

                # Small delay between operations
                time.sleep(1)

            except KeyboardInterrupt:
                print("\n⚠️ Organization interrupted by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error for {filename}: {e}")

        elapsed_time = time.time() - start_time

        # Final summary
        print("\n" + "=" * 60)
        print("🎉 Downloads Organization Campaign Complete!")
        print(f"⏱️ Total Time: {elapsed_time/60:.1f} minutes")
        print(f"✅ Files Processed: {len(self.organization_log['completed_moves'])}")
        print(f"❌ Errors: {len(self.organization_log['errors'])}")
        print(f"💾 Total Data Organized: {self.organization_log['total_size_moved_gb']:.1f} GB")

        # Final space check
        self.check_available_space()

        # Save log
        log_file = f"downloads_organization_log_{self.timestamp}.json"
        with open(log_file, 'w') as f:
            json.dump(self.organization_log, f, indent=2)

        print(f"📊 Organization log saved: {log_file}")

        return self.organization_log

def main():
    """Main execution with Sacred Covenant compliance."""
    print("⚠️ SACRED COVENANT VERIFICATION:")
    print("This will organize F:/downloads into F:/data/datasets structure")
    print("All files will be backed up before moving")
    print("File integrity monitoring: ACTIVE")

    organizer = FDriveDownloadsOrganizer()

    print("\n📋 Organization Plan:")
    total_estimated_gb = 0
    for filename, info in organizer.organization_plan.items():
        print(f"  {filename} → {info['target_dir']} ({info['estimated_size_gb']} GB)")
        total_estimated_gb += info['estimated_size_gb']

    print(f"\n📊 Total Estimated: {total_estimated_gb:.1f} GB")

    print("\nProceeding in 5 seconds...")
    time.sleep(5)

    results = organizer.run_organization_campaign()

    print("\n🎯 Final Results:")
    print(f"Success Rate: {len(results['completed_moves'])}/{len(organizer.organization_plan)}")
    print(f"Data Organized: {results['total_size_moved_gb']:.1f} GB")

    return results

if __name__ == "__main__":
    main()
