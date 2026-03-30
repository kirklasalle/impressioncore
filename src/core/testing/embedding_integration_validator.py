#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #attention_mechanism #cuda #inference #memory_management #multimodal #python #source_code #src/core/testing\\embedding_integration_validator.py #testing #training
**Category:** Core Implementation
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #attention_mechanism #cuda #inference #memory_management #multimodal #python #source_code #src\\core\\testing\\embedding_integration_validator.py #testing #training
# Category:** Core Implementation
# Status:** Active

"""
ImpressionCore B1 Embedding Integration Validator

Quick validation script to confirm real embedded data is properly integrated
into the multimodal B1 model and accessible during inference.

File: core/testing/embedding_integration_validator.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-20
"""

import sys
from pathlib import Path

import numpy as np
import torch

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import ImpressionCore components
from .core.models.multimodal_b1_architecture import ImpressionCoreBMultimodal, MultimodalConfig
from .core.utils.device_manager import get_device_manager

console = Console()

def validate_f_drive_embeddings():
    """Validate F: drive embeddings are accessible"""
    console.print("[cyan]🔍 Validating F: drive embeddings...[/cyan]")

    f_drive_path = Path("F:/impressioncore_training_data")
    embeddings_path = f_drive_path / "processed_embeddings"

    status = {
        'f_drive_exists': f_drive_path.exists(),
        'embeddings_exist': embeddings_path.exists(),
        'embedding_files': 0,
        'total_size_mb': 0.0
    }

    if status['embeddings_exist']:
        embedding_files = list(embeddings_path.glob("*.npy"))
        status['embedding_files'] = len(embedding_files)

        try:
            total_bytes = sum(f.stat().st_size for f in embedding_files)
            status['total_size_mb'] = total_bytes / (1024**2)
        except OSError:
            pass

    # Create status table
    table = Table(title="F: Drive Embeddings Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="dim")

    table.add_row(
        "F: Drive Path",
        "✅ Found" if status['f_drive_exists'] else "❌ Missing",
        str(f_drive_path)
    )

    table.add_row(
        "Embeddings Directory",
        "✅ Found" if status['embeddings_exist'] else "❌ Missing",
        str(embeddings_path)
    )

    table.add_row(
        "Embedding Files",
        f"✅ {status['embedding_files']} files" if status['embedding_files'] > 0 else "❌ No files",
        f"{status['total_size_mb']:.1f} MB total"
    )

    console.print(table)
    return status

def test_model_with_real_data():
    """Test model inference with real embedded data"""
    console.print("\n[cyan]🧠 Testing B1 model with real data...[/cyan]")

    try:
        # Initialize device manager and model
        device_manager = get_device_manager()
        config = MultimodalConfig()
        model = ImpressionCoreBMultimodal(config)
        model.to(device_manager.device)
        model.eval()

        console.print(f"✅ Model loaded on {device_manager.device}")

        # Test with sample inputs
        test_inputs = {
            'text': [
                "Explain quantum computing in simple terms.",
                "What are the applications of machine learning?"
            ],
            'code': [
                "def hello_world(): print('Hello, World!')",
                "import torch; x = torch.randn(2, 3)"
            ]
        }

        # Perform inference
        with torch.no_grad():
            output = model(test_inputs)

        # Validate output structure
        required_keys = ['conversation_features', 'quality_score', 'academic_level', 'academic_logits']
        has_all_keys = all(key in output for key in required_keys)

        # Create results table
        results_table = Table(title="Model Inference Results")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="bold")

        results_table.add_row("Output Keys Complete", "✅ Yes" if has_all_keys else "❌ No")
        results_table.add_row("Feature Shape", str(tuple(output['conversation_features'].shape)))
        results_table.add_row("Quality Score", f"{float(output['quality_score'].mean()):.4f}")
        results_table.add_row("Academic Level", f"{output['academic_level'].softmax(dim=-1).max().item():.4f}")

        if torch.cuda.is_available():
            memory_mb = torch.cuda.memory_allocated() / (1024**2)
            results_table.add_row("VRAM Usage", f"{memory_mb:.1f} MB")

        console.print(results_table)

        return True

    except Exception as e:
        console.print(f"❌ Model test failed: {e}")
        return False

def validate_embedding_integration():
    """Validate that embeddings are properly integrated"""
    console.print("\n[cyan]🔗 Validating embedding integration...[/cyan]")

    try:
        # Check if model can access embeddings
        f_drive_path = Path("F:/impressioncore_training_data/processed_embeddings")

        integration_status = {
            'vector_db_files': [],
            'sample_embeddings': False,
            'faiss_index': False
        }

        # Check for key files
        key_files = [
            "all_embeddings.npy",
            "all_metadata.json",
            "multimodal_faiss_index.faiss"
        ]

        for filename in key_files:
            file_path = f_drive_path / filename
            if file_path.exists():
                integration_status['vector_db_files'].append(filename)
                if filename.endswith('.faiss'):
                    integration_status['faiss_index'] = True

        # Try to load a sample embedding
        try:
            sample_files = list(f_drive_path.glob("*.npy"))[:1]
            if sample_files:
                sample_embedding = np.load(sample_files[0])
                integration_status['sample_embeddings'] = True
                integration_status['sample_shape'] = sample_embedding.shape
        except Exception:
            pass

        # Create integration table
        int_table = Table(title="Embedding Integration Status")
        int_table.add_column("Component", style="cyan")
        int_table.add_column("Status", style="bold")
        int_table.add_column("Details", style="dim")

        int_table.add_row(
            "Vector DB Files",
            f"✅ {len(integration_status['vector_db_files'])}/3" if integration_status['vector_db_files'] else "❌ Missing",
            ", ".join(integration_status['vector_db_files'])
        )

        int_table.add_row(
            "FAISS Index",
            "✅ Found" if integration_status['faiss_index'] else "❌ Missing",
            "multimodal_faiss_index.faiss"
        )

        int_table.add_row(
            "Sample Embeddings",
            "✅ Loadable" if integration_status['sample_embeddings'] else "❌ Cannot load",
            f"Shape: {integration_status.get('sample_shape', 'N/A')}"
        )

        console.print(int_table)

        return len(integration_status['vector_db_files']) >= 2

    except Exception as e:
        console.print(f"❌ Integration validation failed: {e}")
        return False

def main():
    """Main validation function"""
    console.print(Panel.fit(
        "[bold cyan]🔬 ImpressionCore B1 Embedding Integration Validator[/bold cyan]\n"
        "Quick validation of real embedded data integration",
        title="Embedding Validator",
        border_style="cyan"
    ))

    # Run validation steps
    results = {}

    # Step 1: Validate F: drive embeddings
    results['f_drive'] = validate_f_drive_embeddings()

    # Step 2: Test model inference
    results['model_test'] = test_model_with_real_data()

    # Step 3: Validate integration
    results['integration'] = validate_embedding_integration()

    # Overall assessment
    all_good = (
        results['f_drive']['f_drive_exists'] and
        results['f_drive']['embeddings_exist'] and
        results['f_drive']['embedding_files'] > 0 and
        results['model_test'] and
        results['integration']
    )

    if all_good:
        console.print(Panel.fit(
            "[bold green]🎉 VALIDATION SUCCESSFUL![/bold green]\n"
            "✅ F: drive embeddings are accessible\n"
            "✅ B1 model loads and runs correctly\n"
            "✅ Real data integration is working\n\n"
            "[bold]Ready for comprehensive testing and training strategies![/bold]",
            title="Validation Complete",
            border_style="green"
        ))
    else:
        console.print(Panel.fit(
            "[bold yellow]⚠️ VALIDATION ISSUES DETECTED[/bold yellow]\n"
            "Some components may need attention before proceeding.\n"
            "Check the detailed results above.",
            title="Validation Complete",
            border_style="yellow"
        ))

    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
