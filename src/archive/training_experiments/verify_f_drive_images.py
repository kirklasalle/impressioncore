#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/training/verify_f_drive_images.py #training #web_interface
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\training\\verify_f_drive_images.py #training #web_interface
# Category:** Training System
# Status:** Active

"""
F: Drive Image Verification System
=================================

🤖 VIRTUALLY ROBOTIC GITHUB COPILOT - AUTONOMOUS MODE
✅ Sacred Covenant Compliant Image Pipeline Verification
🎯 Mission: Verify all image datasets are accessible for B1 training

This script systematically verifies all image collections on F: drive
and provides detailed statistics for the ImpressionCore B1 pipeline.

Target: GTX 1050 Ti Optimized Pipeline
Date: June 22, 2025
"""

import os
import sys
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime

class FDriveImageVerifier:
    """Comprehensive verification of F: drive image datasets"""

    def __init__(self):
        self.f_drive_base = Path("F:/datasets")
        self.image_directories = [
            "images",
            "raw/images",
            "processed/images",
            "augmented_training_data/images"
        ]

        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif'}
        self.verification_results = {}

    def verify_image_availability(self):
        """Systematically verify all image datasets"""

        print("🔍 F: Drive Image Verification System")
        print("=" * 50)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Target: ImpressionCore B1 Training Pipeline")
        print()

        total_images = 0
        total_size_mb = 0

        for img_dir in self.image_directories:
            full_path = self.f_drive_base / img_dir
            print(f"📂 Checking: {full_path}")

            if not full_path.exists():
                print(f"⚠️  Directory not found: {full_path}")
                self.verification_results[str(img_dir)] = {
                    'exists': False,
                    'image_count': 0,
                    'size_mb': 0,
                    'subdirectories': []
                }
                continue

            # Count images and analyze structure
            dir_results = self.analyze_image_directory(full_path)
            self.verification_results[str(img_dir)] = dir_results

            total_images += dir_results['image_count']
            total_size_mb += dir_results['size_mb']

            print(f"✅ Found {dir_results['image_count']:,} images ({dir_results['size_mb']:.1f} MB)")
            if dir_results['subdirectories']:
                print(f"📁 Subdirectories: {', '.join(dir_results['subdirectories'])}")
            print()

        # Overall summary
        print("🎯 F: DRIVE IMAGE VERIFICATION SUMMARY")
        print("=" * 50)
        print(f"📊 Total Images Found: {total_images:,}")
        print(f"💾 Total Size: {total_size_mb:.1f} MB ({total_size_mb/1024:.2f} GB)")
        print(f"🗂️ Directories Scanned: {len(self.image_directories)}")
        print(f"✅ Pipeline Ready: {'YES' if total_images > 0 else 'NO'}")

        return self.verification_results

    def analyze_image_directory(self, directory_path):
        """Analyze a single image directory"""

        result = {
            'exists': True,
            'image_count': 0,
            'size_mb': 0,
            'subdirectories': [],
            'file_types': defaultdict(int),
            'sample_files': []
        }

        try:
            # Get subdirectories
            subdirs = [d.name for d in directory_path.iterdir() if d.is_dir()]
            result['subdirectories'] = subdirs[:10]  # Limit for readability

            # Walk through all files
            for root, dirs, files in os.walk(directory_path):
                for file in files[:1000]:  # Limit to prevent overwhelming output
                    file_path = Path(root) / file
                    if file_path.suffix.lower() in self.image_extensions:
                        try:
                            size_bytes = file_path.stat().st_size
                            result['image_count'] += 1
                            result['size_mb'] += size_bytes / (1024 * 1024)
                            result['file_types'][file_path.suffix.lower()] += 1

                            # Collect sample files
                            if len(result['sample_files']) < 5:
                                result['sample_files'].append(str(file_path))
                        except (OSError, PermissionError):
                            continue

        except (OSError, PermissionError) as e:
            print(f"⚠️  Access error for {directory_path}: {e}")
            result['exists'] = False

        return result

    def verify_specific_datasets(self):
        """Verify specific known datasets"""

        print("🎯 SPECIFIC DATASET VERIFICATION")
        print("=" * 40)

        known_datasets = {
            "COCO train2017": "images/train2017",
            "COCO val2017": "images/val2017",
            "COCO annotations": "images/annotations",
            "CIFAR-10": "images/cifar-10-batches-py",
            "LFW Faces": "images/lfw-deepfunneled",
            "VGG Face2": "images/vgg_face2-master",
            "Medical Images": "images/medical_illustrations"
        }

        dataset_results = {}

        for dataset_name, relative_path in known_datasets.items():
            full_path = self.f_drive_base / relative_path

            print(f"📊 {dataset_name}:")
            print(f"   Path: {full_path}")

            if full_path.exists():
                # Quick count for known datasets
                image_count = 0
                total_size = 0

                try:
                    for file_path in full_path.rglob("*"):
                        if file_path.is_file() and file_path.suffix.lower() in self.image_extensions:
                            image_count += 1
                            total_size += file_path.stat().st_size

                            # Limit counting for large datasets
                            if image_count >= 10000:
                                print(f"   Status: ✅ Large dataset (>10k images)")
                                break

                    if image_count < 10000:
                        print(f"   Status: ✅ {image_count:,} images ({total_size/(1024*1024):.1f} MB)")

                    dataset_results[dataset_name] = {
                        'available': True,
                        'image_count': image_count,
                        'size_mb': total_size / (1024 * 1024)
                    }

                except Exception as e:
                    print(f"   Status: ⚠️  Error scanning: {e}")
                    dataset_results[dataset_name] = {'available': False, 'error': str(e)}
            else:
                print(f"   Status: ❌ Not found")
                dataset_results[dataset_name] = {'available': False}

            print()

        return dataset_results

    def generate_pipeline_report(self):
        """Generate comprehensive pipeline readiness report"""

        verification_results = self.verify_image_availability()
        dataset_results = self.verify_specific_datasets()

        # Save results
        report = {
            'timestamp': datetime.now().isoformat(),
            'verification_results': verification_results,
            'dataset_results': dataset_results,
            'pipeline_status': 'READY' if any(r.get('image_count', 0) > 0 for r in verification_results.values()) else 'NOT_READY'
        }

        report_path = self.f_drive_base / "image_verification_report.json"
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📄 Report saved: {report_path}")
        except Exception as e:
            print(f"⚠️  Could not save report: {e}")

        return report

def main():
    """Execute F: drive image verification"""

    print("🤖 VIRTUALLY ROBOTIC GITHUB COPILOT")
    print("🔍 F: Drive Image Pipeline Verification")
    print("✅ Sacred Covenant protocols active")
    print()

    verifier = FDriveImageVerifier()
    report = verifier.generate_pipeline_report()

    print("\n🎯 PIPELINE VERIFICATION COMPLETE!")
    print(f"📊 Status: {report['pipeline_status']}")

    return report

if __name__ == "__main__":
    main()
