#!/usr/bin/env python3
"""
Manual fix for PhonemeEmbeddingConfig model_path issue.
Direct text replacement approach for the specific error.
"""
import os

def manual_fix_phoneme_config():
    """
    Manual fix for PhonemeEmbeddingConfig missing attributes.
    Uses direct file manipulation to add the required attributes.
    """
    file_path = r"D:\Projects\impressioncore\src\models\impressioncore-base\b1_unified_model.py"
    
    print("=== Manual PhonemeEmbeddingConfig Fix ===")
    print(f"Target file: {file_path}")
    
    # Read the entire file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and add the attributes right after the PhonemeExtractor initialization
    # Look for the line that causes the error and add a workaround before it
    
    # Strategy: Add the missing attributes to the config object before PhonemeExtractor is called
    old_line = "        self.phoneme_extractor = PhonemeExtractor(self.phoneme_embedding_config)"
    new_lines = """        # Ensure PhonemeEmbeddingConfig has all required attributes
        if not hasattr(self.phoneme_embedding_config, 'model_path'):
            self.phoneme_embedding_config.model_path = "microsoft/wavlm-base-plus"
        if not hasattr(self.phoneme_embedding_config, 'use_huggingface'):
            self.phoneme_embedding_config.use_huggingface = True
        if not hasattr(self.phoneme_embedding_config, 'device'):
            self.phoneme_embedding_config.device = "auto"
        if not hasattr(self.phoneme_embedding_config, 'memory_optimization'):
            self.phoneme_embedding_config.memory_optimization = True
        
        self.phoneme_extractor = PhonemeExtractor(self.phoneme_embedding_config)"""
    
    if old_line in content:
        updated_content = content.replace(old_line, new_lines)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✓ Successfully added missing attributes to PhonemeEmbeddingConfig")
        print("✓ Added: model_path, use_huggingface, device, memory_optimization")
        return True
    else:
        print("❌ Could not find target line for PhonemeExtractor initialization")
        print("Manual inspection required")
        return False

if __name__ == "__main__":
    success = manual_fix_phoneme_config()
    if success:
        print("\n🚀 Ready to test: python -m src.models.impressioncore-base.b1_unified_model")
    else:
        print("\n⚠️  Manual code inspection required")
