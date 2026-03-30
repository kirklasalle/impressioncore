#!/usr/bin/env python3
"""
Fix script for PhonemeEmbeddingConfig model_path attribute issue.
Adds missing model_path and related attributes to PhonemeEmbeddingConfig.
Enhanced with rich progress indicators for better user experience.
"""
from datetime import datetime
import sys
import os
import re

# Try to import rich for enhanced output (graceful fallback if not available)
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.panel import Panel
    from rich import print as rprint
    console = Console()
    use_rich = True
except ImportError:
    console = None
    use_rich = False
    rprint = print

def fix_phoneme_config_issue():
    """
    Fix PhonemeEmbeddingConfig missing model_path attribute.
    
    Adds model_path and related configuration attributes to enable
    Hugging Face model integration for phoneme processing.
    """
    file_path = r"D:\Projects\impressioncore\src\models\impressioncore-base\b1_unified_model.py"
    
    if use_rich:
        console.print(Panel.fit(
            "[bold blue]PhonemeEmbeddingConfig Fix Script[/bold blue]\n"
            "[green]Adding missing model_path attribute[/green]\n"
            f"[dim]Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
            border_style="blue"
        ))
    else:
        print("=== PhonemeEmbeddingConfig Fix Script ===")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        error_msg = f"Error: File not found - {file_path}"
        if use_rich:
            console.print(f"[red]{error_msg}[/red]")
        else:
            print(error_msg)
        sys.exit(1)
    
    try:
        if use_rich:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console
            ) as progress:
                # Read file
                task1 = progress.add_task("Reading B1 model file...", total=100)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                progress.update(task1, completed=25)
                
                # Find PhonemeEmbeddingConfig class
                progress.update(task1, description="Locating PhonemeEmbeddingConfig...")
                
                # Pattern to find the __init__ method of PhonemeEmbeddingConfig
                pattern = r'(class PhonemeEmbeddingConfig:.*?def __init__\(self[^)]*\):.*?)(        self\.custom_tokenizer_characters = custom_tokenizer_characters)'
                
                if re.search(pattern, content, re.DOTALL):
                    progress.update(task1, completed=50)
                    progress.update(task1, description="Found PhonemeEmbeddingConfig, applying fix...")
                    
                    # Add the missing attributes
                    replacement = r'\1\2\n        self.model_path = getattr(self, "model_path", "microsoft/wavlm-base-plus")\n        self.use_huggingface = getattr(self, "use_huggingface", True)\n        self.device = getattr(self, "device", "auto")\n        self.memory_optimization = getattr(self, "memory_optimization", True)'
                    
                    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                    progress.update(task1, completed=75)
                    
                    # Write back
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    progress.update(task1, description="✓ Added missing model_path attributes", completed=100)
                    
                    console.print("[green]✓ Successfully added model_path and related attributes to PhonemeEmbeddingConfig[/green]")
                else:
                    # Alternative approach - simple text replacement
                    progress.update(task1, description="Using alternative fix approach...")
                    old_text = "self.custom_tokenizer_characters = custom_tokenizer_characters"
                    new_text = """self.custom_tokenizer_characters = custom_tokenizer_characters
        # Add missing model_path and related attributes for Hugging Face integration
        self.model_path = getattr(self, 'model_path', 'microsoft/wavlm-base-plus')
        self.use_huggingface = getattr(self, 'use_huggingface', True)
        self.device = getattr(self, 'device', 'auto')
        self.memory_optimization = getattr(self, 'memory_optimization', True)"""
                    
                    if old_text in content:
                        updated_content = content.replace(old_text, new_text)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                        progress.update(task1, description="✓ Applied alternative fix", completed=100)
                        console.print("[green]✓ Successfully added model_path attributes using alternative method[/green]")
                    else:
                        progress.update(task1, description="❌ Could not locate target code", completed=100)
                        console.print("[red]❌ Could not locate PhonemeEmbeddingConfig.__init__ method[/red]")
                        
        else:
            print("Reading B1 model file...")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print("Applying fix for PhonemeEmbeddingConfig...")
            old_text = "self.custom_tokenizer_characters = custom_tokenizer_characters"
            new_text = """self.custom_tokenizer_characters = custom_tokenizer_characters
        # Add missing model_path and related attributes for Hugging Face integration
        self.model_path = getattr(self, 'model_path', 'microsoft/wavlm-base-plus')
        self.use_huggingface = getattr(self, 'use_huggingface', True)
        self.device = getattr(self, 'device', 'auto')
        self.memory_optimization = getattr(self, 'memory_optimization', True)"""
            
            if old_text in content:
                updated_content = content.replace(old_text, new_text)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print("✓ Successfully added model_path attributes to PhonemeEmbeddingConfig")
            else:
                print("❌ Could not locate target code in PhonemeEmbeddingConfig")
            
    except Exception as e:
        error_msg = f"Error during fix operation: {e}"
        if use_rich:
            console.print(f"[red]{error_msg}[/red]")
        else:
            print(error_msg)
        sys.exit(1)

if __name__ == "__main__":
    fix_phoneme_config_issue()
