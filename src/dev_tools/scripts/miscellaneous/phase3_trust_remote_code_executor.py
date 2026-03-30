#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/scripts/miscellaneous/phase3_trust_remote_code_executor.py
**Category:** Source Code
**Status:** Active
"""



import json
import time
from datetime import datetime
from pathlib import Path

from datasets import load_dataset


class Phase3TrustRemoteCodeExecutor:
    def __init__(self):
        self.start_time = time.time()
        self.results = {
            "phase": "3",
            "mission": "Trust Remote Code Recovery",
            "start_time": datetime.now().isoformat(),
            "datasets_attempted": 0,
            "datasets_recovered": 0,
            "total_samples": 0,
            "recovery_details": {},
            "error_log": []
        }

        # F: drive datasets directory
        self.f_datasets_dir = Path("F:/data/datasets")
        self.f_datasets_dir.mkdir(parents=True, exist_ok=True)

        # Create specialized directories
        (self.f_datasets_dir / "audio" / "vctk").mkdir(parents=True, exist_ok=True)
        (self.f_datasets_dir / "text" / "ted_talks").mkdir(parents=True, exist_ok=True)
        (self.f_datasets_dir / "text" / "opensubtitles").mkdir(parents=True, exist_ok=True)

        print("🚀 PHASE 3: TRUST REMOTE CODE RECOVERY")
        print("=" * 60)
        print("Executing with trust_remote_code=True for specialized datasets")
        print("=" * 60)

    def recover_vctk_corpus(self):
        """Recover VCTK Corpus with trust_remote_code=True"""
        print("🎯 RECOVERING: VCTK Corpus (Multi-speaker)")
        print("=" * 60)

        try:
            print("📥 Method: HuggingFace VCTK with trust_remote_code=True")

            # Load with trust_remote_code=True
            dataset = load_dataset("vctk", trust_remote_code=True)

            # Check available splits
            print("✅ VCTK dataset loaded successfully!")
            print(f"   📊 Available splits: {list(dataset.keys())}")

            # Get sample counts
            total_samples = 0
            for split_name, split_data in dataset.items():
                samples = len(split_data)
                total_samples += samples
                print(f"   • {split_name}: {samples:,} samples")

            # Save to F: drive
            save_path = self.f_datasets_dir / "audio" / "vctk" / "vctk_hf"
            print(f"💾 Saving to: {save_path}")

            # Save dataset
            dataset.save_to_disk(str(save_path))

            self.results["recovery_details"]["vctk"] = {
                "status": "SUCCESS",
                "method": "HuggingFace with trust_remote_code=True",
                "samples": total_samples,
                "location": str(save_path),
                "splits": list(dataset.keys())
            }

            print("✅ SUCCESS: VCTK Corpus recovered!")
            print(f"   📊 Total samples: {total_samples:,}")
            print(f"   📁 Location: {save_path}")

            self.results["datasets_recovered"] += 1
            self.results["total_samples"] += total_samples
            return True

        except Exception as e:
            error_msg = f"VCTK recovery failed: {e!s}"
            print(f"❌ {error_msg}")
            self.results["error_log"].append(error_msg)
            self.results["recovery_details"]["vctk"] = {
                "status": "FAILED",
                "error": str(e)
            }
            return False

    def recover_ted_talks(self):
        """Recover TED Talks with trust_remote_code=True"""
        print("\n🎯 RECOVERING: TED Talks Transcripts")
        print("=" * 60)

        try:
            print("📥 Method: HuggingFace TED Talks IWSLT with trust_remote_code=True")

            # Load with trust_remote_code=True
            dataset = load_dataset("ted_talks_iwslt", trust_remote_code=True,
                                 language_pair=("en", "de"))  # English-German pair

            print("✅ TED Talks dataset loaded successfully!")
            print(f"   📊 Available splits: {list(dataset.keys())}")

            # Get sample counts
            total_samples = 0
            for split_name, split_data in dataset.items():
                samples = len(split_data)
                total_samples += samples
                print(f"   • {split_name}: {samples:,} samples")

            # Save to F: drive
            save_path = self.f_datasets_dir / "text" / "ted_talks" / "ted_talks_hf"
            print(f"💾 Saving to: {save_path}")

            # Save dataset
            dataset.save_to_disk(str(save_path))

            self.results["recovery_details"]["ted_talks"] = {
                "status": "SUCCESS",
                "method": "HuggingFace with trust_remote_code=True",
                "samples": total_samples,
                "location": str(save_path),
                "splits": list(dataset.keys())
            }

            print("✅ SUCCESS: TED Talks recovered!")
            print(f"   📊 Total samples: {total_samples:,}")
            print(f"   📁 Location: {save_path}")

            self.results["datasets_recovered"] += 1
            self.results["total_samples"] += total_samples
            return True

        except Exception as e:
            error_msg = f"TED Talks recovery failed: {e!s}"
            print(f"❌ {error_msg}")
            self.results["error_log"].append(error_msg)
            self.results["recovery_details"]["ted_talks"] = {
                "status": "FAILED",
                "error": str(e)
            }
            return False

    def recover_opensubtitles(self):
        """Recover OpenSubtitles with trust_remote_code=True"""
        print("\n🎯 RECOVERING: OpenSubtitles Corpus")
        print("=" * 60)

        try:
            print("📥 Method: HuggingFace OpenSubtitles with trust_remote_code=True")

            # Load with trust_remote_code=True (English only)
            dataset = load_dataset("open_subtitles", trust_remote_code=True,
                                 lang1="en", lang2="en")

            print("✅ OpenSubtitles dataset loaded successfully!")
            print(f"   📊 Available splits: {list(dataset.keys())}")

            # Get sample counts
            total_samples = 0
            for split_name, split_data in dataset.items():
                samples = len(split_data)
                total_samples += samples
                print(f"   • {split_name}: {samples:,} samples")

            # Save to F: drive
            save_path = self.f_datasets_dir / "text" / "opensubtitles" / "opensubtitles_hf"
            print(f"💾 Saving to: {save_path}")

            # Save dataset
            dataset.save_to_disk(str(save_path))

            self.results["recovery_details"]["opensubtitles"] = {
                "status": "SUCCESS",
                "method": "HuggingFace with trust_remote_code=True",
                "samples": total_samples,
                "location": str(save_path),
                "splits": list(dataset.keys())
            }

            print("✅ SUCCESS: OpenSubtitles recovered!")
            print(f"   📊 Total samples: {total_samples:,}")
            print(f"   📁 Location: {save_path}")

            self.results["datasets_recovered"] += 1
            self.results["total_samples"] += total_samples
            return True

        except Exception as e:
            error_msg = f"OpenSubtitles recovery failed: {e!s}"
            print(f"❌ {error_msg}")
            self.results["error_log"].append(error_msg)
            self.results["recovery_details"]["opensubtitles"] = {
                "status": "FAILED",
                "error": str(e)
            }
            return False

    def verify_existing_datasets(self):
        """Verify and count existing recovered datasets"""
        print("\n🔍 VERIFYING EXISTING RECOVERED DATASETS")
        print("=" * 60)

        existing_datasets = {}

        # Check WikiText-103
        wikitext_path = self.f_datasets_dir / "text" / "wikitext_103_hf"
        if wikitext_path.exists():
            try:
                from datasets import load_from_disk
                dataset = load_from_disk(str(wikitext_path))
                total_samples = sum(len(split) for split in dataset.values())
                existing_datasets["wikitext_103"] = {
                    "samples": total_samples,
                    "location": str(wikitext_path),
                    "status": "VERIFIED"
                }
                print(f"✅ WikiText-103: {total_samples:,} samples")
            except Exception as e:
                print(f"⚠️ WikiText-103 verification failed: {e}")

        # Check Google Speech Commands
        gsc_path = Path("F:/data/datasets/phonemes/google_speech_commands_v2")
        if gsc_path.exists():
            try:
                # Count audio files
                audio_files = list(gsc_path.rglob("*.wav"))
                existing_datasets["google_speech_commands"] = {
                    "samples": len(audio_files),
                    "location": str(gsc_path),
                    "status": "VERIFIED"
                }
                print(f"✅ Google Speech Commands V2: {len(audio_files):,} samples")
            except Exception as e:
                print(f"⚠️ Google Speech Commands verification failed: {e}")

        return existing_datasets

    def execute_mission(self):
        """Execute the complete Phase 3 recovery mission"""
        print("🎯 Starting Phase 3 Trust Remote Code Recovery...")

        # Verify existing datasets first
        existing = self.verify_existing_datasets()

        # Track attempt counter
        self.results["datasets_attempted"] = 3

        # Execute recoveries with trust_remote_code=True
        recoveries = [
            self.recover_vctk_corpus,
            self.recover_ted_talks,
            self.recover_opensubtitles
        ]

        for recovery_func in recoveries:
            try:
                recovery_func()
            except Exception as e:
                print(f"❌ Recovery function failed: {e}")

        # Final summary
        self.generate_final_report(existing)

    def generate_final_report(self, existing_datasets):
        """Generate comprehensive Phase 3 final report"""
        print("\n📊 PHASE 3 TRUST REMOTE CODE RECOVERY COMPLETE")
        print("=" * 70)

        # Calculate totals including existing
        total_existing_samples = sum(d.get("samples", 0) for d in existing_datasets.values())
        grand_total_samples = self.results["total_samples"] + total_existing_samples

        self.results["end_time"] = datetime.now().isoformat()
        self.results["duration_seconds"] = time.time() - self.start_time
        self.results["existing_datasets"] = existing_datasets
        self.results["grand_total_samples"] = grand_total_samples

        # Success rate calculation
        total_possible = len(existing_datasets) + self.results["datasets_attempted"]
        total_successful = len(existing_datasets) + self.results["datasets_recovered"]
        success_rate = (total_successful / total_possible) * 100 if total_possible > 0 else 0

        print("📋 PHASE 3 SUMMARY:")
        print(f"   🎯 New datasets attempted: {self.results['datasets_attempted']}")
        print(f"   ✅ New datasets recovered: {self.results['datasets_recovered']}")
        print(f"   📊 New samples acquired: {self.results['total_samples']:,}")
        print(f"   📈 Phase 3 Success Rate: {(self.results['datasets_recovered']/self.results['datasets_attempted']*100):.1f}%")

        print("\n🏆 CUMULATIVE MISSION STATUS:")
        print(f"   📊 Total datasets available: {total_successful}")
        print(f"   📊 Grand total samples: {grand_total_samples:,}")
        print(f"   📈 Overall Success Rate: {success_rate:.1f}%")

        # List successful recoveries
        print("\n🎉 ALL AVAILABLE DATASETS:")

        for name, details in existing_datasets.items():
            print(f"   ✅ {name}: {details['samples']:,} samples")
            print(f"      📁 {details['location']}")

        for name, details in self.results["recovery_details"].items():
            if details.get("status") == "SUCCESS":
                print(f"   ✅ {name}: {details['samples']:,} samples")
                print(f"      📁 {details['location']}")

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"PHASE3_TRUST_REMOTE_CODE_REPORT_{timestamp}.json"

        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n📁 Report saved: {report_file}")
        print("\n🚀 READY FOR B3 EMBEDDING GENERATION WITH ALL RECOVERED DATASETS!")

if __name__ == "__main__":
    executor = Phase3TrustRemoteCodeExecutor()
    executor.execute_mission()
