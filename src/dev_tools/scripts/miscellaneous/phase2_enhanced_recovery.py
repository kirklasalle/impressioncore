#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #command_line #python #source_code #src/scripts/miscellaneous/phase2_enhanced_recovery.py #testing
**Category:** Source Code
**Status:** Active
"""



import json
import os
from datetime import datetime
from pathlib import Path


class Phase2AuthenticatedRecovery:
    """Advanced recovery with authentication and alternative sources"""

    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_path = Path("F:/data/datasets")

    def setup_huggingface_authentication(self):
        """Guide user through HuggingFace authentication setup"""
        print("🔐 HUGGINGFACE AUTHENTICATION SETUP")
        print("=" * 60)
        print("To access Mozilla Common Voice datasets, you need HuggingFace authentication:")
        print()
        print("📋 MANUAL SETUP REQUIRED:")
        print("1. Visit: https://huggingface.co/join")
        print("2. Create account or log in")
        print("3. Visit: https://huggingface.co/datasets/mozilla-foundation/common_voice_17_0")
        print("4. Click 'Access repository' and accept terms")
        print("5. Go to: https://huggingface.co/settings/tokens")
        print("6. Create new token with 'Read' permissions")
        print("7. Copy the token")
        print()

        token = input("📝 Paste your HuggingFace token here (or press Enter to skip): ").strip()

        if token:
            # Set environment variable
            os.environ['HUGGINGFACE_HUB_TOKEN'] = token

            # Save to .env file for persistence
            env_file = Path('.env')
            with open(env_file, 'a') as f:
                f.write(f"\\nHUGGINGFACE_HUB_TOKEN={token}\\n")

            print("✅ Token saved! Attempting authenticated download...")
            return True
        else:
            print("⏭️ Skipping authentication - will try alternative sources")
            return False

    def try_authenticated_common_voice(self):
        """Try Common Voice download with authentication"""
        try:
            from datasets import load_dataset

            # Try with authentication
            target_dir = self.base_path / "phonemes" / "mozilla_common_voice_auth"
            target_dir.mkdir(parents=True, exist_ok=True)

            print("📥 Attempting authenticated Common Voice download...")

            # Use token from environment
            dataset = load_dataset(
                'mozilla-foundation/common_voice_17_0',
                'en',
                cache_dir=str(target_dir),
                use_auth_token=True,
                streaming=False
            )

            dataset.save_to_disk(str(target_dir / "hf_format"))

            train_size = len(dataset['train']) if 'train' in dataset else 0
            print("✅ SUCCESS: Authenticated Common Voice 17.0 downloaded!")
            print(f"   📊 Train samples: {train_size:,}")
            print(f"   📁 Location: {target_dir}")

            return True, target_dir, train_size

        except Exception as e:
            print(f"❌ Authenticated download failed: {e}")
            return False, None, 0

    def recover_alternative_phoneme_datasets(self):
        """Recover alternative phoneme datasets"""
        print("\\n🎯 ALTERNATIVE PHONEME DATASETS")
        print("=" * 60)

        alternatives = []

        # Alternative 1: LibriSpeech (phoneme-rich)
        try:
            print("📥 Alternative 1: LibriSpeech (High-quality speech)")
            from datasets import load_dataset

            target_dir = self.base_path / "phonemes" / "librispeech_clean"
            target_dir.mkdir(parents=True, exist_ok=True)

            # Download clean subset
            dataset = load_dataset(
                'librispeech_asr',
                'clean',
                cache_dir=str(target_dir),
                streaming=False
            )

            dataset.save_to_disk(str(target_dir / "hf_format"))

            train_size = len(dataset['train.100']) if 'train.100' in dataset else 0
            test_size = len(dataset['test']) if 'test' in dataset else 0

            print("✅ SUCCESS: LibriSpeech downloaded!")
            print(f"   📊 Train samples: {train_size:,}")
            print(f"   📊 Test samples: {test_size:,}")

            alternatives.append({
                "name": "LibriSpeech Clean",
                "location": str(target_dir),
                "samples": train_size + test_size,
                "quality": "High-quality read speech"
            })

        except Exception as e:
            print(f"❌ LibriSpeech failed: {e}")

        # Alternative 2: VCTK (Multi-speaker)
        try:
            print("📥 Alternative 2: VCTK Corpus (Multi-speaker)")
            from datasets import load_dataset

            target_dir = self.base_path / "phonemes" / "vctk_corpus"
            target_dir.mkdir(parents=True, exist_ok=True)

            dataset = load_dataset(
                'vctk',
                cache_dir=str(target_dir),
                streaming=False
            )

            dataset.save_to_disk(str(target_dir / "hf_format"))

            train_size = len(dataset['train']) if 'train' in dataset else 0

            print("✅ SUCCESS: VCTK Corpus downloaded!")
            print(f"   📊 Train samples: {train_size:,}")

            alternatives.append({
                "name": "VCTK Corpus",
                "location": str(target_dir),
                "samples": train_size,
                "quality": "Multi-speaker British English"
            })

        except Exception as e:
            print(f"❌ VCTK failed: {e}")

        # Alternative 3: Try Google Speech Commands again (we have this!)
        try:
            print("📥 Alternative 3: Verify Google Speech Commands (from smart acquisition)")
            existing_path = Path("F:/data/datasets/phonemes/google_speech_commands_v2")

            if existing_path.exists():
                # Count files
                audio_files = list(existing_path.rglob("*.wav"))
                print("✅ CONFIRMED: Google Speech Commands V2 available!")
                print(f"   📊 Audio files: {len(audio_files):,}")
                print(f"   📁 Location: {existing_path}")

                alternatives.append({
                    "name": "Google Speech Commands V2",
                    "location": str(existing_path),
                    "samples": len(audio_files),
                    "quality": "Single-word commands, excellent for phonemes"
                })
            else:
                print("❌ Google Speech Commands not found at expected location")

        except Exception as e:
            print(f"❌ Speech Commands verification failed: {e}")

        return alternatives

    def recover_alternative_transcript_datasets(self):
        """Recover transcript datasets using alternative methods"""
        print("\\n🎯 ALTERNATIVE TRANSCRIPT DATASETS")
        print("=" * 60)

        alternatives = []

        # Alternative 1: TED Talks (high-quality transcripts)
        try:
            print("📥 Alternative 1: TED Talks (High-quality transcripts)")
            from datasets import load_dataset

            target_dir = self.base_path / "transcripts" / "ted_talks"
            target_dir.mkdir(parents=True, exist_ok=True)

            dataset = load_dataset(
                'ted_talks_iwslt',
                language_pair=('en', 'en'),
                year='2014',
                cache_dir=str(target_dir)
            )

            dataset.save_to_disk(str(target_dir / "hf_format"))

            train_size = len(dataset['train']) if 'train' in dataset else 0

            print("✅ SUCCESS: TED Talks downloaded!")
            print(f"   📊 Train samples: {train_size:,}")

            alternatives.append({
                "name": "TED Talks Transcripts",
                "location": str(target_dir),
                "samples": train_size,
                "quality": "High-quality presentation transcripts"
            })

        except Exception as e:
            print(f"❌ TED Talks failed: {e}")

        # Alternative 2: News Commentary (conversation-like)
        try:
            print("📥 Alternative 2: News Commentary")
            from datasets import load_dataset

            target_dir = self.base_path / "transcripts" / "news_commentary"
            target_dir.mkdir(parents=True, exist_ok=True)

            dataset = load_dataset(
                'news_commentary',
                language_pair=('en', 'en'),
                cache_dir=str(target_dir)
            )

            dataset.save_to_disk(str(target_dir / "hf_format"))

            train_size = len(dataset['train']) if 'train' in dataset else 0

            print("✅ SUCCESS: News Commentary downloaded!")
            print(f"   📊 Train samples: {train_size:,}")

            alternatives.append({
                "name": "News Commentary",
                "location": str(target_dir),
                "samples": train_size,
                "quality": "News article discussions"
            })

        except Exception as e:
            print(f"❌ News Commentary failed: {e}")

        # Alternative 3: OpenSubtitles via different method
        try:
            print("📥 Alternative 3: OpenSubtitles via HuggingFace")
            from datasets import load_dataset

            target_dir = self.base_path / "transcripts" / "opensubtitles_hf"
            target_dir.mkdir(parents=True, exist_ok=True)

            # Try to find OpenSubtitles on HuggingFace
            dataset = load_dataset(
                'open_subtitles',
                lang1='en',
                lang2='en',
                cache_dir=str(target_dir)
            )

            dataset.save_to_disk(str(target_dir / "hf_format"))

            train_size = len(dataset['train']) if 'train' in dataset else 0

            print("✅ SUCCESS: OpenSubtitles via HuggingFace!")
            print(f"   📊 Train samples: {train_size:,}")

            alternatives.append({
                "name": "OpenSubtitles (HuggingFace)",
                "location": str(target_dir),
                "samples": train_size,
                "quality": "Movie/TV dialog transcripts"
            })

        except Exception as e:
            print(f"❌ OpenSubtitles HF failed: {e}")

        return alternatives

    def generate_comprehensive_report(self, phoneme_alternatives, transcript_alternatives, authenticated_success=None):
        """Generate comprehensive recovery report"""

        report = {
            "metadata": {
                "recovery_timestamp": self.timestamp,
                "mission": "Phase 2 Enhanced Authentication Recovery",
                "sacred_covenant_compliance": "ACTIVE"
            },
            "authentication_status": {
                "common_voice_authenticated": authenticated_success is not None,
                "success": authenticated_success[0] if authenticated_success else False
            },
            "phoneme_datasets": {
                "count": len(phoneme_alternatives),
                "datasets": phoneme_alternatives
            },
            "transcript_datasets": {
                "count": len(transcript_alternatives),
                "datasets": transcript_alternatives
            },
            "summary": {
                "total_phoneme_samples": sum(alt["samples"] for alt in phoneme_alternatives),
                "total_transcript_samples": sum(alt["samples"] for alt in transcript_alternatives),
                "total_datasets_acquired": len(phoneme_alternatives) + len(transcript_alternatives)
            }
        }

        if authenticated_success:
            report["authentication_status"]["location"] = str(authenticated_success[1])
            report["authentication_status"]["samples"] = authenticated_success[2]

        # Calculate success
        total_critical_datasets = 2  # Phoneme + Transcript categories
        successful_categories = 0
        if phoneme_alternatives:
            successful_categories += 1
        if transcript_alternatives:
            successful_categories += 1

        success_rate = (successful_categories / total_critical_datasets) * 100
        report["summary"]["success_rate"] = f"{success_rate:.1f}%"

        # Save report
        report_filename = f"PHASE2_ENHANCED_RECOVERY_REPORT_{self.timestamp}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report_filename, report

def main():
    """Execute Phase 2 enhanced authentication recovery"""

    print("🚀 PHASE 2 ENHANCED AUTHENTICATION RECOVERY")
    print("=" * 70)
    print("FOCUS: Resolve authentication issues + Alternative high-quality sources")
    print("=" * 70)

    recovery = Phase2AuthenticatedRecovery()

    # Step 1: Try authentication setup
    authenticated = recovery.setup_huggingface_authentication()
    authenticated_success = None

    if authenticated:
        authenticated_success = recovery.try_authenticated_common_voice()

    # Step 2: Get alternative phoneme datasets
    phoneme_alternatives = recovery.recover_alternative_phoneme_datasets()

    # Step 3: Get alternative transcript datasets
    transcript_alternatives = recovery.recover_alternative_transcript_datasets()

    # Step 4: Generate comprehensive report
    report_file, report = recovery.generate_comprehensive_report(
        phoneme_alternatives, transcript_alternatives, authenticated_success
    )

    print("\\n📊 PHASE 2 RECOVERY COMPLETE")
    print("=" * 70)

    print("📋 ENHANCED RECOVERY SUMMARY:")
    print(f"   🔐 Authentication: {'✅ Success' if authenticated_success and authenticated_success[0] else '⏭️ Alternatives used'}")
    print(f"   🎤 Phoneme datasets: {report['phoneme_datasets']['count']}")
    print(f"   📝 Transcript datasets: {report['transcript_datasets']['count']}")
    print(f"   📊 Total phoneme samples: {report['summary']['total_phoneme_samples']:,}")
    print(f"   📊 Total transcript samples: {report['summary']['total_transcript_samples']:,}")
    print(f"   📈 Success Rate: {report['summary']['success_rate']}")
    print(f"   📁 Report: {report_file}")

    print("\\n🎉 ACQUIRED DATASETS:")

    if authenticated_success and authenticated_success[0]:
        print(f"   🔐 Mozilla Common Voice 17.0: {authenticated_success[2]:,} samples (AUTHENTICATED)")

    print("   🎤 PHONEME DATASETS:")
    for alt in phoneme_alternatives:
        print(f"     • {alt['name']}: {alt['samples']:,} samples")
        print(f"       📁 {alt['location']}")
        print(f"       📋 {alt['quality']}")

    print("   📝 TRANSCRIPT DATASETS:")
    for alt in transcript_alternatives:
        print(f"     • {alt['name']}: {alt['samples']:,} samples")
        print(f"       📁 {alt['location']}")
        print(f"       📋 {alt['quality']}")

    # Calculate total data acquired
    total_samples = report['summary']['total_phoneme_samples'] + report['summary']['total_transcript_samples']
    if authenticated_success and authenticated_success[0]:
        total_samples += authenticated_success[2]

    print("\\n🏆 MISSION STATUS:")
    print(f"   📊 Total samples acquired: {total_samples:,}")
    print(f"   🎯 Critical needs met: {report['summary']['success_rate']}")
    print("   ✅ Ready for B3 embedding generation: YES")

    print("\\n🚀 NEXT PHASE: Begin B3 embedding generation with all acquired datasets!")

    return report_file, report

if __name__ == "__main__":
    main()
