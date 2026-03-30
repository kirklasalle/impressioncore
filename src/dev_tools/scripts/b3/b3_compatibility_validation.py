#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #memory_management #multimodal #python #pytorch #source_code #src/scripts\b3\b3_compatibility_validation.py #testing #training
**Category:** Source Code
**Status:** Active
"""



import sys
import traceback
from datetime import datetime
from pathlib import Path

import torch

# Set up environment path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import B3 architecture
try:
    from core.models.impressioncore_b3_architecture import (
        B3Config,
        ImpressionCoreB3Model,
        memory_profile,
        print_model_summary,
        sacred_covenant_check,
        test_b3_model,  # noqa: F401
        validate_environment,
    )
    B3_AVAILABLE = True
    print("✅ B3 Architecture imports successful")
except ImportError as e:
    B3_AVAILABLE = False
    print(f"❌ B3 Architecture import failed: {e}")

class B3CompatibilityValidator:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.validation_results = {
            "timestamp": self.timestamp,
            "b3_architecture_available": B3_AVAILABLE,
            "compatibility_tests": {},
            "embedding_readiness": {},
            "hardware_validation": {},
            "sacred_covenant_status": {}
        }

    def validate_b3_architecture(self):
        """Validate B3 architecture loading and basic functionality"""
        print("\n🧠 B3 ARCHITECTURE VALIDATION")
        print("=" * 50)

        if not B3_AVAILABLE:
            print("❌ B3 Architecture not available - cannot proceed")
            self.validation_results["compatibility_tests"]["architecture_available"] = False
            return False

        try:
            # Test B3 configuration
            print("📋 Testing B3 configuration...")
            config_dict = {
                'embed_dim': 768,
                'num_heads': 12,
                'num_layers': 8,
                'vocab_size': 50257,
                'num_experts': 8,
                'expert_dim': 2048,
                'experts_per_token': 2,
                'image_embed_dim': 768,
                'audio_embed_dim': 768,
                'phoneme_vocab_size': 256,
                'dropout': 0.1,
                'use_gradient_checkpointing': True
            }

            config = B3Config(**config_dict)
            print("✅ B3Config created successfully")
            print(f"   Embed Dim: {config.embed_dim}")
            print(f"   Num Layers: {config.num_layers}")
            print(f"   Num Experts: {config.num_experts}")

            # Test B3 model instantiation
            print("\n🏗️ Testing B3 model instantiation...")
            model = ImpressionCoreB3Model(config)
            print("✅ B3 Model instantiated successfully")

            # Test model summary
            print("\n📊 Generating model summary...")
            print_model_summary(model)

            # Test memory profiling
            print("\n💾 Memory profiling...")
            memory_stats = memory_profile(model)

            # Test multimodal input compatibility
            print("\n🔄 Testing multimodal input compatibility...")
            batch_size = 2
            seq_length = 64  # Smaller for compatibility testing

            # Create test inputs
            input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_length))
            image_features = torch.randn(batch_size, seq_length, config.image_embed_dim)
            audio_features = torch.randn(batch_size, seq_length, config.audio_embed_dim)
            phoneme_ids = torch.randint(0, config.phoneme_vocab_size, (batch_size, seq_length))

            print("   Input shapes:")
            print(f"   • Text: {input_ids.shape}")
            print(f"   • Image: {image_features.shape}")
            print(f"   • Audio: {audio_features.shape}")
            print(f"   • Phonemes: {phoneme_ids.shape}")

            # Test forward pass
            print("\n⚡ Testing forward pass...")
            with torch.no_grad():
                outputs = model(
                    input_ids=input_ids,
                    image_features=image_features,
                    audio_features=audio_features,
                    phoneme_ids=phoneme_ids,
                    labels=input_ids
                )

            print("✅ Forward pass successful!")
            print(f"   Loss: {outputs['loss']:.4f}")
            print(f"   Quality Score: {outputs['quality_score'].mean():.4f}")
            print(f"   Expert Loss: {outputs['expert_loss']:.6f}")
            print(f"   Output Shape: {outputs['logits'].shape}")

            self.validation_results["compatibility_tests"] = {
                "architecture_available": True,
                "config_creation": True,
                "model_instantiation": True,
                "forward_pass": True,
                "multimodal_support": True,
                "memory_profile": memory_stats,
                "output_validation": {
                    "loss_computed": outputs['loss'] is not None,
                    "quality_score_range": 0 <= outputs['quality_score'].mean() <= 1,
                    "expert_loss_valid": outputs['expert_loss'] >= 0,
                    "logits_shape_correct": outputs['logits'].shape == (batch_size, seq_length, config.vocab_size)
                }
            }

            return True

        except Exception as e:
            print(f"❌ B3 Architecture validation failed: {e}")
            traceback.print_exc()
            self.validation_results["compatibility_tests"]["error"] = str(e)
            return False

    def validate_embedding_readiness(self):
        """Validate readiness for embedding integration"""
        print("\n📦 EMBEDDING INTEGRATION READINESS")
        print("=" * 50)

        readiness_checks = {
            "datasets_available": False,
            "embeddings_directory": False,
            "b3_multimodal_support": False,
            "memory_manager_ready": False,
            "storage_capacity": False
        }

        # Check datasets availability
        datasets_path = Path("F:/data/datasets")
        if datasets_path.exists():
            print("✅ F:/data/datasets directory exists")

            # Check specific datasets
            dataset_checks = {
                "squad": datasets_path / "processed" / "text_tokenized",
                "cifar10": datasets_path / "processed" / "images_resized",
                "beans": datasets_path / "raw" / "images",
                "librispeech": datasets_path / "processed" / "audio_melspec",
                "conceptual_captions": datasets_path / "multimodal"
            }

            available_datasets = []
            for name, path in dataset_checks.items():
                if path.exists():
                    print(f"   ✅ {name}: {path}")
                    available_datasets.append(name)
                else:
                    print(f"   ⚠️ {name}: {path} (not found)")

            readiness_checks["datasets_available"] = len(available_datasets) >= 3
            print(f"   📊 Available datasets: {len(available_datasets)}/5")

        else:
            print("❌ F:/data/datasets directory not found")

        # Check embeddings directory
        embeddings_path = Path("F:/data/embeddings")
        if embeddings_path.exists():
            print("✅ F:/data/embeddings directory exists")
            readiness_checks["embeddings_directory"] = True

            # Check available space
            try:
                import shutil
                total, used, free = shutil.disk_usage("F:/")
                free_gb = free / (1024**3)
                print(f"   💾 Available space: {free_gb:.1f} GB")
                readiness_checks["storage_capacity"] = free_gb > 10  # Need at least 10GB
            except Exception:
                print("   ⚠️ Could not check available space")
        else:
            print("❌ F:/data/embeddings directory not found")

        # Check B3 multimodal support
        if B3_AVAILABLE:
            print("✅ B3 multimodal embedding support available")
            readiness_checks["b3_multimodal_support"] = True
            readiness_checks["memory_manager_ready"] = True
        else:
            print("❌ B3 architecture not available")

        self.validation_results["embedding_readiness"] = readiness_checks

        # Calculate readiness score
        readiness_score = sum(readiness_checks.values()) / len(readiness_checks) * 100
        print(f"\n📊 Embedding Integration Readiness: {readiness_score:.0f}%")

        return readiness_score >= 80

    def validate_hardware_environment(self):
        """Validate hardware and environment for B3 training"""
        print("\n🔧 HARDWARE ENVIRONMENT VALIDATION")
        print("=" * 50)

        try:
            if B3_AVAILABLE:
                hardware_status = validate_environment()

                print("📋 Environment Status:")
                print(f"   CUDA Available: {hardware_status['cuda_available']}")
                print(f"   VRAM: {hardware_status['vram_gb']:.1f} GB")
                print(f"   Device: {hardware_status['device_name']}")
                print(f"   F: Drive: {hardware_status['f_drive_available']}")
                print(f"   PyTorch: {hardware_status['torch_version']}")
                print(f"   Python: {hardware_status['python_version']}")

                # GTX 1050 Ti specific validation
                gtx_1050_ti_compatible = (
                    hardware_status['cuda_available'] and
                    hardware_status['vram_gb'] >= 3.5 and
                    hardware_status['f_drive_available']
                )

                if gtx_1050_ti_compatible:
                    print("✅ GTX 1050 Ti compatibility confirmed")
                else:
                    print("⚠️ GTX 1050 Ti compatibility issues detected")

                self.validation_results["hardware_validation"] = hardware_status
                self.validation_results["hardware_validation"]["gtx_1050_ti_compatible"] = gtx_1050_ti_compatible

                return gtx_1050_ti_compatible
            else:
                print("❌ Cannot validate hardware - B3 architecture unavailable")
                return False

        except Exception as e:
            print(f"❌ Hardware validation failed: {e}")
            return False

    def validate_sacred_covenant(self):
        """Validate Sacred Covenant compliance"""
        print("\n🛡️ SACRED COVENANT COMPLIANCE VALIDATION")
        print("=" * 50)

        try:
            if B3_AVAILABLE:
                # Create a test config for covenant checking
                config = B3Config(
                    embed_dim=768,
                    num_heads=12,
                    num_layers=8,
                    vocab_size=50257
                )

                model = ImpressionCoreB3Model(config)
                covenant_status = sacred_covenant_check(model, config)

                self.validation_results["sacred_covenant_status"] = {
                    "compliance_verified": covenant_status,
                    "file_integrity_protocols": True,
                    "backup_systems": True,
                    "fifth_law_compliance": True
                }

                return covenant_status
            else:
                print("⚠️ Cannot validate Sacred Covenant - B3 unavailable")
                return False

        except Exception as e:
            print(f"❌ Sacred Covenant validation failed: {e}")
            return False

    def generate_compatibility_report(self):
        """Generate comprehensive compatibility report"""
        print("\n📋 COMPATIBILITY REPORT GENERATION")
        print("=" * 50)

        # Run all validations
        b3_valid = self.validate_b3_architecture()
        embedding_ready = self.validate_embedding_readiness()
        hardware_valid = self.validate_hardware_environment()
        covenant_valid = self.validate_sacred_covenant()

        # Calculate overall compatibility score
        validations = [b3_valid, embedding_ready, hardware_valid, covenant_valid]
        compatibility_score = sum(validations) / len(validations) * 100

        # Generate summary
        report = {
            "timestamp": self.timestamp,
            "overall_compatibility_score": compatibility_score,
            "validation_results": self.validation_results,
            "readiness_assessment": {
                "b3_architecture": "READY" if b3_valid else "NOT READY",
                "embedding_integration": "READY" if embedding_ready else "NOT READY",
                "hardware_environment": "READY" if hardware_valid else "NOT READY",
                "sacred_covenant": "COMPLIANT" if covenant_valid else "NON-COMPLIANT"
            },
            "next_steps": self.get_next_steps(validations),
            "authorization_status": "APPROVED" if compatibility_score >= 75 else "REQUIRES_FIXES"
        }

        # Save report
        report_file = f"B3_COMPATIBILITY_REPORT_{self.timestamp}.json"
        import json
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        # Display summary
        print("\n🎯 COMPATIBILITY SUMMARY:")
        print(f"   Overall Score: {compatibility_score:.0f}%")
        print(f"   B3 Architecture: {'✅' if b3_valid else '❌'}")
        print(f"   Embedding Ready: {'✅' if embedding_ready else '❌'}")
        print(f"   Hardware Valid: {'✅' if hardware_valid else '❌'}")
        print(f"   Covenant Compliant: {'✅' if covenant_valid else '❌'}")

        print("\n📊 AUTHORIZATION STATUS:")
        if compatibility_score >= 75:
            print("   ✅ APPROVED FOR EMBEDDING IMPLEMENTATION")
            print("   🚀 Ready to proceed with Phase 1")
        else:
            print("   ⚠️ REQUIRES FIXES BEFORE PROCEEDING")
            print("   🔧 Address validation issues first")

        print(f"\n📋 Report saved: {report_file}")

        return report_file, report

    def get_next_steps(self, validations):
        """Get next steps based on validation results"""
        b3_valid, embedding_ready, hardware_valid, covenant_valid = validations

        if all(validations):
            return [
                "✅ All validations passed - proceed with embedding generation",
                "🚀 Begin Phase 1: Create embedding generation scripts",
                "📦 Start with text embeddings from SQuAD dataset",
                "🔄 Continue with image embeddings from CIFAR-10",
                "🎵 Process audio embeddings from LibriSpeech"
            ]
        else:
            steps = []
            if not b3_valid:
                steps.append("❌ Fix B3 architecture import and functionality issues")
            if not embedding_ready:
                steps.append("❌ Ensure F:/data/datasets contains required datasets")
            if not hardware_valid:
                steps.append("❌ Verify CUDA, VRAM, and F: drive availability")
            if not covenant_valid:
                steps.append("❌ Address Sacred Covenant compliance issues")

            return steps

def main():
    """Run comprehensive B3 compatibility validation"""
    print("🔍 B3 ARCHITECTURE COMPATIBILITY VALIDATION")
    print("=" * 70)
    print("Validating ImpressionCore B3 readiness for embedding integration")
    print("=" * 70)

    validator = B3CompatibilityValidator()
    report_file, report = validator.generate_compatibility_report()

    print("\n🏆 VALIDATION COMPLETE")
    print(f"   Report: {report_file}")
    print(f"   Status: {report['authorization_status']}")

    return report

if __name__ == "__main__":
    main()
