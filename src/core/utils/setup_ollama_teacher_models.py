#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #inference #performance #python #source_code #src/core/utils/setup_ollama_teacher_models.py #training
**Category:** Core Implementation
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #api #inference #performance #python #source_code #src\\core\\utils\\setup_ollama_teacher_models.py #training
# Category:** Core Implementation
# Status:** Active

"""
Ollama Teacher Models Setup for ImpressionCore B1

This script sets up Ollama with specific high-quality models that can serve as
teacher sources for ImpressionCore B1 training, embedding enhancement, and
knowledge distillation.

Purpose:
- Download proven high-quality models for teacher-student training
- Set up models optimized for knowledge distillation
- Configure embeddings-compatible models for F: drive integration
- Establish baseline models for performance comparison

Created: 2025-06-17
"""

import os
import subprocess
import time
from pathlib import Path


class OllamaTeacherSetup:
    def __init__(self):
        # OPTIMIZED FOR 10GB CONSTRAINT - HIGH SCHOOL GRADUATE 10/10 DIALOGUE
        self.recommended_models = {
            # PRIMARY TEACHER - Premium conversational quality
            "llama3.1:8b": {
                "purpose": "PRIMARY TEACHER - Exceptional conversation quality for 10/10 dialogue",
                "size": "4.7GB",
                "strength": "Superior reasoning, high school graduate level explanations",
                "priority": 1,
                "quality_score": "10/10",
                "specialization": "General conversation excellence"
            },
            # EFFICIENCY SPECIALIST - Fast reasoning and technical content
            "phi3:mini": {
                "purpose": "EFFICIENCY SPECIALIST - Fast reasoning for training data generation",
                "size": "2.3GB",
                "strength": "Technical accuracy, efficient knowledge distillation",
                "priority": 2,
                "quality_score": "9/10",
                "specialization": "Reasoning and technical explanations"
            },
            # BACKUP OPTIONS (if space allows)
            "mistral:7b": {
                "purpose": "ALTERNATIVE PRIMARY - Fast inference with good general knowledge",
                "size": "4.1GB",
                "strength": "Fast inference, broad knowledge coverage",
                "priority": 3,
                "quality_score": "8.5/10",
                "specialization": "Rapid training data generation"
            },
            "gemma2:2b": {
                "purpose": "DIVERSITY TEACHER - Alternative linguistic patterns",
                "size": "1.6GB",
                "strength": "Different training approach, conversation diversity",
                "priority": 4,
                "quality_score": "8/10",
                "specialization": "Linguistic diversity"
            }
        }

        self.embedding_models = {
            "nomic-embed-text": {
                "purpose": "HIGH-QUALITY text embeddings for F: drive integration",
                "size": "274MB",
                "strength": "Excellent embeddings, F: drive compatible",
                "priority": 1
            },
            "all-minilm": {
                "purpose": "FAST embedding model for batch processing",
                "size": "23MB",
                "strength": "Very fast, training data embedding generation",
                "priority": 2
            }
        }

        # 10GB CONSTRAINT TRACKING
        self.total_space_limit = 10 * 1024 * 1024 * 1024  # 10GB in bytes
        self.recommended_combination = [
            "llama3.1:8b",      # 4.7GB - Primary teacher
            "phi3:mini",        # 2.3GB - Efficiency specialist
            "nomic-embed-text", # 274MB - Embeddings
            "all-minilm"        # 23MB - Fast embeddings
        ]
        # Total: ~7.3GB (2.7GB buffer)

    def check_ollama_status(self):
        """Check if Ollama is running and accessible."""
        try:
            result = subprocess.run(['ollama', 'list'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Ollama is running and accessible")
                return True
            else:
                print("❌ Ollama is not responding properly")
                return False
        except Exception as e:
            print(f"❌ Error checking Ollama status: {e}")
            return False

    def get_current_models(self):
        """Get list of currently installed models."""
        try:
            result = subprocess.run(['ollama', 'list'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                models = []
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if parts:
                            models.append(parts[0])
                return models
            return []
        except Exception as e:
            print(f"Error getting model list: {e}")
            return []

    def download_model(self, model_name, model_info):
        """Download a specific model."""
        print(f"\n🔄 Downloading {model_name}...")
        print(f"   Purpose: {model_info['purpose']}")
        print(f"   Size: {model_info['size']}")
        print(f"   Strength: {model_info['strength']}")

        try:
            # Run ollama pull with real-time output
            process = subprocess.Popen(['ollama', 'pull', model_name],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     text=True,
                                     universal_newlines=True)

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(f"   {output.strip()}")

            if process.returncode == 0:
                print(f"✅ Successfully downloaded {model_name}")
                return True
            else:
                print(f"❌ Failed to download {model_name}")
                return False

        except Exception as e:
            print(f"❌ Error downloading {model_name}: {e}")
            return False

    def setup_teacher_models(self, max_models=3):
        """Set up recommended teacher models."""
        print("🚀 ImpressionCore B1 Teacher Models Setup")
        print("=" * 60)
        print("🎯 Purpose: Download high-quality models for teacher-student training")
        print("🧠 Target: Knowledge distillation and embedding enhancement")
        print("⚡ Hardware consideration: GTX 1050 Ti (4GB VRAM)")
        print("")

        if not self.check_ollama_status():
            print("Please ensure Ollama is running before continuing.")
            return False

        current_models = self.get_current_models()
        print(f"📋 Currently installed models: {len(current_models)}")
        for model in current_models:
            print(f"   • {model}")
        print("")

        # Sort models by priority
        sorted_models = sorted(self.recommended_models.items(),
                             key=lambda x: x[1]['priority'])

        print("🎯 Recommended Teacher Models for ImpressionCore B1:")
        for i, (model_name, info) in enumerate(sorted_models[:max_models], 1):
            print(f"{i}. {model_name}")
            print(f"   • {info['purpose']}")
            print(f"   • Size: {info['size']}")
            print(f"   • {info['strength']}")
            if 'note' in info:
                print(f"   • Note: {info['note']}")
            print("")

        # Download models
        downloaded = []
        for model_name, info in sorted_models[:max_models]:
            if model_name not in current_models:
                success = self.download_model(model_name, info)
                if success:
                    downloaded.append(model_name)
                else:
                    print(f"⚠️ Skipping {model_name} due to download error")
            else:
                print(f"✅ {model_name} already installed")

        return downloaded

    def setup_embedding_models(self):
        """Set up embedding models for F: drive integration."""
        print("\n🧠 Setting up Embedding Models for F: Drive Integration")
        print("=" * 50)

        current_models = self.get_current_models()
        downloaded = []

        for model_name, info in self.embedding_models.items():
            if model_name not in current_models:
                success = self.download_model(model_name, info)
                if success:
                    downloaded.append(model_name)
            else:
                print(f"✅ {model_name} already installed")

        return downloaded

    def create_usage_script(self, downloaded_models):
        """Create a script for using the downloaded models."""
        script_content = f"""#!/bin/bash
# ImpressionCore B1 Teacher Models Usage Script
# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

echo "🎓 ImpressionCore B1 Teacher Models Ready!"
echo "Available teacher models for knowledge distillation:"

"""

        for model in downloaded_models:
            if model in self.recommended_models:
                info = self.recommended_models[model]
                script_content += f"""
# {model}
echo "  • {model}: {info['purpose']}"
# Usage: ollama run {model} "Your prompt here"

"""

        script_content += """
echo ""
echo "💡 Usage Examples:"
echo ""
echo "1. Generate training data:"
echo "   ollama run llama3.1:8b 'Explain quantum computing in simple terms'"
echo ""
echo "2. Technical content generation:"
echo "   ollama run codellama:7b 'Explain how neural networks learn'"
echo ""
echo "3. Embedding generation:"
echo "   ollama run nomic-embed-text 'Text to embed'"
echo ""
echo "🔄 For ImpressionCore B1 integration:"
echo "   Use these models as teacher sources in your training pipeline"
echo "   Extract embeddings for F: drive integration"
echo "   Generate high-quality training examples"
"""

        script_path = Path("ollama_teacher_usage.sh")
        with open(script_path, 'w') as f:
            f.write(script_content)

        # Make executable
        os.chmod(script_path, 0o755)
        print(f"📝 Created usage script: {script_path}")

    def run_setup(self):
        """Run the complete setup process."""
        try:
            # Setup teacher models (limit to 3 for GTX 1050 Ti)
            downloaded_teachers = self.setup_teacher_models(max_models=3)

            # Setup embedding models
            downloaded_embeddings = self.setup_embedding_models()

            all_downloaded = downloaded_teachers + downloaded_embeddings

            if all_downloaded:
                print(f"\n🎉 Successfully set up {len(all_downloaded)} models!")
                print("📋 Downloaded models:")
                for model in all_downloaded:
                    print(f"   ✅ {model}")

                # Create usage script
                self.create_usage_script(all_downloaded)

                print("\n🚀 Next Steps for ImpressionCore B1:")
                print("1. Use these models as teacher sources for knowledge distillation")
                print("2. Generate high-quality training data with the teacher models")
                print("3. Extract embeddings for F: drive integration")
                print("4. Benchmark ImpressionCore B1 performance against these models")
                print("")
                print("💡 Integration with ImpressionCore B1:")
                print("   • Teacher-student training: Use larger models to train smaller B1")
                print("   • Embedding enhancement: Extract embeddings for F: drive")
                print("   • Quality comparison: Benchmark B1 against teacher performance")
                print("   • Data augmentation: Generate diverse training examples")

                return True
            else:
                print("\n⚠️ No new models were downloaded")
                return False

        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            return False

def main():
    setup = OllamaTeacherSetup()

    print("🔍 ImpressionCore B1 Teacher Models Setup")
    print("This will download high-quality models for:")
    print("  • Knowledge distillation training")
    print("  • Embedding generation for F: drive")
    print("  • Performance benchmarking")
    print("  • Training data augmentation")
    print("")

    # Check available space
    try:
        import shutil
        free_space = shutil.disk_usage('.').free / (1024**3)  # GB
        print(f"💾 Available disk space: {free_space:.1f} GB")
        print("📊 Recommended models will use ~15-20 GB total")
        print("")

        if free_space < 25:
            print("⚠️ Warning: Limited disk space. Consider downloading fewer models.")
            print("")
    except OSError:
        pass

    success = setup.run_setup()

    if success:
        print("\n🎓 Teacher models are ready for ImpressionCore B1 integration!")
        print("🔗 Run './ollama_teacher_usage.sh' for usage examples")
    else:
        print("\n💥 Setup incomplete. Check Ollama installation and try again.")

if __name__ == "__main__":
    main()
