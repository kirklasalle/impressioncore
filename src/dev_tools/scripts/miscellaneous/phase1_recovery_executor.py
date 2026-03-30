#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #pytorch #source_code #src/scripts/miscellaneous/phase1_recovery_executor.py #testing
**Category:** Source Code
**Status:** Active
"""



import json
import os
from datetime import datetime
from pathlib import Path

import requests


class Phase1RecoveryExecutor:
    """Execute immediate recovery for high-priority datasets"""

    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_path = Path("F:/data/datasets")
        self.results = {
            "mozilla_common_voice": {"status": "pending", "methods_tried": [], "success": False},
            "podcast_transcripts": {"status": "pending", "methods_tried": [], "success": False},
            "movie_subtitles": {"status": "pending", "methods_tried": [], "success": False},
            "wikitext_103": {"status": "pending", "methods_tried": [], "success": False}
        }

    def test_huggingface_access(self):
        """Test if HuggingFace datasets library is available and working"""
        try:
            import datasets
            print("✅ HuggingFace datasets library available")
            return True
        except ImportError:
            print("❌ HuggingFace datasets not installed")
            print("📦 Installing HuggingFace datasets...")
            os.system("pip install datasets")
            try:
                import datasets  # noqa: F401
                print("✅ HuggingFace datasets installed successfully")
                return True
            except ImportError:
                print("❌ Failed to install HuggingFace datasets")
                return False

    def recover_mozilla_common_voice(self):
        """Recover Mozilla Common Voice dataset using multiple methods"""
        print("\\n🎯 RECOVERING: Mozilla Common Voice Phonemes")
        print("=" * 60)

        dataset_name = "mozilla_common_voice"
        self.results[dataset_name]["methods_tried"] = []

        # Method 1: HuggingFace Datasets with streaming
        try:
            print("📥 Method 1: HuggingFace Datasets (Common Voice 17.0)")
            if self.test_huggingface_access():
                from datasets import load_dataset

                # Create target directory
                target_dir = self.base_path / "phonemes" / "mozilla_common_voice_17"
                target_dir.mkdir(parents=True, exist_ok=True)

                print("📂 Loading Common Voice 17.0 dataset...")
                dataset = load_dataset(
                    'mozilla-foundation/common_voice_17_0',
                    'en',
                    cache_dir=str(target_dir),
                    streaming=False  # Download full dataset
                )

                print("💾 Saving dataset...")
                dataset.save_to_disk(str(target_dir / "hf_format"))

                # Get dataset info
                train_size = len(dataset['train']) if 'train' in dataset else 0
                test_size = len(dataset['test']) if 'test' in dataset else 0
                validation_size = len(dataset['validation']) if 'validation' in dataset else 0

                print("✅ SUCCESS: Mozilla Common Voice 17.0 downloaded!")
                print(f"   📊 Train samples: {train_size:,}")
                print(f"   📊 Test samples: {test_size:,}")
                print(f"   📊 Validation samples: {validation_size:,}")
                print(f"   📁 Location: {target_dir}")

                self.results[dataset_name]["status"] = "success"
                self.results[dataset_name]["success"] = True
                self.results[dataset_name]["method_used"] = "HuggingFace Common Voice 17.0"
                self.results[dataset_name]["location"] = str(target_dir)
                self.results[dataset_name]["samples"] = train_size + test_size + validation_size
                return True

        except Exception as e:
            print(f"❌ Method 1 failed: {e}")
            self.results[dataset_name]["methods_tried"].append(f"HuggingFace CV17: {e!s}")

        # Method 2: Try Common Voice 16.0 (fallback)
        try:
            print("📥 Method 2: HuggingFace Datasets (Common Voice 16.0 - Fallback)")
            from datasets import load_dataset

            target_dir = self.base_path / "phonemes" / "mozilla_common_voice_16"
            target_dir.mkdir(parents=True, exist_ok=True)

            dataset = load_dataset(
                'mozilla-foundation/common_voice_16_0',
                'en',
                cache_dir=str(target_dir),
                streaming=False
            )

            dataset.save_to_disk(str(target_dir / "hf_format"))

            train_size = len(dataset['train']) if 'train' in dataset else 0
            print("✅ SUCCESS: Mozilla Common Voice 16.0 downloaded!")
            print(f"   📊 Train samples: {train_size:,}")
            print(f"   📁 Location: {target_dir}")

            self.results[dataset_name]["status"] = "success"
            self.results[dataset_name]["success"] = True
            self.results[dataset_name]["method_used"] = "HuggingFace Common Voice 16.0"
            self.results[dataset_name]["location"] = str(target_dir)
            self.results[dataset_name]["samples"] = train_size
            return True

        except Exception as e:
            print(f"❌ Method 2 failed: {e}")
            self.results[dataset_name]["methods_tried"].append(f"HuggingFace CV16: {e!s}")

        # Method 3: Alternative Common Voice versions
        for version in ['13_0', '11_0', '8_0']:
            try:
                print(f"📥 Method 3: Common Voice {version} (Alternative)")
                from datasets import load_dataset

                target_dir = self.base_path / "phonemes" / f"mozilla_common_voice_{version}"
                target_dir.mkdir(parents=True, exist_ok=True)

                dataset = load_dataset(
                    f'mozilla-foundation/common_voice_{version}',
                    'en',
                    cache_dir=str(target_dir),
                    streaming=False
                )

                dataset.save_to_disk(str(target_dir / "hf_format"))

                train_size = len(dataset['train']) if 'train' in dataset else 0
                print(f"✅ SUCCESS: Mozilla Common Voice {version} downloaded!")
                print(f"   📊 Train samples: {train_size:,}")

                self.results[dataset_name]["status"] = "success"
                self.results[dataset_name]["success"] = True
                self.results[dataset_name]["method_used"] = f"HuggingFace Common Voice {version}"
                self.results[dataset_name]["location"] = str(target_dir)
                self.results[dataset_name]["samples"] = train_size
                return True

            except Exception as e:
                print(f"❌ Common Voice {version} failed: {e}")
                self.results[dataset_name]["methods_tried"].append(f"CV {version}: {e!s}")
                continue

        self.results[dataset_name]["status"] = "failed"
        return False

    def recover_wikitext_103(self):
        """Recover WikiText-103 using PyTorch and HuggingFace"""
        print("\\n🎯 RECOVERING: WikiText-103")
        print("=" * 60)

        dataset_name = "wikitext_103"

        # Method 1: HuggingFace Datasets
        try:
            print("📥 Method 1: HuggingFace Datasets (WikiText)")
            if self.test_huggingface_access():
                from datasets import load_dataset

                target_dir = self.base_path / "text" / "wikitext_103_hf"
                target_dir.mkdir(parents=True, exist_ok=True)

                dataset = load_dataset(
                    'wikitext',
                    'wikitext-103-v1',
                    cache_dir=str(target_dir)
                )

                dataset.save_to_disk(str(target_dir / "hf_format"))

                train_size = len(dataset['train']) if 'train' in dataset else 0
                print("✅ SUCCESS: WikiText-103 downloaded via HuggingFace!")
                print(f"   📊 Train samples: {train_size:,}")
                print(f"   📁 Location: {target_dir}")

                self.results[dataset_name]["status"] = "success"
                self.results[dataset_name]["success"] = True
                self.results[dataset_name]["method_used"] = "HuggingFace WikiText"
                self.results[dataset_name]["location"] = str(target_dir)
                self.results[dataset_name]["samples"] = train_size
                return True

        except Exception as e:
            print(f"❌ HuggingFace WikiText failed: {e}")
            self.results[dataset_name]["methods_tried"].append(f"HuggingFace: {e!s}")

        # Method 2: Try alternative text datasets
        try:
            print("📥 Method 2: Alternative - WikiText-2 (smaller version)")
            from datasets import load_dataset

            target_dir = self.base_path / "text" / "wikitext_2_hf"
            target_dir.mkdir(parents=True, exist_ok=True)

            dataset = load_dataset('wikitext', 'wikitext-2-v1', cache_dir=str(target_dir))
            dataset.save_to_disk(str(target_dir / "hf_format"))

            train_size = len(dataset['train']) if 'train' in dataset else 0
            print("✅ SUCCESS: WikiText-2 downloaded as alternative!")
            print(f"   📊 Train samples: {train_size:,}")

            self.results[dataset_name]["status"] = "success"
            self.results[dataset_name]["success"] = True
            self.results[dataset_name]["method_used"] = "HuggingFace WikiText-2"
            self.results[dataset_name]["location"] = str(target_dir)
            self.results[dataset_name]["samples"] = train_size
            return True

        except Exception as e:
            print(f"❌ WikiText-2 failed: {e}")
            self.results[dataset_name]["methods_tried"].append(f"WikiText-2: {e!s}")

        self.results[dataset_name]["status"] = "failed"
        return False

    def recover_movie_subtitles(self):
        """Recover movie subtitles using OpenSubtitles corpus"""
        print("\\n🎯 RECOVERING: Movie Subtitle Corpus")
        print("=" * 60)

        dataset_name = "movie_subtitles"

        # Method 1: Download from OPUS-OpenSubtitles
        try:
            print("📥 Method 1: OPUS OpenSubtitles Corpus")

            # Create target directory
            target_dir = self.base_path / "text" / "opensubtitles_corpus"
            target_dir.mkdir(parents=True, exist_ok=True)

            # Download URL for English OpenSubtitles
            opus_url = "https://opus.nlpl.eu/download.php?f=OpenSubtitles/v2018/mono/en.txt.gz"

            print("📥 Downloading OpenSubtitles corpus...")
            response = requests.get(opus_url, stream=True)

            if response.status_code == 200:
                output_file = target_dir / "opensubtitles_en.txt.gz"
                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                # Extract the file
                import gzip
                with gzip.open(output_file, 'rt', encoding='utf-8') as f_in:
                    with open(target_dir / "opensubtitles_en.txt", 'w', encoding='utf-8') as f_out:
                        lines_count = 0
                        for line in f_in:
                            f_out.write(line)
                            lines_count += 1

                print("✅ SUCCESS: OpenSubtitles corpus downloaded!")
                print(f"   📊 Lines: {lines_count:,}")
                print(f"   📁 Location: {target_dir}")

                self.results[dataset_name]["status"] = "success"
                self.results[dataset_name]["success"] = True
                self.results[dataset_name]["method_used"] = "OPUS OpenSubtitles"
                self.results[dataset_name]["location"] = str(target_dir)
                self.results[dataset_name]["samples"] = lines_count
                return True

            else:
                print(f"❌ Download failed: HTTP {response.status_code}")

        except Exception as e:
            print(f"❌ OPUS method failed: {e}")
            self.results[dataset_name]["methods_tried"].append(f"OPUS: {e!s}")

        self.results[dataset_name]["status"] = "failed"
        return False

    def generate_recovery_report(self):
        """Generate comprehensive recovery report"""

        report = {
            "metadata": {
                "recovery_timestamp": self.timestamp,
                "mission": "Phase 1 High-Priority Dataset Recovery",
                "sacred_covenant_compliance": "ACTIVE"
            },
            "results": self.results,
            "summary": {
                "total_attempted": len(self.results),
                "successful_recoveries": sum(1 for r in self.results.values() if r["success"]),
                "failed_recoveries": sum(1 for r in self.results.values() if not r["success"])
            }
        }

        # Calculate success rate
        success_rate = (report["summary"]["successful_recoveries"] / report["summary"]["total_attempted"]) * 100
        report["summary"]["success_rate"] = f"{success_rate:.1f}%"

        # Save report
        report_filename = f"PHASE1_RECOVERY_REPORT_{self.timestamp}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report_filename, report

def main():
    """Execute Phase 1 recovery for high-priority datasets"""

    print("🚀 PHASE 1 RECOVERY EXECUTION")
    print("=" * 70)
    print("HIGH PRIORITY: Mozilla Common Voice + Supporting Datasets")
    print("=" * 70)

    executor = Phase1RecoveryExecutor()

    # Execute recoveries in priority order
    recoveries = [
        ("Mozilla Common Voice", executor.recover_mozilla_common_voice),
        ("WikiText-103", executor.recover_wikitext_103),
        ("Movie Subtitles", executor.recover_movie_subtitles)
    ]

    success_count = 0
    for name, recovery_func in recoveries:
        try:
            if recovery_func():
                success_count += 1
                print(f"✅ {name}: RECOVERED")
            else:
                print(f"❌ {name}: FAILED")
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")

    # Generate final report
    print("\\n📊 PHASE 1 RECOVERY COMPLETE")
    print("=" * 70)

    report_file, report = executor.generate_recovery_report()

    print("📋 RECOVERY SUMMARY:")
    print(f"   ✅ Successful: {report['summary']['successful_recoveries']}/{report['summary']['total_attempted']}")
    print(f"   📈 Success Rate: {report['summary']['success_rate']}")
    print(f"   📁 Report: {report_file}")

    # Display successful recoveries
    print("\\n🎉 SUCCESSFUL RECOVERIES:")
    for dataset, result in report["results"].items():
        if result["success"]:
            print(f"   • {dataset}: {result['method_used']}")
            print(f"     📁 {result['location']}")
            if 'samples' in result:
                print(f"     📊 {result['samples']:,} samples")

    print("\\n🚀 NEXT PHASE: Begin B3 embedding generation with recovered datasets!")

    return report_file, report

if __name__ == "__main__":
    main()
