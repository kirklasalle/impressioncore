"""
Path A: Knowledge Distillation Setup
Download DialoGPT-medium teacher model and prepare for distillation training
"""

import sys
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def download_teacher_model():
    """Download DialoGPT-medium teacher model"""

    print("\n" + "="*80)
    print("🎓 PATH A: KNOWLEDGE DISTILLATION SETUP")
    print("="*80)
    print("\nStep 1: Downloading Teacher Model (DialoGPT-medium)")
    print("-" * 80)

    teacher_name = "microsoft/DialoGPT-medium"
    cache_dir = "F:/models/teachers/dialogpt_medium"

    print(f"\n📥 Downloading: {teacher_name}")
    print(f"📁 Cache Directory: {cache_dir}")
    print(f"💾 Expected Size: ~1.5 GB")
    print(f"📚 Training Data: 147 million Reddit conversations")
    print(f"🔢 Parameters: 354 million")
    print("\n⏳ This may take 5-10 minutes depending on connection speed...")

    try:
        # Create cache directory
        Path(cache_dir).mkdir(parents=True, exist_ok=True)

        # Download tokenizer
        print("\n[1/2] Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            teacher_name,
            cache_dir=cache_dir
        )
        print("✅ Tokenizer downloaded successfully")

        # Download model
        print("\n[2/2] Downloading model (this is the large download)...")
        model = AutoModelForCausalLM.from_pretrained(
            teacher_name,
            cache_dir=cache_dir,
            torch_dtype=torch.float32,  # Use FP32 for compatibility
            use_safetensors=True  # Use safetensors format (more secure)
        )
        print("✅ Model downloaded successfully")

        # Get model info
        num_params = sum(p.numel() for p in model.parameters())

        print("\n" + "="*80)
        print("✅ TEACHER MODEL READY!")
        print("="*80)
        print(f"\n📊 Model Statistics:")
        print(f"   - Name: {teacher_name}")
        print(f"   - Parameters: {num_params:,}")
        print(f"   - Location: {cache_dir}")
        print(f"   - Vocabulary Size: {len(tokenizer)}")
        print(f"   - Max Position: {model.config.max_position_embeddings}")

        # Test generation
        print("\n🧪 Testing teacher model generation...")
        test_input = "Hello, how are you?"
        inputs = tokenizer(test_input, return_tensors="pt")

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=50,
                num_return_sequences=1,
                pad_token_id=tokenizer.eos_token_id
            )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"\n👤 Test Input: {test_input}")
        print(f"🎓 Teacher Response: {response}")

        print("\n" + "="*80)
        print("🎉 Setup Complete! Ready for Knowledge Distillation")
        print("="*80)
        print("\nNext Steps:")
        print("  1. ✅ Teacher model downloaded")
        print("  2. ⏳ Prepare conversation datasets")
        print("  3. ⏳ Build distillation trainer")
        print("  4. ⏳ Start training")
        print("\n")

        return True

    except Exception as e:
        print(f"\n❌ Error downloading teacher model: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = download_teacher_model()
    sys.exit(0 if success else 1)
